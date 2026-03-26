---
name: amazon-product-phase6-design-generation
description: "亚马逊精益开发 Phase 6：工业设计概念图生成。基于 Phase 5 设计调研成果（品类基本型、形态约束、基准草图、风格规划），自动生成风格概念图、执行偏离度检查、结构化评审、主推方案深化（场景图/正面图/剖面图/全家福）。"
argument-hint: "[产品名称] [--research-pack 调研数据包路径] [--style 风格] [--variants 变体数]"
user-invocable: true
---

# 工业设计概念图生成（精益开发 Phase 6）

## 定位

`amazon-product-phase6-design-generation` 是精益产品开发闭环的第六阶段，衔接上游的设计调研（`amazon-product-phase5-design-research`，Phase 5）。本阶段专注于**概念图生成**——基于 Phase 5 输出的 `design_research_pack.json`（品类基本型描述、形态约束、基准草图、风格规划），自动构建专业 Prompt 并调用图像生成 API，生成高质量工业设计概念图。

**本阶段的所有 Prompt 构建必须基于 Phase 5 的调研成果，不得跳过调研直接生图。**

## API 配置

### 生图服务
- **服务地址**: `https://new.suxi.ai/v1/chat/completions`
- **认证**: `Authorization: Bearer sk-DDlvJ0LEbYpjfzKHotRfcNY4taKqc290t9O6G7NOTWSBG5KL`
- **模型**: `gemini-3-pro-image-preview`（高质量）或 `gemini-3.1-flash-image-preview`（快速）
- **代理**: 需通过 `--proxy http://127.0.0.1:7897` 访问（本机 VPN 端口）
- **返回格式**: 响应中 `choices[0].message.content` 包含 `![image](URL)` 格式的图片链接
- **图片下载**: 从返回的 URL 下载图片到本地输出目录
- **注意**: 有时返回内容在 URL 前有文字说明，需用正则 `https://[^\s\)]+\.jpg` 提取 URL

### 调用示例
```bash
curl -s -L --proxy http://127.0.0.1:7897 "https://new.suxi.ai/v1/chat/completions" \
  -H "Authorization: Bearer sk-DDlvJ0LEbYpjfzKHotRfcNY4taKqc290t9O6G7NOTWSBG5KL" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro-image-preview",
    "messages": [{"role": "user", "content": "YOUR PROMPT HERE"}],
    "max_tokens": 4096
  }'
```

### 响应解析
```bash
python -c "
import json, re
d = json.load(open('response.json'))
c = d['choices'][0]['message']['content']
urls = re.findall(r'https://[^\s\)]+\.jpg', c)
print(urls[0] if urls else 'NO_URL')
"
```

### 并行生成规则
- **多张图片必须用后台并行生成**（`run_in_background: true`），不要串行等待
- 每张图响应时间约 30-60 秒，4 张并行 ≈ 1 分钟完成
- 所有后台任务完成后，统一提取 URL 并批量下载

## 调用方式

### 方式 1：Slash 命令（关联 Phase 5 调研包）
```
/amazon-product-phase6-design-generation garment steamer --research-pack ./output/design_research_pack.json
```

### 方式 2：自然语言
```
帮我基于上一步的设计调研，生成手持挂烫机的工业设计概念图
```

### 方式 3：自定义风格
```
/amazon-product-phase6-design-generation garment steamer --research-pack ./output/design_research_pack.json --style 极简,北欧,赛博朋克,博朗
```

---

## 执行概览

| 步骤 | 动作 | 详细说明 |
|------|------|---------|
| 1 | **加载方法论** | 读取本 SKILL.md |
| 2 | **加载 Phase 5 调研包** | 读取 `design_research_pack.json`，提取品类基本型描述、形态约束、基准草图、风格规划 |
| 3 | **加载 Phase 3** | 若需补充信息（配色/用户画像/堆叠数据），读取 Phase 3 MVP 蓝图 |
| **4** | **第一轮：风格探索** | 基于调研包的风格规划，构建 4 套 Prompt → 4 张概念图（并行生成）。偏离度目标 **6-15%** |
| **5** | **品类形态偏离度检查** | 将每张生成图与 Phase 5 的**基准草图**对比，评估 8 维度偏离度。>15% 或 <6% 必须重新生成 |
| **6** | **第一轮评审** | 仅对通过偏离度检查的图进入评审。逐张评审品类辨识度/记忆点/配色/问题，选出主推方案 + 备选方案 |
| **7** | **第二轮：主推方案深化** | 生成使用场景图 + 正面视图 + 内部剖面图 + 全家福（并行生成） |
| **8** | **输出报告** | Markdown 报告 + HTML 可视化看板 + prompts.json |

