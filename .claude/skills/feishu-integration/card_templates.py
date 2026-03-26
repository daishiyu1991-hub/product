#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书消息卡片模板 — 亚马逊精益产品开发 Pipeline
===============================================
为 8 个 Phase 的关键决策设计彩色交互式卡片。
"""


def get_phase_card(phase: str, product: str, decision: str,
                   metrics: dict = None) -> dict:
    """
    根据 Phase 编号获取对应的卡片模板

    Args:
        phase: Phase 编号 ("1"-"8")
        product: 产品名称
        decision: 决策结果
        metrics: 指标数据字典
    """
    metrics = metrics or {}
    phase = str(phase).strip()

    template_map = {
        "1": phase1_decision_card,
        "2": phase2_validation_card,
        "3": phase3_mvp_card,
        "4": phase4_design_card,
        "5": phase5_concept_card,
        "6": phase6_review_card,
        "7": phase7_iteration_card,
        "8": phase8_scale_card,
    }

    func = template_map.get(phase, generic_phase_card)
    return func(product=product, decision=decision, metrics=metrics)


# ============================================================================
# Phase 1 — 选品分析决策卡片
# ============================================================================

def phase1_decision_card(product: str, decision: str, metrics: dict) -> dict:
    """
    Phase 1 选品分析完成卡片
    decision: GO / CONDITIONAL_GO / HOLD / NO_GO
    """
    color_map = {
        "GO": "green",
        "CONDITIONAL_GO": "yellow",
        "CONDITIONAL GO": "yellow",
        "HOLD": "orange",
        "NO_GO": "red",
        "NO GO": "red",
    }
    emoji_map = {
        "GO": "🟢",
        "CONDITIONAL_GO": "🟡",
        "CONDITIONAL GO": "🟡",
        "HOLD": "🟠",
        "NO_GO": "🔴",
        "NO GO": "🔴",
    }

    decision_upper = decision.upper().replace("-", "_")
    color = color_map.get(decision_upper, "blue")
    emoji = emoji_map.get(decision_upper, "📊")

    return {
        "header": {
            "title": {"tag": "plain_text", "content": f"📊 Phase 1 选品分析 — {product}"},
            "template": color,
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**决策结果：** {emoji} **{decision}**",
                },
            },
            {"tag": "hr"},
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("月销量", metrics.get("monthly_sales", "N/A")),
                    _metric_column("平均价", f"${metrics['avg_price']}" if 'avg_price' in metrics else "N/A"),
                ],
            },
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("竞争度", metrics.get("competition", "N/A")),
                    _metric_column("新品占比", f"{metrics['new_product_share']}%" if 'new_product_share' in metrics else "N/A"),
                ],
            },
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("头部集中度", f"{metrics['top3_share']}%" if 'top3_share' in metrics else "N/A"),
                    _metric_column("亚马逊自营", f"{metrics['amazon_share']}%" if 'amazon_share' in metrics else "N/A"),
                ],
            },
            {"tag": "hr"},
            _note_element(metrics.get("summary", "")),
        ],
    }


# ============================================================================
# Phase 2 — 需求验证卡片
# ============================================================================

def phase2_validation_card(product: str, decision: str, metrics: dict) -> dict:
    """
    Phase 2 需求验证完成卡片
    decision: TRUE_DEMAND / FALSE_DEMAND / INCONCLUSIVE
    """
    color_map = {
        "TRUE_DEMAND": "green",
        "TRUE DEMAND": "green",
        "FALSE_DEMAND": "red",
        "FALSE DEMAND": "red",
        "INCONCLUSIVE": "yellow",
    }
    emoji_map = {
        "TRUE_DEMAND": "✅",
        "TRUE DEMAND": "✅",
        "FALSE_DEMAND": "❌",
        "FALSE DEMAND": "❌",
        "INCONCLUSIVE": "🤔",
    }

    decision_upper = decision.upper().replace("-", "_")
    color = color_map.get(decision_upper, "blue")
    emoji = emoji_map.get(decision_upper, "🔍")

    feature = metrics.get("feature", "")
    title_suffix = f" — {feature}" if feature else ""

    return {
        "header": {
            "title": {"tag": "plain_text", "content": f"🔍 Phase 2 需求验证 — {product}{title_suffix}"},
            "template": color,
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**验证结果：** {emoji} **{decision}**",
                },
            },
            {"tag": "hr"},
            {
                "tag": "column_set",
                "flex_mode": "trisect",
                "background_style": "default",
                "columns": [
                    _metric_column("Review信号", metrics.get("review_signal", "N/A")),
                    _metric_column("关键词信号", metrics.get("keyword_signal", "N/A")),
                    _metric_column("社区信号", metrics.get("community_signal", "N/A")),
                ],
            },
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("差评提及率", f"{metrics['complaint_rate']}%" if 'complaint_rate' in metrics else "N/A"),
                    _metric_column("好评提及率", f"{metrics['positive_rate']}%" if 'positive_rate' in metrics else "N/A"),
                ],
            },
            {"tag": "hr"},
            _note_element(metrics.get("summary", "")),
        ],
    }


# ============================================================================
# Phase 3 — MVP 蓝图卡片
# ============================================================================

def phase3_mvp_card(product: str, decision: str, metrics: dict) -> dict:
    """
    Phase 3 MVP 蓝图完成卡片
    """
    return {
        "header": {
            "title": {"tag": "plain_text", "content": f"📋 Phase 3 MVP蓝图 — {product}"},
            "template": "blue",
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "**MVP 产品规格书已生成**",
                },
            },
            {"tag": "hr"},
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("Must-have", f"{metrics.get('must_have_count', 'N/A')} 项"),
                    _metric_column("Nice-to-have", f"{metrics.get('nice_to_have_count', 'N/A')} 项"),
                ],
            },
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("目标成本", f"${metrics['target_cost']}" if 'target_cost' in metrics else "N/A"),
                    _metric_column("目标售价", f"${metrics['target_price']}" if 'target_price' in metrics else "N/A"),
                ],
            },
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("预估毛利率", f"{metrics['gross_margin']}%" if 'gross_margin' in metrics else "N/A"),
                    _metric_column("盈亏平衡", f"{metrics.get('break_even', 'N/A')} 单/月"),
                ],
            },
            {"tag": "hr"},
            _note_element(metrics.get("summary", "")),
        ],
    }


# ============================================================================
# Phase 4 — 工业设计调研卡片
# ============================================================================

def phase4_design_card(product: str, decision: str, metrics: dict) -> dict:
    """Phase 4 设计调研完成卡片"""
    return {
        "header": {
            "title": {"tag": "plain_text", "content": f"🎨 Phase 4 设计调研 — {product}"},
            "template": "purple",
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "**工业设计调研已完成**",
                },
            },
            {"tag": "hr"},
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("竞品图片", f"{metrics.get('competitor_images', 'N/A')} 张"),
                    _metric_column("形态族群", f"{metrics.get('archetypes', 'N/A')} 类"),
                ],
            },
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("基线线稿", f"{metrics.get('baselines', 'N/A')} 张"),
                    _metric_column("风格方案", f"{metrics.get('style_count', 'N/A')} 种"),
                ],
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**目标形态：** {metrics.get('selected_archetype', 'N/A')}\n**设计方向：** {metrics.get('design_direction', 'N/A')}",
                },
            },
            _note_element(metrics.get("summary", "")),
        ],
    }


# ============================================================================
# Phase 5 — 概念图生成卡片
# ============================================================================

def phase5_concept_card(product: str, decision: str, metrics: dict) -> dict:
    """Phase 5 概念图生成完成卡片"""
    return {
        "header": {
            "title": {"tag": "plain_text", "content": f"🖼️ Phase 5 概念图 — {product}"},
            "template": "purple",
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "**工业设计概念图已生成**",
                },
            },
            {"tag": "hr"},
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("生成图片", f"{metrics.get('total_images', '8')} 张"),
                    _metric_column("主推风格", metrics.get("primary_style", "N/A")),
                ],
            },
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("形态偏离度", f"{metrics.get('deviation', 'N/A')}%"),
                    _metric_column("评审结果", metrics.get("review_result", "N/A")),
                ],
            },
            {"tag": "hr"},
            _note_element(metrics.get("summary", "")),
        ],
    }


# ============================================================================
# Phase 6 — 上架复盘决策卡片
# ============================================================================

def phase6_review_card(product: str, decision: str, metrics: dict) -> dict:
    """
    Phase 6 上架复盘卡片
    decision: Kill / Continue / Pivot
    """
    color_map = {"Kill": "red", "Continue": "green", "Pivot": "yellow"}
    emoji_map = {"Kill": "💀", "Continue": "✅", "Pivot": "🔄"}

    # 标准化 decision
    decision_title = decision.strip().title()
    color = color_map.get(decision_title, "blue")
    emoji = emoji_map.get(decision_title, "📋")
    days = metrics.get("days", "N/A")
    asin = metrics.get("asin", "")

    title_asin = f" ({asin})" if asin else ""

    return {
        "header": {
            "title": {"tag": "plain_text", "content": f"{emoji} Phase 6 复盘{title_asin} — {product} ({days}天)"},
            "template": color,
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**决策结果：** {emoji} **{decision_title}**",
                },
            },
            {"tag": "hr"},
            {
                "tag": "column_set",
                "flex_mode": "trisect",
                "background_style": "default",
                "columns": [
                    _metric_column("BSR 排名", metrics.get("bsr", "N/A")),
                    _metric_column("转化率", f"{metrics['cvr']}%" if 'cvr' in metrics else "N/A"),
                    _metric_column("ACOS", f"{metrics['acos']}%" if 'acos' in metrics else "N/A"),
                ],
            },
            {
                "tag": "column_set",
                "flex_mode": "trisect",
                "background_style": "default",
                "columns": [
                    _metric_column("日均销量", metrics.get("daily_sales", "N/A")),
                    _metric_column("评分", f"{metrics.get('rating', 'N/A')}⭐"),
                    _metric_column("Review数", metrics.get("review_count", "N/A")),
                ],
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": _traffic_light_text(metrics.get("dimensions", {})),
                },
            },
            _note_element(metrics.get("rationale", metrics.get("summary", ""))),
        ],
    }


# ============================================================================
# Phase 7 — 迭代优化卡片
# ============================================================================

def phase7_iteration_card(product: str, decision: str, metrics: dict) -> dict:
    """Phase 7 迭代优化方案卡片"""
    return {
        "header": {
            "title": {"tag": "plain_text", "content": f"🔧 Phase 7 迭代方案 — {product}"},
            "template": "blue",
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "**迭代优化方案已生成**",
                },
            },
            {"tag": "hr"},
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("Quick Win", f"{metrics.get('quick_wins', 'N/A')} 项"),
                    _metric_column("重要改进", f"{metrics.get('major_improvements', 'N/A')} 项"),
                ],
            },
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("长期投资", f"{metrics.get('long_term', 'N/A')} 项"),
                    _metric_column("优先级", metrics.get("top_priority", "N/A")),
                ],
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": _action_plan_text(metrics.get("action_plan", [])),
                },
            },
            _note_element(metrics.get("summary", "")),
        ],
    }


# ============================================================================
# Phase 8 — 规模化决策卡片
# ============================================================================

def phase8_scale_card(product: str, decision: str, metrics: dict) -> dict:
    """
    Phase 8 规模化决策卡片
    decision: Go Big / Maintain / Harvest / Exit
    """
    color_map = {
        "Go Big": "green",
        "GO BIG": "green",
        "Maintain": "blue",
        "MAINTAIN": "blue",
        "Harvest": "yellow",
        "HARVEST": "yellow",
        "Exit": "red",
        "EXIT": "red",
    }
    emoji_map = {
        "Go Big": "🚀",
        "GO BIG": "🚀",
        "Maintain": "⚖️",
        "MAINTAIN": "⚖️",
        "Harvest": "🌾",
        "HARVEST": "🌾",
        "Exit": "🚪",
        "EXIT": "🚪",
    }

    color = color_map.get(decision, color_map.get(decision.upper(), "blue"))
    emoji = emoji_map.get(decision, emoji_map.get(decision.upper(), "📊"))

    return {
        "header": {
            "title": {"tag": "plain_text", "content": f"{emoji} Phase 8 规模化决策 — {product}"},
            "template": color,
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**决策结果：** {emoji} **{decision}**",
                },
            },
            {"tag": "hr"},
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("净利率", f"{metrics['net_margin']}%" if 'net_margin' in metrics else "N/A"),
                    _metric_column("月均利润", f"${metrics.get('monthly_profit', 'N/A')}"),
                ],
            },
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("自然流量占比", f"{metrics['organic_share']}%" if 'organic_share' in metrics else "N/A"),
                    _metric_column("Review数", metrics.get("review_count", "N/A")),
                ],
            },
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": [
                    _metric_column("供应链评分", metrics.get("supply_chain_score", "N/A")),
                    _metric_column("护城河评分", metrics.get("moat_score", "N/A")),
                ],
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**12个月预测营收：** ${metrics.get('forecast_revenue', 'N/A')}\n"
                               f"**12个月预测利润：** ${metrics.get('forecast_profit', 'N/A')}",
                },
            },
            _note_element(metrics.get("summary", "")),
        ],
    }


# ============================================================================
# 通用卡片（Phase 2/4/5/7 或未知 Phase）
# ============================================================================

def generic_phase_card(product: str, decision: str, metrics: dict) -> dict:
    """通用 Phase 完成通知卡片"""
    phase_num = metrics.get("phase", "?")

    return {
        "header": {
            "title": {"tag": "plain_text", "content": f"📊 Phase {phase_num} 完成 — {product}"},
            "template": "blue",
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**状态：** {decision}",
                },
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": _metrics_to_md(metrics),
                },
            },
            _note_element(metrics.get("summary", "")),
        ],
    }


# ============================================================================
# 辅助函数
# ============================================================================

def _metric_column(label: str, value) -> dict:
    """生成指标列"""
    return {
        "tag": "column",
        "width": "weighted",
        "weight": 1,
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**{label}**\n{value}",
                },
            }
        ],
    }


def _note_element(text: str) -> dict:
    """生成备注元素"""
    if not text:
        return {
            "tag": "note",
            "elements": [
                {"tag": "plain_text", "content": "📍 由亚马逊精益产品开发 Pipeline 自动生成"}
            ],
        }
    return {
        "tag": "note",
        "elements": [
            {"tag": "plain_text", "content": f"💡 {text}"}
        ],
    }


def _traffic_light_text(dimensions: dict) -> str:
    """将 6 维度红绿灯评估转为文本"""
    if not dimensions:
        return ""

    light_map = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
    lines = ["**维度评估：**"]
    for dim_name, status in dimensions.items():
        emoji = light_map.get(status.lower(), "⚪")
        lines.append(f"  {emoji} {dim_name}")

    return "\n".join(lines)


def _action_plan_text(plan: list) -> str:
    """将 30 天行动计划转为文本"""
    if not plan:
        return "**30天行动计划已生成，详见完整报告**"

    lines = ["**30天行动计划摘要：**"]
    for item in plan[:5]:  # 最多显示 5 条
        lines.append(f"• {item}")

    if len(plan) > 5:
        lines.append(f"... 还有 {len(plan) - 5} 项")

    return "\n".join(lines)


def _metrics_to_md(metrics: dict) -> str:
    """将指标字典转为 Markdown 表格"""
    skip_keys = {"summary", "phase", "report_url", "next_phase_url"}
    items = [(k, v) for k, v in metrics.items() if k not in skip_keys]

    if not items:
        return "分析已完成，详见完整报告。"

    lines = ["| 指标 | 数值 |", "|------|------|"]
    for k, v in items[:10]:  # 最多 10 行
        lines.append(f"| {k} | {v} |")

    return "\n".join(lines)
