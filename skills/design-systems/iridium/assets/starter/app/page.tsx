import { PageLayout } from "@native/ui/page-layout";

import { SiteHeader } from "./components/site-header";
import { Hero } from "./components/hero";
import { TokensSection } from "./components/tokens-section";
import { TypographySection } from "./components/typography-section";
import { ComponentsShowcase } from "./components/components-showcase";

export default function Page() {
  return (
    <div className="min-h-dvh bg-background">
      <SiteHeader />
      <Hero />
      <PageLayout>
        <div className="flex flex-col gap-16 py-4">
          <TokensSection />
          <TypographySection />
          <ComponentsShowcase />
        </div>
      </PageLayout>
      <footer className="border-t border-border">
        <div className="mx-auto max-w-[1440px] px-4 py-8 sm:px-6 lg:px-8">
          <p className="text-xs text-foreground-muted">
            Iridium · @native/ui — dark-first design system. Built with Tailwind
            v4, React 19, and Radix primitives.
          </p>
        </div>
      </footer>
    </div>
  );
}