---

## 前置条件：加载 Phase 5 调研包

执行前必须加载 Phase 5 输出的 `design_research_pack.json`，提取以下必需数据：

| 数据项 | 来源字段 | 用途 |
|-------|---------|------|
| 品类基本型描述 | `category_archetype.description` | 所有 Prompt 的强制前缀 |
| 使用场景形态约束 | `category_archetype.usage_ergonomics` | Prompt 后缀补充 |
| 否定描述 | `category_archetype.negative_examples` | 防止 AI 品类混淆 |
| 基准草图路径 | `baseline_sketch.file` | 偏离度检查的对比基准 |
| 选定风格 | `style_plan.selected_styles` | 第一轮 4 种风格 |
| 记忆点设计 | `style_plan.selected_styles[].memory_point` | 每种风格的记忆特征 |
| 配色方案 | `style_plan.color_scheme` | 主色 + 辅色 + 备选色 |
| 内部堆叠 | `internal_stacking` | 剖面图组件列表 |
| 用户画像 | Phase 3 | 使用场景图人物形象 |

**如果 `design_research_pack.json` 不存在**，提示用户先执行 Phase 5 设计调研。

---

## 第一轮：风格探索（4 张概念图）

### Prompt 构建公式

```
[品类基本型描述 — 来自 design_research_pack.json category_archetype.description — 200-400 字]

[使用场景形态约束 — 来自 category_archetype.usage_ergonomics — 50-100 字]

Design style: [风格名称 — 来自 style_plan.selected_styles]. [风格具体描述 — 材质/曲面/线条感 50-100 字].
The single visual memory point is [记忆点 — 来自 style_plan.selected_styles[].memory_point — 位置/形状/功能 30-50 字].

Color scheme: [主色 — 来自 style_plan.color_scheme.primary + 具体 Pantone 参考]. [辅色描述]. [水箱/底板等功能部件颜色].

Photo style: Professional product photography on pure white background,
[角度], [灯光], product centered, no hands, no props,
ultra-high resolution, 8K quality. [氛围描述].
```

### 生成规则
- **4 张图必须并行生成**（后台 curl 命令，不要串行等待）
- 每张图对应 1 种风格（来自 Phase 5 风格规划）
- 统一使用 Phase 3 确定的配色方案（主色+辅色）
- 备选色方案可用 1 张图探索

---

## 品类形态偏离度检查（必须在评审前执行）

### 为什么需要偏离度检查？

AI 生图即使给了精确的品类基本型描述，仍然可能在以下方面偏离真实品类形态：
- **比例失调** — 蒸汽头太大/太小，握把太长/太短
- **功能部件缺失** — 水箱消失、底板形状变异、按钮位置错误
- **品类混淆** — 看起来像吹风机/按摩枪/手电筒
- **结构不合理** — 底座无法站立、握把角度不符合人体工学

**偏离度超过 15% 的概念图不能进入评审阶段，必须调整 Prompt 后重新生成。偏离度低于 6% 的概念图创新不足，也需重新生成以增加差异化。**

### 检查方法

**第一步：逐张对比**

将每张生成图与 Phase 5 的**基准草图**（`output/images/00_baseline_archetype.jpg`）进行视觉对比。用 Read 工具同时加载生成图和基准草图。

> 注意：对比对象是 Phase 5 的**基准草图**，不是竞品原图。基准草图是统一的品类形态锚点。

**第二步：8 维度偏离度评分**

对每张生成图逐一评分，每个维度 0-100%（0%=完全一致，100%=完全偏离）：

