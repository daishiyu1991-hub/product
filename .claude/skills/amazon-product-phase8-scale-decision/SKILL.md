---
name: amazon-product-phase8-scale-decision
description: "亚马逊精益开发 Phase 8：产品经过验证和迭代后的规模化决策。评估单位经济学、供应链就绪度、竞争护城河、品牌建设能力，输出 Go Big / Maintain / Harvest / Exit 四象限决策。含 12 个月财务预测模型和产品线扩展规划。优先调用 Sorftime MCP；无 Sorftime 时降级为 WebSearch + 用户手动输入运营数据。"
argument-hint: "[ASIN] [站点] [--months 已运营月数] [--target-revenue 目标月营收]"
user-invocable: true
---

# 规模化决策（精益开发 Phase 8）

## 定位

`amazon-product-phase8-scale-decision` 是精益产品开发闭环的最后阶段。产品已经过 MVP 验证（Phase 3）、设计调研（Phase 4）、工业设计（Phase 5）和 1-2 轮迭代优化（Phase 6-7），需要回答一个关键问题：**这个产品值得 all-in 吗？**

## 适用场景

- 产品上架 3-6 个月，数据稳定，需要决定是否大批量采购
- 准备从空运切换到海运，需要评估供应链就绪度
- 考虑多站点复制（US → EU/JP/AU）
- 评估是否值得投入品牌建设（Brand Store/A+ Premium/品牌故事）
- 产品线扩展决策（升级款/入门款/跨品类/Bundle）

## 前置条件

- 已运营 3 个月以上的产品 ASIN
- 历史运营数据（推荐）
- Python 3.9+，安装 `openpyxl`

## 使用方法

### 方式1：指定 ASIN
```
/amazon-product-phase8-scale-decision B0XXXXXXXX US --months 6
```

### 方式2：带目标营收
```
/amazon-product-phase8-scale-decision B0XXXXXXXX US --months 4 --target-revenue 50000
```

### 方式3：自然语言
```
帮我评估一下 B0XXXXXXXX 是否值得规模化，已经运营 5 个月了
```

## 执行步骤

当调用此 Skill 时，执行以下流程：

1. **读取完整方法论** — 加载 `skills/amazon-product-phase8-scale-decision/SKILL.md`
2. **单位经济学验证** — 真实 ACOS/退货率/自然流量占比/单位净利润
3. **规模化成本模型** — 大批量采购降幅/海运切换/仓储规划/广告边际效益
4. **供应链就绪评估** — 产能/MOQ/交期/质检/备用供应商/库存模型
5. **竞争护城河评估** — 品牌注册/专利/Review壁垒/自然排名
6. **品牌建设就绪度** — Brand Store/A+/品牌故事/站外引流/多渠道
7. **产品线扩展规划** — 纵向延伸/横向延伸/多站点复制
8. **最终决策矩阵** — Go Big / Maintain / Harvest / Exit 四象限决策
9. **输出与验证** — 生成文档，运行 `scripts/validate_deliverables.py`

## 核心输出

| 类型 | 文件命名 | 用途 |
|------|----------|------|
| 报告 | `[日期]_[站点]_[ASIN]_规模化决策报告.md` | 完整评估报告 |
| 财务 | `[日期]_[站点]_[ASIN]_财务预测模型.xlsx` | 12 个月财务预测 |
| 规划 | `[日期]_[站点]_[ASIN]_产品线规划.md` | 扩品路线图 |

## 决策输出

| 决策 | 条件 | 行动 |
|------|------|------|
| **Go Big** | 净利率>15%, 自然流量>50%, Review>100, 供应链稳定 | 大批量采购+品牌建设+多站点 |
| **Maintain** | 净利率10-15%, 稳定出单, 竞争加剧 | 维持现状+防御性广告 |
| **Harvest** | 利润下降但仍为正, 市场饱和 | 减少投入, 收割利润 |
| **Exit** | 净利率<5%, 竞争激烈, 无护城河 | 清库存退出, 资源转移 |

## 上下游对接

- 上游：`amazon-product-phase7-iteration-playbook`（Phase 7：迭代优化）+ `amazon-product-phase6-launch-review`（Phase 6：上架复盘）
- 下游：Go Big 决策后进入规模化执行

## 完整方法论

详见 `skills/amazon-product-phase8-scale-decision/SKILL.md`


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
