import type { MetadataRoute } from "next";
import { getAllSlugs } from "@/lib/articles";

const BASE_URL = "https://predictionbets.com";
const LOCALES = ["en", "pt", "es"];
const CATEGORIES = [
  "politics",
  "crypto",
  "ai-tech",
  "sports",
  "markets",
  "culture",
  "geopolitics",
];

export default function sitemap(): MetadataRoute.Sitemap {
  const entries: MetadataRoute.Sitemap = [];

  // Static pages per locale
  for (const locale of LOCALES) {
    const prefix = locale === "en" ? "" : `/${locale}`;
    entries.push(
      {
        url: `${BASE_URL}${prefix}`,
        lastModified: new Date(),
        changeFrequency: "daily",
        priority: 1,
      },
      {
        url: `${BASE_URL}${prefix}/about`,
        lastModified: new Date(),
        changeFrequency: "monthly",
        priority: 0.5,
      },
      {
        url: `${BASE_URL}${prefix}/newsletter`,
        lastModified: new Date(),
        changeFrequency: "monthly",
        priority: 0.5,
      },
      {
        url: `${BASE_URL}${prefix}/community`,
        lastModified: new Date(),
        changeFrequency: "daily",
        priority: 0.7,
      }
    );

    // Category pages
    for (const cat of CATEGORIES) {
      entries.push({
        url: `${BASE_URL}${prefix}/category/${cat}`,
        lastModified: new Date(),
        changeFrequency: "daily",
        priority: 0.7,
      });
    }
  }

  // Article pages
  const slugs = getAllSlugs("en");
  for (const locale of LOCALES) {
    const prefix = locale === "en" ? "" : `/${locale}`;
    for (const slug of slugs) {
      entries.push({
        url: `${BASE_URL}${prefix}/article/${slug}`,
        lastModified: new Date(),
        changeFrequency: "weekly",
        priority: 0.8,
      });
    }
  }

  return entries;
}