| 偏离维度 | 检查内容 | 偏离示例 | 权重 |
|---------|---------|---------|------|
| **1. 整体轮廓** | 外形是否属于品类共性形态族群？ | 应是枪型但变成了棒型 | 20% |
| **2. 握持结构** | 握把类型/位置/角度是否正确？ | 环形握把变成了直柄 | 15% |
| **3. 功能面(底板/蒸汽头)** | 底板/蒸汽头的形状/大小/位置是否正确？ | 圆形底板变成了三角形(像熨斗) | 20% |
| **4. 水箱** | 水箱的位置/形态/可见性是否正确？ | 水箱消失或变到了错误位置 | 10% |
| **5. 比例关系** | 各部分的大小比例是否合理？ | 蒸汽头占整机 50%（实际应 30%） | 15% |
| **6. 站立/底座** | 底部设计能否物理站立？ | 底座太小无法稳定站立 | 5% |
| **7. 品类辨识** | 不看文字说明，能否一眼认出品类？ | 像按摩枪/吹风机/手电筒 | 10% |
| **8. 功能细节** | 蒸汽孔/吸力孔/LED/按钮等是否可见？ | 底板没有蒸汽孔，变成光滑表面 | 5% |

**第三步：计算加权偏离度**

```
加权偏离度 = Σ (维度偏离% × 维度权重)
```

**第四步：判定**

| 加权偏离度 | 判定 | 动作 |
|-----------|------|------|
| **<6%** | 🔵 创新不足 | **必须重新生成**。增加差异化元素，偏离度目标 6-15% |
| **6-15%** | ✅ 合格 | 进入评审 |
| **>15%** | 🚫 不合格 | **必须重新生成**。强化品类基本型约束 |

### 重新生成策略

**偏离度 >15% 时**：
1. 定位偏离维度：找出权重最高的偏离维度
2. 强化 Prompt：增加否定描述 + 精确尺寸比例 + 相对位置描述
3. 保留风格：不改变风格/配色/记忆点，只强化形态约束
4. 单张重新生成：只重新生成不合格的那张

**偏离度 <6% 时**：
1. 增加差异化：强化记忆点描述，增加更具体的风格特征
2. 调整材质/纹理：增加更大胆的材质或表面处理
3. 单张重新生成

---

## 第一轮评审矩阵

对通过偏离度检查的每张图进行结构化评审：

| 评审维度 | 评分标准 | 权重 |
|---------|---------|------|
| 品类辨识度 | 一眼能认出是什么产品 (★1-5) | 最高 |
| 记忆点强度 | 记忆点是否突出且独特 (★1-5) | 高 |
| Phase 3 一致性 | 配色/功能/尺寸是否符合 MVP 蓝图 (★1-5) | 高 |
| Primary 用户适配 | 主力用户(60-70%)是否会喜欢 (★1-5) | 高 |
| Secondary 用户适配 | 次要用户(20-30%)是否会喜欢 (★1-5) | 中 |
| 功能表达完整度 | 水箱/底板/控制等功能细节是否充分表达 (★1-5) | 中 |
| 差异化 vs 竞品 | 与竞品外观的区分度 (★1-5) | 中 |

评审结果分类：
- **⭐ 主推方案** — 综合评分最高，作为第二轮深化对象
- **✅ 强推荐(备选色)** — 适合作为 V2 第二配色 SKU
- **✅ 推荐** — 有亮点但非最优
- **⚠️ 备选** — 存在明显偏离，仅作参考

---

## 第二轮：主推方案深化（4 张深化图）

选定主推方案后，必须生成以下 4 张深化图（并行生成）：

### 图1：使用场景图 (Lifestyle)
```
Prompt 要素：
- 用户形象：匹配 Phase 3 Primary Persona（年龄/性别/着装/场景）
- 产品外观：必须与主推方案一致（配色/记忆点/比例）
- 场景：Phase 3 中描述的典型使用场景
- 使用姿态：基于 Phase 5 场景形态约束（握持角度/手臂姿态/操作方向）
- 拍摄风格：editorial lifestyle, 暖色自然光, 浅景深, 杂志级质感
用途 → Listing 图2 或 A+ Hero Banner
```

### 图2：正面视图 (Front View)
```
Prompt 要素：
- 品类基本型描述（来自 Phase 5 调研包）
- 主推方案风格和配色
- 视角：正面直视 (straight-on front view)
- 产品站立状态（展示底座设计）
- 重点展示：水箱刻度线、控制面板、记忆点细节
用途 → Listing 图4 (细节/水箱特写)
```

### 图3：内部剖面图 (Cross-Section)
```
Prompt 要素：
- 品类基本型描述（确保外形正确）
- 视图类型："technical cross-section cutaway illustration"
- 半剖结构：左半剖内部 + 右半完整外观
- 所有内部组件从 Phase 3 堆叠数据（经 Phase 5 确认）逐区列出
- 标注要求：leader lines + text labels + 尺寸
- 工程图风格 + 白/浅灰背景
用途 → A+ 技术模块 / 供应商沟通 / Listing 图6
```

