# 飞书集成 (Feishu Integration)

飞书集成技能，为亚马逊精益产品开发 Pipeline 提供消息通知、文档同步和多维表格写入能力。

## 触发条件

当用户说出以下关键词时触发：
- "发到飞书"、"推送到飞书"、"通知飞书"、"飞书通知"
- "发到群里"、"推送结果"、"通知群聊"
- "创建飞书文档"、"写入多维表格"、"同步到飞书"
- "/feishu-setup"、"/feishu-notify"、"/feishu-test"

## 核心能力

### 1. 消息通知（Webhook + App API）

**Webhook 模式**（无需 App，5 分钟配置）：
- 通过群自定义机器人发送通知
- 支持纯文本、富文本、交互式卡片

**App API 模式**（需要自建应用）：
- 向指定群聊或个人发送消息
- 支持更丰富的卡片交互

### 2. 飞书文档

- 将 Markdown 报告转换为飞书云文档
- 自动解析标题、列表、粗体、代码块等格式
- 上传图片和附件

### 3. 多维表格

- 将 XLSX/CSV 数据写入飞书多维表格
- 自动推断字段类型（文本/数字/日期）
- 支持多 Sheet 批量写入

## 执行流程

### 凭据检测

执行前检测环境变量：
1. `FEISHU_WEBHOOK_URL` — Webhook 群机器人地址
2. `FEISHU_APP_ID` + `FEISHU_APP_SECRET` — App 凭据

如果都未配置，引导用户运行 `/feishu-setup` 进行配置。

### 消息推送

各 Phase 分析完成后，通过以下方式推送：

```bash
python "$HOME/.claude/skills/feishu-integration/feishu_sdk.py" \
  notify \
  --phase <阶段编号> \
  --product "<产品名>" \
  --decision "<决策结果>" \
  --metrics '{"key":"value"}' \
  --report "<报告.md路径>" \
  --xlsx "<数据.xlsx路径>" \
  --push-doc \
  --push-bitable
```

### 卡片模板

每个 Phase 有专属卡片模板：
- **Phase 1**: GO/NO-GO 选品决策（绿/红），含月销量、均价、竞争度
- **Phase 2**: TRUE/FALSE DEMAND 验证结果，含三维信号强度
- **Phase 3**: MVP 蓝图摘要，含 KANO 分类统计、成本利润
- **Phase 4**: 设计调研完成，含形态族群、基线线稿数
- **Phase 5**: 概念图生成完成，含风格、偏离度
- **Phase 6**: Kill/Continue/Pivot 复盘决策（红/绿/黄），含 BSR/CVR/ACOS
- **Phase 7**: 迭代方案，含 Quick Win 数量、30天计划摘要
- **Phase 8**: Go Big/Maintain/Harvest/Exit 规模化决策，含财务预测

## 文件结构

```
feishu-integration/
├── SKILL.md              # 本文件
├── feishu_sdk.py          # 核心 SDK（认证+消息+文档+表格+上传+CLI）
├── card_templates.py      # 8 个 Phase 的消息卡片模板
├── test_connection.py     # 连通性测试
└── setup_guide.md         # 凭据配置指南
```

## 环境变量

在 `settings.local.json` 的 `env` 中配置：

| 变量 | 必需 | 说明 |
|------|------|------|
| `FEISHU_WEBHOOK_URL` | 推荐 | Webhook 群机器人地址 |
| `FEISHU_WEBHOOK_SECRET` | 可选 | Webhook 签名密钥 |
| `FEISHU_APP_ID` | 高级 | 自建应用 App ID |
| `FEISHU_APP_SECRET` | 高级 | 自建应用 App Secret |
| `FEISHU_DEFAULT_CHAT_ID` | 可选 | 默认群聊 ID |
| `FEISHU_DEFAULT_USER_ID` | 可选 | 默认用户 ID |
| `FEISHU_DEFAULT_FOLDER_TOKEN` | 可选 | 默认云文档文件夹 |
| `FEISHU_PROXY` | 可选 | 代理地址（默认 127.0.0.1:7897） |
| `FEISHU_USE_LARK` | 可选 | 设为 "true" 使用国际版 Lark API |

## 与各 Phase 的集成

当 Phase 分析完成且检测到飞书凭据已配置时：
1. 自动构建对应 Phase 的卡片消息
2. 从分析结果中提取关键指标
3. 调用 `feishu_sdk.py notify` 推送
4. 如果用户要求，同时创建飞书文档和多维表格

用户可以通过以下方式触发推送：
- 直接说"推送到飞书"/"发到群里"
- 使用 `/feishu-notify` 命令
- Phase 分析完成时自动提示是否推送
