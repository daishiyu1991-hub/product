---
name: amazon-product-phase3-mvp-blueprint
description: "亚马逊精益开发 Phase 3：将选品分析和需求验证结论转化为可执行的 MVP 产品规格书。使用 KANO 模型分类功能满意度类型（基本型/期望型/兴奋型/无差异/反向型），结合四维影响力评分定义 Must-have/Nice-to-have/Cut 功能矩阵。包含痛点根因原理层拆解、量化测试标准（Pass/Fail）、成本与盈亏平衡分析、Listing 上架规划。整合：场景拆解 + 价值网分析 + 五层体验设计。采用分段写入架构防止输出卡死。"
argument-hint: "[品类关键词] [站点] [--budget 预算] [--source 上游报告路径]"
user-invocable: true
---

# MVP 产品蓝图（精益开发 Phase 3）

## 定位

`amazon-product-phase3-mvp-blueprint` 是精益产品开发闭环的第三阶段，衔接上游 Phase 1（选品分析）和 Phase 2（需求验证），将数据结论转化为**可执行的最小可行产品规格书**。

核心问题：**最少做什么就能验证市场？**

整合梁宁产品思维中的**场景拆解**（场景=时间+空间+情绪）、**价值网分析**（颠覆式创新判断）和**五层体验设计**（从存在层到感知层），在功能矩阵之外增加场景维度、竞争格局维度和体验架构维度，使 MVP 蓝图更立体。

## 使用方法

```
/amazon-product-phase3-mvp-blueprint bluetooth speaker US
/amazon-product-phase3-mvp-blueprint bluetooth speaker US --source ./path/to/upstream/
```

## ⚠️ 分段写入架构（防卡死）

本 Skill 采用 **4 阶段分段写入**，每个阶段独立落盘。即使中间断开也不丢失前序成果。

```
Phase 3 执行流程：

Stage A: 数据采集 + 用户洞察
  → 写入 _stage_a.json（结构化数据）
  → 写入 MD 文件前半部分（用户画像+JTBD+场景+价值网+五层）

Stage B: 功能分析 + KANO 矩阵
  → 写入 _stage_b.json（功能评分数据）
  → 追加 MD 文件中段（痛点根因+影响力评分+用户价值+KANO矩阵+规格书）

Stage C: 商业规划
  → 追加 MD 文件后段（成本盈亏+测试标准+Listing规划+供应商指南）
  → 写入 XLSX 财务模型

Stage D: 可视化渲染
  → 基于 _stage_a.json + _stage_b.json 生成完整 HTML 看板
  → 清理临时 JSON 文件
```

**关键规则：**
- 每个 Stage 结束时必须执行 Write/Edit 落盘，不要积压
- Stage 之间用 JSON 文件传递数据，而非依赖 context 记忆
- HTML 在最后 Stage D 一次性生成，但数据来自已落盘的 JSON，不需要重新计算
- 如果某个 Stage 中断，告知用户"从 Stage X 继续"，读取已有 JSON 恢复

## 执行步骤

当调用此 Skill 时，**先读取本文件，再按需读取 `references/` 下的详细方法论**。

---

### Stage A：数据采集 + 用户洞察（Steps 1-6）

**目标**：完成所有数据采集和用户/场景/竞争分析，产出结构化数据文件。

**Step 1: 读取方法论** — 加载本文件（SKILL.md）获取执行流程和关键规则

**Step 2: 读取上游数据** — 加载 Phase 1 选品报告和 Phase 2 需求验证报告，提取核心结论。**重点：从 Phase 2 提取 complaint_rate 和 positive_mention_rate（详见 `references/kano_methodology.md`），这是 KANO 分类的核心输入，不需要自己重新搜索 Review。** 无 Phase 2 上游时降级为自行调用 Sorftime `product_reviews` 采集

