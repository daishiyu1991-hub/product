---
name: allen-product-design
description: 根据产品定义，利用 NanoBanana API 自动生成工业设计概念图。支持多变体探索（颜色/材质/比例）、风格探索（极简/工业/复古等）、多角度渲染（正面/侧面/45度）、使用场景可视化。输入可以是自然语言描述或结构化产品属性表。
argument-hint: "[产品描述或产品名称] [--style 风格] [--angles 角度] [--variants 变体数]"
user-invocable: true
---

# allen-product-design — 产品定义生图 Skill

## 定位
面向**工业设计找方向**的 AI 生图工具。根据产品定义（自然语言或结构化属性），自动构建专业 Prompt，调用 NanoBanana API 生成高质量概念图。

## 调用方式

### 方式 1：Slash 命令
```
/allen-product-design 一款带 LED 灯的蓝牙耳机，黑色哑光，运动风格
```

### 方式 2：带参数调用
```
/allen-product-design 便携榨汁杯 --style 极简,工业 --angles 正面,45度 --variants 3 --resolution 2K
```

### 方式 3：结构化输入
```
/allen-product-design
{
  "product": "无线充电器",
  "category": "消费电子",
  "features": ["磁吸对齐", "LED 指示灯", "超薄设计"],
  "materials": ["铝合金", "钢化玻璃"],
  "colors": ["太空灰", "银色"],
  "target_audience": "科技爱好者",
  "style_inspiration": "Apple 设计语言"
}
```

## 执行概览

| 步骤 | 动作 |
|------|------|
| 1 | 读取完整方法论 — 加载 `skills/allen-product-design/SKILL.md` |
| 2 | 解析产品定义 — 自然语言 → 结构化属性提取；JSON → 直接解析 |
| **3** | **内部堆叠调研** — 调研产品内部组件堆叠（搜索 teardown/patent/engineering），确定外形约束（最小宽度/高度/角度/重心）和品类基本型。如果调用方已提供堆叠数据（如 Phase 3 传入），直接使用。 |
| **4** | **目标用户风格发散** — 根据目标用户年龄段选择 3-4 种匹配的设计风格进行发散探索（见下方「年龄→风格映射」）。每种风格必须遵守堆叠约束 + 品类基本型 + 五条设计准则。 |
| 5 | 构建 Prompt 矩阵 — 根据风格发散结果 + 堆叠约束生成 Prompt 列表。每个 Prompt 必须包含：品类基本型描述、内部尺寸约束、风格关键词、记忆点定义。 |
| 6 | 调用 NanoBanana API — 执行 `python skills/allen-product-design/scripts/generate_images.py` |
| 7 | 轮询等待结果 — 自动检查任务状态直至完成 |
| 8 | 下载与整理 — 按维度分组下载图片到输出目录 |
| 9 | 生成报告 — 输出可视化报告（含所有图片 + Prompt + 参数） |

## 年龄→风格映射表

| 用户年龄段 | 推荐发散风格 | 理由 |
|-----------|-------------|------|
| 18-25 岁 | 可爱(cute)、Y2K、波普(playful)、赛博朋克 | 年轻、社媒分享、个性表达 |
| 25-35 岁 | 极简(minimal)、北欧(Scandi)、有机(organic)、苹果风 | 干净利落、品质感、Instagram 审美 |
| 30-45 岁 | 北欧、无印(MUJI)、B&O风、包豪斯(Bauhaus) | 成熟克制、设计内涵、生活品质 |
| 35-50 岁 | 包豪斯、博朗(Braun)、奢华(luxury)、经典 | 永恒设计、材质感、不跟风 |
| 50+ 岁 | 复古(retro)、经典、简约大方 | 易识别、不花哨、质感 |
| 混合/广泛 | 极简 + 任选 2 个匹配风格 | 覆盖主力 + 做差异化尝试 |

## 五条设计准则（硬规则）

所有外观概念图必须遵守：

1. **少即是多** — 每个方案最多 1 个视觉记忆点，其余保持克制
2. **使用基本型** — 基于品类已有的经典外形，用几何基本体（圆柱/长方体/圆锥）构成，不使用复杂异形曲面
3. **保持品类辨识度** — 消费者一眼能认出这是什么产品
4. **有且仅有一个记忆特征** — 消费者必须记住一个东西，这个特征同时也是品牌锚点
5. **遵从人体工学** — 使用时手腕保持中性位，不做反关节运动

## 内部堆叠调研要求

当生成外观概念图时，**必须先确认内部堆叠**。堆叠数据来源优先级：

1. **调用方已传入** — Phase 3 MVP Blueprint 已完成堆叠调研，直接使用
2. **自行调研** — 通过 WebSearch 搜索 `[product] teardown` / `[product] internal structure` / `[product] patent`，提取组件列表、尺寸、堆叠顺序
3. **推断** — 根据品类常识推断关键约束，标注 ⚠️

堆叠约束作为 Prompt 构建的**硬约束**，确保每个概念图都是可制造的。

## 输出物

| 文件 | 说明 |
|------|------|
| `output/images/` | 按维度分组的生成图片 |
| `output/report.md` | Markdown 格式的可视化报告 |
| `output/prompts.json` | 所有 Prompt 及对应参数记录 |
| `output/summary.md` | 生成概要（模型/分辨率/耗时/费用） |

## 环境要求
- 环境变量 `NANOBANANA_API_KEY` 已设置
- Python 3.8+（requests 库）

## 详细方法论
详见 `skills/allen-product-design/SKILL.md`
