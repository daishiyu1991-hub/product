"""
Prompt 矩阵构建器 — 根据产品定义生成结构化的 Prompt 列表。
用于将产品属性 × 风格 × 角度 × 场景交叉组合成 prompts.json。
"""

import argparse
import json
import sys
import io
from pathlib import Path
from itertools import product as iter_product

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# ─── 风格关键词库 ─────────────────────────────────────────────
STYLE_KEYWORDS = {
    # ── 经典设计风格 ──
    "minimal": "Minimalist industrial design aesthetic. Clean lines, simple geometry, Scandinavian design influence. Understated elegance with focus on form and function.",
    "industrial": "Industrial design aesthetic. Robust construction, utility-focused details, visible mechanical elements. Form follows function with deliberate material contrast.",
    "retro": "Retro-futuristic design aesthetic. Mid-century modern influence with Art Deco elements. Warm color palette, rounded edges, nostalgic yet forward-looking.",
    "futuristic": "Futuristic design aesthetic. Sleek aerodynamic form, seamless surfaces, holographic accents. Cutting-edge appearance with advanced material finishing.",
    "organic": "Organic design aesthetic. Biomorphic curves, nature-inspired flowing forms. Smooth transitions, soft edges, biomimetic structural patterns.",
    "luxury": "Premium luxury design aesthetic. Gold accents, fine leather details, haute couture finish. Exquisite craftsmanship with meticulous attention to surface quality.",

    # ── 品牌灵感风格 ──
    "apple": "Apple-inspired design aesthetic. Ultra-clean unibody aluminum or polycarbonate shell, razor-thin bezels, seamless curves, monochrome palette with subtle material transitions. Jony Ive design philosophy.",
    "braun": "Braun / Dieter Rams design aesthetic. Less but better. Geometric purity, muted earth tones, clear grid-based layout, honest materials. Timeless 1960s German functionalism.",
    "dyson": "Dyson-inspired design aesthetic. Bold engineering-forward form, visible cyclone or airflow mechanics, transparent polycarbonate sections, distinctive color blocking with purple and silver accents.",
    "muji": "MUJI-inspired design aesthetic. No-brand minimalism, natural materials, matte white or kraft textures, understated and anonymous. Warm neutral palette, anti-design philosophy.",
    "bang-olufsen": "Bang & Olufsen inspired design aesthetic. Sculptural audio-visual elegance, brushed aluminum surfaces, floating forms, architectural presence. Danish luxury meets technology.",

    # ── 材质驱动风格 ──
    "transparent": "Transparent design aesthetic. Clear polycarbonate or glass shell revealing internal mechanisms and PCB. See-through industrial beauty, Nothing Phone / Teenage Engineering inspired.",
    "wooden": "Natural wood design aesthetic. Warm walnut or bamboo body with precision metal accents. Craft-meets-technology, artisan workshop feel, Japanese woodworking precision.",
    "ceramic": "Ceramic design aesthetic. Smooth matte ceramic body with rounded edges, porcelain-like surface quality. Warm to touch, premium feel, subtle glazed color variations.",
    "metal": "Full metal machined design aesthetic. CNC-milled aluminum or titanium unibody, precision chamfered edges, anodized color finish. Tool-watch level craftsmanship.",
    "fabric": "Fabric-wrapped design aesthetic. Premium knit or woven textile exterior, soft-touch feel, rounded friendly forms. Google Home / Sonos inspired lifestyle integration.",

    # ── 情感驱动风格 ──
    "cute": "Kawaii cute design aesthetic. Rounded blob-like form, pastel candy colors, friendly face-like feature placement, toy-like proportions. Approachable and smile-inducing.",
    "rugged": "Rugged outdoor design aesthetic. Military-grade build, rubberized armor, high-visibility orange or yellow accents, oversized grip textures. IP67 waterproof adventure-ready.",
    "cyberpunk": "Cyberpunk design aesthetic. Neon accent lighting, dark matte body with glowing edge strips, angular aggressive geometry, RGB LED elements. Blade Runner meets consumer tech.",
    "steampunk": "Steampunk design aesthetic. Brass and copper mechanical details, exposed gears and rivets, Victorian-era ornamentation meets functional machinery. Antique patina finish.",
    "eco": "Eco-sustainable design aesthetic. Recycled ocean plastic or bio-based materials, muted earth tones, visible material grain, minimal packaging philosophy. Patagonia meets product design.",
    "playful": "Playful pop-art design aesthetic. Bold primary colors, geometric patterns, Memphis Group influence, unexpected color combinations. Fun, energetic, youthful.",
    "zen": "Zen Japanese design aesthetic. Wabi-sabi imperfection, stone-like matte textures, asymmetric balance, ink-wash inspired color gradients. Meditative calm and restraint.",

    # ── 年代风格 ──
    "80s": "1980s design aesthetic. Bold geometric shapes, neon colors, chrome accents, grid patterns. Miami Vice meets Tron, synthesizer-era visual language.",
    "90s": "1990s design aesthetic. Translucent colored plastic, iMac G3 influence, bubbly organic forms, candy-colored bezels. Y2K optimism and tech exuberance.",
    "2000s": "Year 2000s design aesthetic. Brushed metal with piano black accents, chrome trim, early iPod era simplicity. Transitional elegance between analog and digital.",
    "y2k": "Y2K futurism design aesthetic. Chrome liquid metal surfaces, iridescent holographic finishes, bubble shapes, translucent layers. Early internet era techno-optimism.",
}

