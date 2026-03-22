# 内部堆叠剖面图方法论

## 为什么要做？

| 没有堆叠图 | 有堆叠图 |
|-----------|---------|
| 根因拆解写了「加挡板」，不知道放哪里 | 图上标注「此处加挡板」，一目了然 |
| 工业设计天马行空，内部放不下 | 外观受内部尺寸约束，造型能落地 |
| 供应商看文字，理解 50% | 供应商看带标注的图，理解 95% |

## 执行流程

### Step 5.1：调研内部结构

WebSearch 搜索关键词：
- `[product type] teardown`
- `[product type] internal structure diagram`
- `[product type] disassembly repair`
- `[product type] patent drawing internal`

提取信息：组件列表（名称/材质/尺寸）、堆叠顺序、关键热区、密封面、哪个组件决定外轮廓。

### Step 5.2：标注改善点

将 Step 4 根因拆解的改良方案标注到堆叠图上：
```
[组件名称] ← ⚠️ 改善: [具体内容]

例如：
[密封圈 NBR] ← ⚠️ 改善: 换 EPDM 硅胶，硬度 50±5 Shore A
[蒸汽出口] ← ⚠️ 改善: 加 3 层不锈钢多孔挡板
[配件接口 Push-fit] ← ⚠️ 改善: 改 Snap-Lock 卡扣，保持力 ≥50N
```

## 输出物

在蓝图 MD 中用 ASCII 图画出组件堆叠 + 改善点标注。

> **注意：** 剖面渲染图和外观概念图由下游 Phase 4/5 负责。Phase 3 只输出 ASCII 堆叠图。
