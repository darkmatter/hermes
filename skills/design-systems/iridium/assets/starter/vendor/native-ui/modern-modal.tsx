import { useEffect, type ReactNode } from "react";

/**
 * ModernModal — self-contained modal for the modernized ("Glow") surfaces.
 * Overlay + esc-to-close + body scroll-lock + a rounded dark panel. Callers
 * provide their own header/content. Renders in place (inherits .modern-ui),
 * and also self-applies the modern context so it's correct if portaled.
 */
export function ModernModal({
  open,
  onClose,
  children,
}: {
  open: boolean;
  onClose: () => void;
  children: ReactNode;
}) {
  useEffect(() => {
    const onEsc = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    if (open) {
      document.addEventListener("keydown", onEsc);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", onEsc);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      onClick={(e) => e.target === e.currentTarget && onClose()}
      className="modern-ui dark fixed inset-0 z-50 flex items-end justify-center bg-black/80 font-sans backdrop-blur-sm sm:items-center sm:p-6"
    >
      <div className="relative max-h-[95vh] w-full overflow-auto overscroll-contain rounded-t-2xl border border-white/10 bg-neutral-950 shadow-2xl sm:max-h-[90vh] sm:max-w-3xl sm:rounded-2xl">
        {children}
      </div>
    </div>
  );
}