**Step 3: 用户画像 + JTBD 任务地图** — 先读取 `references/user_persona.md` 构建目标用户画像，然后读取 `references/jtbd_methodology.md` 构建 JTBD 任务地图（3-6个 Job，含🔧功能型/💛情感型/👥社会型）。为每个 Job 评估重要性和当前满足度，计算 Gap（机会分）。Gap 最大的 Job = 核心差异化方向

**Step 4: 场景拆解** — 读取 `references/scene_decomposer.md`，用 Sorftime `keyword_extends` + `product_reviews` 提取场景信号（关键词场景 + Review 场景），拆解每个场景为**时间×空间×情绪**，按搜索量排序，识别未被占领的空白场景，确定主攻/辅攻场景。场景分析指导后续 Listing 写法和 A+ 规划

**Step 5: 价值网分析** — 读取 `references/value_network.md`，判断你的产品在哪个价值网竞争：同网竞争/低端颠覆/新市场颠覆。评估颠覆可行性，输出竞争策略建议。价值网定位决定定价策略和差异化方向

**Step 6: 五层体验设计** — 读取 `references/five_layer_experience.md`，从存在层→能力层→资源层→角色层→感知层自下而上设计产品体验架构。结合 Step 3 的用户画像和 Step 4 的场景数据：
  - **存在层**：产品的战略意义（为什么做这个产品）
  - **能力层**：需要具备的核心能力（供应链/技术/品牌）
  - **资源层**：可调用的资源（工厂/渠道/数据）
  - **角色层**：用户以什么身份使用（角色框架设计）
  - **感知层**：用户直接感知的体验（视觉/触觉/开箱）
  - 输出：每层的设计标准和验收准则

**🔴 Stage A 落盘点：**
```
1. 写入 `[输出目录]/_stage_a.json`：
   {
     "product": "产品名",
     "site": "站点",
     "user_persona": { ... },
     "jtbd_jobs": [ ... ],
     "scenes": [ ... ],
     "value_network": { ... },
     "five_layer_design": { ... },
     "upstream_data": {
       "complaint_rates": { ... },
       "positive_rates": { ... },
       "market_summary": { ... }
     }
   }
2. 写入 MD 文件前半部分：
   - 标题 + 市场概况
   - 用户画像 + JTBD 任务地图
   - 场景拆解分析
   - 价值网分析
   - 五层体验设计
```

---

### Stage B：功能分析 + KANO 矩阵（Steps 7-12）

**目标**：完成功能层面的深度分析和 MVP 矩阵定版。

**Step 7: 痛点根因拆解** — 读取 `references/root_cause_analysis.md`，对每个差评痛点执行原理层拆解（5 Whys → 物理根因 → 工程方案 → 供应商话术）。complaint_rate 和 positive_mention_rate 从 `_stage_a.json` 读取

**Step 8: 内部堆叠结构调研** — 读取 `references/stack_cross_section.md`，通过 WebSearch 调研产品内部结构，在蓝图 MD 中用 ASCII 图画出组件堆叠 + 改善点标注。**剖面渲染图由下游 Phase 5/6 负责**

**Step 9: 创新亮点 & 外观差异化** — 读取 `references/influence_scoring.md` 中的创新清单，基于用户画像+竞品空白提出进攻型功能和外观差异化方案

**Step 10: 用户影响力排序** — 按 `references/influence_scoring.md` 的四维评分模型（A 可感知度 35% + B 决策力 30% + C 体验力 20% + D 成本效率 15%）统一评分排序。评分表必须包含 positive_mention_rate 列和**关联 Job 列**供 Step 12 使用

**Step 11: 用户价值公式评定** — 读取 `references/user_value_formula.md`，对整个 MVP 方案执行梁宁"用户价值公式"评定。量化新体验分、旧体验分、五类替换成本，计算用户价值净值，输出 GO/CAUTION/STOP 信号。**此步骤是对整体 MVP 方案的战略校验，在逐功能 KANO 排序之后、最终矩阵定版之前执行**

