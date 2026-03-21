---
name: lean-product-develop-launch-review
description: "亚马逊精益开发 Phase 4：产品上架后 30/60/90 天数据复盘。采集核心指标（BSR/转化率/ACOS/Review），对照 MVP 蓝图测试标准，执行 Kill/Continue/Pivot 决策框架。优先调用 Sorftime MCP 获取产品数据；无 Sorftime 时支持用户手动输入 Seller Central 数据。"
argument-hint: "[ASIN] [站点] [--days 复盘天数] [--mvp-blueprint 蓝图路径]"
user-invocable: true
---

# 上架数据复盘（精益开发 Phase 4）

## 定位

`lean-product-develop-launch-review` 是精益产品开发闭环的第四阶段。产品上架后，用数据回答一个关键问题：**这个产品该继续还是该杀掉？**

通过对照 MVP 蓝图中设定的测试标准，客观评估产品表现，做出 Kill / Continue / Pivot 决策。

## 适用场景

- 产品上架 30 天后的首次复盘（判断是否继续投入广告）
- 产品上架 60 天中期复盘（判断是否需要 Pivot）
- 产品上架 90 天终局复盘（最终 Kill/Continue 决策）
- 定期数据复盘（跟踪趋势变化）

## 前置条件

- 已上架的产品 ASIN
- MVP 蓝图中的测试标准（推荐，非强制）
- Python 3.9+，安装 `openpyxl`

## 使用方法

### 方式1：指定 ASIN
```
/lean-product-develop-launch-review B0XXXXXXXX US --days 30
```

### 方式2：关联 MVP 蓝图
```
/lean-product-develop-launch-review B0XXXXXXXX US --days 60 --mvp-blueprint ./工作成果/brands/AORYVIC/精益开发/bluetooth-speaker/mvp-blueprint/
```

### 方式3：自然语言
```
帮我复盘一下 B0XXXXXXXX 上架 30 天的数据表现
```

## 执行步骤

当调用此 Skill 时，执行以下流程：

1. **读取完整方法论** — 加载 `skills/lean-product-develop-launch-review/SKILL.md`
2. **读取基线** — 加载 MVP 蓝图中的测试标准作为对照基线
3. **核心指标采集** — Sorftime（product_detail/product_trend/product_reviews）或用户手动输入
4. **流量分析** — 自然流量关键词排名 + 广告数据（ACOS/TACoS/CPC/CTR）
5. **转化分析** — 转化率 vs 品类平均，趋势分析
6. **客户反馈分析** — 早期 Review 情感分析 + 退货原因归类
7. **竞品对标** — 与 MVP 蓝图中的对标竞品对比
8. **Kill/Continue/Pivot 决策** — 6 维度红绿灯评估 + 最终决策
9. **输出复盘报告** — 生成文档，运行 `scripts/validate_deliverables.py`

## 核心输出

| 类型 | 文件命名 | 用途 |
|------|----------|------|
| 报告 | `[日期]_[站点]_[ASIN]_上架复盘_[天数]天.md` | 复盘报告 |
| 数据 | `[日期]_[站点]_[ASIN]_复盘数据.xlsx` | 指标明细+趋势 |

## 下游对接

- Continue 决策 → `lean-product-develop-iteration-playbook`（迭代优化）
- Pivot 决策 → 修改产品后重新进入 launch-review
- Kill 决策 → 清库存退出，资源释放给新品

## 数据诚信规则

- **绝不捏造数据**：所有指标必须来自 Sorftime MCP 或用户提供的 Seller Central 数据
- **Sorftime 不可获取的数据**（如转化率、Sessions、广告数据）必须明确标注「用户输入」
- **区分事实与推测**：事实用数据支撑，推测必须标注「推测」

## 完整方法论

详见 `skills/lean-product-develop-launch-review/SKILL.md`
