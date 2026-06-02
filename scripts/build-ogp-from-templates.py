#!/usr/bin/env python3
"""
副業詐欺録 OGPサムネ 41枚一括生成
ChatGPT派手版テンプレ3枚（joho/ai/mlm）を基に、カテゴリマッピングで41記事すべて生成。
金額（右上）とスキーム名（その下）だけPILで差し替え。
"""
import json, glob, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/toppo/マイファイル/副業詐欺録")
OGP_DIR = ROOT / "public" / "ogp"
OUT_DIR = ROOT / "public" / "ogp"
FONT_PATH = "/System/Library/Fonts/Hiragino Sans GB.ttc"

# テンプレ
TEMPLATES = {
    "joho": Image.open(OGP_DIR / "fukugyo-joho-001.png").convert("RGB").resize((1200, 630), Image.LANCZOS),
    "ai": Image.open(OGP_DIR / "fukugyo-ai-001.png").convert("RGB").resize((1200, 630), Image.LANCZOS),
    "mlm": Image.open(OGP_DIR / "fukugyo-mlm-001.png").convert("RGB").resize((1200, 630), Image.LANCZOS),
}

# カテゴリ→テンプレ
CAT_TO_TPL = {
    "joho": "joho",
    "ai": "ai",
    "mlm": "mlm",
    "coach": "joho",
    "invest": "mlm",
    "romance": "mlm",
    "busshu": "joho",
    "overseas": "ai",
}

# 既存のテンプレ画像で「金額」「スキーム」が描かれている領域 (resize後1200x630基準)
# 右上のテキスト領域全体（金額+スキーム名）
TEMPLATE_TEXT_AREA = {
    "joho": {"x1": 670, "y1": 0, "x2": 1200, "y2": 290},
    "ai": {"x1": 670, "y1": 0, "x2": 1200, "y2": 290},
    "mlm": {"x1": 670, "y1": 0, "x2": 1200, "y2": 290},
}


def short_scheme(scheme: str) -> str:
    s = scheme.split("（")[0].split("(")[0].strip()
    if len(s) > 14:
        s = s[:14] + "…"
    if not s.endswith("詐欺"):
        s += "詐欺"
    return s


def draw_text_with_outline(img, draw, text, pos, font, fill, outline, stroke=3):
    x, y = pos
    for dx in range(-stroke, stroke+1):
        for dy in range(-stroke, stroke+1):
            if dx*dx + dy*dy <= stroke*stroke:
                draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)


def build(article):
    cat = article["category"]
    tpl_key = CAT_TO_TPL[cat]
    img = TEMPLATES[tpl_key].copy()
    area = TEMPLATE_TEXT_AREA[tpl_key]
    draw = ImageDraw.Draw(img, "RGBA")

    # Step 1: マスク（右上の元金額・スキーム名を消す）
    # ダークネイビーグラデで覆う
    mx1, my1, mx2, my2 = area["x1"], area["y1"], area["x2"], area["y2"]
    grad = Image.new("RGB", (mx2 - mx1, my2 - my1), (0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for x in range(mx2 - mx1):
        ratio = x / (mx2 - mx1)
        r = int(22 - ratio * 12)
        g = int(28 - ratio * 18)
        b = int(45 - ratio * 25)
        gd.line([(x, 0), (x, my2 - my1)], fill=(r, g, b))
    img.paste(grad, (mx1, my1))
    # 下端ぼかし（背景となじむように）
    blend = Image.new("RGBA", (mx2 - mx1, 18), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blend)
    for y in range(18):
        bd.rectangle([0, y, mx2 - mx1, y + 1], fill=(0, 0, 0, 200 - y * 11))
    img.paste(blend, (mx1, my2 - 18), blend)
    draw = ImageDraw.Draw(img, "RGBA")

    # Step 2: 金額テキスト描画
    amount_man = article["loss_amount_yen"] // 10000
    amount_text = f"{amount_man}万円消えた"
    digits = "".join(c for c in str(amount_man) if c.isdigit())
    if len(digits) <= 2:
        size_amt = 80
    elif len(digits) == 3:
        size_amt = 68
    else:
        size_amt = 58
    font_amt = ImageFont.truetype(FONT_PATH, size_amt)
    bbox = draw.textbbox((0, 0), amount_text, font=font_amt)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    ax = mx1 + (mx2 - mx1 - tw) // 2
    ay = my1 + 8
    draw_text_with_outline(img, draw, amount_text, (ax, ay), font_amt,
                           fill=(255, 255, 255), outline=(200, 20, 20), stroke=4)

    # Step 3: スキーム名テキスト描画
    scheme_label = short_scheme(article["scheme"])
    if len(scheme_label) <= 8:
        size_sc = 44
    elif len(scheme_label) <= 12:
        size_sc = 36
    elif len(scheme_label) <= 16:
        size_sc = 30
    else:
        size_sc = 26
    font_sc = ImageFont.truetype(FONT_PATH, size_sc)
    bbox = draw.textbbox((0, 0), scheme_label, font=font_sc)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    sx = mx1 + (mx2 - mx1 - tw) // 2
    sy = ay + size_amt + 12
    draw_text_with_outline(img, draw, scheme_label, (sx, sy), font_sc,
                           fill=(255, 220, 30), outline=(20, 15, 5), stroke=2)

    return img


def main():
    drafts = sorted(glob.glob(str(ROOT / "approved" / "draft-*.json")))
    print(f"Found {len(drafts)} drafts")
    SKIP = {"fukugyo-joho-001", "fukugyo-ai-001", "fukugyo-mlm-001"}
    count = 0
    for jf in drafts:
        a = json.load(open(jf))
        if not all(k in a for k in ("slug", "loss_amount_yen", "scheme", "category")):
            continue
        if a["slug"] in SKIP:
            print(f"  skip {a['slug']} (existing ChatGPT original)")
            continue
        img = build(a)
        out = OUT_DIR / f"{a['slug']}.png"
        img.save(out, optimize=True)
        count += 1
        print(f"  ✓ {a['slug']} ({a['loss_amount_yen']//10000}万) tpl={CAT_TO_TPL[a['category']]}")
    # default
    default = TEMPLATES["joho"].copy()
    default.save(OUT_DIR / "og-default.png", optimize=True)
    print(f"  ✓ og-default.png")
    print(f"\nGenerated {count} thumbnails (3 original + {count} derived = {count+3} total)")


if __name__ == "__main__":
    main()
