import type { ReactNode } from "react";
import type { Metadata } from "next";
import Script from "next/script";
import { inter, jetbrains } from "@/lib/fonts";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://predictionbets.club"),
  title: {
    default: "Prediction Bets — The Cultural Center of Prediction Markets",
    template: "%s | Prediction Bets",
  },
  description:
    "Prediction markets news, analysis, and education. Real signal from Polymarket, Kalshi, and Metaculus. Reality beats opinion. Markets reveal truth.",
  keywords: [
    "prediction markets",
    "Polymarket",
    "Kalshi",
    "Metaculus",
    "forecasting",
    "prediction market news",
    "betting markets",
    "market predictions",
    "crypto prediction markets",
    "election odds",
  ],
  authors: [{ name: "Prediction Bets" }],
  creator: "Prediction Bets",
  publisher: "Prediction Bets",
  icons: {
    icon: "/logo-icon.svg",
    apple: "/logo-icon.svg",
  },
  openGraph: {
    type: "website",
    siteName: "Prediction Bets",
    title: "Prediction Bets — The Cultural Center of Prediction Markets",
    description:
      "Prediction markets news, analysis, and education. Real signal from Polymarket, Kalshi, and Metaculus.",
    url: "https://predictionbets.club",
    images: [
      {
        url: "/logo-full.svg",
        width: 240,
        height: 32,
        alt: "Prediction Bets",
      },
    ],
    locale: "en_US",
    alternateLocale: ["pt_BR", "es_ES"],
  },
  twitter: {
    card: "summary_large_image",
    title: "Prediction Bets — The Cultural Center of Prediction Markets",
    description:
      "Prediction markets news, analysis, and education. Reality beats opinion. Markets reveal truth.",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  alternates: {
    canonical: "https://predictionbets.club",
    languages: {
      en: "https://predictionbets.club",
      pt: "https://predictionbets.club/pt",
      es: "https://predictionbets.club/es",
    },
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrains.variable}`}>
      <head>
        <Script
          async
          src="https://www.googletagmanager.com/gtag/js?id=G-9FWBSNDJL6"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-9FWBSNDJL6');
          `}
        </Script>
      </head>
      <body className="min-h-screen flex flex-col font-sans">
        {children}
      </body>
    </html>
  );
}
