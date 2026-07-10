import { cn } from "@/utils/cn"

export function Page({ children }) {
  return <div className="flex flex-col gap-2 flex-1 min-w-0">{children}</div>
}

export function PageGroup({ children, className }) {
  return <div className={cn("flex gap-2 min-h-0 shrink-0", className)}>{children}</div>
}

export function PageBlock({ children, last, className }) {
  return (
    <div
      className={cn(
        "flex border rounded-lg bg-background/70 overflow-auto shrink-0",
        last && "rounded-b-none border-b-0",
        className,
      )}
    >
      {children}
    </div>
  )
}
