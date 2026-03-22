---
name: amazon-product-phase4-design-research
description: "亚马逊精益开发 Phase 4：工业设计调研。下载竞品图片→Agent形态分类→用户选目标形态→蒸馏baseline线稿→场景人因约束→风格规划→输出design_research_pack.json供Phase 5使用。"
argument-hint: "[产品名称] [站点]"
user-invocable: true
---

# Phase 4：工业设计调研

竞品图片下载 → 形态分类 → 基准线稿蒸馏 → 风格规划 → 输出交接包。全流程在一个会话完成。

## 生图 API

- **Endpoint**: `https://new.suxi.ai/v1/chat/completions`
- **Auth**: `Authorization: Bearer sk-DDlvJ0LEbYpjfzKHotRfcNY4taKqc290t9O6G7NOTWSBG5KL`
- **Model**: `gemini-3-pro-image-preview`（高质量）/ `gemini-3.1-flash-image-preview`（快速）
- **Proxy**: `--proxy http://127.0.0.1:7897`
- **Timeout**: 180s
- **响应解析**: content 中提取 `https://...jpg` URL → curl 下载；或 base64 解码

## 输出目录结构
```
[工作目录]/phase4_design_research/output/
  ├── competitor_images/        # 竞品产品图
  ├── baselines/                # 蒸馏线稿
  ├── archetype_classification.json
  ├── scene_observations.json
  ├── design_research_pack.json # ⭐ Phase 5 主输入
  └── YYYYMMDD_*_设计调研报告.md
```

## Step 1：竞品图片下载

1. 用 Sorftime `product_search` 搜索品类关键词，获取 Top 50 产品
2. 可补充 `category_report` 获取 Top 100
3. 筛选 ≥20 款产品（月销 Top 10 必选 + 不同品牌 + 不同价格带 + 新品 + 高评分）
4. 从搜索结果提取主图 URL，需要高清图时用 `product_detail`
5. 补充副图：构造 `https://www.amazon.com/dp/[ASIN]`，用 curl 抓取页面，grep 提取 `"hiRes":"https://...jpg"` URL
6. curl 下载到 `competitor_images/`，命名 `[序号]_[品牌缩写]_[场景].jpg`
7. 目标：≥20 张主图 + ≥20 张使用场景/功能信息图
8. 写入 `competitor_images/image_index.json`（每张图的 ASIN/品牌/价格/月销/类型）

## Step 2：Agent 形态分类

将竞品**主图 + 产品角度图**分组（每 Agent ≤12 张），启动并行 Agent：

**Agent prompt 要点**：
- 角色：工业设计形态分析专家
- 用 Read 工具逐张查看图片（给绝对路径）
- 按整体轮廓/silhouette 相似性归类为形态族群
- 不看颜色/品牌，只看结构形状
- 每族群：中英文名 + 100 字结构描述（握持/面板/水箱/比例/底座/轮廓） + 产品列表 + 代表图 + 子变体差异
- 返回纯 JSON

同时启动另一 **Agent 观察场景图**：
- 角色：人体工学分析专家
- 逐张 Read 使用场景图和功能信息图
- 记录：握持方式、操作姿态、蒸汽方向、衣物挂置、环境、用户类型、接触方式
- 非使用场景标注 N/A 跳过
- 汇总：dominant_grip / posture / steam_direction / garment_setup / environment / weight / 5条关键人因发现
- 输出含英文 prompt_supplement（50-80词，供后续概念图生成用）
- 返回纯 JSON

主会话合并 Agent 结果 → 写入 `archetype_classification.json` + `scene_observations.json`

## Step 3：逐张生成 baseline 线稿

**核心原则：每张竞品图 1:1 生成对应的 baseline 线稿，不合并。下了多少张就生成多少张。**

