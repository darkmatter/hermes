import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import {
  Inter,
  Lora,
  IBM_Plex_Mono,
  Geist_Mono,
  Source_Code_Pro,
} from "next/font/google";
import { Toaster } from "@native/ui/sonner";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
const lora = Lora({ subsets: ["latin"], variable: "--font-lora", display: "swap" });
const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-ibm-plex-mono",
  display: "swap",
});
const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
  display: "swap",
});
const sourceCodePro = Source_Code_Pro({
  subsets: ["latin"],
  variable: "--font-source-code-pro",
  display: "swap",
});

const fontVariables = [
  inter.variable,
  lora.variable,
  ibmPlexMono.variable,
  geistMono.variable,
  sourceCodePro.variable,
].join(" ");

export const metadata: Metadata = {
  title: "Iridium — Design System",
  description:
    "Iridium is a dark-first, terminal-inspired design system built on Tailwind v4, React 19, and Radix primitives.",
  icons: {
    icon: [{ url: "/favicon.svg", type: "image/svg+xml" }],
  },
};

export const viewport: Viewport = {
  themeColor: "#0E0F0F",
  colorScheme: "dark",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={`dark ${fontVariables}`}>
      <body>
        {children}
        <Toaster />
      </body>
    </html>
  );
}
