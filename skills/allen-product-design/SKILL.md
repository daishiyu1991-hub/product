# allen-product-design — 完整方法论

## 概述

本 Skill 将产品定义转换为高质量工业设计概念图。核心流程：**产品定义解析 → Prompt 矩阵构建 → NanoBanana API 调用 → 结果整理与报告**。

---

## 硬规则

- ⛔ 不跳过 Prompt 构建步骤直接调 API
- ⛔ 不在 Prompt 中编造产品不具备的功能或属性
- ⛔ 不使用超过用户授权的 API 调用次数（默认上限：单次执行不超过 20 张图）
- ⛔ 不存储或打印 API Key（仅通过环境变量传递）
- ⛔ 下载图片失败时不伪造结果，标记 FAILED 并继续

---

## Step 1：环境检查

```bash
python skills/allen-product-design/scripts/check_env.py
```

检查项：
1. `NANOBANANA_API_KEY` 环境变量是否设置
2. Python `requests` 库是否可用
3. API Key 是否有效（调用 Get Account Credits 验证）
4. 输出目录是否可写

如果 API Key 未设置，提示用户：
```
请设置环境变量：
set NANOBANANA_API_KEY=你的API密钥
（API Key 获取地址：https://nanobananaapi.ai/dashboard）
```

---

## Step 2：解析产品定义

### 2A：自然语言输入

从用户的自然语言描述中提取以下结构化属性：

| 属性 | 示例 |
|------|------|
| `product_name` | 蓝牙耳机 |
| `category` | 消费电子 / 家居 / 户外 / 厨房 / 美妆 / 运动 |
| `features` | ["LED 灯", "降噪", "可折叠"] |
| `materials` | ["铝合金", "硅胶", "ABS塑料"] |
| `colors` | ["黑色", "白色"] |
| `dimensions` | "紧凑型" / "便携" / 具体尺寸 |
| `style` | "极简" / "工业" / "复古" / "未来感" |
| `target_audience` | "年轻人" / "专业人士" / "运动爱好者" |
| `brand_reference` | "类似 Apple 设计" / "Braun 风格" |
| `usage_scenario` | "办公" / "运动" / "户外" / "厨房" |

### 2B：结构化输入（JSON）

直接解析 JSON 对象，验证必填字段（product_name 或 product）。

### 2C：默认值填充

| 属性 | 默认值 |
|------|--------|
| `colors` | 如未指定，使用 ["白色"（极简）, "黑色"（工业）, "大地色"（复古）] |
| `materials` | 根据产品类别推断合理材质 |
| `style` | ["极简"] |
| `angles` | ["45度透视"] |
| `resolution` | "2K" |
| `model` | "nanobanana-2"（默认使用最新模型） |

---

## Step 3：构建 Prompt 矩阵

### 3.1 Prompt 模板系统

详见 `references/prompt_templates.md`

**基础模板结构：**
```
[SUBJECT] [MATERIAL] [COLOR] [STYLE] [LIGHTING] [ANGLE] [BACKGROUND] [RENDERING_QUALITY]
```

**完整 Prompt 示例：**
```
A [product_name], [features_description]. Made of [material] in [color] finish.
[style] industrial design aesthetic. [lighting_description].
Shot from [angle] view. [background_description].
Professional product photography, 8K render quality, studio lighting,
photorealistic, highly detailed, clean composition.
```

### 3.2 探索维度

根据用户需求（或默认值），构建以下维度的交叉矩阵：

#### 维度 A：风格变体
| 风格 ID | 风格名 | Prompt 关键词 |
|---------|--------|---------------|
| minimal | 极简 | minimalist, clean lines, simple geometry, Scandinavian design |
| industrial | 工业 | industrial design, robust, utility-focused, exposed mechanics |
| retro | 复古 | retro-futuristic, vintage, mid-century modern, Art Deco elements |
| futuristic | 未来感 | futuristic, sci-fi inspired, holographic, sleek aerodynamic |
| organic | 有机 | organic curves, biomorphic, nature-inspired, flowing forms |
| luxury | 奢华 | premium luxury, gold accents, leather details, haute couture |

#### 维度 B：角度
| 角度 ID | 名称 | Prompt 关键词 |
|---------|------|---------------|
| front | 正面 | front view, straight-on, eye level |
| side | 侧面 | side profile view, 90 degree angle |
| 45deg | 45度 | three-quarter view, 45 degree angle, hero shot |
| top | 俯视 | top-down view, bird's eye, overhead |
| perspective | 透视 | dynamic perspective, dramatic angle |

#### 维度 C：颜色/材质变体
从用户定义的 `colors` 和 `materials` 组合。

#### 维度 D：使用场景
| 场景 ID | 名称 | Prompt 关键词 |
|---------|------|---------------|
| studio | 工作室 | white studio background, professional product photography |
| lifestyle | 生活场景 | lifestyle photography, natural environment, in-use context |
| exploded | 爆炸图 | exploded view, showing internal components, technical drawing |
| context | 场景化 | environmental context, user interaction, real-world setting |

