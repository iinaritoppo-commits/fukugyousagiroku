#!/usr/bin/env python3
"""
副業詐欺録 OGP プレミアム版v2：明るいオフホワイト基調・AdSense適合
週刊文春・FRIDAY風だが「明るい告発誌」に転換
1200x630
"""
import json, glob, os, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/toppo/マイファイル/副業詐欺録")
OUT_DIR = ROOT / "public" / "ogp"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_MINCHO = "/System/Library/Fonts/Hiragino Mincho ProN.ttc"
FONT_SANS = "/System/Library/Fonts/Hiragino Sans GB.ttc"
if not os.path.exists(FONT_MINCHO):
    FONT_MINCHO = FONT_SANS

# 配色（明るいオフホワイト基調・AdSense対応）
BG = (252, 249, 241)            # オフホワイト（紙色）
BG_SOFT = (245, 240, 228)       # 薄ベージュ
BG_BAND = (175, 30, 30)         # 深紅帯（告発色）
BG_BAND_DARK = (140, 22, 22)    # より深い赤
INK = (28, 30, 38)              # 墨色
INK_SOFT = (74, 80, 92)         # 中濃グレー
INK_DIM = (130, 134, 144)       # 薄グレー
RED = (175, 30, 30)             # メイン赤
GOLD = (200, 158, 76)           # 金（高級感）
LINE = (216, 208, 188)          # 薄線

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

CAT_TRAP = {
    "joho": "情報商材の罠",
    "mlm": "連鎖販売の罠",
    "coach": "高額コーチング",
    "ai": "AI副業の幻想",
    "invest": "投資型副業",
    "romance": "ロマンス商法",
    "busshu": "物販スクール",
    "overseas": "海外案件",
}

CAT_PRE_HEAD = {
    "joho": "「コピペで稼げる」を信じた先にあった現実",
    "mlm": "「友人にも勧めれば月収倍増」の末路",
    "coach": "「人生が変わる」と言われた先",
    "ai": "「AIで自動収益」を信じた末路",
    "invest": "「副業として安全な投資」を信じた先",
    "romance": "「あなたを信じている」と言われた先",
    "busshu": "「主婦の副収入で月20万」の現実",
    "overseas": "「海外輸入で月100万」の末路",
}

CAT_SUB_CATCH = {
    "joho": "気づけば、口座も信頼も、消えた。",
    "mlm": "友人も、貯金も、消えた。",
    "coach": "コーチは消え、私だけが残った。",
    "ai": "提供物は、誰でも作れるものだった。",
    "invest": "「副業」の名は、ただの言い換えだった。",
    "romance": "信じた相手は、別人の写真だった。",
    "busshu": "倉庫に残ったのは、売れない商品の山。",
    "overseas": "関税と返品が、利益を全部食った。",
}


def short_scheme(scheme: str) -> str:
    s = scheme.split("（")[0].split("(")[0].strip()
    if len(s) > 22:
        s = s[:22] + "…"
    if not s.endswith("詐欺"):
        s += "詐欺"
    return s


