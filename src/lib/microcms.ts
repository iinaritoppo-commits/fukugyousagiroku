import { createClient } from "microcms-js-sdk";
import type { MicroCMSImage, MicroCMSDate } from "microcms-js-sdk";

// 記事の型定義（怪談録 articles API スキーマと一致）
export type Article = {
  title: string;
  slug: string;
  content: string;
  thumbnail?: MicroCMSImage;
  description?: string;
  category?: string | string[];
} & MicroCMSDate;

const SD = import.meta.env.MICROCMS_SERVICE_DOMAIN;
const KEY = import.meta.env.MICROCMS_API_KEY;
const HAS_VALID_KEY = KEY && KEY !== "PLACEHOLDER_REPLACE_ME";

export const client = HAS_VALID_KEY
  ? createClient({ serviceDomain: SD, apiKey: KEY })
  : null;

// 全記事取得（一覧用）─ API key 無効時は空配列でフォールバック
export const getArticles = async (queries?: { limit?: number; offset?: number }) => {
  if (!client) {
    return { contents: [], totalCount: 0, offset: 0, limit: queries?.limit ?? 0 };
  }
  try {
    return await client.getList<Article>({
      endpoint: "articles",
      queries: {
        limit: queries?.limit ?? 100,
        offset: queries?.offset ?? 0,
        orders: "-publishedAt",
      },
    });
  } catch (e) {
    console.warn("microCMS getArticles failed:", (e as Error)?.message);
    return { contents: [], totalCount: 0, offset: 0, limit: queries?.limit ?? 0 };
  }
};

export const getArticleBySlug = async (slug: string) => {
  if (!client) return null;
  try {
    const data = await client.getList<Article>({
      endpoint: "articles",
      queries: { filters: `slug[equals]${slug}`, limit: 1 },
    });
    return data.contents[0] ?? null;
  } catch {
    return null;
  }
};

export const getAllSlugs = async () => {
  if (!client) return [] as string[];
  try {
    const data = await client.getList<Article>({
      endpoint: "articles",
      queries: { fields: "slug", limit: 100 },
    });
    return data.contents.map((c) => c.slug);
  } catch {
    return [] as string[];
  }
};
