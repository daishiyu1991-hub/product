#!/usr/bin/env python3
"""
daily_reminder.py — 每日日程飞书推送
用法:
  python3 daily_reminder.py              # 推送今日日程到飞书
  python3 daily_reminder.py tomorrow     # 推送明日日程（前一天晚上预告）

可配合 Windows 任务计划程序定时执行：
  每天 08:00 推送今日日程
  每天 21:00 推送明日预告
"""

import sys
import io
import json
import hashlib
import hmac
import base64
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 配置
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/8512b6b2-c0e4-4c35-897a-9e1d1c888c92"
WEBHOOK_SECRET = "K4sFvPUgHZVhD2sT5gFSZc"
HELPER_SCRIPT = Path(r"C:\Users\Administrator\.claude\skills\schedule-manager\scripts\schedule_helper.py")
PYTHON = r"C:\Program Files\Python312\python.exe"

WEEKDAYS_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def gen_sign(timestamp, secret):
    """生成飞书 Webhook 签名"""
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def call_helper(command):
    """调用 schedule_helper.py"""
    import subprocess
    result = subprocess.run(
        [PYTHON, str(HELPER_SCRIPT), command],
        capture_output=True, text=True, encoding='utf-8'
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return None
    return json.loads(result.stdout)


def build_today_card(data):
    """构建今日日程飞书卡片"""
    now = datetime.now()
    date_cn = f"{now.year}年{now.month}月{now.day}日"
    weekday = WEEKDAYS_CN[now.weekday()]

    # 日程表
    schedule_text = ""
    if data.get("schedule"):
        for item in data["schedule"]:
            note = f" — {item['note']}" if item.get('note') else ""
            schedule_text += f"**{item['time']}** {item['event']}{note}\n"
    else:
        schedule_text = "今天没有特殊日程安排\n"

    # 待办
    todo_text = ""
    if data.get("todos"):
        for t in data["todos"]:
            todo_text += f"☐ {t['event']}（截止 {t['deadline']}）\n"

    # 构建卡片
    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"日安主人 | {date_cn} {weekday}"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**今日日程**\n{schedule_text}"
                    }
                }
            ]
        }
    }

    if todo_text:
        card["card"]["elements"].append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**今日待办**\n{todo_text}"
            }
        })

    card["card"]["elements"].append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": "祝主人今天高效愉快！"
        }
    })

    return card


def build_tomorrow_card(data):
    """构建明日预告飞书卡片"""
    tomorrow = datetime.now() + timedelta(days=1)
    date_cn = f"{tomorrow.month}月{tomorrow.day}日"
    weekday = WEEKDAYS_CN[tomorrow.weekday()]

    schedule_text = ""
    if data.get("schedule"):
        for item in data["schedule"]:
            note = f" — {item['note']}" if item.get('note') else ""
            schedule_text += f"**{item['time']}** {item['event']}{note}\n"
    else:
        schedule_text = "明天没有特殊日程安排\n"

    todo_text = ""
    if data.get("todos"):
        for t in data["todos"]:
            todo_text += f"☐ {t['event']}（截止 {t['deadline']}）\n"

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"明日预告 | {date_cn} {weekday}"
                },
                "template": "purple"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**明日日程**\n{schedule_text}"
                    }
                }
            ]
        }
    }

    if todo_text:
        card["card"]["elements"].append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**待完成**\n{todo_text}"
            }
        })

    card["card"]["elements"].append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": "早点休息，明天继续加油！"
        }
    })

    return card


def send_to_feishu(card):
    """发送卡片到飞书"""
    timestamp = str(int(time.time()))
    sign = gen_sign(timestamp, WEBHOOK_SECRET)
    card["timestamp"] = timestamp
    card["sign"] = sign

    data = json.dumps(card, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("code") == 0:
                print("推送成功！")
            else:
                print(f"推送失败: {result}")
    except urllib.error.URLError as e:
        print(f"网络错误: {e}")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "today"

    if mode == "today":
        data = call_helper("today")
        if data:
            card = build_today_card(data)
            send_to_feishu(card)
    elif mode == "tomorrow":
        data = call_helper("tomorrow")
        if data:
            card = build_tomorrow_card(data)
            send_to_feishu(card)
    else:
        print(f"未知模式: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
