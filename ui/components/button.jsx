import { cn } from "@/utils/cn"

export function Button({ variant = "default", disabled, children, className, ...props }) {
  const itemVarient = {
    default: disabled
      ? "text-secondary/70"
      : "bg-background dark:bg-background-dark hover:bg-background-dark/50 active:bg-background-dark/30 border-b-muted active:border-border/70",
    primary: disabled
      ? "text-secondary/70 bg-muted/70 border-transparent"
      : "text-background dark:text-white bg-accent hover:bg-accent/90 active:bg-accent/80 border-transparent border-b-secondary/70 dark:border-b-muted/70 active:border-b-secondary/20",
  }

  return (
    <button
      className={cn(
        "flex-center gap-2 h-8 px-4 border rounded-sm cursor-pointer transition shrink-0",
        disabled && "cursor-not-allowed",
        itemVarient[variant],
        className,
      )}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  )
}
