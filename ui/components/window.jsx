import { type } from "@tauri-apps/plugin-os"

import { useConfigStore } from "@/store/config"
import { cn } from "@/utils/cn"

export function AppWindow({ children }) {
  const config = useConfigStore((s) => s.config)
  const enableVibrancy = config?.window_vibrancy ?? true

  const itemPlatform = {
    windows: enableVibrancy ? "" : "bg-background-dark",
    macos: enableVibrancy ? "bg-background-dark/80" : "bg-background-dark",
    linux: "bg-background-dark",
  }

  return <div className={cn("flex flex-col h-screen", itemPlatform[type()])}>{children}</div>
}

export function TitleBar() {
  const itemPlatform = {
    windows: "h-2",
    macos: "h-9",
    linux: "",
  }

  return <div className={cn("w-full", itemPlatform[type()])} data-tauri-drag-region />
}

export function MainContent({ children }) {
  return <div className="flex-1 flex gap-2 px-2 overflow-hidden">{children}</div>
}
