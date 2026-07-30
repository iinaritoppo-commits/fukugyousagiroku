#!/usr/bin/env python3
"""approved/*.json の本文金額 × title/description/loss_amount_yen 突合チェック。

目的: 別記事からの内容混入（金額の取り違え）を機械的に洗い出す。
出力: 記事ごとに「想定金額セットに無い本文金額」を文脈付きで列挙。
判定はしない。人間が読んで裁定するための候補リストを出すだけ。
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPROVED = ROOT / "approved"

# 1,234円 / 80000円 形式
RE_DIGIT = re.compile(r"([0-9][0-9,]*)\s*円")
# 8万円 / 1.5万円 / 8万5千円 / 3億円 形式
RE_KANJI = re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*(億|万|千)\s*(?:([0-9]+(?:\.[0-9]+)?)\s*(万|千))?\s*円")
RE_TAG = re.compile(r"<[^>]+>")

UNIT = {"億": 100_000_000, "万": 10_000, "千": 1_000}
# 「実際に払った」ことを示す文脈。ここでの金額は損失額と一致していなければおかしい。
PAY_HINT = re.compile(r"(振込|振り込|送金|決済|支払|支払い|入金|払っ|払い|購入代金|代金|請求)")
# 損失額と一致しなくて当然の文脈（返金・収入・訴求・段階課金の内訳）
BENIGN_HINT = re.compile(r"(返金|回収|和解|取り戻|年収|月収|時給|日給|月商|月給|手取り|貯金|残り|損失は|月額|コース|講座|プログラム|プラン|メンター|研修|訴求|謳|うたっ|稼げ|稼い|収益|利益|報酬|売上|平均)")


def to_yen(m_kanji):
    head, unit, tail, tail_unit = m_kanji.groups()
    val = float(head) * UNIT[unit]
    if tail and tail_unit:
        val += float(tail) * UNIT[tail_unit]
    return int(val)


def extract(text):
    """(金額, 開始位置) のリストを返す。漢数字単位を優先し、重複区間は除外。"""
    found = []
    spans = []
    for m in RE_KANJI.finditer(text):
        found.append((to_yen(m), m.start(), m.group(0)))
        spans.append((m.start(), m.end()))
    for m in RE_DIGIT.finditer(text):
        if any(s <= m.start() < e for s, e in spans):
            continue
        found.append((int(m.group(1).replace(",", "")), m.start(), m.group(0)))
    return sorted(found, key=lambda x: x[1])


def context(text, pos, width=34):
    s = max(0, pos - width)
    e = min(len(text), pos + width)
    return text[s:e].replace("\n", " ")


def main():
    files = sorted(APPROVED.glob("*.json"))
    if not files:
        print(f"approved が見つからない: {APPROVED}", file=sys.stderr)
        return 1

    total_flags = 0
    print(f"対象: {len(files)}本  ({APPROVED.relative_to(ROOT)})\n")

    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        meta = " ".join(str(data.get(k, "")) for k in ("title", "description", "scheme", "trigger"))
        loss = data.get("loss_amount_yen")

        expected = {a for a, _, _ in extract(meta)}
        if isinstance(loss, int):
            expected.add(loss)
        # 端数込みの決済額（本体＋振込手数料）を許容
        expected |= {a + f for a in list(expected) for f in (110, 220, 330, 440, 550, 660, 770, 880, 990)}

        body = RE_TAG.sub(" ", data.get("content", ""))
        flags = []
        for amount, pos, raw in extract(body):
            if amount in expected:
                continue
            if amount < 10_000:  # 手数料・少額は対象外
                continue
            ctx = context(body, pos)
            if not PAY_HINT.search(ctx):
                continue  # 支払いを語っていない金額は対象外
            if BENIGN_HINT.search(ctx):
                continue  # 返金額・収入・訴求額・段階課金の内訳
            flags.append((amount, raw, "支払い文脈", ctx))

        if flags:
            total_flags += len(flags)
            print(f"■ {path.name}  loss_amount_yen={loss:,}" if isinstance(loss, int) else f"■ {path.name}  loss_amount_yen=None")
            print(f"   title: {data.get('title','')}")
            for amount, raw, label, ctx in flags:
                print(f"   [{label}] {raw} = {amount:,}円  … {ctx}")
            print()

    print(f"---- 要確認候補 合計 {total_flags} 件 ----")
    return 0


if __name__ == "__main__":
    sys.exit(main())
