#!/usr/bin/env python3
"""
迭代优化 - 行动计划生成器
组装迭代手册 Markdown + 30 天行动计划。
"""

import json
import sys
import os
from datetime import datetime, timedelta


def generate_action_plan(payload):
    """生成迭代手册和 30 天行动计划"""
    meta = payload.get("metadata", {})
    asin = meta.get("asin", "")
    site = meta.get("site", "US")
    version = meta.get("version", "v1")
    date_str = meta.get("date", datetime.now().strftime("%Y%m%d"))

    actions = payload.get("prioritized_actions", [])
    listing_plan = payload.get("listing_optimization", {})
    product_plan = payload.get("product_improvement", {})
    ad_plan = payload.get("ad_optimization", {})
    expansion_plan = payload.get("expansion_plan", {})

    # ===== 迭代手册 =====
    manual_lines = []
    manual_lines.append(f"# 迭代优化手册 — {asin}")
    manual_lines.append("")
    manual_lines.append(f"**ASIN**: {asin} | **站点**: {site} | **版本**: {version} | **日期**: {date_str}")
    manual_lines.append("")

    # 优先级排序
    manual_lines.append("## 一、优化优先级排序")
    manual_lines.append("")
    manual_lines.append("| 排名 | 优化项 | 类别 | Impact | Effort | Priority | 象限 | 预期效果 |")
    manual_lines.append("|------|--------|------|--------|--------|----------|------|----------|")
    for i, a in enumerate(actions, 1):
        manual_lines.append(f"| {i} | {a.get('name', '')} | {a.get('category', '')} | {a.get('impact', '')} | {a.get('effort', '')} | {a.get('priority', '')} | {a.get('quadrant', '')} | {a.get('expected_effect', '')} |")
    manual_lines.append("")

    # Listing 优化
    if listing_plan:
        manual_lines.append("## 二、Listing 优化方案")
        manual_lines.append("")
        for section_key, section_label in [
            ("title", "标题优化"),
            ("bullets", "五点描述优化"),
            ("images", "图片优化"),
            ("pricing", "价格策略"),
        ]:
            content = listing_plan.get(section_key)
            if content:
                manual_lines.append(f"### {section_label}")
                manual_lines.append("")
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            manual_lines.append(f"- **{item.get('item', '')}**: {item.get('current', '')} → {item.get('optimized', '')} (理由: {item.get('reason', '')})")
                        else:
                            manual_lines.append(f"- {item}")
                elif isinstance(content, str):
                    manual_lines.append(content)
                manual_lines.append("")

    # 产品改良
    if product_plan:
        manual_lines.append("## 三、产品改良方案")
        manual_lines.append("")
        improvements = product_plan.get("improvements", [])
        if improvements:
            manual_lines.append("| 差评主题 | 频率 | 严重度 | 改良方案 | 额外成本 | 优先级 |")
            manual_lines.append("|----------|------|--------|----------|---------|--------|")
            for imp in improvements:
                manual_lines.append(f"| {imp.get('theme', '')} | {imp.get('frequency', '')} | {imp.get('severity', '')} | {imp.get('solution', '')} | {imp.get('cost', '')} | {imp.get('priority', '')} |")
            manual_lines.append("")

    # 广告优化
    if ad_plan:
        manual_lines.append("## 四、广告优化方案")
        manual_lines.append("")
        keyword_layers = ad_plan.get("keyword_layers", [])
        if keyword_layers:
            manual_lines.append("### 关键词分层")
            manual_lines.append("")
            manual_lines.append("| 层级 | 关键词 | 当前表现 | 优化策略 |")
            manual_lines.append("|------|--------|----------|----------|")
            for kl in keyword_layers:
                manual_lines.append(f"| {kl.get('layer', '')} | {kl.get('keywords', '')} | {kl.get('performance', '')} | {kl.get('strategy', '')} |")
            manual_lines.append("")

    # 变体/扩品
    if expansion_plan:
        manual_lines.append("## 五、变体/扩品规划")
        manual_lines.append("")
        variants = expansion_plan.get("variants", [])
        if variants:
            manual_lines.append("| 变体方向 | 理由 | 预期销量 | 投入 | 优先级 |")
            manual_lines.append("|----------|------|----------|------|--------|")
            for v in variants:
                manual_lines.append(f"| {v.get('direction', '')} | {v.get('reason', '')} | {v.get('expected_sales', '')} | {v.get('investment', '')} | {v.get('priority', '')} |")
            manual_lines.append("")

    manual = "\n".join(manual_lines)

    # ===== 30 天行动计划 =====
    plan_lines = []
    plan_lines.append(f"# 30 天行动计划 — {asin}")
    plan_lines.append("")
    plan_lines.append(f"**起始日期**: {date_str}")
    plan_lines.append("")

    # 按优先级分配到 4 周
    quick_wins = [a for a in actions if "Quick Win" in a.get("quadrant", "")]
    high_value = [a for a in actions if "High Value" in a.get("quadrant", "")]
    fill_ins = [a for a in actions if "Fill In" in a.get("quadrant", "")]

    weeks = [
        ("第 1 周 (Day 1-7)", "Quick Win 立即执行", quick_wins[:3]),
        ("第 2 周 (Day 8-14)", "Quick Win 收尾 + High Value 启动", quick_wins[3:] + high_value[:2]),
        ("第 3 周 (Day 15-21)", "High Value 推进", high_value[2:4] + fill_ins[:2]),
        ("第 4 周 (Day 22-30)", "效果评估 + 下轮规划", []),
    ]

    for week_title, focus, week_actions in weeks:
        plan_lines.append(f"### {week_title}")
        plan_lines.append(f"**重点**: {focus}")
        plan_lines.append("")
        if week_actions:
            plan_lines.append("| 序号 | 任务 | 类别 | 预期效果 | 完成标准 |")
            plan_lines.append("|------|------|------|----------|----------|")
            for i, a in enumerate(week_actions, 1):
                plan_lines.append(f"| {i} | {a.get('name', '')} | {a.get('category', '')} | {a.get('expected_effect', '')} | {a.get('done_criteria', '完成并记录结果')} |")
        else:
            plan_lines.append("| 序号 | 任务 | 说明 |")
            plan_lines.append("|------|------|------|")
            plan_lines.append("| 1 | 对比各周优化前后数据 | 收集优化效果数据 |")
            plan_lines.append("| 2 | 更新复盘报告 | 执行 lean-product-develop-launch-review |")
            plan_lines.append("| 3 | 规划下一轮迭代 | 基于新数据重新排序优先级 |")
        plan_lines.append("")

    plan = "\n".join(plan_lines)

    return manual, plan


def main():
    import argparse
    parser = argparse.ArgumentParser(description="迭代行动计划生成器")
    parser.add_argument("--input", required=True, help="Payload JSON 路径")
    parser.add_argument("--output-dir", default=None, help="输出目录")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        payload = json.load(f)

    manual, plan = generate_action_plan(payload)

    output_dir = args.output_dir or os.path.dirname(args.input)
    meta = payload.get("metadata", {})
    asin = meta.get("asin", "product")
    site = meta.get("site", "US")
    version = meta.get("version", "v1")
    date_str = meta.get("date", datetime.now().strftime("%Y%m%d"))

    manual_path = os.path.join(output_dir, f"{date_str}_{site}_{asin}_迭代手册_{version}.md")
    plan_path = os.path.join(output_dir, f"{date_str}_{site}_{asin}_30天行动计划.md")

    with open(manual_path, "w", encoding="utf-8") as f:
        f.write(manual)
    with open(plan_path, "w", encoding="utf-8") as f:
        f.write(plan)

    print(f"迭代手册已保存: {manual_path}")
    print(f"行动计划已保存: {plan_path}")
    print("generate_ok")


if __name__ == "__main__":
    main()
