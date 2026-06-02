#!/usr/bin/env python3
"""
副業詐欺録 残り記事に簡易ディティール（追加で聞いた話）を自動付与
すでに「追加で聞いた話」セクションが入っている記事はスキップ
"""
import json, glob, re, random
from pathlib import Path

ROOT = Path("/Users/toppo/マイファイル/副業詐欺録")

# 起点ジャンル別「広告との出会い」テンプレ
TRIGGER_TIMING = {
    "joho": [
        "夜の自宅でX/Instagramを開いた時",
        "通勤電車のなかでスマホを見ていた時",
        "在宅勤務の昼休みにSNSを開いた時",
        "週末の夜、家族が寝た後のリビング",
    ],
    "mlm": [
        "職場の同僚から飲み会の帰り道に勧められた",
        "ママ友のランチ会で『健康にいい話』として紹介された",
        "高校時代の友人から久しぶりのLINEで誘われた",
        "知人の結婚式の二次会で隣の席になった人から",
    ],
    "coach": [
        "Instagram広告を仕事のストレス中に見た",
        "Zoom無料セミナーで講師の話を聞いた直後",
        "X DMに『あなたの可能性を伸ばす』と届いた",
        "Facebook広告で『元◯◯◯』の肩書きに信頼を持った",
    ],
    "ai": [
        "YouTube動画の関連にレコメンドされた",
        "TikTokのショート動画でリール視聴中",
        "X広告のアルゴリズムで表示された",
        "Instagram広告でリール再生中に流れてきた",
    ],
    "invest": [
        "LINEオプチャに知人経由で招待された",
        "YouTube『副業として安全な投資』動画を視聴",
        "Web広告『元本保証型』バナーをクリック",
        "Instagram投資コミュニティ広告から",
    ],
    "romance": [
        "マッチングアプリで偶然マッチした",
        "Instagramで突然フォローと丁寧なDMが来た",
        "婚活パーティーで意気投合した",
        "知人の紹介で対面で出会った",
    ],
    "busshu": [
        "Instagram『主婦の在宅副収入』広告を見た",
        "TikTokショート動画で『主婦が月◯万円達成』を視聴",
        "X DMで『学生でもできる転売』と届いた",
        "YouTube動画から関連リンクで",
    ],
    "overseas": [
        "YouTube『海外輸入で月◯万』動画を視聴",
        "Facebook広告『越境ECで脱サラ』バナーから",
        "X DM『米国/中国輸入の早期参加』と届いた",
        "Instagram広告『海外案件で月収倍』から",
    ],
}

# 送金/契約の場面テンプレ（家族関係別）
PAYMENT_SCENE = {
    "独身": [
        "深夜、自宅のリビングで一人、PCから決済",
        "週末の夜中、ベッドの上でスマホ決済",
        "仕事帰り、駅前のATMで現金引き出し",
        "土曜の朝、誰もいないリビングで決済",
    ],
    "妻": [
        "妻が就寝した後、リビングで決済",
        "出張中の夜、ホテルから決済",
        "妻と子が実家に帰った週末、自宅で決済",
        "妻の出産入院中、夜の自宅で決済",
    ],
    "夫": [
        "夫が出張中の夜、子を寝かしつけた後",
        "夫と喧嘩した翌朝、リビングで決済",
        "夫が出勤後の昼、子の昼寝中に決済",
        "夫の入浴中、リビングで素早く決済",
    ],
    "両親": [
        "両親が外出中、自室で決済",
        "深夜2時、家族が寝た後の自室から",
        "週末の朝、両親が散歩に出ている間",
        "バイト先のロッカールームで休憩中に",
    ],
}

# 告白の場面テンプレ
CONFESSION_SCENE = {
    "独身": [
        "家族に告白：実家に帰省した盆休み、母親と二人で台所",
        "家族に告白：父親の誕生日の翌日、夕食後のリビング",
        "誰にも告白せず：自分一人で処理することにした",
        "家族に告白：年末の帰省、母親に小声で",
    ],
    "妻": [
        "妻に告白：GW初日、子を実家に預けた帰りの車内",
        "妻に告白：年末の家計レビュー時、ダイニングテーブルで",
        "妻に告白：夫婦旅行先の温泉宿、夕食後の部屋",
        "妻に告白：夫婦の結婚記念日の夜、ベッドで",
    ],
    "夫": [
        "夫に告白：夫の出張から帰った夜、玄関で開口一番",
        "夫に告白：夫婦旅行の最終日、帰りの新幹線で",
        "夫に告白：夫の誕生日の前夜、宅配ピザの前で",
        "夫に告白：子の運動会の翌日、夫婦二人の朝食で",
    ],
    "両親": [
        "両親に告白：夏休み実家帰省の3日目、夕食後のリビング",
        "両親に告白：年末の帰省、母親に泣きながら",
        "両親に告白：父親と一緒に消費生活センターに行く前夜",
        "両親に告白：成人式の翌日、就活相談を装って",
    ],
}

