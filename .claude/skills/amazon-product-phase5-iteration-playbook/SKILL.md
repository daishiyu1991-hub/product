---
name: amazon-product-phase5-iteration-playbook
description: "亚马逊精益开发 Phase 5：基于上架复盘数据，生成可执行的迭代优化方案。用 Impact x Effort 矩阵排序优先级，覆盖 Listing 优化、产品改良、广告策略、变体扩展四大方向，输出 30 天行动计划。优先调用 Sorftime MCP；无 Sorftime 时降级为 WebSearch + 用户手动输入。"
argument-hint: "[ASIN] [站点] [--review-report 复盘报告路径] [--focus listing|product|ads|expansion]"
user-invocable: true
---

# 迭代优化手册（精益开发 Phase 5）

## 定位

`amazon-product-phase5-iteration-playbook` 是精益产品开发闭环的第五阶段。基于复盘数据（Phase 4：`amazon-product-phase4-launch-review`），回答一个关键问题：**下一个 30 天应该优先做什么？**

将复盘中发现的问题转化为排过优先级的、具体可执行的优化行动项。

## 适用场景

- 上架复盘后决策为 Continue，需要制定优化计划
- 产品销量增长停滞，需要找到突破口
- 准备产品迭代（二代产品），需要数据驱动的改良方向
- 广告 ACOS 过高，需要系统性广告优化方案
- 计划扩展变体（颜色/尺寸/套装）

## 前置条件

- 上架复盘报告（推荐，非强制）
- 已上架产品的 ASIN
- Python 3.9+，安装 `openpyxl`

## 使用方法

### 方式1：指定 ASIN 和聚焦方向
```
/amazon-product-phase5-iteration-playbook B0XXXXXXXX US --focus listing
```

### 方式2：关联复盘报告
```
/amazon-product-phase5-iteration-playbook B0XXXXXXXX US --review-report ./工作成果/brands/AORYVIC/精益开发/bluetooth-speaker/launch-review/
```

### 方式3：自然语言
```
帮我为 B0XXXXXXXX 制定一个迭代优化计划，重点是广告和 Listing
```

## 执行步骤

当调用此 Skill 时，执行以下流程：

1. **读取完整方法论** — 加载 `skills/amazon-product-phase5-iteration-playbook/SKILL.md`
2. **读取复盘数据** — 加载 launch-review（Phase 4）的复盘报告
3. **优化优先级排序** — Impact x Effort 矩阵，四大方向评估
4. **Listing 优化方案** — 标题/图片/A+/五点/价格策略
5. **产品改良方案** — 差评主题映射 + 改良优先级
6. **广告优化方案** — 关键词分层策略 + 出价 + 广告结构
7. **变体/扩品规划** — 变体分析 + 扩品方向 + 套装机会
8. **30 天行动计划** — 按周拆解的任务清单
9. **输出与验证** — 生成文档，运行 `scripts/validate_deliverables.py`

## 核心输出

| 类型 | 文件命名 | 用途 |
|------|----------|------|
| 手册 | `[日期]_[站点]_[ASIN]_迭代手册_v[n].md` | 优化方案全文 |
| 矩阵 | `[日期]_[站点]_[ASIN]_迭代优先级.xlsx` | Impact x Effort 矩阵 |
| 计划 | `[日期]_[站点]_[ASIN]_30天行动计划.md` | 每周任务清单 |

## 上下游对接

- 上游：`amazon-product-phase4-launch-review`（Phase 4：上架复盘）
- 下游：
  - 迭代优化完成后 → 产品进入下一轮 `amazon-product-phase4-launch-review`（Phase 4）复盘
  - 如果多轮迭代后表现稳定 → 进入 `amazon-product-phase6-scale-decision`（Phase 6：规模化决策）

## 完整方法论

详见 `skills/amazon-product-phase5-iteration-playbook/SKILL.md`
