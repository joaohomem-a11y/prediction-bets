import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { remark } from "remark";
import html from "remark-html";
import type { Article, ArticleFrontmatter, Category } from "@/types/article";

const CONTENT_DIR = path.join(process.cwd(), "src/content/articles");

function getArticleDir(locale: string): string {
  if (locale === "en") return CONTENT_DIR;
  return path.join(CONTENT_DIR, locale);
}

function calculateReadingTime(content: string): number {
  const wordsPerMinute = 200;
  const words = content.trim().split(/\s+/).length;
  return Math.max(1, Math.ceil(words / wordsPerMinute));
}

export async function getArticleBySlug(
  slug: string,
  locale: string = "en"
): Promise<Article | null> {
  const dir = getArticleDir(locale);
  const filePath = path.join(dir, `${slug}.md`);

  if (!fs.existsSync(filePath)) return null;

  const raw = fs.readFileSync(filePath, "utf-8");
  const { data, content } = matter(raw);
  const frontmatter = data as ArticleFrontmatter;

  const processed = await remark().use(html).process(content);

  return {
    ...frontmatter,
    slug,
    content: processed.toString(),
    readingTime: calculateReadingTime(content),
  };
}

export async function getAllArticles(
  locale: string = "en"
): Promise<Article[]> {
  const dir = getArticleDir(locale);

  if (!fs.existsSync(dir)) return [];

  const files = fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".md") && !f.startsWith("."));

  const articles = await Promise.all(
    files.map(async (file) => {
      const slug = file.replace(/\.md$/, "");
      return getArticleBySlug(slug, locale);
    })
  );

  return articles
    .filter((a): a is Article => a !== null)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}

export async function getArticlesByCategory(
  category: Category,
  locale: string = "en"
): Promise<Article[]> {
  const all = await getAllArticles(locale);
  return all.filter((a) => a.category === category);
}

export async function getFeaturedArticles(
  locale: string = "en"
): Promise<Article[]> {
  const all = await getAllArticles(locale);
  return all.filter((a) => a.featured);
}

export function getAllSlugs(locale: string = "en"): string[] {
  const dir = getArticleDir(locale);
  if (!fs.existsSync(dir)) return [];

  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".md"))
    .map((f) => f.replace(/\.md$/, ""));
}
