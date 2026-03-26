#!/usr/bin/env python3
"""
schedule_helper.py — 日程管理引擎
用法:
  python3 schedule_helper.py today          # 今日日程（JSON）
  python3 schedule_helper.py tomorrow       # 明日日程
  python3 schedule_helper.py week           # 本周日程
  python3 schedule_helper.py conflicts "15:00" "16:00" "2026-03-28"  # 冲突检测
  python3 schedule_helper.py expired        # 过期未完成待办
  python3 schedule_helper.py roll_week      # 生成下周模板
  python3 schedule_helper.py info           # 当前日期信息
"""

import sys
import re
import json
import io
from datetime import datetime, timedelta
from pathlib import Path

# Fix Windows console UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SCHEDULE_FILE = Path(r"C:\Users\Administrator\metabot-workspace\.claude\memory\schedule.md")
WEEKDAYS_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def read_schedule():
    """读取 schedule.md 原文"""
    if not SCHEDULE_FILE.exists():
        return ""
    return SCHEDULE_FILE.read_text(encoding="utf-8")


def get_date_info():
    """返回当前日期的完整信息"""
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "date_cn": f"{now.year}年{now.month}月{now.day}日",
        "weekday": WEEKDAYS_CN[now.weekday()],
        "weekday_num": now.weekday(),  # 0=周一
        "month_day": f"{now.month}/{now.day}",
        "time": now.strftime("%H:%M"),
    }


def parse_daily_fixed(content):
    """解析每日固定日程"""
    items = []
    section = False
    for line in content.split("\n"):
        if "## 每日固定日程" in line:
            section = True
            continue
        if section and line.startswith("## "):
            break
        if section and "|" in line and "时间" not in line and "---" not in line:
            cols = [c.strip() for c in line.split("|") if c.strip()]
            if len(cols) >= 2:
                items.append({
                    "time": cols[0],
                    "event": cols[1],
                    "note": cols[2] if len(cols) > 2 else "",
                    "type": "daily_fixed"
                })
    return items


def parse_weekly_section(content, target_date):
    """解析本周日程中指定日期的事项"""
    items = []
    day = target_date.day
    month = target_date.month
    weekday = WEEKDAYS_CN[target_date.weekday()]

    # 匹配 "### 周三 3/26" 格式
    pattern = rf"###\s*{weekday}\s*{month}/{day}"
    lines = content.split("\n")
    in_section = False

    for line in lines:
        if re.search(pattern, line):
            in_section = True
            continue
        if in_section and line.startswith("### "):
            break
        if in_section and "|" in line and "时间" not in line and "---" not in line:
            cols = [c.strip() for c in line.split("|") if c.strip()]
            if len(cols) >= 2:
                items.append({
                    "time": cols[0],
                    "event": cols[1],
                    "note": cols[2] if len(cols) > 2 else "",
                    "type": "weekly"
                })
    return items


def parse_todos(content):
    """解析临时待办"""
    items = []
    section = False
    for line in content.split("\n"):
        if "## 临时待办" in line:
            section = True
            continue
        if section and line.startswith("## "):
            break
        if section and "|" in line and "日期" not in line and "---" not in line:
            cols = [c.strip() for c in line.split("|") if c.strip()]
            if len(cols) >= 3:
                items.append({
                    "deadline": cols[0],
                    "event": cols[1],
                    "status": cols[2],
                })
    return items


def parse_milestones(content):
    """解析里程碑"""
    items = []
    section = False
    for line in content.split("\n"):
        if "## 里程碑追踪" in line:
            section = True
            continue
        if section and line.startswith("## "):
            break
        if section and "|" in line and "---" not in line and "截止" not in line:
            cols = [c.strip() for c in line.split("|") if c.strip()]
            if len(cols) >= 2:
                items.append({
                    "deadline": cols[0],
                    "goal": cols[1],
                    "progress": cols[2] if len(cols) > 2 else "",
                })
    return items


def get_day_schedule(target_date):
    """获取指定日期的完整日程"""
    content = read_schedule()
    daily_fixed = parse_daily_fixed(content)
    weekly_items = parse_weekly_section(content, target_date)
    todos = parse_todos(content)

    # 筛选截止今天或之前的待办
    today_str = f"{target_date.month}/{target_date.day}"
    relevant_todos = []
    for t in todos:
        if t["status"] == "待办":
            # 解析 "3/26前" 格式
            m = re.match(r"(\d+)/(\d+)", t["deadline"])
            if m:
                todo_month = int(m.group(1))
                todo_day = int(m.group(2))
                todo_date = target_date.replace(month=todo_month, day=todo_day)
                if todo_date <= target_date:
                    relevant_todos.append(t)

    # 合并并按时间排序
    all_items = daily_fixed + weekly_items

    def sort_key(item):
        t = item.get("time", "")
        m = re.match(r"(\d{1,2}):(\d{2})", t)
        if m:
            return int(m.group(1)) * 60 + int(m.group(2))
        if "上午" in t:
            return 540  # 9:00
        if "下午" in t or "白天" in t:
            return 780  # 13:00
        if "晚上" in t:
            return 1140  # 19:00
        return 1440  # 末尾

    all_items.sort(key=sort_key)

    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "date_cn": f"{target_date.year}年{target_date.month}月{target_date.day}日",
        "weekday": WEEKDAYS_CN[target_date.weekday()],
        "schedule": all_items,
        "todos": relevant_todos,
    }


