#!/usr/bin/env python3
"""
上架复盘 - 复盘报告生成器
"""

import json
import sys
import os
from datetime import datetime


def generate_review_report(payload):
    """生成复盘报告 Markdown"""
    meta = payload.get("metadata", {})
    asin = meta.get("asin", "")
    site = meta.get("site", "US")
    days = meta.get("review_days", 30)
    date_str = meta.get("date", datetime.now().strftime("%Y%m%d"))

    metrics = payload.get("metrics", {})
    traffic_lights = payload.get("traffic_lights", [])
    decision = payload.get("decision", {})
    review_analysis = payload.get("review_analysis", {})
    competitor_comparison = payload.get("competitor_comparison", [])
    traffic_analysis = payload.get("traffic_analysis", {})

    lines = []
    lines.append(f"# 上架复盘报告 — {asin}")
    lines.append("")
    lines.append(f"**ASIN**: {asin}  ")
    lines.append(f"**站点**: {site}  ")
    lines.append(f"**复盘天数**: {days} 天  ")
    lines.append(f"**日期**: {date_str}")
    lines.append("")

    # 复盘决策（置顶）
    if decision:
        lines.append("## 📊 复盘决策")
        lines.append("")
        final = decision.get("final_decision", "待评估")
        emoji = {"Kill": "🔴", "Pivot": "🟡", "Continue": "🟢", "Conditional Continue": "🟢🟡"}.get(final, "⚪")
        lines.append(f"**决策**: {emoji} **{final}**  ")
        lines.append(f"**理由**: {decision.get('reason', '')}  ")
        lines.append("")
        actions = decision.get("next_actions", [])
        if actions:
            lines.append("**下一步行动**:")
            for i, a in enumerate(actions, 1):
                lines.append(f"{i}. {a}")
            lines.append("")

    # 红绿灯评估表
    lines.append("## 一、Kill/Continue/Pivot 红绿灯评估")
    lines.append("")
    lines.append("| 指标 | 当前值 | Kill 🔴 | Pivot 🟡 | Continue 🟢 | 状态 | 趋势 |")
    lines.append("|------|--------|---------|----------|-------------|------|------|")
    for tl in traffic_lights:
        lines.append(f"| {tl.get('label', '')} | {tl.get('current_value', '')} | {tl.get('kill_threshold', '')} | {tl.get('pivot_threshold', '')} | {tl.get('continue_threshold', '')} | {tl.get('light', '⚪')} | {tl.get('trend', '→')} |")
    lines.append("")

    # 核心指标汇总
    lines.append("## 二、核心指标")
    lines.append("")
    lines.append("| 指标 | 值 | 趋势 |")
    lines.append("|------|-----|------|")
    metric_labels = {
        "price": "当前售价", "bsr": "BSR 排名", "monthly_sales": "月销量",
        "daily_sales": "日均销量", "rating": "评分", "review_count": "Review 数",
        "conversion_rate": "转化率", "acos": "ACOS", "tacos": "TACoS",
        "organic_share": "自然流量占比", "return_rate": "退货率"
    }
    for k, label in metric_labels.items():
        val = metrics.get(k, "N/A")
        trend = metrics.get(f"{k}_trend", "→")
        if val != "N/A":
            if k in ("price",):
                lines.append(f"| {label} | ${val} | {trend} |")
            elif k in ("conversion_rate", "acos", "tacos", "organic_share", "return_rate"):
                lines.append(f"| {label} | {val}% | {trend} |")
            else:
                lines.append(f"| {label} | {val} | {trend} |")
    lines.append("")

    # 流量分析
    if traffic_analysis:
        lines.append("## 三、流量分析")
        lines.append("")
        keywords = traffic_analysis.get("keywords", [])
        if keywords:
            lines.append("| 关键词 | 排名 | 搜索量 | 流量占比 | 趋势 |")
            lines.append("|--------|------|--------|----------|------|")
            for kw in keywords:
                lines.append(f"| {kw.get('keyword', '')} | #{kw.get('rank', '')} | {kw.get('search_volume', '')} | {kw.get('traffic_share', '')}% | {kw.get('trend', '→')} |")
            lines.append("")

    # Review 分析
    if review_analysis:
        lines.append("## 四、客户反馈分析")
        lines.append("")
        positives = review_analysis.get("positives", [])
        negatives = review_analysis.get("negatives", [])
        if positives:
            lines.append("### 好评主题")
            for p in positives:
                lines.append(f"- **{p.get('theme', '')}** (频次: {p.get('count', '')}): {p.get('insight', '')}")
            lines.append("")
        if negatives:
            lines.append("### 差评主题")
            for n in negatives:
                lines.append(f"- **{n.get('theme', '')}** (频次: {n.get('count', '')}): {n.get('insight', '')} → 建议: {n.get('action', '')}")
            lines.append("")

    # 竞品对标
    if competitor_comparison:
        lines.append("## 五、竞品对标")
        lines.append("")
        lines.append("| 指标 | 我们 | " + " | ".join(c.get("brand", c.get("asin", "")) for c in competitor_comparison) + " |")
        lines.append("|------|------|" + "|".join(["---" for _ in competitor_comparison]) + "|")
        comp_metrics = ["price", "monthly_sales", "rating", "review_count", "bsr"]
        comp_labels = ["价格", "月销量", "评分", "Review数", "BSR"]
        for metric, label in zip(comp_metrics, comp_labels):
            row = f"| {label} | {metrics.get(metric, 'N/A')} |"
            for c in competitor_comparison:
                row += f" {c.get(metric, 'N/A')} |"
            lines.append(row)
        lines.append("")

    lines.append("---")
    lines.append(f"\n*生成日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="复盘报告生成器")
    parser.add_argument("--input", required=True, help="Payload JSON 路径")
    parser.add_argument("--output", default=None, help="输出 MD 路径")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        payload = json.load(f)

    report = generate_review_report(payload)

    output_path = args.output
    if not output_path:
        meta = payload.get("metadata", {})
        base = os.path.dirname(args.input)
        asin = meta.get("asin", "product")
        site = meta.get("site", "US")
        days = meta.get("review_days", 30)
        date_str = meta.get("date", datetime.now().strftime("%Y%m%d"))
        output_path = os.path.join(base, f"{date_str}_{site}_{asin}_上架复盘_{days}天.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"报告已保存: {output_path}")
    print("generate_ok")


if __name__ == "__main__":
    main()
