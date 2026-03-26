#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书任务轮询器 — 从本地队列或远程中继获取待处理任务

用法:
  python feishu_poll.py              # 轮询一次，输出待处理任务 JSON
  python feishu_poll.py --complete <task_id> [--result "..."] [--error "..."]
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import requests
except ImportError:
    print("需要 requests: pip install requests")
    sys.exit(1)

RELAY_URL = os.environ.get("FEISHU_RELAY_URL", "")
RELAY_API_KEY = os.environ.get("FEISHU_RELAY_API_KEY", "")
PROXY = os.environ.get("FEISHU_PROXY", "http://127.0.0.1:7897")

# 本地任务队列目录（与 feishu_ws_client.py 共享）
TASK_QUEUE_DIR = Path(os.environ.get(
    "FEISHU_TASK_QUEUE_DIR",
    os.path.expanduser("~/.claude/skills/feishu-integration/task_queue")
))

COMMAND_SKILL_MAP = {
    "analyze":  "amazon-product-phase1-research",
    "validate": "amazon-product-phase2-demand-validator",
    "mvp":      "amazon-product-phase3-mvp-blueprint",
    "design":   "amazon-product-phase4-design-research",
    "concept":  "amazon-product-phase5-design-generation",
    "review":   "amazon-product-phase6-launch-review",
    "iterate":  "amazon-product-phase7-iteration-playbook",
    "scale":    "amazon-product-phase8-scale-decision",
}


def _req(method, path, json_data=None):
    """Authenticated request to relay, with proxy fallback."""
    url = f"{RELAY_URL.rstrip('/')}{path}"
    headers = {"Authorization": f"Bearer {RELAY_API_KEY}"}
    kw = {"headers": headers, "timeout": 15}
    if json_data:
        kw["json"] = json_data
    try:
        return getattr(requests, method)(url, **kw).json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        try:
            kw["proxies"] = {"https": PROXY, "http": PROXY}
            return getattr(requests, method)(url, **kw).json()
        except Exception as e:
            return {"error": str(e)}


def fetch_pending():
    """获取待处理任务 — 优先读本地队列，其次读远程中继"""
    # 本地队列（来自 feishu_ws_client.py 长连接）
    local_tasks = _fetch_local_pending()
    if local_tasks:
        return local_tasks

    # 远程中继（Cloudflare Worker，如果配了的话）
    if RELAY_URL and RELAY_API_KEY:
        r = _req("get", "/tasks?status=pending")
        return r.get("tasks", []) if r and "tasks" in r else []

    return []


def _fetch_local_pending():
    """从本地任务队列目录读取 pending 任务"""
    if not TASK_QUEUE_DIR.exists():
        return []
    tasks = []
    for f in sorted(TASK_QUEUE_DIR.glob("task_*.json")):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                task = json.load(fh)
                if task.get("status") == "pending":
                    tasks.append(task)
        except Exception:
            pass
    return tasks


def claim(task_id):
    """认领任务（状态从 pending → processing）"""
    return _req("post", f"/tasks/{task_id}/claim")


def complete(task_id, result=None, error=None):
    """完成任务（本地或远程）"""
    # 先尝试本地
    task_file = TASK_QUEUE_DIR / f"{task_id}.json"
    if task_file.exists():
        with open(task_file, 'r', encoding='utf-8') as f:
            task = json.load(f)
        task["status"] = "failed" if error else "completed"
        task["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        task["result"] = result
        task["error"] = error
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task, f, ensure_ascii=False, indent=2)
        return {"ok": True, "source": "local"}

    # 远程
    if RELAY_URL and RELAY_API_KEY:
        p = {}
        if result:
            p["result"] = result
        if error:
            p["error"] = error
            p["status"] = "failed"
        return _req("post", f"/tasks/{task_id}/complete", json_data=p)

    return {"error": "task not found"}


def send_ack(task):
    """向用户发送'正在处理'确认消息"""
    try:
        from feishu_sdk import FeishuMessenger, FeishuAuth
        cmd = task.get("command", "")
        args = task.get("args", "")
        skill = COMMAND_SKILL_MAP.get(cmd, cmd)
        text = (
            f"🔄 正在处理你的请求...\n"
            f"命令: {cmd}\n"
            f"参数: {args}\n"
            f"技能: {skill}\n\n"
            f"请稍候，分析完成后会自动推送结果。"
        )
        auth = FeishuAuth(
            app_id=os.environ.get("FEISHU_APP_ID"),
            app_secret=os.environ.get("FEISHU_APP_SECRET")
        )
        m = FeishuMessenger(auth)
        uid = task.get("user_open_id", "")
        if uid:
            m.send_to_user(uid, "text", {"text": text}, id_type="open_id")
        elif task.get("chat_id"):
            m.send_to_chat(task["chat_id"], "text", {"text": text})
    except Exception as e:
        pass  # 确认消息发送失败不影响任务执行


