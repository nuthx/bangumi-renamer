import { cn } from "@/utils/cn"

export function Badge({ children, variant = "default", className, onClick, ...props }) {
  const variants = {
    default: "bg-accent border-accent text-background dark:text-white",
    outline: "border-muted/80 text-primary/80",
  }

  const Component = onClick ? "button" : "span"

  return (
    <Component
      type={onClick ? "button" : undefined}
      className={cn(
        "flex-center gap-1 h-7 px-4 border text-[13px] rounded-full transition",
        onClick && "hover:bg-background-dark/50 hover:border-muted cursor-pointer",
        variants[variant],
        className,
      )}
      onClick={onClick}
      {...props}
    >
      {children}
    </Component>
  )
}
