"""
报告生成器 — 根据生成结果构建 Markdown 报告。
"""

import argparse
import json
import sys
import io
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def generate_report(prompts_path: str, results_path: str, images_dir: str, output_path: str):
    """生成 Markdown 格式的可视化报告"""

    # Load data
    with open(prompts_path, "r", encoding="utf-8") as f:
        prompts_data = json.load(f)

    product = prompts_data.get("product", {})
    config = prompts_data.get("config", {})
    entries = prompts_data.get("prompts", prompts_data if isinstance(prompts_data, list) else [])

    results = []
    if Path(results_path).exists():
        with open(results_path, "r", encoding="utf-8") as f:
            results = json.load(f)

    summary = {}
    summary_path = Path(images_dir).parent / "summary.json"
    if summary_path.exists():
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

    # Build result map
    result_map = {r["index"]: r for r in results}

    # Group by category
    groups = defaultdict(list)
    for i, entry in enumerate(entries):
        group = entry.get("group", "ungrouped")
        r = result_map.get(i, {"status": "NOT_RUN"})
        groups[group].append({**entry, "index": i, "result": r})

    # --- Write report ---
    product_name = product.get("product_name") or product.get("product", "Unknown Product")
    lines = []

    lines.append(f"# 产品概念图报告 — {product_name}")
    lines.append("")
    lines.append(f"**生成日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**模型**: {summary.get('model', config.get('model', 'nanobanana-2'))}")
    lines.append(f"**分辨率**: {summary.get('resolution', config.get('resolution', '2K'))}")
    lines.append(f"**总图片数**: {summary.get('total', len(entries))}")
    lines.append(f"**成功/失败**: {summary.get('success', '?')}/{summary.get('failed', '?')}")
    lines.append(f"**预估费用**: ${summary.get('estimated_cost_usd', '?')}")
    lines.append("")

    # Product definition
    lines.append("## 产品定义")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(product, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")

    # Results by group
    group_titles = {
        "style_minimal": "极简风格",
        "style_industrial": "工业风格",
        "style_retro": "复古风格",
        "style_futuristic": "未来感风格",
        "style_organic": "有机风格",
        "style_luxury": "奢华风格",
        "angle_variants": "角度变体",
        "color_variants": "颜色变体",
        "scene_variants": "场景变体",
        "ungrouped": "其他",
    }

    for group_id, items in groups.items():
        title = group_titles.get(group_id, group_id)
        lines.append(f"## {title}")
        lines.append("")

        for item in items:
            r = item["result"]
            label = item.get("label", f"image_{item['index']}")
            status = r.get("status", "NOT_RUN")

            if status == "SUCCESS" and r.get("file"):
                rel_path = r["file"].replace("\\", "/")
                lines.append(f"### {label}")
                lines.append(f"![{label}]({rel_path})")
                lines.append("")
                meta = item.get("meta", {})
                if meta:
                    lines.append(f"- **风格**: {meta.get('style', '-')}")
                    lines.append(f"- **角度**: {meta.get('angle', '-')}")
                    lines.append(f"- **颜色**: {meta.get('color', '-')}")
                    lines.append(f"- **场景**: {meta.get('scene', '-')}")
                lines.append(f"- **比例**: {item.get('aspect_ratio', '-')}")
                lines.append("")
                lines.append("<details>")
                lines.append(f"<summary>Prompt</summary>")
                lines.append("")
                lines.append(f"```")
                lines.append(item["prompt"])
                lines.append(f"```")
                lines.append("</details>")
                lines.append("")
            else:
                lines.append(f"### {label} — ❌ {status}")
                if r.get("error"):
                    lines.append(f"> Error: {r['error']}")
                lines.append("")

    # Full prompt table
    lines.append("## 完整 Prompt 记录")
    lines.append("")
    lines.append("| # | 标签 | 分组 | 状态 | 文件 |")
    lines.append("|---|------|------|------|------|")
    for i, entry in enumerate(entries):
        r = result_map.get(i, {})
        status = r.get("status", "NOT_RUN")
        file_name = Path(r.get("file", "-")).name if r.get("file") else "-"
        label = entry.get("label", f"image_{i}")
        group = entry.get("group", "-")
        emoji = "✅" if status == "SUCCESS" else "❌"
        lines.append(f"| {i+1} | {label} | {group} | {emoji} {status} | {file_name} |")

    lines.append("")
    lines.append("---")
    lines.append(f"*Generated by allen-product-design Skill*")

    # Write
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"generated: report -> {output}")


def main():
    parser = argparse.ArgumentParser(description="Generate image report")
    parser.add_argument("--prompts", required=True, help="Path to prompts.json")
    parser.add_argument("--results", default=None, help="Path to generation_results.json")
    parser.add_argument("--images-dir", default="output/images", help="Images directory")
    parser.add_argument("--output", default="output/report.md", help="Output report path")
    args = parser.parse_args()

    results_path = args.results or str(Path(args.images_dir).parent / "generation_results.json")
    generate_report(args.prompts, results_path, args.images_dir, args.output)


if __name__ == "__main__":
    main()