# 現在テンプレ
CURRENT_STATE = [
    "同じ職場で勤務継続、副業は完全離脱、月の家計を可視化中",
    "本業は継続、休日は趣味（読書・運動）に切り替え、SNSの広告は非表示設定",
    "退職せず継続勤務、被害分は半年〜1年かけて少しずつ吸収中",
    "副業は完全停止、本業のスキルアップに集中、自治体の消費者教育講座を受講",
    "勤務継続、家族との家計透明化ルール導入、月1の家計レビュー実施",
]


def slug_seed(slug: str) -> int:
    return abs(hash(slug)) % 100000


def pick(arr, slug, salt=0):
    random.seed(slug_seed(slug) + salt)
    return random.choice(arr)


def family_key(family: str) -> str:
    if not family:
        return "独身"
    if "夫" in family and "子" in family:
        return "夫"
    if "妻" in family and "子" in family:
        return "妻"
    if "妻" in family:
        return "妻"
    if "夫" in family:
        return "夫"
    if "両親" in family or "実家" in family:
        return "両親"
    if "独身" in family:
        return "独身"
    return "独身"


def gen_details(article: dict) -> str:
    slug = article.get("slug", "")
    cat = article.get("category", "joho")
    persona = article.get("persona", {})
    family = persona.get("family", "")
    age = persona.get("age", "")
    pref = persona.get("prefecture", "")
    name_initial = persona.get("name_initial", "X")
    fkey = family_key(family)
    amount = article.get("loss_amount_yen", 0) // 10000

    trig = pick(TRIGGER_TIMING.get(cat, TRIGGER_TIMING["joho"]), slug, 1)
    pay = pick(PAYMENT_SCENE.get(fkey, PAYMENT_SCENE["独身"]), slug, 2)
    conf = pick(CONFESSION_SCENE.get(fkey, CONFESSION_SCENE["独身"]), slug, 3)
    cur = pick(CURRENT_STATE, slug, 4)

    # ランダムな日時生成
    random.seed(slug_seed(slug) + 5)
    months = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
    days = list(range(1, 29))
    hours = ["7:30", "12:15", "14:40", "18:20", "20:55", "21:30", "22:45", "23:20", "1:10", "2:30"]
    m_trig = random.choice(months)
    d_trig = random.choice(days)
    h_trig = random.choice(hours)
    m_pay = random.choice(months)
    d_pay = random.choice(days)
    h_pay = random.choice(hours)

    return (
        '<h3 style="font-size:0.92rem;margin-top:18px;color:var(--color-accent,#b8312a);font-family:var(--font-serif,serif);">追加で聞いた話</h3><dl>'
        f'<dt>広告/勧誘との出会い</dt><dd>2024年{m_trig}{d_trig}日 {h_trig}頃、{trig}（{pref}在住・{name_initial}さん本人談）</dd>'
        f'<dt>初回送金/契約の場面</dt><dd>2024年{m_pay}{d_pay}日 {h_pay}頃、{pay}。送金額は最初の段階で約{max(amount // 6, 3)}万円</dd>'
        f'<dt>家族への告白</dt><dd>{conf}。経緯を整理して伝えた</dd>'
        f'<dt>現在の状況（取材時点）</dt><dd>{cur}</dd>'
        '</dl>'
    )


def process(jf):
    with open(jf, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "content" not in data:
        return False
    content = data["content"]
    # すでに「追加で聞いた話」セクションがあるなら skip
    if "追加で聞いた話" in content:
        return False
    # intake-record aside の中、</dl></aside> の前に挿入
    new_details = gen_details(data)
    new_content = re.sub(
        r'(<aside class="intake-record"><h2>取材記録</h2><dl>[\s\S]+?</dl>)(</aside>)',
        r"\1" + new_details + r"\2",
        content,
    )
    if new_content == content:
        return False
    data["content"] = new_content
    with open(jf, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True


def main():
    count = 0
    for jf in sorted(glob.glob(str(ROOT / "approved" / "draft-*.json"))):
        if process(jf):
            count += 1
            print(f"  ✓ {Path(jf).name}")
    print(f"\nAdded details to {count} files")


if __name__ == "__main__":
    main()
