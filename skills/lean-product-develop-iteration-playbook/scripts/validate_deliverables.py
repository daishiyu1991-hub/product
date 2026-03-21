#!/usr/bin/env python3
"""
迭代优化 - 交付物验证器
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

    # 检查迭代手册 MD
    manual_files = glob.glob(os.path.join(output_dir, "*迭代手册*.md")) + glob.glob(os.path.join(output_dir, "*iteration*.md"))
    if not manual_files:
        errors.append("缺少迭代手册 Markdown 文件")
    else:
        for md in manual_files:
            with open(md, "r", encoding="utf-8") as f:
                content = f.read()
            if "优先级" not in content and "Priority" not in content:
                errors.append("迭代手册缺少优先级排序")
            if "Impact" not in content and "impact" not in content.lower():
                errors.append("迭代手册缺少 Impact x Effort 评估")

    # 检查优先级矩阵 Excel
    xlsx_files = glob.glob(os.path.join(output_dir, "*优先级*.xlsx")) + glob.glob(os.path.join(output_dir, "*priority*.xlsx"))
    if not xlsx_files:
        errors.append("缺少优先级矩阵 Excel 文件")

    # 检查 30 天行动计划
    plan_files = glob.glob(os.path.join(output_dir, "*行动计划*.md")) + glob.glob(os.path.join(output_dir, "*action*.md"))
    if not plan_files:
        errors.append("缺少 30 天行动计划")
    else:
        for md in plan_files:
            with open(md, "r", encoding="utf-8") as f:
                content = f.read()
            week_count = content.count("第") + content.count("Week")
            if week_count < 4:
                warnings.append("行动计划未按 4 周拆解")

    print("=== 迭代优化交付物验证 ===")
    print(f"检查目录: {output_dir}")
    print(f"手册文件: {len(manual_files)} 个")
    print(f"Excel 文件: {len(xlsx_files)} 个")
    print(f"计划文件: {len(plan_files)} 个")

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
    parser = argparse.ArgumentParser(description="迭代优化交付物验证")
    parser.add_argument("--dir", required=True, help="输出目录路径")
    args = parser.parse_args()

    success = validate(args.dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
