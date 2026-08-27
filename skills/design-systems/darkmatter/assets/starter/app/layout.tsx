import type { Metadata, Viewport } from "next"
import type { ReactNode } from "react"
import { ThemeProvider } from "@/components/theme-provider"
import "./globals.css"

export const metadata: Metadata = {
  title: "darkmatter — design system",
  description:
    "The visual and interaction language for darkmatter: a dark-first, terminal-inspired system built on Radix, Tailwind v4, and Geist Mono.",
  icons: {
    icon: "/img/logo-square-white.svg",
  },
}

export const viewport: Viewport = {
  themeColor: "#000000",
  colorScheme: "dark",
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          forcedTheme="dark"
          enableSystem={false}
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
