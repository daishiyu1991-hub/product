#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书长连接客户端 — 接收飞书消息并存入本地任务队列
================================================================
使用飞书官方 SDK 的 WebSocket 长连接模式，无需公网服务器。
本地运行即可接收飞书机器人的消息。

用法:
  python feishu_ws_client.py              # 启动长连接，持续监听
  python feishu_ws_client.py --daemon     # 后台运行模式
"""

import json
import os
import sys
import io
import time
import threading
from pathlib import Path

# Windows GBK 编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import lark_oapi as lark
    from lark_oapi.api.im.v1 import (
        P2ImMessageReceiveV1,
        ReplyMessageRequest,
        ReplyMessageRequestBody,
    )
except ImportError:
    print("需要安装飞书 SDK: pip install lark-oapi")
    sys.exit(1)

# =========================================================================
# 配置
# =========================================================================

APP_ID = os.environ.get("FEISHU_APP_ID", "cli_a94a9b7561b89cb3")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "BWg4rIV5rbhd9do0N1wYmBQcDLne6cat")

# AI API 配置（用于即时回复自由对话）
AI_API_BASE = os.environ.get("GEMINI_API_BASE", "https://new.suxi.ai")
AI_API_KEY = os.environ.get("KEY", "sk-DDlvJ0LEbYpjfzKHotRfcNY4taKqc290t9O6G7NOTWSBG5KL")
AI_MODEL = os.environ.get("AI_CHAT_MODEL", "gpt-4o")
AI_PROXY = os.environ.get("FEISHU_PROXY", "http://127.0.0.1:7897")

# 本地任务队列文件
TASK_QUEUE_DIR = Path(os.environ.get(
    "FEISHU_TASK_QUEUE_DIR",
    os.path.expanduser("~/.claude/skills/feishu-integration/task_queue")
))

# 命令→技能映射
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


# =========================================================================
# AI 即时对话（用于 freeform 消息）
# =========================================================================

# 每个用户的对话历史（内存中，重启清空）
_chat_histories = {}  # user_open_id -> [{"role": "user"/"assistant", "content": "..."}]

def ai_chat(user_id: str, message: str) -> str:
    """调用 AI API 生成回复，带上下文记忆"""
    import requests as req

    # 获取/初始化对话历史
    if user_id not in _chat_histories:
        _chat_histories[user_id] = []
    history = _chat_histories[user_id]

    # 添加用户消息
    history.append({"role": "user", "content": message})

    # 保留最近 20 轮对话
    if len(history) > 40:
        history[:] = history[-40:]

    # 构建请求
    messages = [
        {"role": "system", "content": (
            "你是一个亚马逊产品开发助手机器人，运行在飞书上。"
            "你可以帮用户回答关于亚马逊选品、产品开发、竞品分析等问题。"
            "回答要简洁实用，适合在聊天中阅读。"
            "如果用户想做深度分析，告诉他们可以使用以下命令：\n"
            "/analyze <产品> — 选品分析\n"
            "/validate <产品> <特性> — 需求验证\n"
            "/help — 查看所有命令"
        )}
    ] + history

    try:
        resp = req.post(
            f"{AI_API_BASE}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {AI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": AI_MODEL,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7,
            },
            proxies={"https": AI_PROXY, "http": AI_PROXY},
            timeout=30,
        )
        data = resp.json()
        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if reply:
            history.append({"role": "assistant", "content": reply})
            return reply
        else:
            return f"AI 返回为空: {data}"
    except Exception as e:
        return f"AI 调用失败: {e}"


# =========================================================================
# 命令解析器
# =========================================================================

def parse_command(text: str) -> dict:
    """解析用户消息为命令"""
    t = text.strip()

    # 斜杠命令
    import re
    patterns = [
        (r"^/(analyze|分析|选品)\s+(.+)", "analyze"),
        (r"^/(validate|验证|需求验证)\s+(.+)", "validate"),
        (r"^/(mvp|蓝图)\s+(.+)", "mvp"),
        (r"^/(design|设计调研)\s+(.+)", "design"),
        (r"^/(concept|概念图)\s+(.+)", "concept"),
        (r"^/(review|复盘)\s+(.+)", "review"),
        (r"^/(iterate|迭代)\s+(.+)", "iterate"),
        (r"^/(scale|规模化)\s+(.+)", "scale"),
    ]

    for pattern, cmd in patterns:
        m = re.match(pattern, t, re.IGNORECASE)
        if m:
            return {"command": cmd, "args": m.group(2).strip()}

    # 无参数命令
    if re.match(r"^/(status|状态)$", t, re.IGNORECASE):
        return {"command": "status", "args": ""}
    if re.match(r"^/(help|帮助)$", t, re.IGNORECASE):
        return {"command": "help", "args": ""}

    # 自然语言
    nl_patterns = [
        (r"(?:分析一下|帮我分析|分析|看看)\s*(.+)", "analyze"),
        (r"(?:验证一下|帮我验证|验证)\s*(.+)", "validate"),
        (r"(?:复盘一下|帮我复盘|复盘)\s*(.+)", "review"),
    ]
    for pattern, cmd in nl_patterns:
        m = re.match(pattern, t)
        if m:
            return {"command": cmd, "args": m.group(1).strip()}

    return {"command": "freeform", "args": t}


# =========================================================================
# 任务队列（本地 JSON 文件）
# =========================================================================

def ensure_queue_dir():
    """确保任务队列目录存在"""
    TASK_QUEUE_DIR.mkdir(parents=True, exist_ok=True)


def save_task(task: dict):
    """保存任务到本地文件"""
    ensure_queue_dir()
    task_file = TASK_QUEUE_DIR / f"{task['id']}.json"
    with open(task_file, 'w', encoding='utf-8') as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    print(f"  Task saved: {task_file.name}")


def get_pending_tasks() -> list:
    """获取所有待处理任务"""
    ensure_queue_dir()
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


def complete_task(task_id: str, result: str = None, error: str = None):
    """标记任务完成"""
    ensure_queue_dir()
    task_file = TASK_QUEUE_DIR / f"{task_id}.json"
    if not task_file.exists():
        return
    with open(task_file, 'r', encoding='utf-8') as f:
        task = json.load(f)
    task["status"] = "failed" if error else "completed"
    task["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    task["result"] = result
    task["error"] = error
    with open(task_file, 'w', encoding='utf-8') as f:
        json.dump(task, f, ensure_ascii=False, indent=2)


# =========================================================================
# 飞书消息回复
# =========================================================================

def reply_text(client, message_id: str, text: str):
    """回复飞书消息"""
    try:
        body = ReplyMessageRequestBody.builder() \
            .msg_type("text") \
            .content(json.dumps({"text": text})) \
            .build()
        req = ReplyMessageRequest.builder() \
            .message_id(message_id) \
            .request_body(body) \
            .build()
        resp = client.im.v1.message.reply(req)
        if not resp.success():
            print(f"  Reply failed: {resp.code} {resp.msg}")
    except Exception as e:
        print(f"  Reply error: {e}")


def send_help(client, message_id: str):
    """发送帮助信息"""
    text = (
        "📖 可用命令:\n"
        "/analyze <产品> — Phase 1 选品分析\n"
        "/validate <产品> <特性> — Phase 2 需求验证\n"
        "/mvp <产品> — Phase 3 MVP蓝图\n"
        "/design <产品> — Phase 4 设计调研\n"
        "/concept <产品> — Phase 5 概念图\n"
        "/review <产品> <ASIN> — Phase 6 复盘\n"
        "/iterate <产品> <ASIN> — Phase 7 迭代\n"
        "/scale <产品> <ASIN> — Phase 8 规模化\n"
        "/status — 查看队列\n"
        "/help — 帮助\n\n"
        '💡 也可发自然语言，如"分析一下 steamer"'
    )
    reply_text(client, message_id, text)


def send_status(client, message_id: str):
    """发送队列状态"""
    tasks = get_pending_tasks()
    if tasks:
        lines = [f"📋 待处理任务: {len(tasks)} 个\n"]
        for t in tasks[:5]:
            lines.append(f"  • [{t['command']}] {t['args']}")
        text = "\n".join(lines)
    else:
        text = "✅ 当前没有待处理任务。"
    reply_text(client, message_id, text)


# =========================================================================
# 消息事件处理器
# =========================================================================

def make_handler(client):
    """创建消息事件处理器"""

    # 去重集合（防止重复处理）
    seen_events = set()

    def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1):
        try:
            event = data.event
            msg = event.message
            sender = event.sender

            # 去重
            event_id = data.header.event_id if data.header else ""
            if event_id in seen_events:
                return
            seen_events.add(event_id)
            # 清理旧事件（保留最近 1000 个）
            if len(seen_events) > 1000:
                seen_events.clear()

            # 忽略非文本消息
            if msg.message_type != "text":
                return

            # 解析文本
            try:
                content = json.loads(msg.content or "{}")
                text = content.get("text", "")
            except Exception:
                text = msg.content or ""

            # 去掉 @提及
            import re
            text = re.sub(r"@_user_\d+", "", text).strip()
            if not text:
                return

            print(f"\n📩 收到消息: \"{text}\" (from {sender.sender_id.open_id})")

            # 解析命令
            parsed = parse_command(text)
            cmd = parsed["command"]
            args = parsed["args"]

            # help/status 立即回复
            if cmd == "help":
                send_help(client, msg.message_id)
                return
            if cmd == "status":
                send_status(client, msg.message_id)
                return

            # freeform 消息 → 调用 claude CLI 即时回复
            if cmd == "freeform":
                print(f"  → Claude CLI 对话模式...")
                def do_ai_reply():
                    try:
                        import subprocess
                        claude_path = os.path.join(os.environ.get("APPDATA", ""), "npm", "claude.cmd")
                        if not os.path.exists(claude_path):
                            claude_path = "claude"  # fallback
                        result = subprocess.run(
                            [claude_path, "-p", text, "--model", "opus"],
                            capture_output=True, text=True, timeout=120,
                            encoding='utf-8', errors='replace'
                        )
                        ai_reply = result.stdout.strip()
                        if not ai_reply:
                            ai_reply = result.stderr.strip() or "无回复"
                        # 飞书消息限制，截断过长回复
                        if len(ai_reply) > 3000:
                            ai_reply = ai_reply[:3000] + "\n\n...(回复过长已截断)"
                        reply_text(client, msg.message_id, ai_reply)
                        print(f"  → 回复完成 ({len(ai_reply)} 字)")
                    except subprocess.TimeoutExpired:
                        reply_text(client, msg.message_id, "回复超时，请稍后再试或简化问题。")
                    except Exception as e:
                        reply_text(client, msg.message_id, f"回复失败: {e}")
                        print(f"  → 回复失败: {e}")
                threading.Thread(target=do_ai_reply, daemon=True).start()
                return

            # 分析命令（/analyze 等）→ 存入队列等 Claude Code 处理
            task_id = f"task_{int(time.time())}_{os.urandom(3).hex()}"
            skill = COMMAND_SKILL_MAP.get(cmd)
            task = {
                "id": task_id,
                "status": "pending",
                "command": cmd,
                "args": args,
                "skill": skill,
                "prompt": f"/{skill} {args}" if skill else text,
                "raw_text": text,
                "user_open_id": sender.sender_id.open_id or "",
                "chat_id": msg.chat_id or "",
                "message_id": msg.message_id or "",
                "chat_type": msg.chat_type or "",
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "completed_at": None,
                "result": None,
                "error": None,
            }
            save_task(task)

            # 回复确认
            skill_name = skill or cmd
            reply_text(
                client, msg.message_id,
                f"✅ 任务已收到！\n命令: {cmd}\n参数: {args}\n\n"
                f"💡 Claude Code 会在下次轮询时自动处理。\n"
                f"发 /status 查看队列。"
            )

            print(f"  → Task {task_id}: {cmd} \"{args}\" → {skill_name}")

        except Exception as e:
            print(f"  Handler error: {e}")
            import traceback
            traceback.print_exc()

    return do_p2_im_message_receive_v1


# =========================================================================
# 主程序
# =========================================================================

def start_client():
    """启动飞书长连接客户端"""
    print("=" * 60)
    print("飞书长连接客户端 — 接收消息并存入本地任务队列")
    print("=" * 60)
    print(f"App ID: {APP_ID}")
    print(f"任务队列: {TASK_QUEUE_DIR}")
    print()

    # 创建客户端
    client = lark.Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .log_level(lark.LogLevel.INFO) \
        .build()

    # 创建事件处理器
    handler = make_handler(client)

    # 注册事件处理器
    event_handler = lark.EventDispatcherHandler.builder("", "") \
        .register_p2_im_message_receive_v1(handler) \
        .build()

    # 创建长连接客户端
    ws_client = lark.ws.Client(
        APP_ID,
        APP_SECRET,
        event_handler=event_handler,
        log_level=lark.LogLevel.INFO,
    )

    print("🔌 正在连接飞书长连接服务...")
    print("📡 连接成功后，在飞书中给机器人发消息即可。")
    print("   按 Ctrl+C 停止。")
    print()

    # 启动（阻塞）
    ws_client.start()


if __name__ == "__main__":
    start_client()
