#!/usr/bin/env python3
"""
副業詐欺録 OGPサムネのChatGPT発注用プロンプト41個を生成
配色：ダークネイビー基調＋カテゴリ別1差し色
"""
import json, glob, os
from pathlib import Path

ROOT = Path("/Users/toppo/マイファイル/副業詐欺録")
OUT = ROOT / "scripts" / "ogp-prompts.json"

# カテゴリ別差し色＋小物
CAT_DATA = {
    "joho": {
        "label": "情報商材",
        "accent": "エメラルドグリーン (#00C896) — LINEブランドカラー寄り",
        "objects": "LINEトーク画面を映したスマホ、契約書、開封済み封筒",
        "scene": "LINEメッセージで巧妙に勧誘される構図",
    },
    "mlm": {
        "label": "MLM・連鎖販売",
        "accent": "アンバーイエロー (#FFC83D) — 警告色",
        "objects": "ピラミッド構造の人型シルエット連鎖、サプリ瓶や化粧品ボトルの山",
        "scene": "ネズミ講式に被害者が連鎖していく構図",
    },
    "coach": {
        "label": "高額コーチング",
        "accent": "ディープバイオレット (#7B5CFF) — 高額感",
        "objects": "空のオフィスチェア、Zoom会議画面、置き去りの契約書",
        "scene": "突然連絡が取れなくなったコーチの空席感",
    },
    "ai": {
        "label": "AI副業",
        "accent": "ネオンシアン (#00D4FF) — テック感",
        "objects": "グリッチかかったAIロボット、コード断片、壊れたPC画面",
        "scene": "AI副業の幻想が崩れる構図",
    },
    "invest": {
        "label": "投資型副業",
        "accent": "クリムゾンレッド (#E63946) — 急落",
        "objects": "急落する折れ線チャート、崩れる札束、デジタル数字",
        "scene": "投資画面の数字が暴落していく構図",
    },
    "romance": {
        "label": "国際ロマンス商法",
        "accent": "ローズピンク (#FF6B9D) — 恋愛感",
        "objects": "割れたハートマーク、LINE既読スルー画面、シルエット男女",
        "scene": "恋愛感情を装った詐欺被害者の絶望",
    },
    "busshu": {
        "label": "物販・転売スクール",
        "accent": "オレンジ (#FF8C42) — 商品",
        "objects": "山積みになった未開封段ボール、売れ残り在庫",
        "scene": "在庫の山に埋もれる構図",
    },
    "overseas": {
        "label": "海外案件・越境EC",
        "accent": "ターコイズ (#26C6DA) — 海外",
        "objects": "パスポート、税関スタンプ、海外送金通知、地球儀",
        "scene": "海外送金が宙に消えていく構図",
    },
}


def short_scheme(scheme: str) -> str:
    s = scheme.split("（")[0].split("(")[0].strip()
    if len(s) > 16:
        s = s[:16]
    if not s.endswith("詐欺"):
        s += "詐欺"
    return s


ART_STYLE = (
    "【アートスタイル（厳守・全41枚で完全統一）】"
    "ミニマル漫画調イラスト。太線手描きタッチ、ヘタウマ感のあるポップ作画。"
    "線は太め・大胆、色数は3〜4色まで（平塗り中心、グラデーション最小）、影・テクスチャ・光沢は禁止。"
    "『告発エンタメ』テイスト、週刊誌の挿絵カット風。"
    "人物は表情を漫画的に誇張（三白眼・冷や汗・口元クィアッ）、顔のディテールは最小限（目はドットや単純な丸、口は線一本程度）。"
    "写真っぽいリアル系イラスト、3D、ベクター滑らかグラデ、フォトリアルは絶対禁止。"
    "AI特有のテカテカ・ベタッとした塗りは避け、紙にペンで描いた質感を意識。"
    "全画像で同一の漫画家による作品のように、線の太さ・配色トーン・キャラのタッチ感を統一すること。"
    "【派手演出（必ず入れる）】漫画的な集中線と効果線、背景にうっすらハーフトーンのドット模様、"
    "札束を背景一面に派手に乱舞（金値差控えめの黄色）、"
    "巨大文字「○○万円消えた」の周りにひびやスパークの効果、"
    "「⚠警告」ピルの周りに黒黄ストライプテープ、"
    "漫画的擬音（『ガン！』『ドン！』など）を1〜2個入れて告発シーン感を強化、"
    "『週刊誌コラム』よりも『コミックスのドラマチック告発シーン』のイメージで。"
)


