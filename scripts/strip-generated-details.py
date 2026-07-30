#!/usr/bin/env python3
"""add-details-bulk.py が自動生成した『追加で聞いた話』ブロックを撤去する。

背景（2026-07-26）:
  add-details-bulk.py は random.seed(slug) で日時・出会いの場面・送金額・
  告白の場面・現在の状況を機械生成し、「（◯◯県在住・◯さん本人談）」と
  署名を付けて23本に埋め込んでいた。「送金額は最初の段階で約N万円」は
  loss_amount_yen÷6 の計算値で、本文の段階的課金の初回額とも矛盾する。
  取材事実が存在しないため修正はできない。撤去する。

対象は自動生成版だけ。記事ごとに手書きされた『追加で聞いた話』
（joho-006 など）は残す。判別キーは <dt>広告/勧誘との出会い</dt>。

  --dry-run  差分の要約だけ出して書き込まない
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPROVED = ROOT / "approved"

# intake-record aside 内に挿入された自動生成ブロック
BLOCK = re.compile(
    r'<h3 style="font-size:0\.92rem;[^"]*">追加で聞いた話</h3><dl>(?:(?!</dl>).)*?</dl>',
    re.DOTALL,
)
MARKER = "<dt>広告/勧誘との出会い</dt>"


def main():
    dry = "--dry-run" in sys.argv
    files = sorted(APPROVED.glob("draft-*.json"))
    if not files:
        print(f"approved が見つからない: {APPROVED}", file=sys.stderr)
        return 1

    changed = 0
    for path in files:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        content = data.get("content", "")

        removed = []

        def drop(m):
            if MARKER not in m.group(0):
                return m.group(0)  # 手書きブロックは温存
            removed.append(m.group(0))
            return ""

        new_content = BLOCK.sub(drop, content)
        if not removed:
            continue

        # 撤去後に <dl></dl> や空の h3 が残っていないか確認
        assert "追加で聞いた話" not in new_content or MARKER not in new_content
        assert new_content.count("<aside") == content.count("<aside")

        changed += 1
        print(f"■ {path.name}  {len(removed)}ブロック撤去 / {len(content)}字 → {len(new_content)}字")
        for blk in removed:
            for dt, dd in re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", blk):
                print(f"   - {dt}: {dd}")

        if not dry:
            data["content"] = new_content
            # 既存ファイルは末尾改行なし（add-details-bulk.py の json.dump 準拠）
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    print(f"\n{'[dry-run] ' if dry else ''}{changed}本を処理")
    return 0


if __name__ == "__main__":
    sys.exit(main())