**Step 12: KANO 增强型 MVP 功能矩阵** — 读取 `references/kano_methodology.md`，基于影响力分 + 差评率/好评率，算法推导 KANO 分类（M/O/A/I/R），通过修正器映射为 Must-have / Nice-to-have / Cut 三级决策。矩阵表必须包含**关联 Job 列**（用 J-F1、J-E1 等标签标注每个功能服务的 Job）。**如果 Step 11 用户价值评定为 CAUTION，在矩阵底部标注风险提醒；如果为 STOP，暂停后续步骤并建议回退 Phase 1 重新选品**

**🔴 Stage B 落盘点：**
```
1. 写入 `[输出目录]/_stage_b.json`：
   {
     "pain_points": [ ... ],
     "influence_scores": [ ... ],
     "user_value": { "new_exp": x, "old_exp": y, "switch_cost": z, "net": n, "signal": "GO" },
     "kano_matrix": {
       "must_have": [ ... ],
       "nice_to_have": [ ... ],
       "cut": [ ... ]
     },
     "kano_corrections": [ ... ]
   }
2. 追加 MD 文件中段（用 Edit 工具追加，不要重写全文）：
   - 痛点根因拆解
   - 内部堆叠结构 ASCII 图
   - 四维影响力评分表
   - 用户价值公式评定
   - KANO 功能矩阵（Must-have / Nice-to-have / Cut）
   - MVP 规格书（每个属性维度的具体规格值+决策依据+原理层解释）
```

---

### Stage C：商业规划（Steps 13-16）

**目标**：完成商业化规划，产出财务模型。

**Step 13: 测试标准定义** — 量化的 Pass/Fail 标准（转化率/BSR/ACOS/退货率/评分/周期）

**Step 14: 成本与盈亏平衡** — 首批采购+模具+头程+FBA+广告预算+盈亏平衡点

**Step 15: Listing 上架规划** — 标题/五点/A+/图片清单/定价策略（文案匹配用户画像 + **场景化写法**，基于 Stage A 场景拆解结果 + **五层感知层设计标准**）

**Step 16: 供应商沟通指南** — 基于根因拆解，生成精确的技术改良需求表

**🔴 Stage C 落盘点：**
```
1. 追加 MD 文件后段（用 Edit 工具追加）：
   - 测试标准
   - 成本与盈亏平衡
   - Listing 上架规划
   - 供应商沟通指南
2. 生成 XLSX 财务模型文件
3. MD 文件写入完成，告知用户"MD + XLSX 已完成，正在生成 HTML 看板..."
```

---

### Stage D：可视化渲染（Step 17）

**目标**：基于已落盘的 JSON 数据生成 HTML 可视化看板。

**Step 17: HTML 看板生成** — 读取 `_stage_a.json` + `_stage_b.json`，生成完整 HTML 看板。数据全部从 JSON 文件读取，不要重新计算或重新分析。

HTML 看板结构见下方「可视化看板图表要求」。

**🔴 Stage D 落盘点：**
```
1. 写入 HTML 看板文件
2. 删除临时文件：_stage_a.json, _stage_b.json
3. 输出三件套路径汇总
4. 用 powershell 自动打开 HTML 文件
```

---

## 中断恢复协议

如果执行中断，按以下逻辑恢复：

| 已有文件 | 说明 | 恢复动作 |
|---------|------|---------|
| 无 | 全新开始 | 从 Stage A Step 1 开始 |
| `_stage_a.json` 存在 | Stage A 已完成 | 从 Stage B Step 7 开始，读取 `_stage_a.json` |
| `_stage_a.json` + `_stage_b.json` 存在 | Stage A+B 已完成 | 从 Stage C Step 13 开始 |
| `_stage_a.json` + `_stage_b.json` + MD 完整 | Stage A+B+C 已完成 | 从 Stage D Step 17 开始 |
| 三件套齐全 | 已全部完成 | 告知用户已完成，询问是否需要修改 |

