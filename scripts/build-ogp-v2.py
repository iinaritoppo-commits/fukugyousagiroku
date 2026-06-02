#!/usr/bin/env python3
"""
副業詐欺録 OGPサムネ v2: テンプレを背景として薄く残し、新テキストを主役に
"""
import json, glob, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

ROOT = Path("/Users/toppo/マイファイル/副業詐欺録")
OGP_DIR = ROOT / "public" / "ogp"
OUT_DIR = ROOT / "public" / "ogp"
FONT_PATH = "/System/Library/Fonts/Hiragino Sans GB.ttc"

# 3カテゴリのChatGPT派手版テンプレ
TEMPLATES = {
    "joho": Image.open(OGP_DIR / "fukugyo-joho-001.png").convert("RGB").resize((1200, 630), Image.LANCZOS),
    "ai": Image.open(OGP_DIR / "fukugyo-ai-001.png").convert("RGB").resize((1200, 630), Image.LANCZOS),
    "mlm": Image.open(OGP_DIR / "fukugyo-mlm-001.png").convert("RGB").resize((1200, 630), Image.LANCZOS),
}

CAT_TO_TPL = {
    "joho": "joho", "coach": "joho", "busshu": "joho",
    "ai": "ai", "overseas": "ai",
    "mlm": "mlm", "invest": "mlm", "romance": "mlm",
}


def short_scheme(scheme: str) -> str:
    s = scheme.split("（")[0].split("(")[0].strip()
    if len(s) > 14:
        s = s[:14] + "…"
    if not s.endswith("詐欺"):
        s += "詐欺"
    return s


def draw_outline(draw, text, pos, font, fill, outline, stroke=4):
    x, y = pos
    for dx in range(-stroke, stroke + 1):
        for dy in range(-stroke, stroke + 1):
            if dx * dx + dy * dy <= stroke * stroke:
                draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)


def build(article):
    cat = article["category"]
    tpl_key = CAT_TO_TPL[cat]
    img = TEMPLATES[tpl_key].copy()

    # 全体に半透明黒紫オーバーレイ（元テキストを薄める）
    overlay = Image.new("RGBA", (1200, 630), (5, 8, 25, 195))  # alpha 195/255
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    # 暗くしすぎないように、彩度＆コントラスト維持
    # Build text

    amount_man = article["loss_amount_yen"] // 10000
    amount_text = f"{amount_man}万円消えた"
    scheme_label = short_scheme(article["scheme"])

    # 金額：中央寄りに巨大に
    digits = "".join(c for c in str(amount_man) if c.isdigit())
    if len(digits) <= 2:
        size_amt = 130
    elif len(digits) == 3:
        size_amt = 110
    else:
        size_amt = 90
    font_amt = ImageFont.truetype(FONT_PATH, size_amt)
    bbox = draw.textbbox((0, 0), amount_text, font=font_amt)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    # Center horizontally, position vertically ~30% from top
    ax = (1200 - tw) // 2
    ay = 95
    draw_outline(draw, amount_text, (ax, ay), font_amt,
                 fill=(255, 255, 255), outline=(200, 30, 30), stroke=5)

    # スキーム：中央下
    if len(scheme_label) <= 8:
        size_sc = 56
    elif len(scheme_label) <= 12:
        size_sc = 48
    elif len(scheme_label) <= 16:
        size_sc = 40
    else:
        size_sc = 34
    font_sc = ImageFont.truetype(FONT_PATH, size_sc)
    bbox = draw.textbbox((0, 0), scheme_label, font=font_sc)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    sx = (1200 - tw) // 2
    sy = ay + size_amt + 30
    draw_outline(draw, scheme_label, (sx, sy), font_sc,
                 fill=(255, 220, 30), outline=(15, 10, 5), stroke=3)

    # 警告ピル（左上）
    warn_text = "⚠ 警告"
    font_warn = ImageFont.truetype(FONT_PATH, 32)
    # red round rect
    wx, wy = 28, 28
    bbox = draw.textbbox((0, 0), warn_text, font=font_warn)
    ww, wh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = 12
    # rounded rectangle approximation
    draw.rectangle([wx, wy, wx + ww + pad * 2, wy + wh + pad * 2 - 4], fill=(180, 30, 30))
    draw.text((wx + pad, wy + pad - 6), warn_text, font=font_warn, fill=(255, 255, 255))

    # 「これが詐欺の手口」キャッチ（左下）
    catch_text = "これが詐欺の手口"
    font_catch = ImageFont.truetype(FONT_PATH, 44)
    bbox = draw.textbbox((0, 0), catch_text, font=font_catch)
    cw, chh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    cx = 36
    cy = 630 - chh - 50
    draw_outline(draw, catch_text, (cx, cy), font_catch,
                 fill=(255, 255, 255), outline=(180, 25, 25), stroke=3)

    return img


def main():
    drafts = sorted(glob.glob(str(ROOT / "approved" / "draft-*.json")))
    print(f"Found {len(drafts)} drafts")
    count = 0
    for jf in drafts:
        a = json.load(open(jf))
        if not all(k in a for k in ("slug", "loss_amount_yen", "scheme", "category")):
            continue
        img = build(a)
        out = OUT_DIR / f"{a['slug']}.png"
        img.save(out, optimize=True)
        count += 1
        print(f"  ✓ {a['slug']} ({a['loss_amount_yen']//10000}万) tpl={CAT_TO_TPL[a['category']]}")

    # og-default
    img = TEMPLATES["joho"].copy()
    img.save(OUT_DIR / "og-default.png", optimize=True)
    print(f"\nGenerated {count} OGP thumbnails")


if __name__ == "__main__":
    main()