### 3.3 矩阵裁剪

默认最大图片数 = 20。如果交叉矩阵超过 20，按优先级裁剪：
1. 保留所有风格（主视角 45度）
2. 保留所有角度（主风格）
3. 颜色变体取前 2 个
4. 场景取 studio + 1 个生活场景

---

## Step 4：模型选择策略

| 场景 | 推荐模型 | 端点 | 原因 |
|------|---------|------|------|
| 快速概念探索（低成本） | NanoBanana | `/generate` | $0.02/张，速度快 |
| 高质量工业设计（默认） | NanoBanana 2 | `/generate-2` | 平衡质量与速度，支持 4K |
| 最高质量/复杂构图 | NanoBanana Pro | `/generate-pro` | 最高质量，支持 8 张参考图混合 |

**默认模型**：NanoBanana 2（`/generate-2`）

---

## Step 5：API 调用执行

```bash
python skills/allen-product-design/scripts/generate_images.py \
  --prompts output/prompts.json \
  --api-key-env NANOBANANA_API_KEY \
  --model nanobanana-2 \
  --resolution 2K \
  --output-dir output/images \
  --max-concurrent 3
```

### 5.1 调用流程

```
对 prompts.json 中的每个 Prompt：
  1. POST /generate-2  →  获取 taskId
  2. 等待 3 秒
  3. GET /record-info?taskId=xxx  →  检查 successFlag
     - 0 (GENERATING): 继续等待，每 3 秒轮询一次，最多 5 分钟
     - 1 (SUCCESS): 下载 resultImageUrl → 保存到 output/images/
     - 2 (CREATE_TASK_FAILED): 记录错误，跳过
     - 3 (GENERATE_FAILED): 记录错误，跳过
  4. 控制并发：最多同时 3 个任务
```

### 5.2 文件命名规范

```
output/images/
├── style_minimal/
│   ├── 45deg_white_aluminum.jpg
│   ├── front_white_aluminum.jpg
│   └── ...
├── style_industrial/
│   ├── 45deg_black_steel.jpg
│   └── ...
├── angle_variants/
│   └── ...
└── scene_variants/
    └── ...
```

---

## Step 6：结果整理与报告

```bash
python skills/allen-product-design/scripts/generate_report.py \
  --prompts output/prompts.json \
  --images-dir output/images \
  --output output/report.md
```

### 报告结构

```markdown
# 产品概念图报告 — [产品名称]
## 生成信息
- 日期: YYYY-MM-DD
- 模型: NanoBanana 2
- 分辨率: 2K
- 总图片数: N
- 成功/失败: N/N
- 预估费用: $X.XX

## 风格探索
### 极简风格
![极简-45度](images/style_minimal/45deg_xxx.jpg)
Prompt: `...`

### 工业风格
![工业-45度](images/style_industrial/45deg_xxx.jpg)
Prompt: `...`

## 角度变体
...

## 使用场景
...

## 完整 Prompt 记录
| # | 维度 | Prompt | 状态 | 文件 |
|---|------|--------|------|------|
| 1 | style:minimal / angle:45deg | ... | SUCCESS | ... |
```

---

## Step 7：验证

```bash
python skills/allen-product-design/scripts/validate_deliverables.py --output-dir output
```

验证清单：
- [ ] output/images/ 至少有 1 张图片
- [ ] output/report.md 存在且非空
- [ ] output/prompts.json 存在且是合法 JSON
- [ ] output/summary.md 存在
- [ ] 图片文件按目录正确分组
- [ ] 失败的任务有错误记录

输出 `validate_ok` = 完成。

---

## 参数参考

### CLI 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--style` | string | "minimal" | 逗号分隔的风格列表 |
| `--angles` | string | "45deg" | 逗号分隔的角度列表 |
| `--variants` | int | 1 | 每个维度生成的变体数 |
| `--colors` | string | 自动推断 | 逗号分隔的颜色列表 |
| `--materials` | string | 自动推断 | 逗号分隔的材质列表 |
| `--scenes` | string | "studio" | 逗号分隔的场景列表 |
| `--model` | string | "nanobanana-2" | API 模型：nanobanana / nanobanana-2 / nanobanana-pro |
| `--resolution` | string | "2K" | 分辨率：1K / 2K / 4K |
| `--format` | string | "jpg" | 输出格式：jpg / png |
| `--max-images` | int | 20 | 最大生成图片数 |
| `--output-dir` | string | "output" | 输出目录路径 |

### API 模型映射

| 模型标识 | API 端点 | 类型字段 | 比例字段 |
|---------|---------|---------|---------|
| nanobanana | `/api/v1/nanobanana/generate` | `type: "TEXTTOIAMGE"` | `image_size` |
| nanobanana-2 | `/api/v1/nanobanana/generate-2` | 不需要 | `aspectRatio` |
| nanobanana-pro | `/api/v1/nanobanana/generate-pro` | 不需要 | `aspectRatio` |
