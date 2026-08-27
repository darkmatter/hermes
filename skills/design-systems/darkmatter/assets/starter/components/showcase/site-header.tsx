"use client"

import { GitHubIcon } from "@/components/ui/github-icon"
import { Button } from "@/components/ui/button"

const NAV = [
  { label: "products", href: "#products" },
  { label: "color", href: "#color" },
  { label: "type", href: "#type" },
  { label: "components", href: "#components" },
  { label: "effects", href: "#effects" },
]

export function SiteHeader() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-zinc-900/70 bg-black/70 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-[1280px] items-center justify-between px-6">
        <a href="#top" className="flex items-center gap-2.5">
          <img src="/img/logo-square-white.svg" alt="darkmatter" width={22} height={22} />
          <span className="font-mono text-sm font-semibold tracking-[-0.01em] text-white">
            darkmatter
          </span>
          <span className="ml-1 rounded-full border border-zinc-800 px-2 py-0.5 font-mono text-[10px] tracking-[0.04em] text-zinc-500 lowercase">
            design system
          </span>
        </a>

        <nav className="hidden items-center gap-7 md:flex">
          {NAV.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="font-sans text-[13px] font-medium tracking-[0.01em] text-zinc-400 capitalize transition-colors hover:text-white"
            >
              {item.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Button asChild variant="ghost" size="icon" className="text-zinc-400 hover:text-white">
            <a href="#" aria-label="GitHub repository">
              <GitHubIcon className="size-4" />
            </a>
          </Button>
          <Button size="sm">Get started</Button>
        </div>
      </div>
    </header>
  )
}