def gen_prompt(article: dict) -> str:
    cat = article["category"]
    d = CAT_DATA[cat]
    p = article["persona"]
    amount_man = article["loss_amount_yen"] // 10000
    scheme_short = short_scheme(article["scheme"])
    age_band = f"{p['age']}歳"
    gender = "男性" if p["gender"] == "男性" else "女性"
    occupation = p["occupation"].split("（")[0]

    return (
        f"副業詐欺録（実話まとめサイト）のOGPサムネを作ってください。サイズ1200x630の横長OGP。"
        f"\n\n{ART_STYLE}"
        f"\n\n【配色】"
        f"背景：深ネイビー〜ブラック（#0E1525〜#1A2030の単色グラデーション）。紫色は使わない。"
        f"差し色（このカテゴリのテーマカラー）：{d['accent']}。"
        f"文字色：白基調＋極太、縁取りは深い赤のみ。"
        f"\n\n【今回の記事】{d['label']}カテゴリ。{scheme_short}で{amount_man}万円を失った話。"
        f"\n\n【画面構成】"
        f"中央〜中央右に主要素として：{d['objects']}（漫画調・線太め）。{d['scene']}。"
        f"右下に困惑表情の{age_band}{gender}（漫画調・ヘタウマ・表情誇張、目はドットや単純線、写真っぽさ厳禁）。"
        f"右上に巨大白文字「{amount_man}万円消えた」（赤縁取り、最大サイズで圧倒的に）。"
        f"その下に「{scheme_short}」（黄色文字、中サイズ）。"
        f"左上に「⚠警告」の赤丸ピル（小さめ）。"
        f"左下に手書き風キャッチ「これが詐欺の手口」（中サイズ）。"
        f"背景にうっすら散らばる札束（漫画調・色控えめ）。"
        f"\n\n【絶対禁止】"
        f"・リアル系・フォトリアル・3D・AI特有のテカテカ塗り"
        f"・「○○カテゴリ」「{age_band}{gender}が」など説明テキスト"
        f"・左側に「{amount_man}万円失った話」のような右側コピーの繰り返し"
        f"・文字要素は4つまで（⚠警告／これが詐欺の手口／{amount_man}万円消えた／{scheme_short}）"
        f"・紫色、マゼンタ、ライムグリーン、ネオン、ホラー要素"
        f"・装飾フレーム・余計なステッカー・縞模様の煽り背景"
    )


def main():
    prompts = []
    drafts = sorted(glob.glob(str(ROOT / "approved" / "draft-*.json")))
    for jf in drafts:
        a = json.load(open(jf))
        if not all(k in a for k in ("slug", "loss_amount_yen", "scheme", "category", "persona")):
            continue
        prompts.append({
            "slug": a["slug"],
            "category": a["category"],
            "amount_man": a["loss_amount_yen"] // 10000,
            "scheme_short": short_scheme(a["scheme"]),
            "prompt": gen_prompt(a),
        })
    OUT.write_text(json.dumps(prompts, ensure_ascii=False, indent=2))
    print(f"Generated {len(prompts)} prompts → {OUT}")
    # Show 2 samples
    print("\n--- Sample 1 (joho) ---")
    print(prompts[6]["prompt"][:300])
    print("\n--- Sample 2 (romance) ---")
    rom = [p for p in prompts if p["category"] == "romance"][0]
    print(rom["prompt"][:300])


if __name__ == "__main__":
    main()
