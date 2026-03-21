# Prompt 模板库 — 工业设计概念图

## 基础 Prompt 结构

所有 Prompt 遵循以下层次结构：

```
[SUBJECT_BLOCK] + [STYLE_BLOCK] + [RENDERING_BLOCK] + [COMPOSITION_BLOCK]
```

---

## SUBJECT_BLOCK — 产品主体描述

### 模板
```
A {product_name}{feature_clause}. {material_clause}. {color_clause}.
```

### 示例
```
A wireless Bluetooth headphone with active noise cancellation and LED indicator lights.
Made of anodized aluminum and premium silicone earpads.
In matte black finish with subtle carbon fiber texture.
```

### 规则
- 必须包含产品名称
- 功能描述使用 "with" 连接，最多列举 3 个关键功能
- 材质使用 "Made of" 引导
- 颜色使用 "In [color] finish" 格式

---

## STYLE_BLOCK — 设计风格

### 风格模板库

#### 经典设计风格

| 风格 ID | 名称 | Template |
|---------|------|----------|
| minimal | 极简 | `Minimalist industrial design aesthetic. Clean lines, simple geometry, Scandinavian design influence. Understated elegance with focus on form and function.` |
| industrial | 工业 | `Industrial design aesthetic. Robust construction, utility-focused details, visible mechanical elements. Form follows function with deliberate material contrast.` |
| retro | 复古 | `Retro-futuristic design aesthetic. Mid-century modern influence with Art Deco elements. Warm color palette, rounded edges, nostalgic yet forward-looking.` |
| futuristic | 未来感 | `Futuristic design aesthetic. Sleek aerodynamic form, seamless surfaces, holographic accents. Cutting-edge appearance with advanced material finishing.` |
| organic | 有机 | `Organic design aesthetic. Biomorphic curves, nature-inspired flowing forms. Smooth transitions, soft edges, biomimetic structural patterns.` |
| luxury | 奢华 | `Premium luxury design aesthetic. Gold accents, fine leather details, haute couture finish. Exquisite craftsmanship with meticulous attention to surface quality.` |

#### 品牌灵感风格

| 风格 ID | 名称 | Template |
|---------|------|----------|
| apple | 苹果风 | `Apple-inspired design aesthetic. Ultra-clean unibody aluminum or polycarbonate shell, razor-thin bezels, seamless curves, monochrome palette with subtle material transitions. Jony Ive design philosophy.` |
| braun | 博朗风 | `Braun / Dieter Rams design aesthetic. Less but better. Geometric purity, muted earth tones, clear grid-based layout, honest materials. Timeless 1960s German functionalism.` |
| dyson | 戴森风 | `Dyson-inspired design aesthetic. Bold engineering-forward form, visible cyclone or airflow mechanics, transparent polycarbonate sections, distinctive color blocking with purple and silver accents.` |
| muji | 无印良品风 | `MUJI-inspired design aesthetic. No-brand minimalism, natural materials, matte white or kraft textures, understated and anonymous. Warm neutral palette, anti-design philosophy.` |
| bang-olufsen | B&O风 | `Bang & Olufsen inspired design aesthetic. Sculptural audio-visual elegance, brushed aluminum surfaces, floating forms, architectural presence. Danish luxury meets technology.` |

#### 材质驱动风格

| 风格 ID | 名称 | Template |
|---------|------|----------|
| transparent | 透明 | `Transparent design aesthetic. Clear polycarbonate or glass shell revealing internal mechanisms and PCB. See-through industrial beauty, Nothing Phone / Teenage Engineering inspired.` |
| wooden | 木质 | `Natural wood design aesthetic. Warm walnut or bamboo body with precision metal accents. Craft-meets-technology, artisan workshop feel, Japanese woodworking precision.` |
| ceramic | 陶瓷 | `Ceramic design aesthetic. Smooth matte ceramic body with rounded edges, porcelain-like surface quality. Warm to touch, premium feel, subtle glazed color variations.` |
| metal | 全金属 | `Full metal machined design aesthetic. CNC-milled aluminum or titanium unibody, precision chamfered edges, anodized color finish. Tool-watch level craftsmanship.` |
| fabric | 织物 | `Fabric-wrapped design aesthetic. Premium knit or woven textile exterior, soft-touch feel, rounded friendly forms. Google Home / Sonos inspired lifestyle integration.` |

#### 情感驱动风格

| 风格 ID | 名称 | Template |
|---------|------|----------|
| cute | 可爱 | `Kawaii cute design aesthetic. Rounded blob-like form, pastel candy colors, friendly face-like feature placement, toy-like proportions. Approachable and smile-inducing.` |
| rugged | 硬核户外 | `Rugged outdoor design aesthetic. Military-grade build, rubberized armor, high-visibility orange or yellow accents, oversized grip textures. IP67 waterproof adventure-ready.` |
| cyberpunk | 赛博朋克 | `Cyberpunk design aesthetic. Neon accent lighting, dark matte body with glowing edge strips, angular aggressive geometry, RGB LED elements. Blade Runner meets consumer tech.` |
| steampunk | 蒸汽朋克 | `Steampunk design aesthetic. Brass and copper mechanical details, exposed gears and rivets, Victorian-era ornamentation meets functional machinery. Antique patina finish.` |
| eco | 环保可持续 | `Eco-sustainable design aesthetic. Recycled ocean plastic or bio-based materials, muted earth tones, visible material grain, minimal packaging philosophy. Patagonia meets product design.` |
| playful | 活泼波普 | `Playful pop-art design aesthetic. Bold primary colors, geometric patterns, Memphis Group influence, unexpected color combinations. Fun, energetic, youthful.` |
| zen | 禅意 | `Zen Japanese design aesthetic. Wabi-sabi imperfection, stone-like matte textures, asymmetric balance, ink-wash inspired color gradients. Meditative calm and restraint.` |

