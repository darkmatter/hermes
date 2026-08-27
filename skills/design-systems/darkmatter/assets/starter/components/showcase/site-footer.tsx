export function SiteFooter() {
  return (
    <footer className="border-t border-zinc-900/50 py-14">
      <div className="mx-auto flex max-w-[1280px] flex-col items-start justify-between gap-6 px-6 md:flex-row md:items-center">
        <div className="flex items-center gap-2.5">
          <img src="/img/logo-square-white.svg" alt="darkmatter" width={20} height={20} />
          <span className="font-mono text-sm font-semibold text-white">darkmatter</span>
        </div>
        <p className="font-mono text-[10px] tracking-[0.04em] text-zinc-700 lowercase">
          © 2026 darkmatter. all rights reserved.
        </p>
      </div>
    </footer>
  )
}
