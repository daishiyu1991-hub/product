#!/usr/bin/env python3
"""
上架复盘 - 交付物验证器
"""

import os
import sys
import glob


def validate(output_dir):
    errors = []
    warnings = []

    if not os.path.isdir(output_dir):
        print(f"ERROR: 目录不存在: {output_dir}")
        print("validate_fail")
        return False

    # 检查复盘报告 MD
    md_files = glob.glob(os.path.join(output_dir, "*复盘*.md")) + glob.glob(os.path.join(output_dir, "*review*.md"))
    if not md_files:
        errors.append("缺少复盘报告 Markdown 文件")
    else:
        for md in md_files:
            with open(md, "r", encoding="utf-8") as f:
                content = f.read()
            if "Kill" not in content and "Continue" not in content and "Pivot" not in content:
                errors.append("复盘报告缺少 Kill/Continue/Pivot 决策")
            if "🟢" not in content and "🟡" not in content and "🔴" not in content:
                errors.append("复盘报告缺少红绿灯评估")
            if "趋势" not in content and "trend" not in content.lower():
                warnings.append("复盘报告未标注指标趋势")

    # 检查复盘数据 Excel
    xlsx_files = glob.glob(os.path.join(output_dir, "*复盘*.xlsx")) + glob.glob(os.path.join(output_dir, "*review*.xlsx"))
    if not xlsx_files:
        errors.append("缺少复盘数据 Excel 文件")

    print("=== 上架复盘交付物验证 ===")
    print(f"检查目录: {output_dir}")
    print(f"MD 文件: {len(md_files)} 个")
    print(f"Excel 文件: {len(xlsx_files)} 个")

    if warnings:
        print(f"\n⚠️ 警告 ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print(f"\n❌ 错误 ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        print("\nvalidate_fail")
        return False
    else:
        print("\n✅ 验证通过")
        print("validate_ok")
        return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="复盘交付物验证")
    parser.add_argument("--dir", required=True, help="输出目录路径")
    args = parser.parse_args()

    success = validate(args.dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
