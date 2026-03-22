---
name: amazon-product-phase3-mvp-blueprint
description: "亚马逊精益开发 Phase 3：将选品分析和需求验证结论转化为可执行的 MVP 产品规格书。使用 KANO 模型分类功能满意度类型（基本型/期望型/兴奋型/无差异/反向型），结合四维影响力评分定义 Must-have/Nice-to-have/Cut 功能矩阵。包含痛点根因原理层拆解、量化测试标准（Pass/Fail）、成本与盈亏平衡分析、Listing 上架规划。"
argument-hint: "[品类关键词] [站点] [--budget 预算] [--source 上游报告路径]"
user-invocable: true
---

# MVP 产品蓝图（精益开发 Phase 3）

## 定位

`amazon-product-phase3-mvp-blueprint` 是精益产品开发闭环的第三阶段，衔接上游 Phase 1（选品分析）和 Phase 2（需求验证），将数据结论转化为**可执行的最小可行产品规格书**。

核心问题：**最少做什么就能验证市场？**

## 使用方法

```
/amazon-product-phase3-mvp-blueprint bluetooth speaker US
/amazon-product-phase3-mvp-blueprint bluetooth speaker US --source ./path/to/upstream/
```

## 执行步骤

当调用此 Skill 时，**先读取本文件，再按需读取 `references/` 下的详细方法论**，执行以下流程：

1. **读取方法论** — 加载本文件（SKILL.md）获取执行流程和关键规则
2. **读取上游数据** — 加载 Phase 1 选品报告和 Phase 2 需求验证报告，提取核心结论。**重点：从 Phase 2 提取 complaint_rate 和 positive_mention_rate（详见 `references/kano_methodology.md`），这是 KANO 分类的核心输入，不需要自己重新搜索 Review。** 无 Phase 2 上游时降级为自行调用 Sorftime `product_reviews` 采集
3. **用户画像 + JTBD 任务地图** — 先读取 `references/user_persona.md` 构建目标用户画像，然后读取 `references/jtbd_methodology.md` 构建 JTBD 任务地图（3-6个 Job，含🔧功能型/💛情感型/👥社会型）。为每个 Job 评估重要性和当前满足度，计算 Gap（机会分）。Gap 最大的 Job = 核心差异化方向
4. **痛点根因拆解** — 读取 `references/root_cause_analysis.md`，对每个差评痛点执行原理层拆解（5 Whys → 物理根因 → 工程方案 → 供应商话术）。complaint_rate 和 positive_mention_rate 从 Step 2 已提取的 Phase 2 数据中计算
5. **内部堆叠结构调研** — 读取 `references/stack_cross_section.md`，通过 WebSearch 调研产品内部结构，在蓝图 MD 中用 ASCII 图画出组件堆叠 + 改善点标注。**剖面渲染图由下游 Phase 4/5 负责**
6. **创新亮点 & 外观差异化** — 读取 `references/influence_scoring.md` 中的创新清单，基于用户画像+竞品空白提出进攻型功能和外观差异化方案
7. **用户影响力排序** — 按 `references/influence_scoring.md` 的四维评分模型（A 可感知度 35% + B 决策力 30% + C 体验力 20% + D 成本效率 15%）统一评分排序。评分表必须包含 positive_mention_rate 列和**关联 Job 列**供 Step 8 使用
8. **KANO 增强型 MVP 功能矩阵** — 读取 `references/kano_methodology.md`，基于影响力分 + 差评率/好评率，算法推导 KANO 分类（M/O/A/I/R），通过修正器映射为 Must-have / Nice-to-have / Cut 三级决策。矩阵表必须包含**关联 Job 列**（用 J-F1、J-E1 等标签标注每个功能服务的 Job）
9. **MVP 规格书** — 每个属性维度的具体规格值 + 决策依据 + 原理层解释。包含外观差异化方向定义，作为下游 Phase 4/5 工业设计的输入
10. **测试标准定义** — 量化的 Pass/Fail 标准（转化率/BSR/ACOS/退货率/评分/周期）
11. **成本与盈亏平衡** — 首批采购+模具+头程+FBA+广告预算+盈亏平衡点
12. **Listing 上架规划** — 标题/五点/A+/图片清单/定价策略（文案匹配用户画像）
13. **供应商沟通指南** — 基于根因拆解，生成精确的技术改良需求表
14. **输出与验证** — 生成文档三件套（MD + HTML + XLSX）

## 核心输出

| 类型 | 文件命名 | 用途 |
|------|----------|------|
| 蓝图 (MD) | `[日期]_[站点]_[关键词]_MVP蓝图_v[n].md` | MVP 完整规格书 |
| 可视化看板 (HTML) | `[日期]_[站点]_[关键词]_MVP蓝图_可视化看板_v[n].html` | 深色主题交互看板（含 KANO 散点图） |
| 财务模型 (XLSX) | `[日期]_[站点]_[关键词]_MVP蓝图_财务模型.xlsx` | 成本测算、盈亏平衡、12个月预测 |

**三件套必须同时输出。** 工业设计图由下游 Phase 4/5 负责。

## 上下游对接

- **上游**：Phase 1（选品分析）+ Phase 2（需求验证）
- **下游**：Phase 4（设计调研）→ Phase 5（概念图生成）→ Phase 6（上架复盘）
- MVP 规格书中的外观方向 + ASCII 堆叠图 + 用户画像 → Phase 4/5 工业设计的核心输入