# ─── 角度关键词库 ─────────────────────────────────────────────
ANGLE_KEYWORDS = {
    "front": "Straight-on front view, eye level, centered composition.",
    "side": "Side profile view, 90-degree angle, clean silhouette visible.",
    "45deg": "Three-quarter hero shot, 45-degree angle, dynamic and engaging perspective.",
    "top": "Top-down bird's eye view, overhead perspective, flat lay composition.",
    "perspective": "Dynamic low-angle perspective, dramatic hero shot with depth.",
    "back": "Rear view, showing back panel details and ports.",
}

# ─── 场景关键词库 ─────────────────────────────────────────────
SCENE_KEYWORDS = {
    "studio": "Pure white studio background, infinite curve backdrop, professional product photography setup.",
    "gradient": "Smooth gradient background from light gray to white, subtle shadow ground plane.",
    "lifestyle": "Natural lifestyle environment, warm ambient lighting, contextual real-world setting showing product in use.",
    "dark": "Dark moody studio background, dramatic spot lighting, floating product visualization.",
    "exploded": "White background, exploded view showing all internal components separated and labeled.",
    "context": "Real-world usage context, environmental storytelling, user interaction scene.",
}

# ─── 渲染后缀 ─────────────────────────────────────────────────
RENDER_SUFFIX = (
    "Professional product photography, studio lighting setup with soft diffusion, "
    "photorealistic rendering, highly detailed surface textures, 8K quality, "
    "clean sharp focus, subtle shadows and reflections."
)

# ─── 中英文材质翻译 ─────────────────────────────────────────
MATERIAL_MAP = {
    "铝合金": "anodized aluminum",
    "不锈钢": "stainless steel",
    "钢化玻璃": "tempered glass",
    "硅胶": "silicone",
    "ABS塑料": "ABS plastic",
    "碳纤维": "carbon fiber",
    "皮革": "premium leather",
    "竹木": "natural bamboo",
    "木质": "natural wood",
    "塑料": "high-quality plastic",
    "陶瓷": "ceramic",
    "铜": "brushed copper",
    "钛合金": "titanium alloy",
    "织物": "premium fabric",
    "橡胶": "soft-touch rubber",
    "树脂": "resin",
    "亚克力": "acrylic",
}

COLOR_MAP = {
    "黑色": "matte black",
    "白色": "pure white",
    "太空灰": "space gray",
    "银色": "silver metallic",
    "玫瑰金": "rose gold",
    "金色": "champagne gold",
    "红色": "crimson red",
    "蓝色": "navy blue",
    "午夜蓝": "midnight blue",
    "绿色": "forest green",
    "薄荷绿": "mint green",
    "象牙白": "ivory white",
    "米色": "beige",
    "橙色": "tangerine orange",
    "粉色": "blush pink",
    "紫色": "royal purple",
    "大地色": "earth tone brown",
    "哑光": "matte finish",
    "亮面": "glossy finish",
    "磨砂": "frosted satin finish",
}


def translate(text: str, mapping: dict) -> str:
    """翻译中文术语到英文"""
    result = text
    for cn, en in mapping.items():
        result = result.replace(cn, en)
    return result


def build_subject_block(product: dict) -> str:
    """构建产品主体描述"""
    name = product.get("product_name") or product.get("product", "product")

    # Features
    features = product.get("features", [])
    feat_str = ""
    if features:
        feat_list = features[:3]  # max 3
        feat_str = " with " + ", ".join(feat_list)

    # Materials
    materials = product.get("materials", [])
    mat_str = ""
    if materials:
        translated = [translate(m, MATERIAL_MAP) for m in materials]
        mat_str = f" Made of {' and '.join(translated)}."

    return f"A {name}{feat_str}.{mat_str}"


def build_color_clause(color: str) -> str:
    """构建颜色描述"""
    translated = translate(color, COLOR_MAP)
    return f"In {translated} finish."


def build_full_prompt(
    product: dict,
    color: str,
    style_id: str,
    angle_id: str,
    scene_id: str,
) -> str:
    """组装完整 Prompt"""
    parts = [
        build_subject_block(product),
        build_color_clause(color),
        STYLE_KEYWORDS.get(style_id, STYLE_KEYWORDS["minimal"]),
        ANGLE_KEYWORDS.get(angle_id, ANGLE_KEYWORDS["45deg"]),
        SCENE_KEYWORDS.get(scene_id, SCENE_KEYWORDS["studio"]),
        RENDER_SUFFIX,
    ]
    return " ".join(parts)


def get_aspect_for_angle(angle_id: str) -> str:
    """根据角度推荐比例"""
    mapping = {
        "front": "4:5",
        "side": "4:5",
        "45deg": "4:3",
        "top": "1:1",
        "perspective": "3:2",
        "back": "4:5",
    }
    return mapping.get(angle_id, "4:3")


