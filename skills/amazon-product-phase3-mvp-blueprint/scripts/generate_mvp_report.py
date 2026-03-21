#!/usr/bin/env python3
"""
MVP 蓝图 - 报告生成器
组装 MVP 蓝图 Markdown 报告。
"""

import json
import sys
import os
from datetime import datetime


def generate_mvp_report(payload):
    """生成 MVP 蓝图 Markdown 报告"""
    meta = payload.get("metadata", {})
    date_str = meta.get("date", datetime.now().strftime("%Y%m%d"))
    site = meta.get("site", "US")
    keyword = meta.get("keyword", "product")
    brand = meta.get("brand", "")
    version = meta.get("version", "v1")

    feature_matrix = payload.get("feature_matrix", [])
    spec_sheet = payload.get("spec_sheet", [])
    test_criteria = payload.get("test_criteria", [])
    cost_analysis = payload.get("cost_analysis", {})
    listing_plan = payload.get("listing_plan", {})
    competitors = payload.get("competitors", [])

    lines = []
    lines.append(f"# MVP 产品蓝图 — {keyword}")
    lines.append("")
    lines.append(f"**品牌**: {brand}  ")
    lines.append(f"**站点**: {site}  ")
    lines.append(f"**日期**: {date_str}  ")
    lines.append(f"**版本**: {version}")
    lines.append("")

    # Executive Summary
    if payload.get("executive_summary"):
        lines.append("## Executive Summary")
        lines.append("")
        for item in payload["executive_summary"]:
            lines.append(f"- {item}")
        lines.append("")

    # 1. 功能矩阵
    lines.append("## 一、MVP 功能矩阵")
    lines.append("")
    lines.append("| 维度 | 分类 | 规格值 | 决策依据 | 数据来源 |")
    lines.append("|------|------|--------|----------|----------|")
    for feat in feature_matrix:
        cls = feat.get("classification", "")
        emoji = {"Must-have": "🟢", "Nice-to-have": "🟡", "Cut": "🔴"}.get(cls, "")
        lines.append(f"| {feat.get('dimension', '')} | {emoji} {cls} | {feat.get('spec_value', '')} | {feat.get('rationale', '')} | {feat.get('source', '')} |")
    lines.append("")

    # 2. MVP 规格书
    lines.append("## 二、MVP 规格书")
    lines.append("")
    lines.append("| 项目 | 规格 | 决策依据 | 数据来源 |")
    lines.append("|------|------|----------|----------|")
    for spec in spec_sheet:
        lines.append(f"| {spec.get('item', '')} | {spec.get('value', '')} | {spec.get('rationale', '')} | {spec.get('source', '')} |")
    lines.append("")

    # 3. 竞品对比
    if competitors:
        lines.append("## 三、MVP vs 竞品对比")
        lines.append("")
        comp_header = "| 维度 | **我们的 MVP** |"
        comp_sep = "|------|--------------|"
        for c in competitors:
            comp_header += f" {c.get('brand', 'N/A')} ({c.get('asin', '')}) |"
            comp_sep += "---|"
        lines.append(comp_header)
        lines.append(comp_sep)
        # Build comparison rows from feature matrix
        for feat in feature_matrix:
            if feat.get("classification") != "Cut":
                row = f"| {feat.get('dimension', '')} | {feat.get('spec_value', '')} |"
                for c in competitors:
                    comp_specs = c.get("specs", {})
                    row += f" {comp_specs.get(feat.get('dimension', ''), 'N/A')} |"
                lines.append(row)
        lines.append("")

    # 4. 测试标准
    lines.append("## 四、测试标准（Pass/Fail）")
    lines.append("")
    lines.append("| 指标 | Pass 阈值 | Fail 阈值 | 数据来源 | 评估时间点 |")
    lines.append("|------|-----------|-----------|----------|-----------|")
    for tc in test_criteria:
        lines.append(f"| {tc.get('metric', '')} | {tc.get('pass_threshold', '')} | {tc.get('fail_threshold', '')} | {tc.get('source', '')} | {tc.get('eval_time', '')} |")
    lines.append("")

    # 5. 成本分析
    if cost_analysis:
        lines.append("## 五、成本与盈亏平衡")
        lines.append("")
        ue = cost_analysis.get("unit_economics", {})
        if ue:
            lines.append("### 单位成本")
            lines.append("")
            lines.append("| 项目 | 金额 (USD) |")
            lines.append("|------|------------|")
            for k, v in ue.items():
                if k not in ("gross_margin_pct",):
                    label = {
                        "price": "售价", "cogs": "采购成本", "shipping_to_fba": "头程物流",
                        "fba_fee": "FBA 配送费", "referral_fee": "平台佣金",
                        "ad_cost_per_unit": "广告成本/件", "return_cost": "退货损耗",
                        "storage_per_unit": "仓储费", "variable_cost_total": "**总可变成本**",
                        "gross_profit": "**单位毛利**"
                    }.get(k, k)
                    lines.append(f"| {label} | ${v:.2f} |")
            lines.append(f"| **毛利率** | **{ue.get('gross_margin_pct', 0):.1f}%** |")
            lines.append("")

        be = cost_analysis.get("breakeven", {})
        if be:
            lines.append("### 盈亏平衡")
            lines.append("")
            lines.append(f"- 盈亏平衡销量：**{be.get('breakeven_units', 'N/A')} 件**")
            lines.append(f"- 盈亏平衡天数：**{be.get('breakeven_days', 'N/A')} 天**")
            lines.append(f"- 首批采购量：{be.get('first_batch_qty', 'N/A')} 件")
            lines.append(f"- 总投入：**${be.get('total_investment', 0):,.2f}**")
            lines.append("")

    # 6. Listing 规划
    if listing_plan:
        lines.append("## 六、Listing 上架规划")
        lines.append("")
        if listing_plan.get("title"):
            lines.append(f"### 标题\n\n```\n{listing_plan['title']}\n```\n")
        if listing_plan.get("bullets"):
            lines.append("### 五点描述\n")
            for i, b in enumerate(listing_plan["bullets"], 1):
                lines.append(f"**Bullet {i}**: {b}")
            lines.append("")
        if listing_plan.get("pricing"):
            lines.append("### 定价策略\n")
            lines.append("| 阶段 | 价格 | 策略 |")
            lines.append("|------|------|------|")
            for p in listing_plan["pricing"]:
                lines.append(f"| {p.get('phase', '')} | ${p.get('price', 0):.2f} | {p.get('strategy', '')} |")
            lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(f"*数据来源：Sorftime MCP + 用户输入 | 生成日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="MVP 蓝图报告生成器")
    parser.add_argument("--input", required=True, help="Payload JSON 路径")
    parser.add_argument("--output", default=None, help="输出 MD 路径")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        payload = json.load(f)

    report = generate_mvp_report(payload)

    output_path = args.output
    if not output_path:
        meta = payload.get("metadata", {})
        base = os.path.dirname(args.input)
        date_str = meta.get("date", datetime.now().strftime("%Y%m%d"))
        site = meta.get("site", "US")
        keyword = meta.get("keyword", "product")
        version = meta.get("version", "v1")
        output_path = os.path.join(base, f"{date_str}_{site}_{keyword}_MVP蓝图_{version}.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"报告已保存: {output_path}")
    print("generate_ok")


if __name__ == "__main__":
    main()
