import rss from "@astrojs/rss";
import fs from "node:fs";
import path from "node:path";
import type { APIRoute } from "astro";

const CAT_LABELS: Record<string, string> = {
  joho: "情報商材", mlm: "MLM", coach: "コンサル詐欺", ai: "AI副業",
  invest: "投資型副業", romance: "ロマンス商法", busshu: "物販系", overseas: "海外案件",
};

export const GET: APIRoute = async (context) => {
  const dir = path.join(process.cwd(), "approved");
  const items: any[] = [];
  if (fs.existsSync(dir)) {
    for (const f of fs.readdirSync(dir)) {
      if (!f.endsWith(".json")) continue;
      try {
        const j = JSON.parse(fs.readFileSync(path.join(dir, f), "utf-8"));
        if (j.slug && j.title) {
          // ファイル更新時刻を pubDate に
          const stat = fs.statSync(path.join(dir, f));
          items.push({
            title: j.title,
            description: j.description ?? "",
            link: `/articles/${j.slug}/`,
            pubDate: stat.mtime,
            categories: [CAT_LABELS[j.category] ?? j.category],
          });
        }
      } catch {}
    }
  }
  // 新しい順、最大50件
  items.sort((a, b) => b.pubDate.getTime() - a.pubDate.getTime());
  return rss({
    title: "副業詐欺録 — 騙された話を、騙される前に。",
    description: "副業詐欺・情報商材・MLM・ロマンス商法など、副業を装った詐欺の実例を取材ベースで記録するアーカイブ。",
    site: context.site ?? "https://fukugyousagiroku.com",
    items: items.slice(0, 50),
    customData: `<language>ja-JP</language>`,
  });
};
