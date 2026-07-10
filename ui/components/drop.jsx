import { FilePlusIcon } from "@phosphor-icons/react"
import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow"
import { useEffect, useState } from "react"

import { cn } from "@/utils/cn"

export function DropArea({ title, onFileDrop, children }) {
  const [isDragging, setIsDragging] = useState(false)

  useEffect(() => {
    const appWindow = getCurrentWebviewWindow()
    const unlisten = appWindow.onDragDropEvent(async (event) => {
      if (event.payload.type === "enter") {
        setIsDragging(true)
      } else if (event.payload.type === "leave") {
        setIsDragging(false)
      } else if (event.payload.type === "drop") {
        setIsDragging(false)
        await onFileDrop(event.payload.paths)
      }
    })
    return () => {
      unlisten.then((fn) => fn())
    }
  }, [onFileDrop])

  return (
    <div className="relative flex-1 flex rounded-lg overflow-auto">
      <div
        className={cn(
          "absolute z-20 flex-center flex-col gap-2 w-full h-full bg-accent/5 border-2 border-accent text-accent rounded-lg transition",
          isDragging ? "opacity-100" : "opacity-0 pointer-events-none",
        )}
      >
        <FilePlusIcon className="size-8" stroke={5} />
        <p>{title}</p>
      </div>
      <div className={cn("flex-1 flex overflow-auto transition", isDragging && "opacity-20 blur-xs")}>{children}</div>
    </div>
  )
}