def send_help(task):
    """发送帮助信息"""
    try:
        from feishu_sdk import FeishuMessenger, FeishuAuth
        text = (
            "📖 可用命令:\n"
            "/analyze <产品> [站点]  — Phase 1 选品分析\n"
            "/validate <产品> <特性>  — Phase 2 需求验证\n"
            "/mvp <产品>             — Phase 3 MVP蓝图\n"
            "/design <产品>          — Phase 4 设计调研\n"
            "/concept <产品>         — Phase 5 概念图\n"
            "/review <产品> <ASIN>   — Phase 6 上架复盘\n"
            "/iterate <产品> <ASIN>  — Phase 7 迭代方案\n"
            "/scale <产品> <ASIN>    — Phase 8 规模化决策\n"
            "/status                 — 查看任务队列\n"
            "/help                   — 显示帮助\n\n"
            '💡 也可以直接发自然语言，如"帮我分析 steamer"'
        )
        auth = FeishuAuth(
            app_id=os.environ.get("FEISHU_APP_ID"),
            app_secret=os.environ.get("FEISHU_APP_SECRET")
        )
        m = FeishuMessenger(auth)
        uid = task.get("user_open_id", "")
        if uid:
            m.send_to_user(uid, "text", {"text": text}, id_type="open_id")
    except Exception:
        pass


def send_status(task):
    """发送当前队列状态"""
    try:
        from feishu_sdk import FeishuMessenger, FeishuAuth
        tasks = fetch_pending()
        if tasks:
            lines = [f"📋 当前待处理任务: {len(tasks)} 个\n"]
            for t in tasks[:5]:
                lines.append(f"  • [{t['command']}] {t['args']} — {t['created_at'][:19]}")
            if len(tasks) > 5:
                lines.append(f"  ... 还有 {len(tasks) - 5} 个")
            text = "\n".join(lines)
        else:
            text = "✅ 当前没有待处理任务。"
        auth = FeishuAuth(
            app_id=os.environ.get("FEISHU_APP_ID"),
            app_secret=os.environ.get("FEISHU_APP_SECRET")
        )
        m = FeishuMessenger(auth)
        uid = task.get("user_open_id", "")
        if uid:
            m.send_to_user(uid, "text", {"text": text}, id_type="open_id")
    except Exception:
        pass


def poll_once():
    """
    轮询一次：获取待处理任务，自动处理 help/status，
    返回需要 Claude Code 执行的任务列表。
    """
    tasks = fetch_pending()
    if not tasks:
        print(f"[{time.strftime('%H:%M:%S')}] No pending tasks.")
        return []

    print(f"[{time.strftime('%H:%M:%S')}] Found {len(tasks)} pending task(s).")
    actionable = []

    for task in tasks:
        tid = task["id"]
        cmd = task.get("command", "freeform")

        # help/status 自动处理，不需要 Claude Code
        if cmd == "status":
            claim(tid)
            send_status(task)
            complete(tid, result="Status sent")
            continue
        if cmd == "help":
            claim(tid)
            send_help(task)
            complete(tid, result="Help sent")
            continue

        # 认领任务
        cr = claim(tid)
        if not cr or not cr.get("ok"):
            print(f"  Could not claim {tid}")
            continue

        # 发送确认消息
        send_ack(task)

        # 构建任务信息供 Claude Code 执行
        skill = COMMAND_SKILL_MAP.get(cmd)
        actionable.append({
            "task_id": tid,
            "command": cmd,
            "args": task.get("args", ""),
            "skill": skill,
            "prompt": f"/{skill} {task.get('args', '')}" if skill else task.get("raw_text", ""),
            "user_open_id": task.get("user_open_id", ""),
            "chat_id": task.get("chat_id", ""),
        })

    return actionable


def main():
    parser = argparse.ArgumentParser(description="飞书中继轮询器")
    parser.add_argument("--complete", help="完成指定任务 ID")
    parser.add_argument("--result", help="任务结果")
    parser.add_argument("--error", help="任务错误信息")
    args = parser.parse_args()

    if not RELAY_URL and not TASK_QUEUE_DIR.exists():
        print("ERROR: No task source available.")
        print("Either run feishu_ws_client.py (local WebSocket), or set FEISHU_RELAY_URL.")
        sys.exit(1)

    if args.complete:
        r = complete(args.complete, result=args.result, error=args.error)
        print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
        return

    results = poll_once()
    # 输出 JSON 供 Claude Code 解析
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