### 图4：全家福 (Hero + Accessories)
```
Prompt 要素：
- 产品站立（主推方案外观）
- 所有附件整齐排列（从 Phase 3 附件清单）
- 包装盒（从 Phase 3 包装设计规划）
- Apple 开箱美学风格
- 白底 studio 灯光
用途 → Listing 图7 (全家福)
```

---

## 内部剖面图生成方法论

### 剖面图 Prompt 构建规则

```
1. [品类基本型描述] — 来自 Phase 5 调研包
2. [外观描述] — 主推方案的风格/配色/记忆点
3. [视图类型] — "technical cross-section cutaway illustration"
4. [外壳可见性] — "half-cutaway view, external shell partially removed to reveal internals"
5. [组件列表] — 从上到下逐一列出每个 ZONE 的内部组件名称、位置、材质
6. [标注要求] — "clean leader lines with text labels pointing to each component"
7. [尺寸标注] — 关键尺寸（高度/宽度）
8. [风格] — "professional engineering technical illustration, white/light background"
9. [配色] — 外壳颜色 + 重点部件高亮色（用记忆点辅色）
```

---

## 六条设计准则（硬规则）

所有外观概念图必须遵守，偏离度检查和评审时必须逐条检查合规：

1. **少即是多** — 每个方案最多 1 个视觉记忆点，其余保持克制
2. **使用基本型** — 基于 Phase 5 品类基本型调研确定的经典外形，不使用复杂异形曲面
3. **保持品类辨识度** — 消费者一眼能认出这是什么产品（通过 Phase 5 品类基本型约束确保）
4. **有且仅有一个记忆特征** — 消费者必须记住一个东西，这个特征同时也是品牌锚点
5. **遵从人体工学** — 使用时手腕保持中性位，不做反关节运动（基于 Phase 5 场景形态约束）
6. **品类形态偏离度 6-15%** — 加权偏离度必须在 6-15% 区间（详见偏离度检查方法论）

---

## 输出物规范

### 必须输出的文件

| 文件 | 命名规则 | 说明 |
|------|---------|------|
| `output/images/01_[style]_[color].jpg` | 第一轮概念图 | 4 种风格各 1 张 |
| `output/images/05_lifestyle_scene.jpg` | 使用场景图 | 匹配 Primary Persona |
| `output/images/06_front_view_[style].jpg` | 正面视图 | 主推方案细节展示 |
| `output/images/07_cross_section.jpg` | 内部剖面工程图 | 与 Phase 3 堆叠对应 |
| `output/images/08_hero_accessories.jpg` | 全家福 | 产品+配件+包装 |
| `output/prompts.json` | Prompt 记录 | 所有 Prompt + 参数 + 图片 URLs |
| `output/YYYYMMDD_[品类]_工业设计概念图报告_v1.md` | Markdown 报告 | 完整分析+评审+建议 |

### 报告必须包含的章节

1. **Executive Summary** — 设计任务/成果总览/主推方案/关键结论
2. **Phase 5 调研回顾** — 品类基本型描述摘要 + 形态约束摘要 + 基准草图展示 + 风格规划摘要
3. **品类形态偏离度检查** — 每张概念图的 8 维度偏离度评分表 + 加权偏离度 + Pass/Fail 判定 + 不合格图的重新生成记录
4. **第一轮概念图** — 每张图的评审（品类辨识度/记忆点/配色/问题/评级）
5. **风格对比矩阵** — 7 个维度的评分对比表
6. **第二轮深化图** — 每张图的内容说明 + Listing 用途映射
7. **设计准则合规检查** — 6 条准则逐条检查（含偏离度准则）
8. **Listing 图片映射建议** — 概念图 → Listing 图位对应
9. **供应商沟通用视觉参考** — 哪几张图打包发供应商
10. **生成概要** — 模型/次数/成功率/文件索引（含重新生成次数）

## 上下游对接

- 上游：`amazon-product-phase5-design-research`（Phase 5：设计调研 → design_research_pack.json + 基准草图 + 竞品图库）
- 下游：`amazon-product-phase7-launch-review`（Phase 7：上架复盘）


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
