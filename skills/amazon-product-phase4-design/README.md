# allen-product-design

根据产品定义，利用 NanoBanana API 自动生成工业设计概念图。

## 安装

### 1. 环境准备

```bash
# Python 3.8+
pip install requests
```

### 2. API Key 配置

1. 前往 [NanoBanana 控制台](https://nanobananaapi.ai/dashboard) 注册并获取 API Key
2. 设置环境变量：

**Windows:**
```cmd
set NANOBANANA_API_KEY=你的API密钥
```

**Linux/Mac:**
```bash
export NANOBANANA_API_KEY=你的API密钥
```

### 3. 验证环境

```bash
python skills/allen-product-design/scripts/check_env.py
```

## 使用方式

### 方式 1：Claude Code Slash 命令（推荐）

```bash
# 自然语言描述
/allen-product-design 一款带 LED 灯的蓝牙耳机，黑色哑光，运动风格

# 带参数
/allen-product-design 便携榨汁杯 --style 极简,工业 --angles 正面,45度 --resolution 2K
```

### 方式 2：手动执行脚本

```bash
# Step 1: 创建产品定义文件
echo '{"product_name": "蓝牙耳机", "features": ["LED灯", "降噪"], "colors": ["黑色"]}' > product.json

# Step 2: 构建 Prompt 矩阵
python skills/allen-product-design/scripts/build_prompts.py \
  --input product.json \
  --styles minimal,industrial,futuristic \
  --angles 45deg,front,side \
  --scenes studio,lifestyle \
  --resolution 2K \
  --output output/prompts.json

# Step 3: 预览（不消耗 API 额度）
python skills/allen-product-design/scripts/generate_images.py \
  --prompts output/prompts.json \
  --model nanobanana-2 \
  --dry-run

# Step 4: 生成图片
python skills/allen-product-design/scripts/generate_images.py \
  --prompts output/prompts.json \
  --model nanobanana-2 \
  --resolution 2K \
  --output-dir output/images

# Step 5: 生成报告
python skills/allen-product-design/scripts/generate_report.py \
  --prompts output/prompts.json \
  --output output/report.md

# Step 6: 验证交付物
python skills/allen-product-design/scripts/validate_deliverables.py --output-dir output
```

## 输出结构

```
output/
├── prompts.json                # 所有 Prompt 及参数
├── generation_results.json     # API 调用结果记录
├── summary.json                # 生成概要
├── report.md                   # 可视化报告
└── images/
    ├── style_minimal/          # 按风格分组
    │   ├── style_minimal_45deg_matte_black.jpg
    │   └── ...
    ├── style_industrial/
    ├── angle_variants/         # 角度变体
    ├── color_variants/         # 颜色变体
    └── scene_variants/         # 场景变体
```

## 支持的参数

| 参数 | 选项 | 说明 |
|------|------|------|
| `--model` | `nanobanana` / `nanobanana-2` / `nanobanana-pro` | API 模型 |
| `--resolution` | `1K` / `2K` / `4K` | 输出分辨率 |
| `--styles` | `minimal,industrial,retro,futuristic,organic,luxury` | 设计风格 |
| `--angles` | `front,side,45deg,top,perspective,back` | 视角 |
| `--scenes` | `studio,gradient,lifestyle,dark,exploded,context` | 背景场景 |
| `--max-images` | 整数 (默认 20) | 最大生成数量 |
| `--format` | `jpg` / `png` | 输出格式 |

## 费用参考

| 模型 | 1K | 2K | 4K |
|------|-----|-----|-----|
| NanoBanana | $0.02 | - | - |
| NanoBanana 2 | $0.04 | $0.06 | $0.09 |
| NanoBanana Pro | $0.09 | $0.09 | $0.12 |

默认配置 (NanoBanana 2, 2K, 10 张) 约 $0.60。

## 文件结构

```
skills/allen-product-design/
├── SKILL.md                    # 完整方法论
├── README.md                   # 本文件
├── references/
│   ├── prompt_templates.md     # Prompt 模板库
│   └── api_reference.md        # API 参数映射表
└── scripts/
    ├── check_env.py            # 环境检查
    ├── build_prompts.py        # Prompt 矩阵构建
    ├── generate_images.py      # API 调用 + 图片下载
    ├── generate_report.py      # 报告生成
    └── validate_deliverables.py # 交付物验证
```
