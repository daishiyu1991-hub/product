# 飞书集成凭据配置指南

## 方式一：Webhook 群机器人（推荐先用，5 分钟搞定）

Webhook 方式只能向**群聊**推送消息，但配置最简单，无需创建应用。

### 操作步骤

1. **打开飞书桌面端或网页版**
2. **进入你要推送通知的群聊**
3. **点击群设置**（群名称右侧 ⓘ 图标）
4. **群机器人** → **添加机器人**
5. **选择「自定义机器人」**
6. **输入机器人名称**（如"亚马逊产品分析"）
7. **复制 Webhook 地址**
   - 格式：`https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
8. **（可选）开启签名校验** → 记录 Secret 密钥
9. **点击完成**

### 配置凭据

在 Claude Code 中运行 `/feishu-setup`，或手动编辑 `~/.claude/settings.local.json`：

```json
{
  "env": {
    "FEISHU_WEBHOOK_URL": "https://open.feishu.cn/open-apis/bot/v2/hook/你的地址",
    "FEISHU_WEBHOOK_SECRET": ""
  }
}
```

### 验证

```bash
python ~/.claude/skills/feishu-integration/test_connection.py
```

如果群里收到测试消息，配置成功！

---

## 方式二：自建应用（完整功能）

自建应用支持：个人消息、丰富卡片交互、创建飞书文档、写入多维表格、上传文件。

### 操作步骤

#### 1. 创建应用

1. 访问 **[飞书开放平台](https://open.feishu.cn/app)**
2. 登录你的飞书账号
3. 点击 **「创建企业自建应用」**
4. 填写应用名称（如"亚马逊产品分析"）和描述
5. 记录以下信息：
   - **App ID**: `cli_xxxxxxxxxx`
   - **App Secret**: `xxxxxxxxxxxxxxxxxx`

#### 2. 配置权限

进入应用 → **权限管理** → **添加权限**，搜索并添加以下权限：

| 权限标识 | 权限名称 | 用途 |
|---------|---------|------|
| `im:message:send_as_bot` | 以应用的身份发消息 | 消息推送 |
| `im:message` | 获取与发送单聊、群组消息 | 消息功能 |
| `contact:user.id:readonly` | 获取用户 user ID | 查找推送目标 |
| `docx:document` | 查看、创建、编辑云文档 | 创建飞书文档 |
| `drive:drive` | 查看、管理云空间 | 文件上传和文件夹操作 |
| `bitable:app` | 查看、创建、编辑多维表格 | 数据表写入 |

#### 3. 启用机器人

进入应用 → **添加应用能力** → **机器人** → 启用

#### 4. 发布应用

1. **版本管理与发布** → **创建版本**
2. 填写版本号和更新说明
3. 点击 **申请线上发布**
4. 等待管理员审批通过

#### 5. 获取推送目标 ID

**获取群聊 chat_id：**
- 在飞书中，将机器人添加到目标群
- 通过 API 查询机器人所在群列表：
  ```
  GET https://open.feishu.cn/open-apis/im/v1/chats
  ```

**获取个人 open_id：**
- 通过 API 按手机号或邮箱查询：
  ```
  GET https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id
  ```

#### 6. 获取文件夹 token

- 打开飞书云文档 → 进入目标文件夹
- URL 中的 token 即为文件夹 token
- 格式：`https://xxx.feishu.cn/drive/folder/fldcnXXXXXXXXXX`
- 其中 `fldcnXXXXXXXXXX` 就是 folder_token

### 配置凭据

```json
{
  "env": {
    "FEISHU_APP_ID": "cli_xxxxxxxxxx",
    "FEISHU_APP_SECRET": "xxxxxxxxxxxxxxxxxx",
    "FEISHU_DEFAULT_CHAT_ID": "oc_xxxxxxxx",
    "FEISHU_DEFAULT_USER_ID": "ou_xxxxxxxx",
    "FEISHU_DEFAULT_FOLDER_TOKEN": "fldcnxxxxxxxx"
  }
}
```

### 验证

```bash
python ~/.claude/skills/feishu-integration/test_connection.py
```

---

## 常见问题

### Q: Webhook 和 App 可以同时配置吗？
A: 可以。SDK 会优先使用 Webhook 发送群通知（更简单快速），需要文档/表格功能时自动使用 App API。

### Q: 我在中国大陆之外，用 Lark 而不是飞书？
A: 在 `settings.local.json` 中设置 `"FEISHU_USE_LARK": "true"`，API 会自动切换到 `open.larksuite.com`。

### Q: 代理怎么配置？
A: SDK 默认会先尝试直连，失败后走本机代理（`http://127.0.0.1:7897`）。如需自定义代理，设置 `"FEISHU_PROXY": "http://your-proxy:port"`。

### Q: 发送消息提示权限不足？
A: 检查应用权限是否已在开放平台添加，且应用版本已发布并通过审批。

### Q: 多维表格数据量很大会怎样？
A: SDK 自动分批写入（每批 500 条），有 API 限流保护。超大文件可能需要几分钟。
