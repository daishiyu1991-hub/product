"""
交付物验证脚本 — 检查所有输出文件是否完整合规。
"""

import json
import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def validate(output_dir: str):
    """验证所有交付物"""
    root = Path(output_dir)
    checks = []
    errors = []

    # 1. Check images directory
    images_dir = root / "images"
    if images_dir.exists():
        image_files = list(images_dir.rglob("*.jpg")) + list(images_dir.rglob("*.png"))
        if image_files:
            checks.append(f"[OK] images/ 包含 {len(image_files)} 张图片")
        else:
            errors.append("[FAIL] images/ 目录存在但没有图片文件")
    else:
        errors.append("[FAIL] images/ 目录不存在")

    # 2. Check report.md
    report = root / "report.md"
    if report.exists() and report.stat().st_size > 0:
        checks.append(f"[OK] report.md 存在 ({report.stat().st_size} bytes)")
    else:
        errors.append("[FAIL] report.md 不存在或为空")

    # 3. Check prompts.json
    prompts = root / "prompts.json"
    if prompts.exists():
        try:
            with open(prompts, "r", encoding="utf-8") as f:
                data = json.load(f)
            count = len(data.get("prompts", data if isinstance(data, list) else []))
            checks.append(f"[OK] prompts.json 合法 ({count} prompts)")
        except json.JSONDecodeError as e:
            errors.append(f"[FAIL] prompts.json 不是合法 JSON: {e}")
    else:
        errors.append("[FAIL] prompts.json 不存在")

    # 4. Check summary.json
    summary = root / "summary.json"
    if summary.exists():
        try:
            with open(summary, "r", encoding="utf-8") as f:
                data = json.load(f)
            checks.append(f"[OK] summary.json 合法 (success={data.get('success')}, failed={data.get('failed')})")
        except json.JSONDecodeError as e:
            errors.append(f"[FAIL] summary.json 不是合法 JSON: {e}")
    else:
        errors.append("[FAIL] summary.json 不存在")

    # 5. Check generation_results.json
    results = root / "generation_results.json"
    if results.exists():
        try:
            with open(results, "r", encoding="utf-8") as f:
                data = json.load(f)
            success_count = sum(1 for r in data if r.get("status") == "SUCCESS")
            fail_count = len(data) - success_count
            checks.append(f"[OK] generation_results.json 合法 ({success_count} success, {fail_count} failed)")

            # 6. Cross-check: are all SUCCESS images actually on disk?
            for r in data:
                if r.get("status") == "SUCCESS" and r.get("file"):
                    if not Path(r["file"]).exists():
                        errors.append(f"[FAIL] 图片文件缺失: {r['file']}")
        except json.JSONDecodeError as e:
            errors.append(f"[FAIL] generation_results.json 不是合法 JSON: {e}")

    # Report
    print("=== 交付物验证 ===")
    for c in checks:
        print(f"  {c}")
    for e in errors:
        print(f"  {e}")

    if errors:
        print(f"\n❌ 验证失败: {len(errors)} 个问题")
        sys.exit(1)
    else:
        print(f"\nvalidate_ok")
        sys.exit(0)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output", help="Output directory to validate")
    args = parser.parse_args()
    validate(args.output_dir)
