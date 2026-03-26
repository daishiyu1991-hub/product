# 项目管理助手 Skill

## 描述
基于飞书 Bitable 的全公司项目任务管理系统。支持通过自然语言创建项目、添加/更新/查询任务、每日自动追踪推送、云端审批队列（方案B）、自动周报。

## 触发词
"项目管理"、"新建项目"、"添加任务"、"项目进度"、"任务更新"、"会议纪要"、"项目追踪"、"任务完成"、"哪些任务到期"、"今天项目"、"项目日报"、"周报"、"审批"、"变更审批"

## 核心引擎
- 脚本位置: `C:\Users\Administrator\metabot-workspace\project-manager\project_tracker.py`
- Python: `C:\Program Files\Python312\python.exe`
- 元数据: `C:\Users\Administrator\metabot-workspace\project-manager\projects_meta.json`

## 架构
```
管理员 MetaBot（本机）
  ├─ 直接操作 Bitable（创建/更新/查询）
  ├─ 接收员工审批请求（云端审批队列）
  └─ 推送日报/周报（Webhook）

员工 MetaBot（各自电脑）
  ├─ 查询自己的任务（只读 Bitable）
  ├─ 提交变更请求 → 云端审批队列
  └─ 接收任务提醒

云端共享
  ├─ 项目 Bitable（任务看板）
  └─ 审批队列 Bitable（app_token: ArJJbrmVIaYmlEsYcNYcMBDWnGd）
```

## 功能清单

### 功能1: 新建项目
触发: "新建一个项目叫xxx"、"创建项目"
```bash
"/c/Program Files/Python312/python.exe" C:/Users/Administrator/metabot-workspace/project-manager/project_tracker.py init "项目名"
```
返回: app_token + bitable_url（可直接在飞书打开看板）

### 功能2: 添加任务（支持会议纪要批量解析）
触发: "添加任务"、"会议决定..."、"今天会议..."

**用户输入示例:**
> 刚开完智能戒指项目会，决定：SDK 3月底交付小张负责，模具4月15号开模找东莞友宏，首批500pcs 5月1号出货

**MetaBot 处理流程:**
1. 解析自然语言为结构化任务列表
2. 调用 project_tracker.py add

```bash
"/c/Program Files/Python312/python.exe" C:/Users/Administrator/metabot-workspace/project-manager/project_tracker.py add "项目名" '[{"name":"任务名","owner":"负责人","deadline":"yyyy-MM-dd","priority":"P0-P3","source":"来源","note":"备注"}]'
```

**解析规则:**
- 识别「谁+做什么+什么时候」三要素
- 日期格式统一为 yyyy-MM-dd
- 优先级默认 P2，含"紧急/关键/必须"关键词则 P0
- 来源自动标记为"会议"或"对话"

### 功能3: 更新任务（管理员直接更新）
触发: "xxx完成了"、"xxx推迟到..."、"xxx改由yyy负责"

```bash
"/c/Program Files/Python312/python.exe" C:/Users/Administrator/metabot-workspace/project-manager/project_tracker.py update "项目名" '[{"task":"任务名","status":"已完成"},{"task":"任务名","deadline":"2026-04-20"}]'
```

**支持的更新字段:**
- 状态: 待开始/进行中/已完成/延期/已取消
- 截止日期: deadline
- 进度: progress (0-100)
- 负责人: owner
- 优先级: priority (P0-P3)
- 备注: note

### 功能4: 查询项目进度
触发: "xxx项目怎么样了"、"项目进度"、"哪些任务到期"

```bash
"/c/Program Files/Python312/python.exe" C:/Users/Administrator/metabot-workspace/project-manager/project_tracker.py query "项目名"
```

**展示格式:**
```
📋 智能戒指V1 项目进度
━━━━━━━━━━━━━━━━━━━
[██████░░░░] 62.5% 完成

🔴 已过期 (1)
  · CE认证申请（小王，截止4/20）

🟡 今日到期 (1)
  · Listing文案（小陈）

🔵 进行中 (2)
  · 外壳模具开模 — 60% — 东莞友宏
  · 包装设计终稿 — 80% — 小李

✅ 已完成 (3)
  · SDK蓝牙模块 · ...

📊 飞书看板: [链接]
```

### 功能5: 每日自动追踪（定时任务 09:00）
已配置 Windows Task Scheduler `ProjectTracker_Daily`
```bash
"/c/Program Files/Python312/python.exe" C:/Users/Administrator/metabot-workspace/project-manager/project_tracker.py push
```