#### 年代风格

| 风格 ID | 名称 | Template |
|---------|------|----------|
| 80s | 80年代 | `1980s design aesthetic. Bold geometric shapes, neon colors, chrome accents, grid patterns. Miami Vice meets Tron, synthesizer-era visual language.` |
| 90s | 90年代 | `1990s design aesthetic. Translucent colored plastic, iMac G3 influence, bubbly organic forms, candy-colored bezels. Y2K optimism and tech exuberance.` |
| 2000s | 2000年代 | `Year 2000s design aesthetic. Brushed metal with piano black accents, chrome trim, early iPod era simplicity. Transitional elegance between analog and digital.` |
| y2k | Y2K未来 | `Y2K futurism design aesthetic. Chrome liquid metal surfaces, iridescent holographic finishes, bubble shapes, translucent layers. Early internet era techno-optimism.` |

---

## RENDERING_BLOCK — 渲染质量

### 通用渲染后缀
```
Professional product photography, studio lighting setup with soft diffusion,
photorealistic rendering, highly detailed surface textures, 8K quality,
clean sharp focus, subtle shadows and reflections.
```

### 按用途调整

| 用途 | 额外关键词 |
|------|-----------|
| 概念展示 | `concept design render, matte finish visualization, design sketch quality` |
| 产品展示 | `commercial product photography, advertising quality, hero shot` |
| 技术参考 | `technical illustration, precise dimensions visible, engineering render` |

---

## COMPOSITION_BLOCK — 构图与背景

### 角度模板

| 角度 ID | Template |
|---------|----------|
| front | `Straight-on front view, eye level, centered composition.` |
| side | `Side profile view, 90-degree angle, clean silhouette visible.` |
| 45deg | `Three-quarter hero shot, 45-degree angle, dynamic and engaging perspective.` |
| top | `Top-down bird's eye view, overhead perspective, flat lay composition.` |
| perspective | `Dynamic low-angle perspective, dramatic hero shot with depth.` |
| back | `Rear view, showing back panel details and ports.` |

### 背景模板

| 场景 ID | Template |
|---------|----------|
| studio | `Pure white studio background, infinite curve backdrop, professional product photography setup.` |
| gradient | `Smooth gradient background from light gray to white, subtle shadow ground plane.` |
| lifestyle | `Natural lifestyle environment, warm ambient lighting, contextual real-world setting showing product in use.` |
| dark | `Dark moody studio background, dramatic spot lighting, floating product visualization.` |
| exploded | `White background, exploded view showing all internal components separated and labeled.` |
| context | `Real-world usage context, environmental storytelling, user interaction scene.` |

---

## 完整组装示例

### 输入
```json
{
  "product_name": "portable blender",
  "features": ["USB-C rechargeable", "self-cleaning mode", "304 stainless steel blades"],
  "materials": ["Tritan plastic", "stainless steel"],
  "colors": ["mint green"],
  "style": "minimal",
  "angle": "45deg",
  "scene": "studio"
}
```

### 输出 Prompt
```
A portable blender with USB-C rechargeable battery, self-cleaning mode, and 304 stainless steel blades.
Made of crystal-clear Tritan plastic body with stainless steel blade assembly.
In fresh mint green finish with white accents.
Minimalist industrial design aesthetic. Clean lines, simple geometry, Scandinavian design influence.
Understated elegance with focus on form and function.
Three-quarter hero shot, 45-degree angle, dynamic and engaging perspective.
Pure white studio background, infinite curve backdrop, professional product photography setup.
Professional product photography, studio lighting setup with soft diffusion,
photorealistic rendering, highly detailed surface textures, 8K quality,
clean sharp focus, subtle shadows and reflections.
```

---

## 多语言支持

Prompt 始终使用**英文**构建（NanoBanana API 英文 Prompt 效果最好）。
用户输入的中文属性需翻译：

| 中文 | English |
|------|---------|
| 铝合金 | anodized aluminum |
| 不锈钢 | stainless steel |
| 钢化玻璃 | tempered glass |
| 硅胶 | silicone |
| ABS塑料 | ABS plastic |
| 碳纤维 | carbon fiber |
| 皮革 | premium leather |
| 竹木 | natural bamboo |
| 亚光/哑光 | matte finish |
| 亮面 | glossy finish |
| 磨砂 | frosted / satin finish |
| 太空灰 | space gray |
| 玫瑰金 | rose gold |
| 象牙白 | ivory white |
| 午夜蓝 | midnight blue |