1. 遍历 `competitor_images/` 中所有产品主图（跳过纯信息图/配件图/包装图）
2. 对每张图，用 Python 转 base64，构建**单图**多模态 API 请求
3. **逐张蒸馏 prompt**：输入 1 张竞品实物图 → 输出 1 张对应的线稿
4. Prompt 核心要求：
   - 输入这张产品实物图，画出它的产品设计线稿图
   - 纯黑线条白色背景 / 专利图风格 / 保持与原图相同的视角
   - 精确还原原图产品的结构轮廓、比例、细节
   - 标注 4-6 个关键结构区域（leader lines）
   - 无色无材质无品牌
5. curl 调用 API → 提取图片 URL → 下载到 `baselines/` 命名与原图对应（如 `01_neakasa_main.jpg` → `baselines/01_neakasa_main_baseline.jpg`）
6. 可并行发起多个 API 请求加速（但注意 API 并发限制）
7. 完成后用 Read 抽查 2-3 张确认质量

## Step 4：风格规划

读取 Phase 3 MVP 蓝图中的用户画像年龄段，选 3-4 种风格：

| 年龄段 | 推荐风格池 |
|--------|-----------|
| 18-25 | 可爱、Y2K、波普、赛博朋克 |
| 25-35 | 极简、北欧、有机、苹果风 |
| 30-45 | 北欧、无印、B&O、包豪斯 |
| 35-50 | 包豪斯、博朗、奢华、经典 |

规则：
- 至少 1 种安全 + 1 种大胆探索
- 每种设计 1 个**视觉记忆点**（非纯配色，必须是结构/材质/光效特征）
- 每种指定：主色 + 点缀色 + 参考品牌 + 表面处理 + 轮廓调整幅度 + 风险等级
- 排出优先级（MVP 主色 → 替代色 → Premium → 实验）

## Step 5：输出交接包 + 报告

### design_research_pack.json（Phase 5 主输入）
```
{
  "meta": {phase/product/site/date/baseline_source},
  "category_archetype": {
    "baseline_images": "baselines/ 目录，每张竞品图对应一张线稿",
    "baseline_description": "中文结构描述",
    "usage_ergonomics": "英文50-100字人因约束",
    "key_identifiers": ["品类辨识特征"],
    "key_structural_features": [{id, name, constraint}]
  },
  "usage_constraints": {grip/operating_angle/arm_position/control/prompt_supplement},
  "style_plan": {
    "user_persona_age", "design_direction",
    "selected_styles": [{id, name, type, reference, memory_point, surface, color_primary, color_accent, silhouette_delta, risk}],
    "priority_order", "phase3_color_mapping"
  },
  "competitive_landscape": {竞品数据摘要},
  "internal_stacking": {Phase 1-4 数据链路摘要}
}
```

### 调研报告 (Markdown)
`output/YYYYMMDD_[品类]_设计调研报告.md`，包含：
1. Executive Summary
2. 竞品外形调研（竞品清单表 + 形态族群分类 + 共性分析）
3. 基准草图（线稿 + 结构区域说明 + 验证表）
4. 使用场景约束（人因约束表 + 关键发现）
5. 风格规划（4 种风格详情表）
6. Phase 5 交接清单

## Agent 注意事项

1. 每 Agent 图片 ≤12 张，给**绝对路径**
2. 形态分类 + 场景观察可 **2 Agent 并行**
3. 生图 API payload **≤6 张图**，超出取最有代表性的
4. curl 生图超时 **180s**
5. Python 构建 base64 JSON 时避免 shell 变量溢出，直接用 Python 文件 I/O

## 交付清单

- [ ] `competitor_images/` ≥20 张 + `image_index.json`
- [ ] `archetype_classification.json` — 形态分类
- [ ] `baselines/*_baseline.jpg` — 每张竞品图对应的1:1线稿
- [ ] `scene_observations.json` — 场景人因观察
- [ ] `design_research_pack.json` — ⭐ Phase 5 主输入
- [ ] `YYYYMMDD_*_设计调研报告.md` — 完整报告
- 告诉用户：**Phase 4 完成，可运行 Phase 5 生成概念图**
