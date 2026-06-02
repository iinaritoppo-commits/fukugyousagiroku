#!/usr/bin/env python3
"""
副業詐欺録 OGP サムネ：週刊文春・FRIDAY 告発系
マスタード黄 × 黒 × 赤、煽り感のある告発誌スタイル
1200x630
"""
import json, glob, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/toppo/マイファイル/副業詐欺録")
OUT_DIR = ROOT / "public" / "ogp"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FONT_SERIF = "/System/Library/Fonts/Hiragino Mincho ProN.ttc"
FONT_SANS = "/System/Library/Fonts/Hiragino Sans GB.ttc"
if not os.path.exists(FONT_SERIF):
    FONT_SERIF = FONT_SANS

# 配色
BG = (243, 213, 74)        # マスタード黄
BG_HEAD = (15, 18, 28)     # 漆黒
INK = (20, 20, 20)         # 真っ黒
INK_SOFT = (60, 60, 60)    # 中濃グレー
RED = (200, 30, 30)        # 告発赤
WHITE = (255, 255, 248)    # 純白

CAT_LABEL = {
    "joho": "情報商材",
    "mlm": "MLM",
    "coach": "コンサル詐欺",
    "ai": "AI副業",
    "invest": "投資型副業",
    "romance": "ロマンス商法",
    "busshu": "物販系",
    "overseas": "海外案件",
}


def build(article: dict) -> Image.Image:
    img = Image.new("RGB", (1200, 630), BG)
    draw = ImageDraw.Draw(img)

    # 黒黄ストライプ枠（上下）
    stripe_h = 18
    for x in range(0, 1200, 30):
        draw.rectangle([x, 0, x + 15, stripe_h], fill=INK)
    for x in range(0, 1200, 30):
        draw.rectangle([x + 15, 612, x + 30, 630], fill=INK)

    # 上の黒帯（ロゴ）
    draw.rectangle([0, stripe_h, 1200, stripe_h + 50], fill=BG_HEAD)
    font_logo = ImageFont.truetype(FONT_SERIF, 26)
    draw.text((36, stripe_h + 10), "副業詐欺録", font=font_logo, fill=BG)
    # ラベル（右）
    font_brand = ImageFont.truetype(FONT_SANS, 14)
    label_en = "FUKUGYO SAGI ROKU ・ FRAUD RECORDS"
    bbox = draw.textbbox((0, 0), label_en, font=font_brand)
    draw.text((1200 - 36 - (bbox[2] - bbox[0]), stripe_h + 18), label_en, font=font_brand, fill=(243, 213, 74))

    # 告発バッジ（左上、ストライプ下）
    badge_text = "！ 告発"
    font_badge = ImageFont.truetype(FONT_SANS, 28)
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bx, by = 64, 110
    pad_x, pad_y = 18, 10
    draw.rectangle([bx, by, bx + bw + pad_x * 2, by + bh + pad_y * 2 - 4], fill=RED)
    draw.text((bx + pad_x, by + pad_y - 6), badge_text, font=font_badge, fill=WHITE)

    # カテゴリラベル（バッジ右隣）
    cat_key = article.get("category", "")
    cat_text = CAT_LABEL.get(cat_key, cat_key)
    font_cat = ImageFont.truetype(FONT_SANS, 22)
    bbox_c = draw.textbbox((0, 0), cat_text, font=font_cat)
    cw, ch = bbox_c[2] - bbox_c[0], bbox_c[3] - bbox_c[1]
    cx = bx + bw + pad_x * 2 + 14
    cy = by + 4
    pad_x2, pad_y2 = 14, 8
    draw.rectangle([cx, cy, cx + cw + pad_x2 * 2, cy + ch + pad_y2 * 2 - 4], fill=INK)
    draw.text((cx + pad_x2, cy + pad_y2 - 4), cat_text, font=font_cat, fill=BG)

    # 金額（中央大）
    loss_yen = article.get("loss_amount_yen", 0)
    amount_man = loss_yen // 10000
    amount_text = f"{amount_man:,}万円消えた"
    digits = len(str(amount_man))
    if digits <= 2:
        amt_size = 140
    elif digits == 3:
        amt_size = 120
    elif digits == 4:
        amt_size = 100
    else:
        amt_size = 88
    font_amt = ImageFont.truetype(FONT_SERIF, amt_size)
    bbox = draw.textbbox((0, 0), amount_text, font=font_amt)
    aw = bbox[2] - bbox[0]
    ax = (1200 - aw) // 2
    ay = 200
    # 影
    for off in [(3, 3), (2, 2)]:
        draw.text((ax + off[0], ay + off[1]), amount_text, font=font_amt, fill=(60, 50, 0))
    draw.text((ax, ay), amount_text, font=font_amt, fill=INK)

    # サブタイトル：スキーム短縮
    scheme = article.get("scheme", "")
    s = scheme.split("（")[0].split("(")[0].strip()
    if len(s) > 22:
        s = s[:22] + "…"
    if not s.endswith("詐欺"):
        s += "詐欺"
    font_sc = ImageFont.truetype(FONT_SERIF, 38)
    bbox = draw.textbbox((0, 0), s, font=font_sc)
    sw = bbox[2] - bbox[0]
    sx = (1200 - sw) // 2
    sy = ay + amt_size + 24
    # 赤角丸下線
    draw.rectangle([sx - 14, sy + 50, sx + sw + 14, sy + 56], fill=RED)
    draw.text((sx, sy), s, font=font_sc, fill=INK)

    # 下帯（黒）
    draw.rectangle([0, 562, 1200, 612], fill=BG_HEAD)
    font_meta = ImageFont.truetype(FONT_SANS, 16)
    draw.text((36, 580), "FUKUGYOUSAGIROKU.PAGES.DEV", font=font_meta, fill=BG)
    p = article.get("persona", {})
    age = p.get("age", "")
    gender = p.get("gender", "")
    pref = p.get("prefecture", "")
    meta_right = f"{age}歳 {gender} ・ {pref} の話"
    bbox = draw.textbbox((0, 0), meta_right, font=font_meta)
    draw.text((1200 - 36 - (bbox[2] - bbox[0]), 580), meta_right, font=font_meta, fill=BG)

    return img


