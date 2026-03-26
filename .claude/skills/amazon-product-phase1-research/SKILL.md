---
name: amazon-product-phase1-research
description: "亚马逊精益开发 Phase 1：基于 Sorftime MCP 的亚马逊选品分析 Skill，用于发现潜力市场、验证竞争格局、完成属性标注与交叉分析，并输出 Go/No-Go 结论及标准化市场调研交付物。"
argument-hint: "[产品/类目关键词] [站点]"
user-invocable: true
---

# 选品分析器（精益开发 Phase 1）

## 定位

`amazon-product-phase1-research` 是精益产品开发闭环的**第一阶段**，用于亚马逊新品上架工作流的第一步：先判断市场值不值得进入，再决定后续是否投入竞品拆解、定价、Listing 文案和广告预算。

核心目标：

1. 发现有机会的细分类目或目标子赛道
2. 识别竞争格局、进入门槛和新品友好度
3. 对 Top100 产品做属性标注与交叉分析
4. 给出 `GO / CONDITIONAL GO / HOLD / NO-GO` 决策
5. 产出可复核的市场调研四件套

## 适用场景

- 用户只有一个产品标题或一个品类词，想先判断能不能做
- 用户准备上新，需要先完成市场调研和选品论证
- 用户已经有供应链资源，想找更合适的切入子市场
- 用户需要标准化交付，方便团队内部审核和复盘

## 前置条件

- Sorftime MCP 已配置并可调用
- Python 3.9+，安装 `openpyxl`（`pip install openpyxl`）
- 明确目标站点，默认 `US`

## 使用方法

### 方式1：指定产品和站点
```
/amazon-product-phase1-research bluetooth speaker US
```

### 方式2：自然语言
```
帮我用 Sorftime 分析美国站蓝牙音箱选品机会
```

### 方式3：带约束条件
```
帮我找美国站月销1000+、价格$15-30、评论门槛低的潜力产品
```

## 执行步骤

当调用此 Skill 时，执行以下流程：

1. **读取完整方法论** - 加载 `skills/amazon-product-phase1-research/SKILL.md`
2. **信息收集** - 交互式确认目标站点、选品场景、约束条件
3. **调用 Sorftime MCP** - 按下方工具编排规则调用数据工具

## 工具编排规则（步骤3适用）

### 工具决策树 — 根据已知信息选择最短路径

**获取品类数据:**
- 已知 nodeId → `category_report(nodeId)` 直接查
- 只有产品名 → `category_search_from_product_name(searchName)` → 取 nodeId → `category_report`
- 只有大品类 → `category_tree` → 用户选节点 → `category_search_from_top_node(topNodeId)`

**获取关键词数据:**
- 有明确关键词 → `keyword_detail(keyword)` + `keyword_trend(keyword)`
- 需要发现关键词 → `keyword_extends(searchKeyword)` → 筛选月搜量 >1000 → 逐个 `keyword_detail`
- 需要竞品流量词 → `product_traffic_terms(asin)` → 提取高频词 → `keyword_detail`

**获取产品数据:**
- 有 ASIN → `product_detail(asin)` + `product_report(asin)`
- 无 ASIN → `product_search(searchName)` → 取 Top ASIN → `product_detail`

### 并行 vs 串行声明

**可并行（互不依赖，同时调用）:**
- `keyword_detail` + `keyword_trend` （同一关键词的不同维度）
- `product_detail` + `product_reviews` + `product_trend` （同一 ASIN 的不同维度）
- 多个 ASIN 的 `product_report` 调用

**必须串行（后者依赖前者输出）:**
- `category_search_from_product_name` → `category_report`（需要 nodeId）
- `product_search` → `product_detail`（需要 ASIN）
- `keyword_extends` → 筛选 → `keyword_detail`（需要先知道哪些词值得查）

### 工具失败处理

| 失败情况 | 处理方式 |
|---------|---------|
| 单工具失败 | 标注 ⚠️，继续后续步骤 |
| `category_report` 失败 | 降级：`product_search` + 手动统计 Top50 |
| `product_reviews` 失败 | 降级：WebSearch 搜 "产品名 + review" |
| `keyword_detail` 失败 | 降级：`keyword_list` 按排名范围搜 |
| MCP 整体不可用 | 告知用户 + WebSearch 降级 + 报告标题加 ⚠️ |

