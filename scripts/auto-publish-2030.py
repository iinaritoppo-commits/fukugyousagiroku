#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
副業詐欺録 X予約スクリプト（毎日20:00 cron）

設計：
- approved/*.json 直読みベース（microCMS不要、Astro SSGがビルド時に拾う）
- 「Xにまだ出してないslug」を曜日カテゴリから1本選ぶ
- X投稿用テキストを logs/x-post-pending.txt に追記
- macOS通知でとよくんに「コピペどうぞ」
- .env に X API キーがあれば自動投稿、無ければ pending のみ
- 投稿済みslugは logs/x-posted-slugs.txt に追記

曜日割（在庫多めから順）：
  月 = joho      （情報商材）9本
  火 = ai        （AI副業）9本
  水 = busshu    （物販）8本
  木 = coach     （コーチング）7本
  金 = invest    （投資副業）7本
  土 = mlm       （MLM）7本
  日 = jirei     （実在事案）5本

fallback: 在庫切れ時は romance → overseas → 任意未投稿の順
"""
import json, os, sys, urllib.request, urllib.error, subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPROVED = ROOT / "approved"
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)
LOG_FILE = LOGS / "publish.log"
POSTED_FILE = LOGS / "x-posted-slugs.txt"
PENDING_FILE = LOGS / "x-post-pending.txt"

SITE_URL = "https://fukugyousagiroku.com"

# .env 読み（X API キーは未設定ならスキップ）
# .env or environ から取得（GitHub Actions対応）
def _get_env(key):
    v = os.environ.get(key)
    if v: return v
    env_file = ROOT / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith(f"{key}=") and not line.strip().startswith("#"):
                    return line.strip().split("=", 1)[1]
    return ""

env = {
    "MICROCMS_SERVICE_DOMAIN": _get_env("MICROCMS_SERVICE_DOMAIN"),
    "MICROCMS_API_KEY": _get_env("MICROCMS_API_KEY"),
    "X_API_KEY": _get_env("X_API_KEY"),
    "X_API_SECRET": _get_env("X_API_SECRET"),
    "X_ACCESS_TOKEN": _get_env("X_ACCESS_TOKEN"),
    "X_ACCESS_TOKEN_SECRET": _get_env("X_ACCESS_TOKEN_SECRET"),
}

DOW_GENRE = {
    0: "joho",     # 月：情報商材
    1: "ai",       # 火：AI副業
    2: "busshu",   # 水：物販
    3: "coach",    # 木：コーチング
    4: "invest",   # 金：投資副業
    5: "mlm",      # 土：MLM
    6: "jirei",    # 日：実在事案
}
FALLBACK_ORDER = ["joho", "ai", "busshu", "coach", "invest", "mlm",
                  "jirei", "romance", "overseas"]

GENRE_TAGS = {
    "joho":     "#情報商材 #副業詐欺",
    "ai":       "#AI副業 #副業詐欺",
    "busshu":   "#物販詐欺 #副業詐欺",
    "coach":    "#コーチング詐欺 #副業詐欺",
    "invest":   "#投資副業 #副業詐欺",
    "mlm":      "#MLM #副業詐欺",
    "jirei":    "#副業詐欺 #実在事案",
    "romance":  "#ロマンス詐欺 #副業詐欺",
    "overseas": "#海外案件詐欺 #副業詐欺",
}


def log(msg):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def load_posted_slugs():
    """既にXに投稿済みのslug集合を返す"""
    if not POSTED_FILE.exists():
        return set()
    return {l.strip() for l in POSTED_FILE.read_text().splitlines() if l.strip()}


def append_posted(slug):
    with open(POSTED_FILE, "a") as f:
        f.write(slug + "\n")


def list_approved_by_genre(prefix):
    return sorted(APPROVED.glob(f"draft-{prefix}-*.json"))


def pick_target(posted_slugs, genre):
    for f in list_approved_by_genre(genre):
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
            if j.get("slug") and j["slug"] not in posted_slugs:
                return j, f
        except Exception:
            pass
    return None, None


def build_x_post(item):
    """X投稿用280字以内テキスト"""
    title = item["title"]
    desc = item.get("description", "")
    slug = item["slug"]
    cat = item.get("category", "joho")
    tags = GENRE_TAGS.get(cat, "#副業詐欺")

    # 1文目で切る（句点 or 120字）
    if "。" in desc:
        first = desc.split("。")[0] + "。"
    else:
        first = desc[:120]
    if len(first) > 120:
        first = first[:118] + "…"

    # 損失額が分かれば1行追加
    loss = item.get("loss_amount_yen", 0)
    loss_line = ""
    if loss and loss >= 10000:
        if loss >= 100000000:
            loss_line = f"払った金額：{loss/100000000:.1f}億円\n"
        elif loss >= 10000:
            loss_line = f"払った金額：{loss/10000:.0f}万円\n"

    text = (
        f"{title}\n\n"
        f"{first}\n"
        f"{loss_line}\n"
        f"{SITE_URL}/articles/{slug}/\n\n"
        f"📝 {tags}"
    )
    return text


def write_x_pending(item):
    text = build_x_post(item)
    with open(PENDING_FILE, "a") as f:
        f.write(f"\n===== {datetime.now().isoformat(timespec='seconds')} =====\n")
        f.write(f"slug: {item['slug']}\n")
        f.write(f"title: {item['title']}\n")
        f.write(f"chars: {len(text)} (URL=23字換算)\n")
        f.write(f"---\n{text}\n---\n")
    return text, len(text)


def try_post_to_x(text):
    """X API有効時のみ実投稿。tweepy未導入や404/402はwarnのみ"""
    keys = ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET")
    if not all(env.get(k) for k in keys):
        return False, "X API keys not set in .env"
    try:
        import tweepy
    except ImportError:
        return False, "tweepy not installed (pip install tweepy)"
    try:
        client = tweepy.Client(
            consumer_key=env["X_API_KEY"],
            consumer_secret=env["X_API_SECRET"],
            access_token=env["X_ACCESS_TOKEN"],
            access_token_secret=env["X_ACCESS_TOKEN_SECRET"],
        )
        resp = client.create_tweet(text=text)
        tid = resp.data.get("id") if resp.data else None
        return True, f"tweet_id={tid}"
    except Exception as e:
        return False, str(e)


def notify_macos(title_str, message):
    try:
        t = title_str.replace('"', '\\"')
        m = message.replace('"', '\\"')
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{m}" with title "{t}" sound name "Submarine"'],
            timeout=5
        )
    except Exception as e:
        log(f"  notify failed: {e}")


def main():
    now = datetime.now()
    dow = now.weekday()
    primary = DOW_GENRE[dow]
    log(f"=== auto-publish-fukugyo start  dow={dow} primary={primary} ===")

    posted = load_posted_slugs()
    log(f"X-posted so far: {len(posted)} slugs")

    item, src = pick_target(posted, primary)
    if not item:
        log(f"No unposted stock for {primary}, trying fallback...")
        for fb in FALLBACK_ORDER:
            if fb == primary:
                continue
            item, src = pick_target(posted, fb)
            if item:
                log(f"  fallback hit: {fb}")
                break

    if not item:
        log("ALL X-POSTED. Out of stock. (正常終了：X投稿は任意なのでビルド&デプロイは継続)")
        notify_macos("副業詐欺録：X在庫切れ", "approved 全てX投稿済み")
        return 0

    log(f"Target: {item['slug']}  ({src.name})")

    # X-pending出力
    try:
        x_text, n = write_x_pending(item)
        log(f"  ✓ X-pending written ({n} chars) → {PENDING_FILE.name}")
    except Exception as e:
        log(f"  ✗ X-pending failed: {e}")
        return 2

    # X API 自動投稿（クレジットあれば）
    ok, msg = try_post_to_x(x_text)
    if ok:
        log(f"  ✓ X posted automatically: {msg}")
        append_posted(item["slug"])
        notify_macos("副業詐欺録：X自動投稿完了",
                     f"{item['title'][:30]}…")
    else:
        log(f"  ⚠ X auto-post skipped: {msg}")
        notify_macos("副業詐欺録：X投稿準備OK（手動）",
                     f"{item['title'][:30]}… ({n}字)")

    log("=== done ===\n")
    return 0



# ============================================================================
# 🔴 2026-07-30 停止（社長承認）
# このスクリプトは記事公開を一切行わず、X投稿用テキスト（x-post-pending.txt）の
# 生成とmacOS通知だけを行っていた。Xは手動運用に移行済みのため、生成された
# pendingは誰も読まないまま蓄積し続けていた（投資2,123行／副業948行）。
# ビルド＆デプロイは GitHub Actions の後続ステップが担うため、ここで抜けても
# サイトの公開・更新には影響しない。
# 再開する場合はこのブロックを削除すること。
# ============================================================================
def main():  # noqa: F811  ← 上の旧main()を意図的に上書きして封印
    log("STOPPED: X-pending生成は2026-07-30に停止（Xは手動運用）。ビルド&デプロイは継続。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
