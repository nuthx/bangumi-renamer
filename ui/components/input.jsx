import { cn } from "@/utils/cn"

export function Input({ className, ...props }) {
  return (
    <input
      className={cn(
        "flex items-center gap-2 w-full h-8 px-3 text-primary placeholder:text-muted truncate rounded-sm transition",
        "bg-background hover:bg-background-dark/50 border border-b-muted focus:border-muted",
        className,
      )}
      {...props}
    />
  )
}
