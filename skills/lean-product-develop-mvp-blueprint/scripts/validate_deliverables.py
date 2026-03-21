#!/usr/bin/env python3
"""
MVP 蓝图 - 交付物验证器
检查 MVP 蓝图输出目录的交付物完整性。
"""

import os
import sys
import glob


def validate(output_dir):
    """验证交付物完整性"""
    errors = []
    warnings = []

    if not os.path.isdir(output_dir):
        print(f"ERROR: 目录不存在: {output_dir}")
        print("validate_fail")
        return False

    # 检查 MVP 蓝图 MD
    md_files = glob.glob(os.path.join(output_dir, "*MVP蓝图*.md"))
    if not md_files:
        errors.append("缺少 MVP 蓝图 Markdown 文件 (*MVP蓝图*.md)")
    else:
        for md in md_files:
            with open(md, "r", encoding="utf-8") as f:
                content = f.read()
            # 检查必要章节
            required_sections = [
                ("功能矩阵", "MVP 功能矩阵"),
                ("规格书", "MVP 规格书"),
                ("测试标准", "测试标准"),
                ("成本", "成本"),
            ]
            for section_id, section_name in required_sections:
                if section_id not in content:
                    errors.append(f"MVP 蓝图缺少章节: {section_name}")

            # 检查 Must-have/Nice-to-have/Cut 分类
            if "Must-have" not in content:
                errors.append("功能矩阵缺少 Must-have 分类")
            if "Cut" not in content:
                warnings.append("功能矩阵未标注任何 Cut 项")

            # 检查量化测试标准
            if "Pass" not in content and "pass" not in content.lower():
                errors.append("缺少量化测试标准 (Pass/Fail 阈值)")

    # 检查财务模型 Excel
    xlsx_files = glob.glob(os.path.join(output_dir, "*财务模型*.xlsx"))
    if not xlsx_files:
        errors.append("缺少财务模型 Excel 文件 (*财务模型*.xlsx)")

    # 检查 Listing 规划
    listing_files = glob.glob(os.path.join(output_dir, "*Listing*.md"))
    if not listing_files:
        warnings.append("缺少 Listing 规划文件 (*Listing*.md)")

    # 输出结果
    print("=== MVP 蓝图交付物验证 ===")
    print(f"检查目录: {output_dir}")
    print(f"MD 文件: {len(md_files)} 个")
    print(f"Excel 文件: {len(xlsx_files)} 个")
    print(f"Listing 文件: {len(listing_files)} 个")

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
    parser = argparse.ArgumentParser(description="MVP 蓝图交付物验证")
    parser.add_argument("--dir", required=True, help="输出目录路径")
    args = parser.parse_args()

    success = validate(args.dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
