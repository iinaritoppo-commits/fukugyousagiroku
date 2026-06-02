#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
副業詐欺録 サムネ刷新版（煽り系）
- 金額大表示は削除
- メイン：詐欺の煽りキャッチ（記事 trigger『〜』 or カテゴリ別テンプレ）
- 副：結末のひと言（→ 払ったのは◯万円、〜）
- 下部：カテゴリpill＋ペルソナ
- WARNINGスタンプ維持
"""
import json, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/toppo/マイファイル/副業詐欺録")
APPROVED = ROOT / "approved"
OGP = ROOT / "public" / "ogp"
OGP.mkdir(exist_ok=True)

W, H = 1200, 630

# 配色（モノクロ報道系・統一）
BG = (250, 250, 248)     # 純白オフホワイト
INK = (26, 26, 26)       # 印刷インク
RED = (200, 32, 28)      # 告発赤
GRAY_TXT = (90, 90, 90)
GRAY_LINE = (216, 216, 216)
GRAY_SUB = (140, 140, 140)


def font(size, weight="bold"):
    paths_bold = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    ]
    paths_normal = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    ]
    paths_serif = [
        "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc",
    ]
    candidates = paths_bold if weight == "bold" else paths_serif if weight == "serif" else paths_normal
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()


# カテゴリ別煽りキャッチのデフォルト
CAT_DEFAULT_CATCH = {
    "joho": "コピペで稼げる",
    "mlm": "使うほど増える",
    "coach": "3か月で起業して脱サラ",
    "ai": "AIで月◯万・完全自動",
    "invest": "月利◯%・元本保証",
    "romance": "あなたを信じている",
    "busshu": "主婦でも月◯万",
    "overseas": "海外で月◯万・誰でもできる",
}

CAT_LABEL = {
    "joho": "情報商材", "mlm": "MLM", "coach": "コンサル詐欺", "ai": "AI副業",
    "invest": "投資型副業", "romance": "ロマンス商法", "busshu": "物販系", "overseas": "海外案件",
}


def extract_catch(j):
    """記事JSONから煽りキャッチを抽出。trigger『〜』が最優先。
    『〜』内に・がある場合は、数字や煽りキーワードを含むパートを優先選出。"""
    trigger = j.get("trigger", "")
    AORI_KW = re.compile(r'[\d月万円％%]|コピペ|絶対|確実|保証|自動|月利|主婦|在宅|完結|スマホ|誰でも|簡単|安定|月収')

    m = re.search(r'[『「]([^』」]+)[』」]', trigger)
    if m:
        catch = m.group(1)
        # 短ければそのまま
        if len(catch) <= 18:
            return catch
        # 長い場合：・で分割して煽りキーワード含むパート優先
        if '・' in catch:
            parts = catch.split('・')
            # 煽りキーワードを最も多く含む短いパート優先
            scored = [(len(AORI_KW.findall(p)), -len(p), p) for p in parts if len(p) <= 18]
            scored.sort(reverse=True)
            if scored and scored[0][0] > 0:
                return scored[0][2]
            # キーワード無ければ最初のパート
            if parts and len(parts[0]) <= 18:
                return parts[0]
        # それでも長ければ前半を切る
        return catch[:16] + "…"

    # scheme から
    scheme = j.get("scheme", "")
    m = re.search(r'[『「]([^』」]+)[』」]', scheme)
    if m and len(m.group(1)) <= 18:
        return m.group(1)
    # カテゴリ別デフォルト
    cat = j.get("category", "joho")
    return CAT_DEFAULT_CATCH.get(cat, "稼げる副業の話")


def build_subline(j):
    """副コピー（結末）：→ 払ったのは◯万円、〜"""
    loss = j.get("loss_amount_yen", 0)
    if loss == 0:
        return ""
    if loss >= 1e8:
        amt = f"{loss/1e8:.1f}億円"
    elif loss >= 1e4:
        amt = f"{int(loss/1e4)}万円"
    else:
        amt = f"{loss:,}円"
    return f"払ったのは {amt}"


def measure(draw, text, fnt):
    bb = draw.textbbox((0, 0), text, font=fnt)
    return bb[2] - bb[0], bb[3] - bb[1]


def wrap_text(text, fnt, draw, max_w):
    """テキスト折り返し（日本語）"""
    lines = []
    current = ""
    for ch in text:
        w, _ = measure(draw, current + ch, fnt)
        if w > max_w and current:
            lines.append(current)
            current = ch
        else:
            current += ch
    if current:
        lines.append(current)
    return lines


def build_thumb(j):
    slug = j["slug"]
    cat = j.get("category", "joho")
    cat_label = CAT_LABEL.get(cat, cat)
    catch = extract_catch(j)
    subline = build_subline(j)
    persona = j.get("persona", {})
    age = persona.get("age", "")
    gender = persona.get("gender", "")
    pref = persona.get("prefecture", "")
    occupation = persona.get("occupation", "")
    if isinstance(occupation, str) and len(occupation) > 20:
        occupation = occupation[:18] + "…"

    im = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(im)

    # 上端赤帯
    dr.rectangle([0, 0, W, 6], fill=RED)

    # ブランドヘッダー
    f_brand = font(26, "serif")
    f_brand_sub = font(14)
    dr.text((36, 22), "副業詐欺録", font=f_brand, fill=INK)
    dr.text((180, 30), "実話・副業詐欺事例アーカイブ", font=f_brand_sub, fill=GRAY_TXT)
    # 右上：FUKUGYO SAGI ROKU
    f_brand_en = font(13)
    en_txt = "FUKUGYO SAGI ROKU"
    bw, _ = measure(dr, en_txt, f_brand_en)
    dr.text((W - 36 - bw, 28), en_txt, font=f_brand_en, fill=RED)

    # ヘッダー下罫線
    dr.line([(36, 72), (W - 36, 72)], fill=GRAY_LINE, width=1)

    # カテゴリpill（左上）
    f_cat = font(20)
    cw, ch = measure(dr, cat_label, f_cat)
    pad_x, pad_y = 14, 8
    pill_w = cw + pad_x * 2
    pill_h = ch + pad_y * 2 + 2
    dr.rectangle([36, 108, 36 + pill_w, 108 + pill_h], fill=INK)
    dr.text((36 + pad_x, 108 + pad_y - 2), cat_label, font=f_cat, fill=(255, 255, 255))

    # WARNING スタンプ（右上）
    cx, cy, cr = W - 130, 175, 78
    for r_off in range(3):
        dr.ellipse([cx - cr + r_off, cy - cr + r_off, cx + cr - r_off, cy + cr - r_off],
                   outline=RED, width=2)
    f_warn_top = font(14)
    f_warn_bot = font(18)
    ww, _ = measure(dr, "WARNING", f_warn_top)
    dr.text((cx - ww // 2, cy - 36), "WARNING", font=f_warn_top, fill=RED)
    wn, _ = measure(dr, cat_label, f_warn_bot)
    dr.text((cx - wn // 2, cy - 5), cat_label, font=f_warn_bot, fill=RED)

    # メインキャッチ（左寄せ・大文字・引用符付き）
    quoted = f"「{catch}」"
    # サイズ調整：長さに応じて
    if len(catch) <= 8:
        f_main_size = 90
    elif len(catch) <= 12:
        f_main_size = 76
    elif len(catch) <= 16:
        f_main_size = 64
    elif len(catch) <= 20:
        f_main_size = 54
    else:
        f_main_size = 46
    f_main = font(f_main_size, "serif")

    # 折り返し（最大幅 ~ W - 220 = 980）
    lines = wrap_text(quoted, f_main, dr, 920)
    # 最大2行に制限
    if len(lines) > 2:
        lines = lines[:2]
        # 最後の行に「…」付ける
        last = lines[-1]
        while True:
            w, _ = measure(dr, last + "…」", f_main)
            if w <= 920 or len(last) <= 5:
                lines[-1] = last + "…」"
                break
            last = last[:-1]

    # 描画開始位置（縦中央寄り）
    line_h = int(f_main_size * 1.15)
    total_h = line_h * len(lines)
    main_y_start = 220
    if len(lines) == 1:
        main_y_start = 250

    for i, line in enumerate(lines):
        dr.text((36, main_y_start + i * line_h), line, font=f_main, fill=INK)

    main_y_end = main_y_start + total_h

    # メイン下の金線
    dr.rectangle([36, main_y_end + 18, 36 + 480, main_y_end + 24], fill=RED)

    # 副コピー（結末・「→」付き）
    if subline:
        f_sub = font(28, "bold")
        dr.text((36, main_y_end + 48), f"→ {subline}", font=f_sub, fill=GRAY_TXT)

    # 下部罫線
    dr.line([(36, H - 60), (W - 36, H - 60)], fill=GRAY_LINE, width=1)

    # 下部：ペルソナ＋ドメイン
    f_persona = font(15)
    persona_txt = f"{pref} ・ {age}歳 ・ {gender}"
    if occupation:
        persona_txt += f" ・ {occupation}"
    dr.text((36, H - 38), persona_txt, font=f_persona, fill=GRAY_TXT)

    # 右下：ドメイン
    f_dom = font(13)
    dom = "FUKUGYOUSAGIROKU.COM"
    dw, _ = measure(dr, dom, f_dom)
    dr.text((W - 36 - dw, H - 36), dom, font=f_dom, fill=RED)

    out = OGP / f"{slug}.png"
    im.save(out, "PNG", optimize=True)


count = 0
for f in sorted(APPROVED.glob("draft-*.json")):
    try:
        j = json.loads(f.read_text(encoding="utf-8"))
        if not j.get("slug"): continue
        build_thumb(j)
        count += 1
    except Exception as e:
        print(f"  ✗ {f.name}: {e}")

print(f"\n生成: {count}枚")