def build_prompt_matrix(product: dict, config: dict) -> list:
    """构建 Prompt 矩阵"""
    styles = config.get("styles", ["minimal"])
    angles = config.get("angles", ["45deg"])
    scenes = config.get("scenes", ["studio"])
    colors = config.get("colors", product.get("colors", ["white"]))
    max_images = config.get("max_images", 20)
    resolution = config.get("resolution", "2K")
    output_format = config.get("output_format", "jpg")

    # Translate colors
    if not colors:
        colors = ["white"]

    prompts = []

    # Strategy: prioritize variety
    # 1. All styles with main angle (45deg) and first color
    for style in styles:
        prompt = build_full_prompt(product, colors[0], style, angles[0], scenes[0])
        prompts.append({
            "prompt": prompt,
            "label": f"style_{style}_{angles[0]}_{translate(colors[0], COLOR_MAP).replace(' ', '_')}",
            "group": f"style_{style}",
            "aspect_ratio": get_aspect_for_angle(angles[0]),
            "resolution": resolution,
            "output_format": output_format,
            "meta": {"style": style, "angle": angles[0], "color": colors[0], "scene": scenes[0]},
        })

    # 2. All angles with main style and first color
    for angle in angles:
        if angle == angles[0] and len(styles) > 0:
            continue  # Already covered
        prompt = build_full_prompt(product, colors[0], styles[0], angle, scenes[0])
        prompts.append({
            "prompt": prompt,
            "label": f"angle_{angle}_{styles[0]}_{translate(colors[0], COLOR_MAP).replace(' ', '_')}",
            "group": "angle_variants",
            "aspect_ratio": get_aspect_for_angle(angle),
            "resolution": resolution,
            "output_format": output_format,
            "meta": {"style": styles[0], "angle": angle, "color": colors[0], "scene": scenes[0]},
        })

    # 3. Color variants with main style + main angle
    for color in colors[1:]:
        prompt = build_full_prompt(product, color, styles[0], angles[0], scenes[0])
        prompts.append({
            "prompt": prompt,
            "label": f"color_{translate(color, COLOR_MAP).replace(' ', '_')}_{styles[0]}_{angles[0]}",
            "group": "color_variants",
            "aspect_ratio": get_aspect_for_angle(angles[0]),
            "resolution": resolution,
            "output_format": output_format,
            "meta": {"style": styles[0], "angle": angles[0], "color": color, "scene": scenes[0]},
        })

    # 4. Scene variants with main style + main angle + first color
    for scene in scenes[1:]:
        prompt = build_full_prompt(product, colors[0], styles[0], angles[0], scene)
        prompts.append({
            "prompt": prompt,
            "label": f"scene_{scene}_{styles[0]}_{angles[0]}",
            "group": "scene_variants",
            "aspect_ratio": "16:9" if scene in ("lifestyle", "context") else get_aspect_for_angle(angles[0]),
            "resolution": resolution,
            "output_format": output_format,
            "meta": {"style": styles[0], "angle": angles[0], "color": colors[0], "scene": scene},
        })

    # Trim to max
    if len(prompts) > max_images:
        print(f"[INFO] Trimmed from {len(prompts)} to {max_images} prompts", file=sys.stderr)
        prompts = prompts[:max_images]

    return prompts


def main():
    parser = argparse.ArgumentParser(description="Build prompt matrix from product definition")
    parser.add_argument("--input", required=True, help="Product definition JSON file")
    parser.add_argument("--output", default="output/prompts.json", help="Output prompts.json path")
    parser.add_argument("--styles", default="minimal,industrial,futuristic",
                        help="Comma-separated style IDs")
    parser.add_argument("--angles", default="45deg,front,side",
                        help="Comma-separated angle IDs")
    parser.add_argument("--scenes", default="studio,lifestyle",
                        help="Comma-separated scene IDs")
    parser.add_argument("--colors", default=None,
                        help="Override colors (comma-separated)")
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])
    parser.add_argument("--format", default="jpg", choices=["jpg", "png"])
    parser.add_argument("--max-images", type=int, default=20)
    args = parser.parse_args()

    # Load product definition
    with open(args.input, "r", encoding="utf-8") as f:
        product = json.load(f)

    config = {
        "styles": [s.strip() for s in args.styles.split(",")],
        "angles": [a.strip() for a in args.angles.split(",")],
        "scenes": [s.strip() for s in args.scenes.split(",")],
        "resolution": args.resolution,
        "output_format": args.format,
        "max_images": args.max_images,
    }
    if args.colors:
        config["colors"] = [c.strip() for c in args.colors.split(",")]

    prompts = build_prompt_matrix(product, config)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"prompts": prompts, "product": product, "config": config},
                  f, ensure_ascii=False, indent=2)

    print(f"generated: {len(prompts)} prompts -> {output_path}")
    for i, p in enumerate(prompts):
        print(f"  [{i+1}] {p['label']}  ({p['group']})  ratio={p['aspect_ratio']}")


if __name__ == "__main__":
    main()