## 数据诚信规则

- **绝不捏造数据**：所有数据必须来自 Sorftime MCP 或明确标注来源
- **区分事实与推测**：推测必须标注 ⚠️
- **区分品类限制与设计缺陷**：根因拆解中必须区分

## KANO 分类快速参考（详见 `references/kano_methodology.md`）

| KANO | 判定条件 | 修正系数 | 优先级 |
|------|---------|---------|--------|
| M 🔴 基本型 | 差评率≥15% 且 好评率<5% | 锁定 | → Must-have |
| O 🟡 期望型 | 差评率≥5% 且 好评率≥5% | ×1.0 | 分≥3.0→Must / 2.0-2.99→Nice |
| A 🟢 兴奋型 | 差评率<5% 且 好评率≥10% | ×1.15 | 修正后≥2.5→Must / <2.5→Nice |
| I ⚪ 无差异 | 差评率<5% 且 好评率<5% 且 分<2.0 | ×0.5 | → Cut |
| R ⛔ 反向型 | ≥3条差评抱怨功能"存在" | ×0.0 | → Cut + ⚠️移除 |

## 可视化看板图表要求

HTML 看板中必须包含以下所有 Section（合并最佳实践）：

### Section 1：市场概况 + MVP 定义 + 用户画像
- 三栏卡片：市场数据 | MVP 产品定义 | 用户画像+JTBD 任务地图
- 用户画像卡片旁配 JTBD Job Map 表格（Job ID / 类型 / 任务描述 / 满足度）

### Section 2：JTBD 雷达图 + KANO 散点图（双栏）
- **JTBD 雷达图**（左）：Chart.js radar，蓝色实线=重要性，红色虚线=满足度，5轴=各Job
- **KANO 散点图**（右）：X轴=影响力分，Y轴=(positive_rate - complaint_rate)，颜色编码 🔴🟡🟢⚪⛔
- 底部汇总条统计各 KANO 类别数量

### Section 3：KANO 功能矩阵表（Tab 切换）
- 三个 Tab：✅ Must-have | 🟡 Nice-to-have | ❌ Cut
- 表头：# | 功能 | KANO | **关联 Job** | 差评率 | 好评率 | 影响力分 | 决策理由
- 每个功能名旁添加 KANO 彩色标签
- 影响力分数悬停显示分解："原始 X | KANO修正 ×Y | 最终 Z"

### Section 4：KANO 纠正旧系统误判对比表
- 表头：功能 | 旧系统判定 | 旧理由 | KANO 判定 | KANO 理由 | 变化（↑拯救 / ↓识别有害 / =不变）
- 突出 KANO 相比纯差评率阈值法的纠偏能力

### Section 5：四维影响力评分明细表
- 表头：功能 | 类型 | A 可感知(35%) | B 决策力(30%) | C 体验力(20%) | D 成本效率(15%) | 原始分 | KANO | 修正 | 最终分
- 底部标注公式：总分 = A×0.35 + B×0.30 + C×0.20 + D×0.15

### Section 6：痛点根因 + 成本盈亏 + 测试标准 + 核心规格
- 痛点根因拆解可视化（进度条显示差评占比）
- 成本拆解柱状图 + 盈亏平衡
- Pass/Fail 测试标准表
- MVP 核心规格表

## Reference 文件索引

详细方法论按需读取，不要一次性全部加载：

| 文件 | 内容 | 何时读取 |
|------|------|---------|
| `references/user_persona.md` | 用户画像构建方法论（数据来源、输出模板、没有数据时的推断方式） | Step 3 |
| `references/jtbd_methodology.md` | JTBD 任务地图方法论（三层分类、Job Map 构建、重要性/满足度评分、Gap 分析、Job→功能映射） | Step 3 |
| `references/root_cause_analysis.md` | 痛点根因拆解方法论（5 Whys 流程、品类限制 vs 设计缺陷、输出模板、品类参考、供应商沟通原则） | Step 4 |
| `references/stack_cross_section.md` | 内部堆叠剖面图方法论（调研流程、ASCII 画法、改善点标注格式） | Step 5 |
| `references/influence_scoring.md` | 用户影响力评估模型（三类角色定义、四维评分标准、隐形改良可视化、创新清单、预算分档） | Step 6-7 |
| `references/kano_methodology.md` | KANO 增强型功能矩阵方法论（五类定义、算法决策树、修正器、数据规则、输出格式模板、示例） | Step 8 |

---

## 飞书通知（可选）

当分析完成后，如果检测到飞书凭据已配置（环境变量 `FEISHU_WEBHOOK_URL` 或 `FEISHU_APP_ID` 存在且非空），询问用户是否推送结果到飞书。

如果用户明确要求"发到飞书"、"推送到飞书"、"通知群里"，则直接执行推送：

```bash
python "$HOME/.claude/skills/feishu-integration/feishu_sdk.py" \
  notify \
  --phase <当前Phase编号> \
  --product "<产品名>" \
  --decision "<决策结果>" \
  --metrics '<JSON格式核心指标>'
```

可选追加参数：
- `--report <报告.md路径>` + `--push-doc`：同时创建飞书文档
- `--xlsx <数据.xlsx路径>` + `--push-bitable`：同时写入多维表格

如果飞书凭据未配置，不执行推送，也不提示配置（避免打断分析流程）。
