#!/usr/bin/env python3
"""SOFTEN置換で生じた不自然な日本語を修正"""
import json, glob, re
from pathlib import Path

ROOT = Path("/Users/toppo/マイファイル/副業詐欺録")

FIXES = [
    # 「大半のケースで」が不自然な箇所
    ("大半のケースで全て", "ほぼすべて"),
    ("大半のケースでが", "大半が"),
    ("大半のケースでで", "大半のケースで"),
    # 「蓋然性が高い」が不自然な箇所
    ("蓋然性が高いに", "高い確率で"),
    ("蓋然性が高いポンジ", "ポンジ系の蓋然性が高い"),
    # 「高い可能性」が不自然な箇所
    ("年利30%高い可能性", "年利30%とされる"),
    ("高い可能性な改善", "確かな改善"),
    ("高い可能性な回収", "現実的な回収"),
    ("高い可能性に防げ", "未然に防げ"),
    # 「回収可能性が極めて低い」が不自然な箇所（既に良いケース）
    # 何もしない
    # 「回収可能性が著しく低い」が不自然な箇所
    ("回収可能性が著しく低い", "回収可能性が極めて低い"),
]


def process(jf):
    with open(jf, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "content" not in data:
        return False
    content = data["content"]
    original = content
    for old, new in FIXES:
        content = content.replace(old, new)
    if content == original:
        return False
    data["content"] = content
    with open(jf, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True


def main():
    count = 0
    for jf in sorted(glob.glob(str(ROOT / "approved" / "draft-*.json"))):
        if process(jf):
            count += 1
    print(f"Fixed {count} files")


if __name__ == "__main__":
    main()
