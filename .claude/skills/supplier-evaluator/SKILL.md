---
name: supplier-evaluator
description: "供应商综合评估器 — 输入产品名称，自动搜索1688货源、对比亚马逊售价计算利润空间、评估供应商资质，输出供应商选择建议。当用户说'找供应商'、'1688比价'、'供应链评估'、'采购成本分析'时触发。"
argument-hint: "[产品名称] [站点(默认US)]"
user-invocable: true
---

# 供应商综合评估器

## 定位

帮助亚马逊卖家快速完成"采购端"决策：找到合适的供应商，计算利润空间，评估合作风险。

核心问题：**这个产品从哪里采购、成本多少、能不能赚钱？**

## 硬约束（⛔ 绝不可违反）

1. **绝对禁止编造价格** — 所有价格数据必须来自 1688 MCP 或 Sorftime MCP 查询结果，查不到标注「⚠️ 数据缺失」
2. **绝对禁止跳过利润计算** — 必须按公式模板完成毛利率和盈亏ACOS计算，不允许"大约能赚钱"
3. **绝对禁止只看价格选供应商** — 必须至少评估 3 个维度（价格、起订量、资质/实力）
4. **如果利润率 < 15%，必须发出红色警告** — 不能默默略过
5. **如果只找到 < 3 个供应商，必须标注「样本量不足，建议扩大搜索」**

## 使用方法

### 方式1：指定产品
```
/supplier-evaluator LED台灯 US
```

### 方式2：自然语言
```
帮我找蓝牙音箱的1688供应商，对比亚马逊美国站的售价
```

### 方式3：带上游数据
```
/supplier-evaluator --source ./phase1_output/unified_payload.json
```

## 工具决策树

### 获取供应商数据
- 有产品名 → `ali1688_similar_product(searchName)` 搜索1688货源
- 需要更多供应商 → 翻页 `ali1688_similar_product(searchName, page=2)`
- 1688 MCP 不可用 → WebSearch 搜索 "产品名 + 1688 批发价"（降级）

### 获取亚马逊售价数据
- 有 ASIN → `product_detail(asin)` 直接取价格
- 无 ASIN，有产品名 → `product_search(searchName)` → 取 Top5 → `product_detail`
- Sorftime 不可用 → WebSearch 搜 "产品名 amazon.com price"（降级）

### 获取物流成本数据
- WebSearch 搜索 "FBA fee calculator [产品类目]" 获取参考费用
- 或用户提供已知的头程+FBA费用

### 并行 vs 串行声明

**可并行（互不依赖）:**
- `ali1688_similar_product(searchName)` 和 `product_search(searchName)` — 供应端和销售端同时查
- 多个 ASIN 的 `product_detail` 调用

**必须串行:**
- `product_search` → 取 ASIN → `product_detail`（需要 ASIN）
- 供应商数据 + 售价数据 → 利润计算（需要两端数据）

## 执行步骤

1. **解析输入** — 确认产品名称、目标站点、是否有上游数据

2. **供应商搜索** — 调用 `ali1688_similar_product(searchName)` 获取供应商列表
   - 提取：供应商名、单价、起订量（MOQ）、交货期、工厂信息
   - 至少获取 5 个供应商，不足则翻页

3. **亚马逊售价采集** — 并行调用 `product_search(searchName)` + Top5 的 `product_detail`
   - 提取：售价范围、月销量、评分、品牌

4. **成本结构计算（⛔ 必须按公式）**
   ```
   产品采购成本 = 1688单价 × 1.05（含税）
   头程物流 = 采购成本 × 0.15（海运估算）或用户提供
   FBA配送费 = 根据产品尺寸重量估算（WebSearch 查 FBA fee）
   落地成本 = 采购成本 + 头程物流 + FBA配送费
   亚马逊佣金 = 售价 × 15%
   毛利 = 售价 - 落地成本 - 佣金
   毛利率 = 毛利 ÷ 售价 × 100%
   ```

5. **供应商对比矩阵**
   ```
   | 供应商 | 单价(¥) | MOQ | 交货期 | 落地成本($) | 毛利率 | 综合评分 |
   |--------|---------|-----|--------|------------|--------|---------|
   ```

6. **利润空间三场景分析**
   ```
   | 场景 | 采购价 | 售价 | 毛利率 | ACOS盈亏线 |
   |------|--------|------|--------|-----------|
   | 乐观 | 最低采购价 | 平均售价 | xx% | xx% |
   | 中等 | 中位采购价 | 中位售价 | xx% | xx% |
   | 保守 | 最高采购价 | 最低售价 | xx% | xx% |
   ```

7. **风险评估（条件分支）**

   IF 毛利率 > 30%:
     → 🟢 利润空间充足，重点评估供应商可靠性
   ELSE IF 毛利率 15-30%:
     → 🟡 利润空间一般，需要严控成本或提高售价
   ELSE IF 毛利率 < 15%:
     → 🔴 **利润危险！** 价格战一打就亏，建议重新评估产品选择

   IF MOQ > 1000:
     → ⚠️ 首批资金压力大，建议谈判降低MOQ或找小批量供应商
   IF 供应商 < 3 家:
     → ⚠️ 供应商选择面窄，建议扩大搜索范围

8. **输出供应商选择建议** — 推荐 Top 3 供应商 + 推荐理由 + 谈判要点

## 三级降级路径

### Level 1: 全功能模式（1688 MCP + Sorftime MCP 均可用）
- 1688 获取供应商真实报价
- Sorftime 获取亚马逊真实售价和销量
- 报告标注 ✅ 完整数据

### Level 2: 部分降级（一端 MCP 不可用）
- 1688 不可用 → WebSearch 搜 "产品名 1688" 获取参考价
- Sorftime 不可用 → WebSearch 搜 "产品名 amazon price" 获取参考价
- 降级维度标注 ⚠️，利润计算标注「估算值」

### Level 3: 全降级（两端 MCP 均不可用）
- 全部用 WebSearch 获取参考数据
- 报告标题加 ⚠️ 降级模式
- 利润计算标注「粗略估算，仅供参考」
- 建议用户提供真实报价后重新计算

## 输入协议

IF 上游 Phase 1 的 `unified_payload.json` 存在:
  → 读取 `market.avgPrice`, `competitors[]`, `keywords[]`
  → 跳过亚马逊售价搜索步骤
ELSE:
  → 要求用户提供产品名称
  → 自行搜索亚马逊售价

## 输出协议

产出 `supplier_evaluation.json`：
```json
{
  "meta": { "phase": "supplier", "product": "...", "site": "US", "date": "..." },
  "suppliers": [
    {
      "name": "供应商名",
      "price_cny": 0.0,
      "moq": 0,
      "delivery_days": 0,
      "score": 0.0,
      "pros": ["..."],
      "cons": ["..."]
    }
  ],
  "profitability": {
    "best_margin": 0.0,
    "avg_margin": 0.0,
    "worst_margin": 0.0,
    "breakeven_acos": 0.0
  },
  "recommendation": {
    "top_supplier": "供应商名",
    "reason": "...",
    "negotiation_tips": ["...", "..."],
    "risk_level": "LOW | MEDIUM | HIGH"
  }
}
```

## 交付前自检

- [ ] 所有价格数据标注了来源（1688 MCP / Sorftime MCP / WebSearch / 用户提供）？
- [ ] 利润计算展示了完整中间步骤？
- [ ] 至少对比了 3 个供应商？
- [ ] 毛利率 < 15% 时有红色警告？
- [ ] 汇率使用了当前汇率（WebSearch 查询），不是硬编码？
