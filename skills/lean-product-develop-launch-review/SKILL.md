---
name: lean-product-develop-launch-review
description: 亚马逊精益开发 Phase 4 - 上架数据复盘完整方法论
argument-hint: "[ASIN] [站点] [--days 复盘天数] [--mvp-blueprint 蓝图路径]"
user-invocable: true
---

# 上架数据复盘 - 完整方法论

## 定位

产品上架后的数据驱动复盘，用量化指标对照 MVP 蓝图中的测试标准，客观执行 **Kill / Continue / Pivot** 决策。

**精益核心原则**：只看数据，不看感觉。没达标就 Kill，不要因为沉没成本而继续。

---

## Script Directory

- `scripts/analyze_performance.py`
  - 用途：解析 Sorftime 产品数据，计算 KPI 对照表
  - 命令：`python skills/lean-product-develop-launch-review/scripts/analyze_performance.py --input <data.json> --baseline <mvp_params.json>`
- `scripts/generate_review_report.py`
  - 用途：组装复盘报告 Markdown + Excel
  - 命令：`python skills/lean-product-develop-launch-review/scripts/generate_review_report.py --input <payload.json>`
- `scripts/validate_deliverables.py`
  - 用途：验证交付物完整性
  - 命令：`python skills/lean-product-develop-launch-review/scripts/validate_deliverables.py --dir <output_dir>`

## References

- `references/kpi_benchmarks.md` — 各品类 KPI 基准值参考
- `references/kill_continue_pivot_framework.md` — Kill/Continue/Pivot 决策框架详细说明
- `references/review_sentiment_rules.md` — Review 情感分析规则

---

## 硬性规则（⛔ 不可省略）

1. ⛔ **必须对照基线**：每个 KPI 必须与 MVP 蓝图中的 Pass/Fail 阈值对比，标注 🟢/🟡/🔴
2. ⛔ **决策必须量化**：最终 Kill/Continue/Pivot 决策必须基于红绿灯数量，不允许主观判断
3. ⛔ **Review 分析不可跳过**：即使只有 1-2 个 Review，也必须分析并记录
4. ⛔ **广告数据透明**：如果 Sorftime 无法获取广告数据，必须向用户索取并明确标注「用户输入」
5. ⛔ **趋势比绝对值更重要**：每个指标必须展示趋势方向（↑/→/↓），不只看当前值
6. ⛔ **竞品对标必须具体**：至少与 3 个竞品对比当前指标
7. ⛔ **行动项必须具体可执行**：禁止 "优化 Listing"、"提高转化率" 等模糊建议

---

## Sorftime MCP 工具清单

| 工具 | 用途 | 优先级 |
|------|------|--------|
| `product_detail` | 产品当前价格/排名/评论数/评分 | ⛔ 必调 |
| `product_trend` | BSR 排名趋势、价格趋势 | ⛔ 必调 |
| `product_reviews` | 客户评价分析（好评+差评） | ⛔ 必调 |
| `product_traffic_terms` | 自然流量关键词排名 | ⛔ 必调 |
| `product_variations` | 变体表现对比（如有变体） | 📋 按需 |
| `competitor_product_keywords` | 竞品关键词曝光 | 📋 按需 |
| `product_search` | 搜索结果中的排名位置 | 📋 按需 |

**降级方案**（无 Sorftime 时）：
- 产品数据：用户从 Seller Central 导出业务报告
- 广告数据：用户从广告控制台导出报表
- Review 分析：WebFetch 亚马逊产品页面
- 关键词排名：WebSearch 手动查看

---

## 执行流程

### Step 0: 信息收集

```
📋 上架复盘 - 信息确认

1. 产品 ASIN：[ASIN]
2. 目标站点：[US/UK/DE 等，默认 US]
3. 上架日期：[YYYY-MM-DD]
4. 复盘天数：[30/60/90 天]
5. MVP 蓝图路径（可选）：[用于对照测试标准]
6. 广告数据（Sorftime 无法获取，需用户提供）：
   - 广告花费总计：$[XXX]
   - 广告销售额：$[XXX]
   - ACOS：[XX%]
   - TACoS：[XX%]
   - 主要关键词 CPC：$[X.XX]
   - 广告转化率：[XX%]
7. Seller Central 数据（可选，提高精度）：
   - Sessions（页面浏览量）：[XXXX]
   - 转化率（Unit Session %）：[XX%]
   - 退货数量/比例：[XX / XX%]
```

