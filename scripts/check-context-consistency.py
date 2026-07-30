#!/usr/bin/env python3
"""approved/*.json の本文 × メタ情報の突合チェック（金額以外の混入検知）。

金額チェック（check-amount-consistency.py）で拾えない別記事からの混入を探す。
 1. 流入チャネル: title/description/trigger に無いチャネルが本文に出ていないか
 2. 居住地: persona.prefecture と違う都道府県が本文に出ていないか

判定はしない。人間が読んで裁定するための候補リストを出すだけ。
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPROVED = ROOT / "approved"
RE_TAG = re.compile(r"<[^>]+>")

# チャネル名 -> 表記ゆれパターン
CHANNELS = {
    "LINEオープンチャット": r"(オープンチャット|オプチャ)",
    "X/Twitter": r"(X\s?DM|XのDM|X上|Twitter|ツイッター|X検索|Xで)",
    "Instagram": r"(Instagram|インスタ)",
    "TikTok": r"(TikTok|ティックトック)",
    "YouTube広告": r"(YouTube広告|ユーチューブ広告)",
    "Facebook": r"(Facebook|フェイスブック)",
    "マッチングアプリ": r"(マッチングアプリ|Pairs|ペアーズ|タップル|with)",
    "知人・ママ友紹介": r"(ママ友|知人からの紹介|友人からの紹介|職場の同僚から)",
}

PREFS = re.compile(
    r"(北海道|青森県|岩手県|宮城県|秋田県|山形県|福島県|茨城県|栃木県|群馬県|埼玉県|千葉県|東京都|"
    r"神奈川県|新潟県|富山県|石川県|福井県|山梨県|長野県|岐阜県|静岡県|愛知県|三重県|滋賀県|京都府|"
    r"大阪府|兵庫県|奈良県|和歌山県|鳥取県|島根県|岡山県|広島県|山口県|徳島県|香川県|愛媛県|高知県|"
    r"福岡県|佐賀県|長崎県|熊本県|大分県|宮崎県|鹿児島県|沖縄県)"
)


def context(text, pos, width=32):
    return text[max(0, pos - width): pos + width].replace("\n", " ")


def main():
    files = sorted(APPROVED.glob("*.json"))
    if not files:
        print(f"approved が見つからない: {APPROVED}", file=sys.stderr)
        return 1

    print(f"対象: {len(files)}本  ({APPROVED.relative_to(ROOT)})\n")
    total = 0

    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        meta = " ".join(str(data.get(k, "")) for k in ("title", "description", "scheme", "trigger"))
        body = RE_TAG.sub(" ", data.get("content", ""))
        persona = data.get("persona") or {}
        pref = persona.get("prefecture", "")

        lines = []

        expected_ch = {n for n, pat in CHANNELS.items() if re.search(pat, meta)}
        for name, pat in CHANNELS.items():
            if name in expected_ch:
                continue
            m = re.search(pat, body)
            if m:
                lines.append(f"   [チャネル] メタに無い『{name}』が本文に … {context(body, m.start())}")

        for m in PREFS.finditer(body):
            if m.group(1) != pref:
                lines.append(f"   [居住地] persona={pref} だが『{m.group(1)}』 … {context(body, m.start())}")

        if lines:
            total += len(lines)
            print(f"■ {path.name}  ({pref} / trigger: {data.get('trigger','')[:40]})")
            print("\n".join(lines))
            print()

    print(f"---- 要確認候補 合計 {total} 件 ----")
    return 0


if __name__ == "__main__":
    sys.exit(main())
