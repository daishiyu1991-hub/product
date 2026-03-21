#!/usr/bin/env python3
"""
规模化决策 - 报告生成器
"""

import json
import sys
import os
from datetime import datetime


def generate_scale_report(payload):
    """生成规模化决策报告"""
    meta = payload.get("metadata", {})
    asin = meta.get("asin", "")
    site = meta.get("site", "US")
    months = meta.get("months_operating", 0)

    unit_economics = payload.get("unit_economics", {})
    scale_costs = payload.get("scale_costs", {})
    supply_chain = payload.get("supply_chain", {})
    moat = payload.get("competitive_moat", {})
    brand = payload.get("brand_readiness", {})
    expansion = payload.get("expansion_plan", {})
    scorecard = payload.get("scorecard", {})
    decision = payload.get("decision", {})

    lines = []
    lines.append(f"# 规模化决策报告 — {asin}")
    lines.append("")
    lines.append(f"**ASIN**: {asin} | **站点**: {site} | **已运营**: {months} 个月 | **日期**: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")

    # 决策置顶
    if decision:
        d = decision.get("verdict", "待评估")
        score = decision.get("total_score", "N/A")
        emoji = {"Go Big": "🚀", "Maintain": "⚡", "Harvest": "🌾", "Exit": "🚪"}.get(d, "❓")
        lines.append(f"## {emoji} 最终决策: **{d}**")
        lines.append(f"**加权总分**: {score}/10")
        lines.append("")
        reasons = decision.get("reasons", [])
        for r in reasons:
            lines.append(f"- {r}")
        lines.append("")

    # 单位经济学
    if unit_economics:
        lines.append("## 一、单位经济学验证")
        lines.append("")
        lines.append("| 项目 | 金额 | 占售价比 |")
        lines.append("|------|------|---------|")
        for item in unit_economics.get("items", []):
            lines.append(f"| {item.get('name', '')} | ${item.get('amount', 0):.2f} | {item.get('pct', '')} |")
        lines.append("")
        indicators = unit_economics.get("indicators", [])
        if indicators:
            lines.append("| 指标 | 当前值 | 健康基准 | 状态 |")
            lines.append("|------|--------|---------|------|")
            for ind in indicators:
                lines.append(f"| {ind.get('name', '')} | {ind.get('value', '')} | {ind.get('benchmark', '')} | {ind.get('status', '')} |")
            lines.append("")

    # 供应链评估
    if supply_chain:
        lines.append("## 二、供应链就绪评估")
        lines.append("")
        dims = supply_chain.get("dimensions", [])
        if dims:
            lines.append("| 维度 | 当前状态 | 规模化要求 | 差距 | 行动项 |")
            lines.append("|------|---------|-----------|------|--------|")
            for dim in dims:
                lines.append(f"| {dim.get('name', '')} | {dim.get('current', '')} | {dim.get('target', '')} | {dim.get('gap', '')} | {dim.get('action', '')} |")
            lines.append("")

    # 竞争护城河
    if moat:
        lines.append("## 三、竞争护城河评估")
        lines.append("")
        items = moat.get("items", [])
        if items:
            lines.append("| 护城河类型 | 当前状态 | 强度 | 说明 |")
            lines.append("|-----------|---------|------|------|")
            for item in items:
                lines.append(f"| {item.get('type', '')} | {item.get('status', '')} | {item.get('strength', '')} | {item.get('note', '')} |")
            lines.append("")

    # 决策评分卡
    if scorecard:
        lines.append("## 四、决策评分卡")
        lines.append("")
        dims = scorecard.get("dimensions", [])
        if dims:
            lines.append("| 维度 | 权重 | 评分(1-10) | 加权分 | 依据 |")
            lines.append("|------|------|-----------|--------|------|")
            for dim in dims:
                lines.append(f"| {dim.get('name', '')} | {dim.get('weight', '')} | {dim.get('score', '')} | {dim.get('weighted', '')} | {dim.get('basis', '')} |")
            lines.append("")

    # 产品线扩展
    if expansion:
        lines.append("## 五、产品线扩展规划")
        lines.append("")
        for direction in ["vertical", "horizontal", "multi_site"]:
            items = expansion.get(direction, [])
            if items:
                label = {"vertical": "纵向延伸", "horizontal": "横向延伸", "multi_site": "多站点复制"}.get(direction, direction)
                lines.append(f"### {label}")
                lines.append("")
                for item in items:
                    lines.append(f"- **{item.get('name', '')}**: {item.get('description', '')} (投入: {item.get('investment', 'N/A')})")
                lines.append("")

    lines.append("---")
    lines.append(f"\n*生成日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="规模化决策报告生成器")
    parser.add_argument("--input", required=True, help="Payload JSON 路径")
    parser.add_argument("--output", default=None, help="输出 MD 路径")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        payload = json.load(f)

    report = generate_scale_report(payload)

    output_path = args.output
    if not output_path:
        meta = payload.get("metadata", {})
        base = os.path.dirname(args.input)
        asin = meta.get("asin", "product")
        site = meta.get("site", "US")
        output_path = os.path.join(base, f"{datetime.now().strftime('%Y%m%d')}_{site}_{asin}_规模化决策报告.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"报告已保存: {output_path}")
    print("generate_ok")


if __name__ == "__main__":
    main()