def main():
    drafts = sorted(glob.glob(str(ROOT / "approved" / "draft-*.json")))
    print(f"Found {len(drafts)} drafts")
    count = 0
    for jf in drafts:
        try:
            a = json.load(open(jf))
        except Exception as e:
            print(f"  skip {jf}: {e}")
            continue
        if not all(k in a for k in ("slug", "loss_amount_yen", "scheme", "category")):
            print(f"  skip {a.get('slug', jf)} (missing fields)")
            continue
        img = build(a)
        out = OUT_DIR / f"{a['slug']}.png"
        img.save(out, optimize=True)
        count += 1
        print(f"  ✓ {a['slug']} ({a['loss_amount_yen']//10000}万)")

    # デフォルト
    img = Image.new("RGB", (1200, 630), BG)
    draw = ImageDraw.Draw(img)
    # ストライプ
    stripe_h = 18
    for x in range(0, 1200, 30):
        draw.rectangle([x, 0, x + 15, stripe_h], fill=INK)
    for x in range(0, 1200, 30):
        draw.rectangle([x + 15, 612, x + 30, 630], fill=INK)
    draw.rectangle([0, stripe_h, 1200, stripe_h + 50], fill=BG_HEAD)
    font_logo = ImageFont.truetype(FONT_SERIF, 28)
    draw.text((36, stripe_h + 10), "副業詐欺録", font=font_logo, fill=BG)
    font_h = ImageFont.truetype(FONT_SERIF, 78)
    draw.text((64, 180), "騙された話を、", font=font_h, fill=INK)
    draw.text((64, 280), "騙される前に。", font=font_h, fill=RED)
    font_sub = ImageFont.truetype(FONT_SANS, 22)
    draw.text((64, 410), "情報商材・MLM・AI副業・コンサル詐欺・ロマンス商法。実例の取材記録アーカイブ。", font=font_sub, fill=INK_SOFT)
    draw.rectangle([0, 562, 1200, 612], fill=BG_HEAD)
    font_meta = ImageFont.truetype(FONT_SANS, 16)
    draw.text((36, 580), "FUKUGYOUSAGIROKU.PAGES.DEV", font=font_meta, fill=BG)
    img.save(OUT_DIR / "og-default.png", optimize=True)
    print(f"  ✓ og-default.png")
    # public/og-default.png にもコピー
    img.save(ROOT / "public" / "og-default.png", optimize=True)
    print(f"\nGenerated {count + 1} OGP thumbnails")


if __name__ == "__main__":
    main()
