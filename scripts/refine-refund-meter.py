#!/usr/bin/env python3
"""
副業詐欺録 全記事の refund-meter aside を「（可能性）」明示・断言回避の丁寧表現に書き換え
"""
import json, glob, re
from pathlib import Path

ROOT = Path("/Users/toppo/マイファイル/副業詐欺録")

# パターン置換テーブル：旧 → 新
# (pattern, replacement)
REPLACEMENTS = [
    # 0-x% 系
    (r'<strong>0-3%</strong>',
     '<strong>0〜3%（あくまで可能性）</strong>'),
    (r'<strong>0-5%</strong>',
     '<strong>0〜5%（あくまで可能性）</strong>'),
    (r'<strong>0-2%</strong>',
     '<strong>0〜2%（あくまで可能性）</strong>'),
    # 10-x%系
    (r'<strong>10-25%</strong>',
     '<strong>10〜25%（あくまで可能性）</strong>'),
    (r'<strong>10-30%</strong>',
     '<strong>10〜30%（あくまで可能性）</strong>'),
    # 15-x%
    (r'<strong>15-25%</strong>',
     '<strong>15〜25%（あくまで可能性）</strong>'),
    (r'<strong>15-30%</strong>',
     '<strong>15〜30%（あくまで可能性）</strong>'),
    (r'<strong>15-40%</strong>',
     '<strong>15〜40%（あくまで可能性）</strong>'),
    # 20-x%
    (r'<strong>20-30%</strong>',
     '<strong>20〜30%（あくまで可能性）</strong>'),
    (r'<strong>20-35%</strong>',
     '<strong>20〜35%（あくまで可能性）</strong>'),
    (r'<strong>20-40%</strong>',
     '<strong>20〜40%（あくまで可能性）</strong>'),
    # 30-50%
    (r'<strong>30-50%</strong>',
     '<strong>30〜50%（あくまで可能性）</strong>'),
    # 5-15%
    (r'<strong>5-15%</strong>',
     '<strong>5〜15%（あくまで可能性）</strong>'),
]

# 断言調を緩める表現置換
SOFTEN = [
    ("回収はほぼ絶望的", "回収可能性は極めて低い"),
    ("ほぼ全て", "大半のケースで"),
    ("ほぼ確実", "蓋然性が高い"),
    ("確実", "高い可能性"),
    ("回収はほぼ不可能", "回収可能性が極めて低い状態"),
    ("実効性なし", "実効性が乏しい"),
    ("回収不可能", "回収可能性が著しく低い"),
    ("ほぼ100%", "高い割合で"),
]

# refund-meter aside の末尾に注意書きを追加
DISCLAIMER = (
    "<p style=\"font-size:0.78rem;color:#7a8595;margin-top:10px;line-height:1.7;\">"
    "※上記の回収率はあくまで本記事被害者の事例における過去の交渉結果に基づく目安です。"
    "事案ごとに状況は大きく異なり、保証された数字ではありません。"
    "実際の被害申告は必ず<a href=\"https://www.kokusen.go.jp/\" target=\"_blank\">消費生活センター（188）</a>"
    "・弁護士など専門家へご相談ください。"
    "</p>"
)


def process_file(jf):
    with open(jf, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "content" not in data:
        return False
    content = data["content"]
    original = content

    # パターン置換
    for pat, rep in REPLACEMENTS:
        content = re.sub(pat, rep, content)
    for old, new in SOFTEN:
        content = content.replace(old, new)

    # refund-meter aside の末尾に注意書きを追加（重複防止チェック）
    if "あくまで本記事被害者の事例" not in content:
        # refund-meter aside の </p></aside> の前に挿入
        # パターン: <aside class="refund-meter">.....</aside>
        new_content = re.sub(
            r'(<aside class="refund-meter">[\s\S]+?)(</aside>)',
            r'\1' + DISCLAIMER + r'\2',
            content,
        )
        if new_content != content:
            content = new_content

    if content == original:
        return False

    data["content"] = content
    with open(jf, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True


def main():
    count = 0
    for jf in sorted(glob.glob(str(ROOT / "approved" / "draft-*.json"))):
        if process_file(jf):
            count += 1
            print(f"  ✓ {Path(jf).name}")
    print(f"\nUpdated {count} files")


if __name__ == "__main__":
    main()
