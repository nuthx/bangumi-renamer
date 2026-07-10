import { createContext, useCallback, useContext, useEffect, useRef } from "react"
import { createPortal } from "react-dom"

import { cn } from "@/utils/cn"

const ContextMenuContext = createContext(null)

export function ContextMenu({ cell, onClose, children, className }) {
  const menuRef = useRef(null)

  // 确定菜单位置，在鼠标上方还是下方显示
  useEffect(() => {
    if (!cell || !menuRef.current) return

    const MARGIN = 20
    const menu = menuRef.current
    const rect = menu.getBoundingClientRect()

    const x =
      cell.x + rect.width + MARGIN > window.innerWidth
        ? Math.max(MARGIN, window.innerWidth - rect.width - MARGIN)
        : cell.x
    const y = cell.y + rect.height + MARGIN > window.innerHeight ? Math.max(MARGIN, cell.y - rect.height) : cell.y

    menu.style.left = `${x}px`
    menu.style.top = `${y}px`
  }, [cell])

  // 关闭菜单
  useEffect(() => {
    if (!cell) return

    const controller = new AbortController()
    const handleClickOutside = (e) => menuRef.current && !menuRef.current.contains(e.target) && onClose()
    const handleEscape = (e) => e.key === "Escape" && onClose()

    document.addEventListener("mousedown", handleClickOutside, { signal: controller.signal })
    document.addEventListener("keydown", handleEscape, { signal: controller.signal })
    return () => controller.abort()
  }, [cell, onClose])

  return createPortal(
    <ContextMenuContext.Provider value={{ onClose }}>
      <div
        ref={menuRef}
        className={cn(
          "fixed z-50 min-w-44 p-1 bg-background/90 backdrop-blur-sm border shadow-lg/15 rounded-lg transition",
          cell ? "opacity-100" : "opacity-0 pointer-events-none",
          className,
        )}
      >
        {children}
      </div>
    </ContextMenuContext.Provider>,
    document.body,
  )
}

export function ContextItem({ title, icon, onClick, danger }) {
  const { onClose } = useContext(ContextMenuContext) || {}

  const handleClick = useCallback(() => {
    onClick?.()
    onClose?.()
  }, [onClick, onClose])

  return (
    <button
      type="button"
      className={cn(
        "flex items-center gap-2.5 w-full px-3 h-8 hover:bg-background-dark rounded-sm cursor-pointer transition",
        danger && "hover:text-error",
      )}
      onClick={handleClick}
    >
      {icon}
      {title}
    </button>
  )
}

export function ContextSeparator() {
  return <div className="mx-1 my-1.5 h-px bg-border" />
}