def check_conflicts(time_start, time_end, date_str):
    """检查指定时间段是否与已有日程冲突"""
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    day_schedule = get_day_schedule(target_date)

    def to_minutes(t):
        m = re.match(r"(\d{1,2}):(\d{2})", t)
        if m:
            return int(m.group(1)) * 60 + int(m.group(2))
        return None

    new_start = to_minutes(time_start)
    new_end = to_minutes(time_end)
    if new_start is None or new_end is None:
        return {"conflicts": [], "has_conflict": False}

    conflicts = []
    for item in day_schedule["schedule"]:
        t = item.get("time", "")
        # 解析 "15:00-16:00" 格式
        m = re.match(r"(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})", t)
        if m:
            exist_start = to_minutes(m.group(1))
            exist_end = to_minutes(m.group(2))
            if exist_start is not None and exist_end is not None:
                if new_start < exist_end and new_end > exist_start:
                    conflicts.append(item)
        else:
            # 单时间点，假设占用 1 小时
            exist_start = to_minutes(t)
            if exist_start is not None:
                exist_end = exist_start + 60
                if new_start < exist_end and new_end > exist_start:
                    conflicts.append(item)

    return {
        "conflicts": conflicts,
        "has_conflict": len(conflicts) > 0,
        "checked_range": f"{time_start}-{time_end}",
        "checked_date": date_str,
    }


def find_expired():
    """找出已过期且未完成的待办"""
    content = read_schedule()
    todos = parse_todos(content)
    now = datetime.now()
    expired = []

    for t in todos:
        if t["status"] != "待办":
            continue
        m = re.match(r"(\d+)/(\d+)", t["deadline"])
        if m:
            todo_month = int(m.group(1))
            todo_day = int(m.group(2))
            try:
                todo_date = now.replace(month=todo_month, day=todo_day, hour=23, minute=59)
                if todo_date < now:
                    t["days_overdue"] = (now - todo_date).days
                    expired.append(t)
            except ValueError:
                pass

    return {"expired_todos": expired, "count": len(expired)}


def get_week_schedule():
    """获取本周完整日程"""
    now = datetime.now()
    # 找到本周一
    monday = now - timedelta(days=now.weekday())
    week = []
    for i in range(7):
        day = monday + timedelta(days=i)
        day_data = get_day_schedule(day)
        day_data["is_today"] = (day.date() == now.date())
        week.append(day_data)

    content = read_schedule()
    milestones = parse_milestones(content)

    return {
        "week_start": monday.strftime("%m/%d"),
        "week_end": (monday + timedelta(days=6)).strftime("%m/%d"),
        "days": week,
        "milestones": milestones,
    }


def generate_next_week_template():
    """生成下周日程模板"""
    now = datetime.now()
    next_monday = now + timedelta(days=(7 - now.weekday()))
    content = read_schedule()
    daily_fixed = parse_daily_fixed(content)

    template_lines = [
        f"\n## 下周日程（{next_monday.month}/{next_monday.day} {WEEKDAYS_CN[next_monday.weekday()]} → "
        f"{(next_monday + timedelta(days=6)).month}/{(next_monday + timedelta(days=6)).day} "
        f"{WEEKDAYS_CN[(next_monday + timedelta(days=6)).weekday()]}）\n"
    ]

    for i in range(7):
        day = next_monday + timedelta(days=i)
        wd = WEEKDAYS_CN[day.weekday()]
        template_lines.append(f"### {wd} {day.month}/{day.day}")
        template_lines.append("| 时间 | 事项 | 备注 |")
        template_lines.append("|------|------|------|")
        for item in daily_fixed:
            template_lines.append(f"| {item['time']} | {item['event']} | {item['note']} |")
        if not daily_fixed:
            template_lines.append("| — | 无特殊安排 | |")
        template_lines.append("")

    return {
        "template": "\n".join(template_lines),
        "week_start": f"{next_monday.month}/{next_monday.day}",
        "week_end": f"{(next_monday + timedelta(days=6)).month}/{(next_monday + timedelta(days=6)).day}",
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "用法: schedule_helper.py <command> [args]"}, ensure_ascii=False))
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "info":
        result = get_date_info()
    elif cmd == "today":
        result = get_day_schedule(datetime.now())
    elif cmd == "tomorrow":
        result = get_day_schedule(datetime.now() + timedelta(days=1))
    elif cmd == "week":
        result = get_week_schedule()
    elif cmd == "conflicts":
        if len(sys.argv) < 5:
            result = {"error": "用法: conflicts <start_time> <end_time> <date>"}
        else:
            result = check_conflicts(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "expired":
        result = find_expired()
    elif cmd == "roll_week":
        result = generate_next_week_template()
    else:
        result = {"error": f"未知命令: {cmd}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
