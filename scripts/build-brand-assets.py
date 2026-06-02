#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
副業詐欺録 ブランドアセット生成
- favicon.svg / favicon.ico / favicon-32.png / apple-touch-icon.png
- og-default.png（1200x630・トップOGP）
- site-logo.svg（ヘッダー用）

デザイン：モノクロ報道系（白×黒×差し色赤）
シンボル：「副」文字の角印（赤背景×白文字）または「!」警告印
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/toppo/マイファイル/副業詐欺録")
PUBLIC = ROOT / "public"

RED = (200, 32, 28)        # アクセント赤
INK = (26, 26, 26)         # 印刷インク色
WHITE = (255, 255, 255)
PAPER = (250, 250, 248)    # 純白に近い
GRAY = (90, 90, 90)


def font(size, bold=True):
    candidates = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc" if bold else "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    ]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    return ImageFont.load_default()


def serif_font(size, bold=True):
    candidates = [
        "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
    ]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    return ImageFont.load_default()


# ============= favicon (512x512 角印「副」) =============
def build_favicon():
    sz = 512
    im = Image.new("RGB", (sz, sz), WHITE)
    dr = ImageDraw.Draw(im)
    # 赤背景の角印
    margin = 28
    dr.rectangle([margin, margin, sz - margin, sz - margin], fill=RED)
    # 内側の細い白枠
    dr.rectangle([margin + 18, margin + 18, sz - margin - 18, sz - margin - 18],
                 outline=WHITE, width=4)
    # 中央に「副」白文字
    f = serif_font(330)
    text = "副"
    bb = dr.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    dr.text((sz // 2 - tw // 2 - bb[0], sz // 2 - th // 2 - bb[1] - 18),
            text, font=f, fill=WHITE)

    # 各サイズ保存
    im.resize((32, 32), Image.LANCZOS).save(PUBLIC / "favicon-32.png", "PNG", optimize=True)
    im.resize((180, 180), Image.LANCZOS).save(PUBLIC / "apple-touch-icon.png", "PNG", optimize=True)
    im.resize((192, 192), Image.LANCZOS).save(PUBLIC / "icon-192.png", "PNG", optimize=True)
    im.resize((512, 512), Image.LANCZOS).save(PUBLIC / "icon-512.png", "PNG", optimize=True)

    # ICO（複数サイズ含む）
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    im.save(PUBLIC / "favicon.ico", format="ICO", sizes=ico_sizes)

    # SVG 版（簡易・スケーラブル）
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect x="28" y="28" width="456" height="456" fill="#c8201c"/>
  <rect x="46" y="46" width="420" height="420" fill="none" stroke="#fff" stroke-width="4"/>
  <text x="256" y="368" font-family="'Yu Mincho', 'Hiragino Mincho ProN', serif" font-size="330" font-weight="900" fill="#fff" text-anchor="middle">副</text>
</svg>
'''
    (PUBLIC / "favicon.svg").write_text(svg, encoding="utf-8")
    print("  ✓ favicon.ico / .svg / -32.png / apple-touch-icon.png / icon-192/512.png")


# ============= site-logo.svg（ヘッダー用：角印 + 「副業詐欺録」テキスト横並び） =============
def build_site_logo():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 64" aria-label="副業詐欺録">
  <!-- 角印（左） -->
  <g transform="translate(0,8)">
    <rect x="2" y="2" width="44" height="44" fill="#c8201c"/>
    <rect x="5" y="5" width="38" height="38" fill="none" stroke="#fff" stroke-width="1"/>
    <text x="24" y="37" font-family="'Yu Mincho', 'Hiragino Mincho ProN', serif" font-size="32" font-weight="900" fill="#fff" text-anchor="middle">副</text>
  </g>
  <!-- テキスト（右） -->
  <text x="60" y="38" font-family="'Yu Mincho', 'Hiragino Mincho ProN', serif" font-size="26" font-weight="900" fill="#1a1a1a" letter-spacing="2">副業詐欺録</text>
  <text x="60" y="54" font-family="'Yu Gothic', 'Hiragino Sans', sans-serif" font-size="7" fill="#c8201c" letter-spacing="3" font-weight="700">FUKUGYO SAGI ROKU</text>
</svg>
'''
    (PUBLIC / "site-logo.svg").write_text(svg, encoding="utf-8")
    print("  ✓ site-logo.svg")


# ============= og-default.png (1200x630・トップOGP) =============
def build_og_default():
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(im)
    # 上端赤帯
    dr.rectangle([0, 0, W, 8], fill=RED)
    # 中央：角印（大）+ サイト名
    seal_size = 220
    seal_x = (W - seal_size) // 2
    seal_y = 80
    dr.rectangle([seal_x, seal_y, seal_x + seal_size, seal_y + seal_size], fill=RED)
    dr.rectangle([seal_x + 12, seal_y + 12, seal_x + seal_size - 12, seal_y + seal_size - 12],
                 outline=WHITE, width=2)
    f_seal = serif_font(160)
    bb = dr.textbbox((0, 0), "副", font=f_seal)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    dr.text((W // 2 - tw // 2 - bb[0], seal_y + seal_size // 2 - th // 2 - bb[1] - 6),
            "副", font=f_seal, fill=WHITE)

    # サイト名
    f_title = serif_font(72)
    title = "副業詐欺録"
    bb = dr.textbbox((0, 0), title, font=f_title)
    tw = bb[2] - bb[0]
    dr.text((W // 2 - tw // 2, seal_y + seal_size + 28), title, font=f_title, fill=INK)

    # サブタイトル
    f_sub = font(28, bold=False)
    sub = "騙された話を、騙される前に。"
    bb = dr.textbbox((0, 0), sub, font=f_sub)
    tw = bb[2] - bb[0]
    dr.text((W // 2 - tw // 2, seal_y + seal_size + 110), sub, font=f_sub, fill=GRAY)

    # 下部英字
    f_en = font(18, bold=True)
    en = "FUKUGYO SAGI ROKU  ・  FRAUD RECORDS"
    bb = dr.textbbox((0, 0), en, font=f_en)
    tw = bb[2] - bb[0]
    dr.text((W // 2 - tw // 2, H - 50), en, font=f_en, fill=RED)

    im.save(PUBLIC / "og-default.png", "PNG", optimize=True)
    print(f"  ✓ og-default.png ({W}x{H})")


print("=== ブランドアセット生成 ===")
build_favicon()
build_site_logo()
build_og_default()
print("完了")
