import { CaretDownIcon } from "@phosphor-icons/react"
import { Children, cloneElement, useEffect, useRef, useState } from "react"
import { Link, useLocation } from "react-router-dom"

import { cn } from "@/utils/cn"

export function SettingsNav({ children }) {
  const navRef = useRef(null)
  const [indicatorStyle, setIndicatorStyle] = useState({ left: 0, width: 0 })
  const [enableTransition, setEnableTransition] = useState(false)
  const location = useLocation()

  // 指示器移动动画
  useEffect(() => {
    const activeButton = navRef.current.querySelector(`[href="#${location.pathname}"]`)
    if (activeButton) {
      const navRect = navRef.current.getBoundingClientRect()
      const buttonRect = activeButton.getBoundingClientRect()

      setIndicatorStyle({
        left: buttonRect.left - navRect.left,
        width: buttonRect.width,
      })
    }
  }, [location.pathname])

  // 延迟启用动画
  useEffect(() => {
    const timer = setTimeout(() => {
      setEnableTransition(true)
    }, 100)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div ref={navRef} className="relative flex items-center gap-6 h-12 px-6 border-b shrink-0">
      {children}
      <div
        className={cn(
          "absolute bottom-0 h-0.75 bg-accent rounded-t-full",
          enableTransition && "transition-all duration-300 ease-out",
        )}
        style={{
          left: `${indicatorStyle.left}px`,
          width: `${indicatorStyle.width}px`,
        }}
      />
    </div>
  )
}

export function SettingsNavButton({ path, title }) {
  return (
    <Link to={path} draggable={false} className="flex-center h-full px-1 cursor-pointer">
      {title}
    </Link>
  )
}

export function SettingsContent({ children }) {
  return (
    <div className="flex-1 overflow-auto">
      <div className="flex flex-col items-center gap-2 p-6">{children}</div>
    </div>
  )
}

export function SettingsTitle({ title }) {
  return <div className="flex items-center w-full p-5 pb-1 first:pt-0 font-medium text-base">{title}</div>
}

export function SettingsCard({ children }) {
  const items = Children.toArray(children)
  const [expanded, setExpanded] = useState(false)

  if (items.length <= 1) return items[0]

  return (
    <div className="flex flex-col w-full border rounded-md overflow-hidden">
      {cloneElement(items[0], { isCardHeader: true, isExpanded: expanded, onClick: () => setExpanded((v) => !v) })}
      <div className={cn("grid transition-all duration-300", expanded ? "grid-rows-[1fr]" : "grid-rows-[0fr]")}>
        <div className="overflow-hidden">
          {items.slice(1).map((item, i) => cloneElement(item, { isSubitem: true, key: i }))}
        </div>
      </div>
    </div>
  )
}

export function SettingsItem({ title, subtitle, icon, children, isCardHeader, isExpanded, isSubitem, ...props }) {
  return (
    <div
      className={cn(
        "flex-center gap-4 h-18 w-full px-5 bg-background",
        isCardHeader ? "cursor-pointer" : "border rounded-md",
        isSubitem && "border-0 border-t rounded-none bg-transparent",
      )}
      {...props}
    >
      {icon && cloneElement(icon, { size: 26, weight: "light" })}
      {isSubitem && !icon && <div className="size-6.5" />}
      <div className="flex-1 flex flex-col gap-0.5">
        <p className={cn(isCardHeader && "cursor-pointer")}>{title}</p>
        {subtitle && <p className={cn("text-xs text-secondary", isCardHeader && "cursor-pointer")}>{subtitle}</p>}
      </div>
      {children}
      {isCardHeader && <CaretDownIcon className={cn("size-4 transition duration-300", isExpanded && "-rotate-180")} />}
    </div>
  )
}
