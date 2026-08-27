import Image from "next/image";
import { Badge } from "@native/ui/badge";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-[1440px] items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <Image
            src="/iridium-symbol.svg"
            alt=""
            aria-hidden="true"
            width={22}
            height={24}
            className="h-6 w-auto"
            priority
          />
          <Image
            src="/iridium-wordmark.svg"
            alt="Iridium"
            width={112}
            height={23}
            className="h-[18px] w-auto"
            priority
          />
          <Badge variant="outline" className="ml-1 hidden sm:inline-flex">
            @native/ui
          </Badge>
        </div>
        <nav className="flex items-center gap-5 text-xs text-foreground-muted">
          <a href="#tokens" className="transition-colors hover:text-foreground">
            Tokens
          </a>
          <a href="#type" className="transition-colors hover:text-foreground">
            Type
          </a>
          <a
            href="#components"
            className="transition-colors hover:text-foreground"
          >
            Components
          </a>
          <span className="hidden items-center gap-1.5 md:inline-flex">
            <span className="h-1.5 w-1.5 rounded-full bg-n-green" />
            <span className="tabular-nums text-foreground-muted">v0.0.0</span>
          </span>
        </nav>
      </div>
    </header>
  );
}