def text_size(draw, txt, font):
    bbox = draw.textbbox((0, 0), txt, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def build(article: dict) -> Image.Image:
    img = Image.new("RGB", (1200, 630), BG)
    draw = ImageDraw.Draw(img)

    # 紙質感の極薄ノイズ
    random.seed(hash(article.get("slug", "x")) % 10000)
    for _ in range(400):
        x = random.randint(0, 1199)
        y = random.randint(72, 568)
        v = random.randint(238, 248)
        draw.point((x, y), fill=(v, v - 2, v - 8))

    # ===== 上の赤帯（高さ72） =====
    draw.rectangle([0, 0, 1200, 72], fill=BG_BAND)
    draw.rectangle([0, 70, 1200, 72], fill=BG_BAND_DARK)
    # ロゴ「副業詐欺録」白大文字
    font_logo = ImageFont.truetype(FONT_MINCHO, 36)
    draw.text((40, 16), "副業詐欺録", font=font_logo, fill=(252, 249, 241))
    # サブラベル
    font_sub_label = ImageFont.truetype(FONT_SANS, 13)
    draw.text((230, 30), "実話・副業詐欺事例アーカイブ", font=font_sub_label, fill=(255, 235, 220))
    # 右側ラベル
    label_right_l1 = "調査・記録・告発"
    label_right_l2 = "FUKUGYO SAGI ROKU"
    bbox = draw.textbbox((0, 0), label_right_l2, font=font_sub_label)
    draw.text((1200 - 40 - (bbox[2] - bbox[0]), 20), label_right_l1, font=font_sub_label, fill=(255, 235, 220))
    draw.text((1200 - 40 - (bbox[2] - bbox[0]), 40), label_right_l2, font=font_sub_label, fill=(255, 235, 220))

    # ===== 金線（赤帯の下） =====
    draw.rectangle([0, 76, 1200, 78], fill=GOLD)

    # ===== カテゴリpill（左、赤背景白文字、AdSense好む） =====
    cat_key = article.get("category", "")
    cat_text = CAT_LABEL.get(cat_key, cat_key)
    font_cat = ImageFont.truetype(FONT_SANS, 15)
    pad_x, pad_y = 16, 8
    bbox = draw.textbbox((0, 0), cat_text, font=font_cat)
    cw, ch = bbox[2] - bbox[0], bbox[3] - bbox[1]
    cx0, cy0 = 64, 108
    draw.rectangle([cx0, cy0, cx0 + cw + pad_x * 2, cy0 + ch + pad_y * 2 - 2], fill=RED)
    draw.text((cx0 + pad_x, cy0 + pad_y - 4), cat_text, font=font_cat, fill=(252, 249, 241))

    # ===== プリヘッド（明朝・墨色） =====
    pre_head = CAT_PRE_HEAD.get(cat_key, "「これは投資ではない」と言われた先")
    font_pre = ImageFont.truetype(FONT_MINCHO, 24)
    pw, ph = text_size(draw, pre_head, font_pre)
    pre_x = 64
    pre_y = 162
    draw.text((pre_x, pre_y), pre_head, font=font_pre, fill=INK)

    # ===== 巨大数字「○○万円」（明朝・墨色・極大） =====
    loss_yen = article.get("loss_amount_yen", 0)
    amount_man = loss_yen // 10000
    amount_text = f"{amount_man:,}万円"
    digits = len(str(amount_man))
    if digits <= 2:
        amt_size = 196
    elif digits == 3:
        amt_size = 164
    elif digits == 4:
        amt_size = 136
    else:
        amt_size = 116
    font_amt = ImageFont.truetype(FONT_MINCHO, amt_size)
    amt_y = pre_y + ph + 24
    draw.text((pre_x, amt_y), amount_text, font=font_amt, fill=INK)

    # 赤太線（金額の下）
    aw, ah = text_size(draw, amount_text, font_amt)
    line_y = amt_y + amt_size + 6
    draw.rectangle([pre_x, line_y, pre_x + min(aw, 720), line_y + 5], fill=RED)

    # ===== サブキャッチ =====
    sub = CAT_SUB_CATCH.get(cat_key, "信じた先に、何もなかった。")
    font_sub_main = ImageFont.truetype(FONT_MINCHO, 32)
    sub_y = line_y + 16
    draw.text((pre_x, sub_y), sub, font=font_sub_main, fill=INK_SOFT)

    # ===== 右上の白丸スタンプ「○○の罠」 =====
    trap = CAT_TRAP.get(cat_key, "投資型副業の罠")
    stamp_cx, stamp_cy = 1060, 192
    stamp_r = 70
    # 白丸（赤枠）
    draw.ellipse([stamp_cx - stamp_r - 3, stamp_cy - stamp_r - 3, stamp_cx + stamp_r + 3, stamp_cy + stamp_r + 3], fill=RED)
    draw.ellipse([stamp_cx - stamp_r, stamp_cy - stamp_r, stamp_cx + stamp_r, stamp_cy + stamp_r], fill=BG)
    draw.ellipse([stamp_cx - stamp_r + 8, stamp_cy - stamp_r + 8, stamp_cx + stamp_r - 8, stamp_cy + stamp_r - 8], outline=RED, width=2)
    # スタンプ内テキスト
    font_stamp_top = ImageFont.truetype(FONT_SANS, 11)
    font_stamp = ImageFont.truetype(FONT_MINCHO, 19)
    top_label = "WARNING"
    tw, th = text_size(draw, top_label, font_stamp_top)
    draw.text((stamp_cx - tw // 2, stamp_cy - 38), top_label, font=font_stamp_top, fill=RED)
    # メインテキスト（改行検討）
    if len(trap) > 6:
        trap_l1 = trap[: len(trap) // 2 + (1 if len(trap) % 2 else 0)]
        trap_l2 = trap[len(trap) // 2 + (1 if len(trap) % 2 else 0):]
    else:
        trap_l1 = trap
        trap_l2 = ""
    w1, h1 = text_size(draw, trap_l1, font_stamp)
    draw.text((stamp_cx - w1 // 2, stamp_cy - 14), trap_l1, font=font_stamp, fill=INK)
    if trap_l2:
        w2, h2 = text_size(draw, trap_l2, font_stamp)
        draw.text((stamp_cx - w2 // 2, stamp_cy + 14), trap_l2, font=font_stamp, fill=INK)

    # ===== 下帯（薄ベージュ） =====
    draw.rectangle([0, 564, 1200, 630], fill=BG_SOFT)
    draw.rectangle([0, 562, 1200, 564], fill=GOLD)
    # 下帯左：投稿者属性
    p = article.get("persona", {})
    age = p.get("age", "")
    gender = p.get("gender", "")
    occ = (p.get("occupation", "") or "").split("（")[0]
    pref = p.get("prefecture", "")
    parts = [s for s in [pref, f"{age}歳" if age else "", gender, occ] if s]
    meta_left = "  ・  ".join(parts)
    font_meta = ImageFont.truetype(FONT_SANS, 14)
    draw.text((40, 588), meta_left, font=font_meta, fill=INK_SOFT)
    # 下帯右：URL
    url = "FUKUGYOUSAGIROKU.PAGES.DEV"
    bbox = draw.textbbox((0, 0), url, font=font_meta)
    draw.text((1200 - 40 - (bbox[2] - bbox[0]), 588), url, font=font_meta, fill=INK_SOFT)

    return img


def main():
    drafts = sorted(glob.glob(str(ROOT / "approved" / "draft-*.json")))
    print(f"Found {len(drafts)} drafts")
    count = 0
    for jf in drafts:
        try:
            a = json.load(open(jf))
        except Exception as e:
            continue
        if not all(k in a for k in ("slug", "loss_amount_yen", "scheme", "category")):
            continue
        img = build(a)
        out = OUT_DIR / f"{a['slug']}.png"
        img.save(out, optimize=True)
        count += 1

    # og-default
    img = Image.new("RGB", (1200, 630), BG)
    draw = ImageDraw.Draw(img)
    random.seed(0)
    for _ in range(400):
        x = random.randint(0, 1199)
        y = random.randint(72, 568)
        v = random.randint(238, 248)
        draw.point((x, y), fill=(v, v - 2, v - 8))
    draw.rectangle([0, 0, 1200, 72], fill=BG_BAND)
    draw.rectangle([0, 70, 1200, 72], fill=BG_BAND_DARK)
    font_logo = ImageFont.truetype(FONT_MINCHO, 36)
    draw.text((40, 16), "副業詐欺録", font=font_logo, fill=(252, 249, 241))
    font_sub_label = ImageFont.truetype(FONT_SANS, 13)
    draw.text((230, 30), "実話・副業詐欺事例アーカイブ", font=font_sub_label, fill=(255, 235, 220))
    draw.rectangle([0, 76, 1200, 78], fill=GOLD)
    font_h_label = ImageFont.truetype(FONT_SANS, 14)
    draw.text((64, 128), "F R A U D   R E C O R D S", font=font_h_label, fill=RED)
    font_h = ImageFont.truetype(FONT_MINCHO, 88)
    draw.text((64, 168), "騙された話を、", font=font_h, fill=INK)
    draw.text((64, 278), "騙される前に。", font=font_h, fill=RED)
    draw.rectangle([64, 402, 220, 408], fill=RED)
    font_msg = ImageFont.truetype(FONT_SANS, 18)
    draw.text((64, 426), "情報商材・MLM・AI副業・コンサル詐欺・ロマンス商法。", font=font_msg, fill=INK_SOFT)
    draw.text((64, 452), "『楽に稼げる』の裏側で起きていた話を、ひとつずつ記録しています。", font=font_msg, fill=INK_SOFT)
    font_quote = ImageFont.truetype(FONT_MINCHO, 18)
    draw.text((64, 498), "─  怪しい話は、聞いてからじゃ遅い。  ─", font=font_quote, fill=INK_DIM)
    draw.rectangle([0, 564, 1200, 630], fill=BG_SOFT)
    draw.rectangle([0, 562, 1200, 564], fill=GOLD)
    font_meta = ImageFont.truetype(FONT_SANS, 14)
    draw.text((40, 588), "情報商材・MLM・AI副業・コンサル詐欺・ロマンス商法", font=font_meta, fill=INK_SOFT)
    url = "FUKUGYOUSAGIROKU.PAGES.DEV"
    bbox = draw.textbbox((0, 0), url, font=font_meta)
    draw.text((1200 - 40 - (bbox[2] - bbox[0]), 588), url, font=font_meta, fill=INK_SOFT)
    img.save(OUT_DIR / "og-default.png", optimize=True)
    img.save(ROOT / "public" / "og-default.png", optimize=True)
    print(f"\nGenerated {count + 1} OGP thumbnails (premium light edition)")


if __name__ == "__main__":
    main()
