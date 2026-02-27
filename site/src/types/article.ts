export type ContentType = "signal" | "analysis" | "reality-check" | "culture" | "edge";

export type Category =
  | "politics"
  | "crypto"
  | "ai-tech"
  | "sports"
  | "markets"
  | "culture"
  | "geopolitics";

export interface ArticleFrontmatter {
  title: string;
  subtitle?: string;
  date: string;
  author: string;
  authorSlug: string;
  category: Category;
  tags: string[];
  image: string;
  imageCaption: string;
  excerpt: string;
  contentType: ContentType;
  featured: boolean;
  lang: string;
}

export interface Article extends ArticleFrontmatter {
  slug: string;
  content: string;
  readingTime: number;
}
