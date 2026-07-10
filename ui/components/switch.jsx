import { cn } from "@/utils/cn"

export function Switch({ checked, onChange }) {
  const handleClick = (e) => {
    e.stopPropagation() // 阻止事件冒泡
    onChange?.(!checked)
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className={cn(
        "group relative flex items-center h-5 w-10 border rounded-full px-0.5 cursor-pointer transition-all overflow-hidden",
        checked
          ? "bg-accent hover:bg-accent/90 active:bg-accent/80 border-accent justify-end"
          : "bg-background hover:bg-background-dark/50 active:bg-background-dark/70 border-secondary/70 justify-start",
      )}
    >
      <div
        className={cn(
          "size-3.5 shadow-sm rounded-full transition-all group-active:w-5 group-active:scale-y-95",
          checked ? "bg-background dark:bg-white shadow-primary/20" : "bg-secondary/70 shadow-transparent",
        )}
      />
    </button>
  )
}