### Step 1: 读取基线

**如果有 MVP 蓝图**：
- 提取测试标准（Pass/Fail 阈值）
- 提取对标竞品 ASIN 列表
- 提取目标定价和利润率

**如果没有 MVP 蓝图**：
- 使用品类默认基准值（见 `references/kpi_benchmarks.md`）
- 通过信息收集获取对标竞品

### Step 2: 核心指标采集

**2.1 Sorftime 数据采集**

调用 `product_detail` 获取：
- 当前价格、排名、评论数、评分
- 月估算销量

调用 `product_trend` 获取：
- BSR 排名趋势（近 30/60/90 天）
- 价格变化趋势

调用 `product_reviews` 获取：
- 好评关键词
- 差评痛点分类

**2.2 用户数据补充**

以下数据 Sorftime 无法提供，需要用户输入：
- Sessions / 转化率
- 广告数据（ACOS/TACoS/CPC）
- 退货数据
- 实际利润数据

### Step 3: 流量分析

**3.1 自然流量评估**

调用 `product_traffic_terms` 获取自然排名关键词：

| 关键词 | 排名位置 | 搜索量 | 流量占比估算 | 趋势 |
|--------|---------|--------|-------------|------|
| [词1] | #[N] | [数据] | [%] | ↑/→/↓ |

**3.2 广告流量评估**（基于用户提供的数据）

| 指标 | 当前值 | MVP 基线 | 状态 |
|------|--------|----------|------|
| 广告花费 | $[XXX] | $[XXX] | 🟢/🟡/🔴 |
| ACOS | [XX%] | ≤[XX%] | 🟢/🟡/🔴 |
| TACoS | [XX%] | — | — |
| 广告转化率 | [XX%] | — | — |
| 核心词 CPC | $[X.XX] | $[X.XX] | 🟢/🟡/🔴 |

**3.3 自然 vs 广告流量占比**

- 自然流量占比：[XX%]
- 广告流量占比：[XX%]
- 趋势：自然流量占比是否在上升？

⛔ 如果自然流量占比 <20% 且无上升趋势，标注为重大风险。

### Step 4: 转化分析

| 指标 | 当前值 | MVP Pass 阈值 | MVP Fail 阈值 | 状态 | 趋势 |
|------|--------|-------------|-------------|------|------|
| 转化率 | [XX%] | ≥[X%] | <[X%] | 🟢/🟡/🔴 | ↑/→/↓ |
| 日均销量 | [N] 件 | ≥[N] 件 | <[N] 件 | 🟢/🟡/🔴 | ↑/→/↓ |
| BSR 排名 | #[N] | Top [N] | Top [N] 外 | 🟢/🟡/🔴 | ↑/→/↓ |

**转化率诊断**：
- 如果流量高但转化率低 → Listing 问题（图片/价格/评分）
- 如果流量低但转化率高 → 曝光问题（关键词/广告/排名）
- 如果流量高转化率也高 → 继续当前策略

### Step 5: 客户反馈分析

**5.1 Review 情感分析**

调用 `product_reviews` 分析已有 Review：

| 类别 | 关键词/主题 | 频次 | 对产品的影响 | 行动建议 |
|------|-----------|------|-------------|----------|
| 好评 | [主题] | [N] | 验证 [卖点] 有效 | 继续强化 |
| 差评 | [主题] | [N] | 影响 [维度] | [具体改良方案] |

**5.2 退货分析**（基于用户数据）

| 退货原因 | 数量/占比 | 严重程度 | 改善方案 |
|----------|----------|---------|----------|
| [原因1] | [N / XX%] | 高/中/低 | [具体方案] |

**5.3 QA 问题分析**（如有）

记录高频 QA 问题，这些往往是 Listing 信息不足的信号。

### Step 6: 竞品对标

与 MVP 蓝图中设定的对标竞品对比：

| 指标 | 我们 | 竞品 A | 竞品 B | 竞品 C | 差距 |
|------|------|--------|--------|--------|------|
| 价格 | $XX | $XX | $XX | $XX | |
| 月销量 | [N] | [N] | [N] | [N] | |
| 评分 | [X.X] | [X.X] | [X.X] | [X.X] | |
| Review 数 | [N] | [N] | [N] | [N] | |
| BSR | #[N] | #[N] | #[N] | #[N] | |

