#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事案アーカイブ記事専用 OGP生成
被害額表示ではなく「会社名・処分年・スキーム名」を主役に
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/toppo/マイファイル/副業詐欺録")
OGP = ROOT / "public" / "ogp"
W, H = 1200, 630

BG = (252, 249, 241)
BAND = (175, 30, 30)
INK = (28, 30, 38)
RED = (175, 30, 30)
GOLD = (200, 158, 76)
SUB = (90, 95, 110)
GRAY = (140, 145, 158)

# Try Hiragino, fallback to system fonts
def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc" if bold else "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    return ImageFont.load_default()


# 事案アーカイブ記事ごとのサムネ定義
JIREI = {
    "fukugyo-jirei-001": {
        "category_label": "事案アーカイブ",
        "stamp_top": "ARCHIVE",
        "stamp_bottom": "預託商法",
        "title_main": "ジャパンライフ社",
        "subtitle_top": "「磁気治療器のレンタルオーナー」と謳った",
        "subtitle_bot": "預託商法・約2,400億円規模の経営破綻事案",
        "footer_left": "1975年創業 ・ 2017年12月 経営破綻 ・ 元会長逮捕",
        "footer_right": "FUKUGYOUSAGIROKU.PAGES.DEV",
    }
}


def measure(draw, text, fnt):
    bb = draw.textbbox((0, 0), text, font=fnt)
    return bb[2] - bb[0], bb[3] - bb[1]


def draw_one(slug, d):
    im = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(im)

    # top band (deep red)
    dr.rectangle([0, 0, W, 75], fill=BAND)
    f_brand = font(28, bold=True)
    f_brand_sub = font(15)
    dr.text((30, 18), "副業詐欺録", font=f_brand, fill=(255, 248, 232))
    dr.text((175, 25), "実話・副業詐欺事例アーカイブ", font=f_brand_sub, fill=(255, 240, 215))
    f_right = font(13)
    dr.text((W - 200, 18), "調査・記録・告発", font=f_right, fill=(255, 240, 215))
    dr.text((W - 200, 38), "FUKUGYO SAGI ROKU", font=f_right, fill=(255, 240, 215))

    # category pill
    cat_label = d["category_label"]
    f_cat = font(20, bold=True)
    cw, ch = measure(dr, cat_label, f_cat)
    pad_x, pad_y = 14, 8
    pill_w = cw + pad_x * 2
    dr.rectangle([30, 110, 30 + pill_w, 110 + ch + pad_y * 2], fill=BAND)
    dr.text((30 + pad_x, 110 + pad_y - 2), cat_label, font=f_cat, fill=(255, 248, 232))

    # WARNING stamp (top-right circle)
    cx, cy, cr = W - 130, 195, 78
    for r_off in range(3):
        dr.ellipse([cx - cr + r_off, cy - cr + r_off, cx + cr - r_off, cy + cr - r_off],
                   outline=BAND, width=2)
    f_warn = font(15, bold=True)
    f_warn_sub = font(20, bold=True)
    ww, wh = measure(dr, d["stamp_top"], f_warn)
    dr.text((cx - ww // 2, cy - 38), d["stamp_top"], font=f_warn, fill=BAND)
    sw, sh = measure(dr, d["stamp_bottom"], f_warn_sub)
    dr.text((cx - sw // 2, cy - 5), d["stamp_bottom"], font=f_warn_sub, fill=BAND)

    # subtitle top
    f_sub_top = font(20)
    dr.text((30, 165), d["subtitle_top"], font=f_sub_top, fill=SUB)

    # main title (社名) - 大文字
    f_main = font(78, bold=True)
    mw, mh = measure(dr, d["title_main"], f_main)
    main_x = 30
    main_y = 220
    dr.text((main_x, main_y), d["title_main"], font=f_main, fill=INK)

    # gold underline
    dr.rectangle([main_x, main_y + mh + 10, main_x + 700, main_y + mh + 14], fill=GOLD)

    # subtitle bottom
    f_sub_bot = font(22, bold=True)
    dr.text((30, main_y + mh + 30), d["subtitle_bot"], font=f_sub_bot, fill=INK)

    # bottom footer line
    dr.line([(30, H - 50), (W - 30, H - 50)], fill=(210, 200, 175), width=1)
    f_foot = font(15)
    dr.text((30, H - 35), d["footer_left"], font=f_foot, fill=SUB)
    fw, fh = measure(dr, d["footer_right"], f_foot)
    dr.text((W - 30 - fw, H - 35), d["footer_right"], font=f_foot, fill=BAND)

    out = OGP / f"{slug}.png"
    im.save(out, "PNG", optimize=True)
    print(f"  ✓ {out.name}")


for slug, d in JIREI.items():
    draw_one(slug, d)

print(f"\n生成: {len(JIREI)}枚")
