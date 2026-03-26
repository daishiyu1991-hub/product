---
name: amazon-product-phase2-demand-validator
description: "亚马逊精益开发 Phase 2：功能需求真伪验证器。面向亚马逊产品开发中的微创新判断，用 Review 信号、关键词信号、社区信号验证某个功能点是真需求还是伪需求。优先调用 Sorftime MCP；若没有 Sorftime，也支持通过本地 review_source_pack 先完成 Review 维度验证。"
argument-hint: "[品类/ASIN] [功能描述] [站点]"
user-invocable: true
allowed-tools: Read, Glob, Bash, Write, WebSearch
---

# 功能需求真伪验证器（精益开发 Phase 2）

这个 Skill 解决的不是"要不要做这个品类"，而是更常见的微创新判断：

**在现有市场供给上加一个小功能，这件事到底值不值得做。**

## 使用方式

### 方式 1：品类 + 功能
```text
/amazon-product-phase2-demand-validator air fryer steam US
```

### 方式 2：ASIN + 功能
```text
/amazon-product-phase2-demand-validator B0XXXX self-cleaning US
```

### 方式 3：自然语言
```text
帮我验证一下空气炸锅加蒸汽功能在美国站是不是真需求
```

## 执行顺序

1. 读取 `skills/amazon-product-phase2-demand-validator/SKILL.md`
2. 解析输入并构造 3-5 个关键词变体
3. **数据源可用性预检** — 轻量调用 `category_name_search("test")` 测试 MCP 连通性
4. Review 维度：按下方三级降级路径执行
5. 关键词维度：按下方三级降级路径执行
6. 社区维度：WebSearch 搜 Reddit / Quora，并用脚本导出 CSV
7. **分析深度自适应** — 根据信号强度调整验证深度（见下方阈值表）
8. 生成报告并运行 `scripts/validate_deliverables.py`

## 三级降级路径

### Level 1: 全功能模式（MCP 可用）
| 维度 | 数据来源 | 标注 |
|------|---------|------|
| Review | `product_reviews(asin)` + `scripts/parse_reviews.py` | ✅ 完整数据 |
| 关键词 | `keyword_detail` + `keyword_trend` + `keyword_extends` | ✅ 完整数据 |
| 社区 | WebSearch | ✅ 完整数据 |

### Level 2: 部分降级（MCP 部分不可用）
| 维度 | 数据来源 | 标注 |
|------|---------|------|
| Review | `review_source_pack/` + `scripts/parse_review_source_pack.py` | ⚠️ 本地数据 |
| 关键词 | 标注「⚠️ 待补充」 | ⚠️ 缺失 |
| 社区 | WebSearch | ✅ 完整数据 |

→ 结论可信度标注为「参考级」，建议 MCP 恢复后补验

### Level 3: 手动输入模式（MCP 完全不可用 + 无本地数据）
| 维度 | 数据来源 | 标注 |
|------|---------|------|
| Review | 用户手动提供评论截图/文本 | ⚠️ 用户提供 |
| 关键词 | WebSearch 搜 "产品名 amazon search volume" | ⚠️ 估算 |
| 社区 | WebSearch | ✅ 完整数据 |

→ 报告标题加「⚠️ 降级模式」，不做决定性结论

## 分析深度自适应（阈值驱动）

根据 Review 维度获取的信号强度，动态调整后续验证深度：

| 信号强度 | 判断标准 | 执行路径 |
|---------|---------|---------|
| **强信号** | 相关 Review 提及率 >15% 或差评中 ≥3 条明确描述该痛点 | → 深度验证：关键词查 10+ 个变体 + 社区搜 3 个平台 + 竞品对比 5 个 |
| **中等信号** | 提及率 5-15% 或差评中 1-2 条相关 | → 标准验证：关键词查 5 个核心词 + 社区搜 Reddit + 竞品对比 3 个 |
| **弱信号** | 提及率 <5% 且无明确差评 | → 快速筛选：关键词查 3 个 + 社区快扫 + 直接给出「信号不足，不建议投入」 |

## 输出

- `[日期]_[品类]_[功能]_功能需求验证报告.md`
- `01_review_信号_原始数据.csv`
- `02_keyword_信号_搜索量数据.csv`
- `03_keyword_信号_趋势数据.csv`
- `04_keyword_信号_延伸词.csv`
- `05_社区_信号_讨论摘要.csv`
- fallback 场景额外保留 `review_source_pack/`

## 上下游对接

- 上游：`amazon-product-phase1-research`（Phase 1：选品分析）
- 下游：`amazon-product-phase3-mvp-blueprint`（Phase 3：MVP 蓝图）

### 输入协议（读取上游数据）

IF Phase 1 的 `unified_payload.json` 存在:
  → 自动读取 `market.nodeId`, `keywords[]`, `competitors[]`, `painPoints[]`
  → 跳过重复的品类搜索步骤
  → 在报告中标注「上游数据来源: Phase 1」
ELSE:
  → 要求用户提供品类/ASIN + 功能描述
  → 自行调用 Sorftime 获取数据

### 输出协议（供下游 Phase 3 读取）

验证完成后必须产出 `phase2_validation.json`：

```json
{
  "meta": { "phase": "phase2", "product": "...", "feature": "...", "site": "US", "date": "..." },
  "validation_result": "TRUE_DEMAND | WEAK_SIGNAL | FALSE_DEMAND",
  "confidence": 0.0-1.0,
  "signals": {
    "review": {
      "complaint_rate": 0.0,
      "positive_mention_rate": 0.0,
      "sample_size": 0,
      "top_complaints": ["...", "..."]
    },
    "keyword": {
      "search_volume": 0,
      "trend": "上升 | 平稳 | 下降",
      "related_terms": ["...", "..."]
    },
    "community": {
      "reddit_mentions": 0,
      "sentiment": "正面 | 中性 | 负面"
    }
  },
  "next_phase": "phase3 | stop"
}
```

**下游触发规则:**
- `TRUE_DEMAND` + `confidence >= 0.7` → 建议执行 Phase 3 MVP 蓝图
- `WEAK_SIGNAL` → 列出需补充验证的维度，用户决定是否继续
- `FALSE_DEMAND` → 终止，不进入 Phase 3

## 强制要求

- Sorftime 可用时必须优先调用
- 无 Sorftime 时只允许 Review 维度降级
- 每个 CSV 都必须带可核查来源字段
- 负面证据必须写进报告
- 只有 `validate_ok` 才算完成

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
