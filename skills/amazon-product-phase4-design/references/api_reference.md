# NanoBanana API 参数映射表

## API 端点

| 模型标识 | 端点 URL | 价格 |
|---------|---------|------|
| `nanobanana` | `POST https://api.nanobananaapi.ai/api/v1/nanobanana/generate` | $0.02/张 |
| `nanobanana-2` | `POST https://api.nanobananaapi.ai/api/v1/nanobanana/generate-2` | $0.04-$0.09/张 |
| `nanobanana-pro` | `POST https://api.nanobananaapi.ai/api/v1/nanobanana/generate-pro` | $0.09-$0.12/张 |
| 查询状态 | `GET https://api.nanobananaapi.ai/api/v1/nanobanana/record-info?taskId=xxx` | 免费 |
| 查询余额 | `GET https://api.nanobananaapi.ai/api/v1/common/get-credits` | 免费 |

## 认证

```
Header: Authorization: Bearer YOUR_API_KEY
```

---

## NanoBanana (基础版) 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `prompt` | string | ✅ | 文本描述 |
| `type` | enum | ✅ | `TEXTTOIAMGE` 或 `IMAGETOIAMGE` |
| `callBackUrl` | string(uri) | ✅ | 回调 URL（可设为空占位） |
| `numImages` | int(1-4) | ❌ | 生成数量，默认 1 |
| `imageUrls` | string[] | ❌ | 输入图片 URL（图生图模式） |
| `watermark` | string | ❌ | 水印文字 |
| `image_size` | enum | ❌ | 比例：`1:1`, `9:16`, `16:9`, `3:4`, `4:3`, `3:2`, `2:3`, `5:4`, `4:5`, `21:9` |

---

## NanoBanana 2 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `prompt` | string(max 20000) | ✅ | 文本描述，最长 20000 字符 |
| `imageUrls` | string[] (max 14) | ❌ | 参考图 URL，空数组=文生图，最多 14 张 |
| `aspectRatio` | enum | ❌ | `1:1`, `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9`, `auto`。默认 `auto` |
| `resolution` | enum | ❌ | `1K`, `2K`, `4K`。默认 `1K` |
| `googleSearch` | bool | ❌ | 搜索增强，默认 `false` |
| `outputFormat` | enum | ❌ | `png`, `jpg`。默认 `jpg` |
| `callBackUrl` | string(uri) | ❌ | 回调 URL（可选） |

---

## NanoBanana Pro 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `prompt` | string | ✅ | 文本描述 |
| `imageUrls` | string[] (max 8) | ❌ | 参考图 URL，最多 8 张 |
| `resolution` | enum | ❌ | `1K`, `2K`, `4K` |
| `callBackUrl` | string(uri) | ❌ | 回调 URL |
| `aspectRatio` | enum | ❌ | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`, `auto` |

---

## 响应格式

### 生成请求响应
```json
{
  "code": 200,
  "msg": "success",        // 或 "message": "success" (NB2/Pro)
  "data": {
    "taskId": "task_12345678"
  }
}
```

### 任务查询响应
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "nanobanana_task_123456",
    "paramJson": "",
    "completeTime": "",
    "response": {
      "originImageUrl": "https://bfl.com/image/original.jpg",   // ⚠️ 10 分钟有效
      "resultImageUrl": "https://ourserver.com/image/result.jpg" // 持久 URL
    },
    "successFlag": 1,
    "errorCode": 0,
    "errorMessage": "",
    "createTime": ""
  }
}
```

### successFlag 状态码
| 值 | 含义 |
|----|------|
| `0` | GENERATING — 正在生成 |
| `1` | SUCCESS — 生成成功 |
| `2` | CREATE_TASK_FAILED — 创建任务失败 |
| `3` | GENERATE_FAILED — 生成失败 |

---

## 比例选择指南（工业设计场景）

| 视角 | 推荐比例 | 原因 |
|------|---------|------|
| 正面/侧面 | `1:1` 或 `4:5` | 适合产品单体展示 |
| 45度英雄照 | `4:3` 或 `3:2` | 经典产品摄影比例 |
| 俯视 | `1:1` | 方形构图适合俯视 |
| 场景化 | `16:9` 或 `3:2` | 宽幅适合场景叙事 |
| 超宽海报 | `21:9` | 横幅/Banner 用途 |
| 手机适配 | `9:16` | 移动端展示 |

---

## 费用估算

| 模型 | 分辨率 | 单价 | 10 张 | 20 张 |
|------|-------|------|-------|-------|
| NanoBanana | - | $0.02 | $0.20 | $0.40 |
| NanoBanana 2 | 1K | $0.04 | $0.40 | $0.80 |
| NanoBanana 2 | 2K | $0.06 | $0.60 | $1.20 |
| NanoBanana 2 | 4K | $0.09 | $0.90 | $1.80 |
| NanoBanana Pro | 1K/2K | $0.09 | $0.90 | $1.80 |
| NanoBanana Pro | 4K | $0.12 | $1.20 | $2.40 |
