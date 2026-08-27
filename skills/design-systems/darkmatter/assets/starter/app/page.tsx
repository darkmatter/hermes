import { SiteHeader } from "@/components/showcase/site-header"
import { Hero } from "@/components/showcase/hero"
import { ColorSection } from "@/components/showcase/color-section"
import { TypeSection } from "@/components/showcase/type-section"
import { ComponentsSection } from "@/components/showcase/components-section"
import { EffectsSection } from "@/components/showcase/effects-section"
import { SiteFooter } from "@/components/showcase/site-footer"

export default function Page() {
  return (
    <div className="min-h-screen bg-black text-white">
      <SiteHeader />
      <main>
        <Hero />
        <ColorSection />
        <TypeSection />
        <ComponentsSection />
        <EffectsSection />
      </main>
      <SiteFooter />
    </div>
  )
}
