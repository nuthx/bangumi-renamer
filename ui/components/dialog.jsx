import { DialogPanel, DialogTitle, Dialog as HeadlessDialog } from "@headlessui/react"
import { type } from "@tauri-apps/plugin-os"

import { cn } from "@/utils/cn"

export function Dialog({ open, onClose, children, className }) {
  return (
    <HeadlessDialog
      open={open}
      onClose={onClose}
      className="fixed inset-0 z-50 flex-center w-full bg-black/40 data-closed:opacity-0 transition"
      transition
    >
      <DialogPanel
        className={cn(
          "w-full max-w-135 bg-background border rounded-lg shadow-xl overflow-hidden data-closed:transform-[scale(95%)] data-closed:opacity-0 transition",
          className,
        )}
        transition
      >
        {type() === "macos" && <div className="fixed top-0 left-0 right-0 h-9" data-tauri-drag-region />}
        {children}
      </DialogPanel>
    </HeadlessDialog>
  )
}

export function DialogContent({ title, subtitle, children, className }) {
  return (
    <div className="flex-center flex-col gap-5 p-6">
      <div className="flex flex-col gap-1 w-full">
        <DialogTitle className="text-xl font-semibold">{title}</DialogTitle>
        {subtitle && <span className="text-xs text-secondary">{subtitle}</span>}
      </div>
      <div className={cn("w-full", className)}>{children}</div>
    </div>
  )
}

export function DialogFooter({ children, className }) {
  return (
    <div className={cn("flex items-center justify-end gap-2 px-6 py-5 bg-background-dark border-t", className)}>
      {children}
    </div>
  )
}