**自动执行:**
- 扫描所有项目的 Bitable
- 识别过期任务，自动标记为"延期"
- 生成追踪日报卡片推送飞书
- 卡片包含：项目完成率进度条 + 过期/今日到期/3天内到期分类
- 随后推送审批队列通知（若有待审批变更）

### 功能6: 列出所有项目
```bash
"/c/Program Files/Python312/python.exe" C:/Users/Administrator/metabot-workspace/project-manager/project_tracker.py list
```

### 功能7: 员工提交变更（云端审批队列）
触发: 员工说"xx任务完成了"、"xx进度更新"
员工 MetaBot 不直接改 Bitable，而是提交到云端审批队列：

```bash
"/c/Program Files/Python312/python.exe" C:/Users/Administrator/metabot-workspace/project-manager/project_tracker.py submit "员工名" "项目名" '[{"task":"任务名","status":"已完成"}]'
```

### 功能8: 管理员审批变更
触发: "查看审批"、"审批 all"、"审批变更"

```bash
# 查看待审批
"/c/Program Files/Python312/python.exe" C:/Users/Administrator/metabot-workspace/project-manager/project_tracker.py review

# 全部通过
"/c/Program Files/Python312/python.exe" C:/Users/Administrator/metabot-workspace/project-manager/project_tracker.py approve all

# 部分通过（指定record_id）
"/c/Program Files/Python312/python.exe" C:/Users/Administrator/metabot-workspace/project-manager/project_tracker.py approve "recXXX,recYYY"

# 驳回
"/c/Program Files/Python312/python.exe" C:/Users/Administrator/metabot-workspace/project-manager/project_tracker.py reject all "原因"
```

### 功能9: 自动周报（每周五 17:00）
已配置 Windows Task Scheduler `ProjectTracker_Weekly`

```bash
# 生成周报数据
"/c/Program Files/Python312/python.exe" C:/Users/Administrator/metabot-workspace/project-manager/project_tracker.py weekly

# 生成并推送飞书
"/c/Program Files/Python312/python.exe" C:/Users/Administrator/metabot-workspace/project-manager/project_tracker.py push-weekly
```

**周报内容:**
- 各项目完成率进度条
- 按人员汇总：本周完成任务、进行中任务、延期任务
- 表现标记：🏆完成且无延期、⚠️有延期、📌无变化

## 云端审批队列
- Bitable URL: https://bytedance.feishu.cn/base/ArJJbrmVIaYmlEsYcNYcMBDWnGd
- 字段: 提交人、项目、任务名称、变更内容、审批状态（待审批/已通过/已驳回）、提交时间、审批时间、驳回原因
- 多台 MetaBot 共享同一个云端队列，无需本地文件同步

## 定时任务
| 任务名 | 触发时间 | 脚本 | 功能 |
|--------|---------|------|------|
| ProjectTracker_Daily | 每日 09:00 | run_daily.bat | 日报推送 + 审批队列通知 |
| ProjectTracker_Weekly | 每周五 17:00 | run_weekly.bat | 周报推送 |

## 状态定义
| 状态 | 含义 | 自动触发 |
|------|------|----------|
| 待开始 | 任务创建后默认 | — |
| 进行中 | 已开工 | — |
| 已完成 | 完成 | 进度自动设为100% |
| 延期 | 超过截止日期 | 每日追踪自动标记 |
| 已取消 | 取消 | 不计入完成率 |

## 优先级定义
| 等级 | 含义 | 触发词 |
|------|------|--------|
| P0 | 紧急 | 紧急、关键、必须、blocking |
| P1 | 重要 | 重要、优先 |
| P2 | 一般 | 默认 |
| P3 | 低优 | 有空再做、不急 |

## 回复风格
- 创建/更新后：简洁确认 + 飞书看板链接
- 查询时：可视化进度条 + 分类展示
- 会议纪要：先展示解析结果让用户确认，再写入
- 审批：展示变更列表，等待管理员确认

## 多项目管理
- 用户可能有多个项目同时运行
- 如果用户没指定项目名，根据上下文推断（最近操作的项目）
- 如果无法推断，列出项目让用户选择

## 多机部署
- 部署工具: `C:\Users\Administrator\metabot-workspace\metabot-deploy\admin_deploy.py`
- 指南: `C:\Users\Administrator\metabot-workspace\metabot-deploy\飞书App批量创建指南.md`
- 每个员工独立飞书App + 独立MetaBot实例
- 共享: Claude API（公司统一）+ 项目Bitable（只读）+ 审批队列Bitable（提交）
