import { openUrl } from "@tauri-apps/plugin-opener"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

import { Button } from "@/components/button.jsx"
import { Dialog, DialogContent, DialogFooter } from "@/components/dialog.jsx"

export function UpdateDialog({ open, onClose, latestVersion, publishDate, releaseNotes }) {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogContent
        title="发现新版本"
        subtitle={`版本 v${latestVersion} ｜ 更新时间 ${publishDate}`}
        className="border rounded-md overflow-hidden"
      >
        <div className="space-y-2 max-h-80 px-5 py-4 bg-background-dark/50 overflow-auto markdown-content">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{releaseNotes}</ReactMarkdown>
        </div>
      </DialogContent>

      <DialogFooter>
        <Button className="flex-1" onClick={onClose}>
          关闭
        </Button>
        <Button
          variant="primary"
          className="flex-1"
          onClick={() => openUrl("https://github.com/nuthx/bangumi-renamer/releases/latest")}
        >
          前往下载
        </Button>
      </DialogFooter>
    </Dialog>
  )
}
