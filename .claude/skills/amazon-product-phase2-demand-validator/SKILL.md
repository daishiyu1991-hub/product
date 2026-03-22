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
3. 优先检测是否可用 Sorftime MCP
4. Review 维度：
   - 有 Sorftime：走 `product_reviews` + `scripts/parse_reviews.py`
   - 无 Sorftime：走 `review_source_pack` + `scripts/parse_review_source_pack.py`
5. 关键词维度：
   - 有 Sorftime：走 `keyword_detail / keyword_trend / keyword_extends`
   - 无 Sorftime：明确写"未验证 / 待补充"，不伪造
6. 社区维度：WebSearch 搜 Reddit / Quora，并用脚本导出 CSV
7. 生成报告并运行 `scripts/validate_deliverables.py`

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