---
4. **市场机会发现** - 类目扫描 + 关键词多维度对比 + 潜力产品预筛
5. **维度自发现** - 标题词频聚类 + 关键词延伸词 + product_detail 属性 Key 提取 → 候选维度列表 → 用户确认
6. **产品属性标注** - Top100 标题解析提取多维度属性 → 对"未知"项批量调 `product_detail` 验证
7. **多维度交叉分析** - 维度交叉矩阵 → 供需缺口自动识别 → 品牌集中度分析
8. **新品分析** - Top100 新品占比 + 时间分桶 + 新品友好度评级
9. **竞争格局验证** - 竞品选择逻辑表（6-10 个竞品）+ 差评维度归类
10. **进入壁垒评估** - 6 类壁垒评估 + 站点合规速查
11. **投入产出测算** - 按下方「投入产出测算公式模板」逐项计算，⛔ 禁止跳过自检
12. **正反方辩论（角色叠加对抗）** - 用两个对立视角审视分析结论，避免单一视角盲区
    - **乐观产品经理**：站在"应该做"的角度，列出 3 个最强的进入理由，引用前面的数据支撑
    - **悲观风控官**：站在"不该做"的角度，针对上述 3 个理由逐一反驳，指出数据中被忽略的风险信号
    - **仲裁总结**：综合两方论点，判断哪方的论据更有说服力，输出平衡结论
    - ⛔ 悲观方不能只说"竞争激烈"等空话，必须引用具体数据反驳
    - ⛔ 如果乐观方和悲观方在某个维度的结论完全一致，说明该维度的判断较可靠
13. **Go/No-Go 综合评分** - 5 维度加权评分 → 决策（基于辩论仲裁结论）
14. **交付前自检 + 一键渲染** - 组装 unified_payload.json v2 → `render_deliverables.py all`

## 核心输出（四件套）

| 类型 | 文件命名 | 用途 |
|------|----------|------|
| 报告 | `[日期]_[站点]_[关键词]_市场调研报告_[version].md` | 完整分析报告（10 章结构） |
| 精简 | `[日期]_[站点]_[关键词]_精简报告_[version].html` | 快速浏览关键结论 |
| 看板 | `[日期]_[站点]_[关键词]_可视化看板_[version].html` | 交互式 Dashboard |
| 数据 | `[日期]_[站点]_[关键词]_市场调研_数据_[version].xlsx` | 多 Sheet 明细数据 |

## 下游对接

选品报告 → `amazon-product-phase2-demand-validator`（Phase 2：需求验证）→ `amazon-product-phase3-mvp-blueprint`（Phase 3：MVP 蓝图）

## 输出协议（Skill 间数据契约）

`unified_payload.json` 必须包含以下字段，供下游 Skill 直接读取：

```json
{
  "meta": {
    "phase": "phase1",
    "product": "产品名",
    "site": "US",
    "date": "2026-03-26",
    "version": "v1"
  },
  "decision": {
    "result": "GO | CONDITIONAL_GO | HOLD | NO_GO",
    "confidence": 0.0-1.0,
    "scores": {
      "market_size": { "score": 1-5, "reason": "..." },
      "competition": { "score": 1-5, "reason": "..." },
      "differentiation": { "score": 1-5, "reason": "..." },
      "profitability": { "score": 1-5, "reason": "..." },
      "feasibility": { "score": 1-5, "reason": "..." }
    },
    "warnings": ["风险1", "风险2"]
  },
  "market": {
    "nodeId": "...",
    "monthSales": 0,
    "avgPrice": 0.0,
    "trendDirection": "上升 | 平稳 | 下降",
    "top3Share": 0.0,
    "newProductShare": 0.0,
    "amazonOwnedShare": 0.0
  },
  "keywords": [
    { "word": "...", "searchVolume": 0, "cpc": 0.0, "trend": "上升|平稳|下降" }
  ],
  "competitors": [
    { "asin": "...", "title": "...", "price": 0.0, "monthlySales": 0, "rating": 0.0, "reviewCount": 0 }
  ],
  "painPoints": ["痛点1", "痛点2"],
  "next_phase": "phase2 | stop"
}
```

**下游触发规则:**
- `decision.result = "GO"` + `confidence >= 0.7` → 自动建议执行 Phase 2
- `decision.result = "CONDITIONAL_GO"` → 列出需满足条件，用户确认后继续
- `decision.result = "HOLD"` → 暂停，列出待补充数据
- `decision.result = "NO_GO"` → 终止，不进入 Phase 2

## 数据诚信规则

- **绝不捏造数据**：所有数据必须来自 Sorftime MCP 调用结果
- **标注数据来源**：每个数据点标注来源工具
- **区分事实与推测**：事实用数据支撑，推测必须标注「⚠️ 推测」