### Step 7: Kill / Continue / Pivot 决策

**7.1 红绿灯评估表**

| 指标 | 当前值 | Kill 🔴 | Pivot 🟡 | Continue 🟢 | 状态 |
|------|--------|---------|----------|-------------|------|
| 转化率 | [XX%] | <5% | 5-10% | >10% | 🟢/🟡/🔴 |
| BSR 趋势 | [描述] | 持续下降 | 波动 | 稳定/上升 | 🟢/🟡/🔴 |
| ACOS | [XX%] | >50% | 30-50% | <30% | 🟢/🟡/🔴 |
| 退货率 | [XX%] | >15% | 8-15% | <8% | 🟢/🟡/🔴 |
| 评分 | [X.X] | <3.5 | 3.5-4.0 | >4.0 | 🟢/🟡/🔴 |
| 自然流量占比 | [XX%] | <20% | 20-40% | >40% | 🟢/🟡/🔴 |

**7.2 决策规则**

| 情况 | 决策 | 行动 |
|------|------|------|
| 🟢 ≥4 个，无 🔴 | **Continue** | 进入迭代优化（lean-product-develop-iteration-playbook）|
| 🟢 ≥3 个，🔴 ≤1 个 | **Conditional Continue** | 重点解决红灯指标，限时 30 天复查 |
| 🟡 ≥3 个 | **Pivot** | 调整产品/定价/目标市场，重新进入测试 |
| 🔴 ≥3 个 | **Kill** | 停止广告投入，清库存退出 |
| 转化率+评分都 🔴 | **Kill**（一票否决） | 产品本身有问题，继续投入无意义 |

**7.3 决策输出**

```
📊 复盘决策

决策：[Kill / Pivot / Conditional Continue / Continue]
信心度：[高/中/低]
理由：[基于红绿灯数据的 2-3 句话总结]

下一步行动：
1. [具体行动1]
2. [具体行动2]
3. [具体行动3]

时间节点：[下次复盘日期]
```

### Step 8: 交付

**8.1 交付物**

| 文件 | 格式 | 说明 |
|------|------|------|
| 复盘报告 | .md | 全维度分析+决策结论 |
| 复盘数据 | .xlsx | KPI 明细+趋势数据+竞品对比 |

**8.2 Excel Sheet 结构**

| Sheet 名 | 内容 |
|----------|------|
| 数据来源说明 | 每个数据的来源（Sorftime/用户输入）和获取时间 |
| KPI 对照表 | 各指标当前值 vs MVP 基线 |
| BSR 趋势 | 每日/每周 BSR 数据（来自 product_trend）|
| 流量分析 | 关键词排名+流量占比 |
| Review 分析 | 好评/差评分类汇总 |
| 竞品对比 | 多竞品多维度对比 |
| 红绿灯评估 | 6 维度评估结果+决策 |

**8.3 自检清单**

- [ ] 每个 KPI 都与 MVP 基线对比了？
- [ ] 每个指标都标注了趋势方向？
- [ ] 红绿灯评估完整（6 个维度）？
- [ ] 决策基于量化规则（非主观判断）？
- [ ] 行动项具体可执行？
- [ ] 数据来源全部标注？
- [ ] Review 分析已完成（即使 Review 很少）？

**运行验证**：
```bash
python skills/lean-product-develop-launch-review/scripts/validate_deliverables.py --dir <output_dir>
```

只有返回 `validate_ok` 才算完成。

---

## 存储路径

```
工作成果/brands/{brand}/精益开发/{品类}/launch-review/{version}/
├── {date}_{site}_{ASIN}_上架复盘_{days}天.md
├── {date}_{site}_{ASIN}_复盘数据.xlsx
└── review_data.json  # 中间数据
```

---

## 数据诚信规则

- **绝不捏造数据**：Sorftime 获取不到的数据（如转化率、广告 ACOS）必须来自用户提供
- **明确标注来源**：区分 Sorftime 数据 vs 用户输入数据 vs 推算数据
- **区分事实与推测**：推测必须标注「⚠️ 推测」
- **广告数据透明**：如果用户未提供广告数据，该维度标注为「未验证」，不影响其他维度评估