**恢复时告知用户**："检测到上次执行到 Stage X，从 Stage Y 继续。"

---

## 核心输出

| 类型 | 文件命名 | 用途 |
|------|----------|------|
| 蓝图 (MD) | `[日期]_[站点]_[关键词]_MVP蓝图_v[n].md` | MVP 完整规格书 |
| 可视化看板 (HTML) | `[日期]_[站点]_[关键词]_MVP蓝图_可视化看板_v[n].html` | 深色主题交互看板（含 KANO 散点图） |
| 财务模型 (XLSX) | `[日期]_[站点]_[关键词]_MVP蓝图_财务模型.xlsx` | 成本测算、盈亏平衡、12个月预测 |

**三件套必须同时输出。** 工业设计图由下游 Phase 5/6 负责。

## 上下游对接

- **上游**：Phase 1（选品分析）+ Phase 2（需求验证）
- **下游**：Phase 4（战略验证）→ Phase 5（设计调研）→ Phase 6（概念图生成）→ Phase 7（上架复盘）
- MVP 规格书中的外观方向 + ASCII 堆叠图 + 用户画像 + **场景拆解** + **价值网定位** + **五层体验设计** → Phase 4 战略验证 + Phase 5/6 工业设计的核心输入

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

### Section 2：JTBD 雷达图 + KANO 散点图 + 用户价值公式（三栏）
- **JTBD 雷达图**（左）：Chart.js radar，蓝色实线=重要性，红色虚线=满足度，5轴=各Job
- **KANO 散点图**（中）：X轴=影响力分，Y轴=(positive_rate - complaint_rate)，颜色编码 🔴🟡🟢⚪⛔
- **用户价值仪表盘**（右）：显示新体验分、旧体验分、替换成本分、净值，用温度计/进度条可视化，底部显示 GO/CAUTION/STOP 信号灯
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

### Section 6：场景矩阵 + 五层体验 + 痛点根因 + 成本盈亏
- **场景矩阵表**：场景名 | 时间 | 空间 | 情绪 | 搜索量 | 竞争强度 | 战略定位（主攻/辅攻/观察）
- **五层体验雷达图**：Chart.js radar，5轴=感知/角色/资源/能力/存在，蓝色=设计目标分，灰色=竞品平均分
- **价值网定位图**：产品在价值网中的位置（同网/低端颠覆/新市场）
- 痛点根因拆解可视化（进度条显示差评占比）
- **内部堆叠剖面图**：如果有渲染图用 base64 嵌入，否则用 `<pre>` ASCII 图
- 成本拆解柱状图 + 盈亏平衡
- Pass/Fail 测试标准表
- MVP 核心规格表

## Reference 文件索引

详细方法论按需读取，不要一次性全部加载：

| 文件 | 内容 | 何时读取 |
|------|------|---------|
| `references/user_persona.md` | 用户画像构建方法论 | Step 3 |
| `references/jtbd_methodology.md` | JTBD 任务地图方法论 | Step 3 |
| `references/scene_decomposer.md` | 场景拆解方法论（梁宁产品思维） | Step 4 |
| `references/value_network.md` | 价值网分析方法论（颠覆式创新判断） | Step 5 |
| `references/five_layer_experience.md` | 五层体验设计方法论（梁宁用户体验模块） | Step 6 |
| `references/root_cause_analysis.md` | 痛点根因拆解方法论 | Step 7 |
| `references/stack_cross_section.md` | 内部堆叠剖面图方法论 | Step 8 |
| `references/influence_scoring.md` | 用户影响力评估模型（四维评分） | Step 9-10 |
| `references/user_value_formula.md` | 用户价值公式方法论（梁宁框架） | Step 11 |
| `references/kano_methodology.md` | KANO 增强型功能矩阵方法论 | Step 12 |

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
