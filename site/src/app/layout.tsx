import type { ReactNode } from "react";
import type { Metadata } from "next";
import { inter, jetbrains } from "@/lib/fonts";
import "./globals.css";

export const metadata: Metadata = {
  title: "Prediction Bets",
  description: "The cultural center of prediction markets. Reality beats opinion.",
  icons: {
    icon: "/logo-icon.svg",
    apple: "/logo-icon.svg",
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrains.variable}`}>
      <body className="min-h-screen flex flex-col font-sans">
        {children}
      </body>
    </html>
  );
}
