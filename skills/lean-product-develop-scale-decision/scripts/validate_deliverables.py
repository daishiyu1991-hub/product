#!/usr/bin/env python3
"""
规模化决策 - 交付物验证器
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

    # 检查决策报告 MD
    md_files = glob.glob(os.path.join(output_dir, "*规模化*.md")) + glob.glob(os.path.join(output_dir, "*scale*.md"))
    if not md_files:
        errors.append("缺少规模化决策报告（*规模化*.md）")
    else:
        for md in md_files:
            with open(md, "r", encoding="utf-8") as f:
                content = f.read()
            decisions = ["Go Big", "Maintain", "Harvest", "Exit"]
            has_decision = any(d in content for d in decisions)
            if not has_decision:
                errors.append("决策报告缺少明确决策（Go Big/Maintain/Harvest/Exit）")
            if "单位经济学" not in content and "unit economics" not in content.lower():
                errors.append("缺少单位经济学分析")
            if "供应链" not in content and "supply chain" not in content.lower():
                warnings.append("缺少供应链评估")
            if "护城河" not in content and "moat" not in content.lower():
                warnings.append("缺少竞争护城河评估")

    # 检查财务预测 Excel
    xlsx_files = glob.glob(os.path.join(output_dir, "*财务预测*.xlsx")) + glob.glob(os.path.join(output_dir, "*financial*.xlsx"))
    if not xlsx_files:
        errors.append("缺少财务预测模型 Excel（*财务预测*.xlsx）")
    else:
        try:
            import openpyxl
            for xlsx in xlsx_files:
                wb = openpyxl.load_workbook(xlsx, read_only=True)
                sheet_names = wb.sheetnames
                wb.close()
                # 检查三场景
                scenarios_found = sum(1 for s in sheet_names if "乐观" in s or "基准" in s or "悲观" in s or "optimistic" in s.lower() or "baseline" in s.lower() or "pessimistic" in s.lower())
                if scenarios_found < 3:
                    errors.append(f"财务预测缺少三场景（乐观/基准/悲观），仅找到 {scenarios_found} 个")
        except ImportError:
            warnings.append("无法验证 Excel 内容（openpyxl 未安装）")

    # 检查产品线规划
    plan_files = glob.glob(os.path.join(output_dir, "*产品线*.md")) + glob.glob(os.path.join(output_dir, "*product_line*.md"))
    if not plan_files:
        warnings.append("缺少产品线规划文件")

    print("=== 规模化决策交付物验证 ===")
    print(f"检查目录: {output_dir}")
    print(f"报告文件: {len(md_files)} 个")
    print(f"Excel 文件: {len(xlsx_files)} 个")
    print(f"规划文件: {len(plan_files)} 个")

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
    parser = argparse.ArgumentParser(description="规模化决策交付物验证")
    parser.add_argument("--dir", required=True, help="输出目录路径")
    args = parser.parse_args()

    success = validate(args.dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
