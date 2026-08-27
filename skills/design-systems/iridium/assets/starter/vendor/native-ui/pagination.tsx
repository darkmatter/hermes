import { cn } from "./lib/utils";

interface PaginationControlsProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function PaginationControls({
  page,
  totalPages,
  onPageChange,
}: PaginationControlsProps) {
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-between mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-border">
      <span className="text-phosphor-dim text-xs sm:text-sm">
        <span className="text-phosphor">{page}</span>/{totalPages}
      </span>
      <div className="flex gap-1.5 sm:gap-2">
        <button
          onClick={() => onPageChange(Math.max(1, page - 1))}
          disabled={page === 1}
          className={cn(
            "px-2 sm:px-3 py-1 text-xs sm:text-sm border border-border transition-all",
            "hover:border-phosphor hover:text-phosphor",
            "disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:border-border disabled:hover:text-phosphor-dim",
          )}
        >
          ◄
        </button>
        <button
          onClick={() => onPageChange(Math.min(totalPages, page + 1))}
          disabled={page === totalPages}
          className={cn(
            "px-2 sm:px-3 py-1 text-xs sm:text-sm border border-border transition-all",
            "hover:border-phosphor hover:text-phosphor",
            "disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:border-border disabled:hover:text-phosphor-dim",
          )}
        >
          ►
        </button>
      </div>
    </div>
  );
}