---

## 投入产出测算公式模板（⛔ 必须严格遵守）

> 执行步骤第 11 步时，**必须按以下模板逐项计算**，不得自由发挥公式。

### A. 成本结构

```
产品落地成本 = 出厂价 + 头程物流 + FBA配送费
亚马逊佣金 = 售价 × 15%（灯具类目标准佣金率）
```

### B. 毛利计算

```
单件毛利 = 售价 - 产品落地成本 - 亚马逊佣金
毛利率 = 单件毛利 ÷ 售价 × 100%
```

### C. ACOS 计算（⛔ 易错公式，必须按此计算）

```
每出1单的广告花费 = CPC ÷ 转化率
ACOS = 每出1单的广告花费 ÷ 售价 × 100%
     = CPC ÷ 转化率 ÷ 售价 × 100%
```

**示例（必须在报告中展示完整计算过程）：**

| 场景 | CPC | 转化率(CVR) | 每单广告花费 = CPC÷CVR | 售价 | ACOS = 每单广告花费÷售价 |
|------|-----|------------|----------------------|------|----------------------|
| 最优 | $0.57 | 15% | $0.57÷0.15 = $3.80 | $24.99 | $3.80÷$24.99 = **15.2%** |
| 中等 | $0.80 | 12% | $0.80÷0.12 = $6.67 | $24.99 | $6.67÷$24.99 = **26.7%** |
| 保守 | $1.13 | 10% | $1.13÷0.10 = $11.30 | $24.99 | $11.30÷$24.99 = **45.2%** |

⛔ **自检：ACOS 绝不可能低于 5%**。如果算出 ACOS < 5%，说明公式用错了，立即停下来检查。
⛔ **常见错误**：把 `CPC × 转化率` 当成每单广告花费 → 这是错的。转化率是分母（需要点 1÷CVR 次才出 1 单），不是乘数。

### D. 净利计算

```
单件广告费 = 售价 × ACOS目标
单件净利 = 单件毛利 - 单件广告费
净利率 = 单件净利 ÷ 售价 × 100%
```

### E. 盈亏平衡

```
月固定成本 = 仓储费 + 工具订阅 + 其他（约 $200-500/月）
盈亏平衡月销量 = 月固定成本 ÷ 单件净利
```

### F. 输出格式

报告中必须包含：
1. 成本结构表（每项带金额和备注）
2. ACOS 三场景表（最优/中等/保守，**展示完整中间计算步骤**）
3. 盈亏平衡表（保守/中等/乐观三场景）

---

## 完整方法论

详见 `skills/amazon-product-phase1-research/SKILL.md`

---

## 交付前自检（⛔ 必须执行，不可跳过）

在输出最终报告之前，对照以下清单逐项检查。发现问题必须修正后再输出。

### 数据完整性检查
- [ ] 所有数据都标注了来源（Sorftime MCP / WebSearch / 用户提供）？
- [ ] 没有出现无来源的具体数字（如"月销量约5000"但没有查数据）？
- [ ] Top100 数据的覆盖率 ≥ 80%（缺失的维度有标注）？

### 逻辑一致性检查
- [ ] 结论（GO/NO-GO）和前面的数据分析方向一致？
  - 反例：数据显示 Top3 占比 60%、新品占比 2%，但结论是 GO → ⛔ 矛盾
- [ ] 前后文没有自相矛盾？
  - 反例：第3章说"竞争激烈"，第8章说"进入门槛低" → ⛔ 矛盾
- [ ] 风险评估和机会评估的权重合理？不能只看好的不看坏的

### 计算验证（重新代入具体数字算一遍）
- [ ] 毛利率 = (售价 - 落地成本 - 佣金) / 售价 → 重新验算
- [ ] 盈亏ACOS = 毛利率 × (1 - 预估自然订单占比) → 重新验算
- [ ] 如果盈亏ACOS < 15% 或 > 60%，大概率计算有误 → 重新检查输入值

### 关键维度覆盖
- [ ] 市场规模（月销量、月搜索量、增长趋势）
- [ ] 竞争格局（Top3占比、品牌集中度、亚马逊自营占比）
- [ ] 新品友好度（3个月内新品在Top100的销量占比）
- [ ] 差异化空间（差评痛点、功能缺口）
- [ ] 利润空间（毛利率、盈亏ACOS、净利率）

如果以上有任何一项未通过，修正后再输出最终报告。

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
