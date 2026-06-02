#!/usr/bin/env python3
"""
副業詐欺録 OGPサムネ一括生成
ベース画像（ChatGPT生成・煽り系）に金額とスキーム名を後乗せ
"""
import json, glob, os, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path("/Users/toppo/マイファイル/副業詐欺録")
BASE_SRC = ROOT / "scripts" / "og-base.png"
OUT_DIR = ROOT / "public" / "ogp"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_PATH = "/System/Library/Fonts/Hiragino Sans GB.ttc"

# Resize base to 1200x630 once
BASE = Image.open(BASE_SRC).convert("RGB").resize((1200, 630), Image.LANCZOS)

# Categories → short fraud labels
CAT_LABEL = {
    "joho": "情報商材",
    "mlm": "MLMネズミ講",
    "coach": "高額コーチング",
    "ai": "AI副業情報商材",
    "invest": "投資型副業",
    "romance": "国際ロマンス",
    "busshu": "物販スクール",
    "overseas": "海外案件副業",
}


def format_amount(yen: int) -> str:
    man = yen // 10000
    return f"{man}万円消えた"


def short_scheme(scheme: str, category: str) -> str:
    # 「○○（…）」の前半だけ + 詐欺
    s = scheme.split("（")[0].split("(")[0].strip()
    if len(s) > 14:
        s = s[:14] + "…"
    if not s.endswith("詐欺"):
        s += "詐欺"
    return s


def draw_thumbnail(article: dict) -> Image.Image:
    img = BASE.copy()
    draw = ImageDraw.Draw(img, "RGBA")

    amount = format_amount(article["loss_amount_yen"])

    # ========== Combined mask covering BOTH original "45万円消えた" + "LINEコピー…詐欺" ==========
    # In resized 1200x630, original texts span (545-1200, 0-225)
    mx1, my1, mx2, my2 = 540, 0, 1200, 248
    grad = Image.new("RGB", (mx2 - mx1, my2 - my1), (0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for x in range(mx2 - mx1):
        ratio = x / (mx2 - mx1)
        r = int(35 - ratio * 28)
        g = int(8 - ratio * 5)
        b = int(48 - ratio * 38)
        gd.line([(x, 0), (x, my2 - my1)], fill=(r, g, b))
    img.paste(grad, (mx1, my1))
    # soft edge bottom (blend with surrounding scene)
    blend = Image.new("RGBA", (mx2 - mx1, 14), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blend)
    for y in range(14):
        bd.rectangle([0, y, mx2 - mx1, y + 1], fill=(0, 0, 0, 200 - y * 14))
    img.paste(blend, (mx1, my2 - 14), blend)
    draw = ImageDraw.Draw(img, "RGBA")

    # ========== Amount text (top half) ==========
    rx1, ry1, rx2, ry2 = mx1 + 5, 5, mx2 - 5, 138

    # Amount font: bold, red+white stroke
    # Size depends on digit length
    digits = "".join(c for c in amount if c.isdigit())
    if len(digits) <= 2:
        amt_size = 100
    elif len(digits) == 3:
        amt_size = 88
    else:
        amt_size = 76
    font_amt = ImageFont.truetype(FONT_PATH, amt_size)
    bbox = draw.textbbox((0, 0), amount, font=font_amt)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    ax = rx1 + (rx2 - rx1 - tw) // 2
    ay = ry1 + (ry2 - ry1 - th) // 2 - 8
    # white stroke + red fill
    for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
        draw.text((ax + dx, ay + dy), amount, font=font_amt, fill=(255, 255, 255))
    draw.text((ax, ay), amount, font=font_amt, fill=(220, 28, 28))

    # ========== Scheme name (bottom half of mask) ==========
    rx1, ry1, rx2, ry2 = mx1 + 5, 142, mx2 - 5, 222

    scheme_label = short_scheme(article["scheme"], article["category"])
    # font sizing
    if len(scheme_label) <= 8:
        sc_size = 48
    elif len(scheme_label) <= 12:
        sc_size = 40
    elif len(scheme_label) <= 16:
        sc_size = 34
    else:
        sc_size = 28
    font_sc = ImageFont.truetype(FONT_PATH, sc_size)
    bbox = draw.textbbox((0, 0), scheme_label, font=font_sc)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    sx = rx1 + (rx2 - rx1 - tw) // 2
    sy = ry1 + (ry2 - ry1 - th) // 2 - 4
    # yellow with black stroke
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
        draw.text((sx + dx, sy + dy), scheme_label, font=font_sc, fill=(0, 0, 0))
    draw.text((sx, sy), scheme_label, font=font_sc, fill=(255, 220, 30))

    return img


def main():
    drafts = sorted(glob.glob(str(ROOT / "approved" / "draft-*.json")))
    print(f"Found {len(drafts)} drafts")
    for jf in drafts:
        with open(jf) as f:
            article = json.load(f)
        if not all(k in article for k in ("slug", "loss_amount_yen", "scheme", "category")):
            print(f"  skip {os.path.basename(jf)} (missing fields)")
            continue
        img = draw_thumbnail(article)
        out = OUT_DIR / f"{article['slug']}.png"
        img.save(out, optimize=True)
        print(f"  ✓ {article['slug']} ({article['loss_amount_yen']//10000}万)")

    # also build og-default.png (homepage)
    default = BASE.copy()
    default.save(OUT_DIR / "og-default.png", optimize=True)
    print(f"  ✓ og-default.png")
    print(f"All written to {OUT_DIR}")


if __name__ == "__main__":
    main()
