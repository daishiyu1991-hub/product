## Windows 使用说明

所有脚本均支持 Windows 环境。

### 环境变量设置

**CMD:**
```cmd
set NANOBANANA_API_KEY=你的API密钥
```

**PowerShell:**
```powershell
$env:NANOBANANA_API_KEY = "你的API密钥"
```

**永久设置（系统环境变量）:**
```cmd
setx NANOBANANA_API_KEY "你的API密钥"
```

### 运行脚本

```cmd
python skills\allen-product-design\scripts\check_env.py
python skills\allen-product-design\scripts\build_prompts.py --input product.json --output output\prompts.json
python skills\allen-product-design\scripts\generate_images.py --prompts output\prompts.json --model nanobanana-2
python skills\allen-product-design\scripts\generate_report.py --prompts output\prompts.json --output output\report.md
python skills\allen-product-design\scripts\validate_deliverables.py --output-dir output
```

### 注意事项
- Windows 路径使用反斜杠 `\`，脚本内部已做兼容处理
- 如果 `requests` 库未安装：`pip install requests`
- 输出文件使用 UTF-8 编码，中文内容正常显示
