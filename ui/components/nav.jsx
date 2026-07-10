import { RocketIcon } from "@phosphor-icons/react"
import { cloneElement, useEffect, useState } from "react"
import { Link, useLocation } from "react-router-dom"

import packageJson from "#/package.json"
import { Button } from "@/components/button"
import { UpdateDialog } from "@/dialogs/update"
import { cn } from "@/utils/cn"

export function Nav({ children }) {
  return <nav className="flex flex-col gap-1 w-46 pb-2 shrink-0">{children}</nav>
}

export function NavSpace() {
  return <div className="w-full flex-1" />
}

export function NavButton({ path, title, icon, disabled }) {
  const pathname = useLocation().pathname
  const isSelected = pathname === path || pathname.startsWith(`${path}/`)

  if (disabled) return null

  return (
    <Link
      to={path}
      draggable={false}
      className={cn(
        "group relative flex items-center gap-2 h-9 px-3 rounded-md hover:bg-primary/10 transition",
        isSelected && "bg-primary/10",
      )}
    >
      {cloneElement(icon, { size: 20 })}
      {title}
      {isSelected && (
        <div className="absolute left-0 w-0.75 h-4 rounded-full bg-accent group-active:h-3 transition-all"></div>
      )}
    </Link>
  )
}

export function NavUpgrade() {
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [hasUpdate, setHasUpdate] = useState(false)
  const [latestVersion, setLatestVersion] = useState("")
  const [publishDate, setPublishDate] = useState("")
  const [releaseNotes, setReleaseNotes] = useState("")

  useEffect(() => {
    fetch("https://api.github.com/repos/nuthx/bangumi-renamer/releases/latest", {
      headers: { "User-Agent": "bangumi-renamer" },
    })
      .then((res) => res.json())
      .then((data) => {
        const latestVersion = data.tag_name
        if (latestVersion && latestVersion !== packageJson.version) {
          setHasUpdate(true)
          setLatestVersion(latestVersion)
          setPublishDate(data.published_at)
          setReleaseNotes(data.body || "")
        }
      })
      .catch(() => {})
  }, [])

  if (!hasUpdate) return null

  return (
    <>
      <Button
        variant="primary"
        className="justify-start h-15 px-3 mb-1 border-none rounded-md"
        onClick={() => setIsDialogOpen(true)}
      >
        <RocketIcon size={20} />
        <div className="flex flex-col items-start gap-0.5">
          <div className="font-medium">发现新版本</div>
          <div className="text-[11px] opacity-90">
            v{latestVersion} ({publishDate.split("T")[0]})
          </div>
        </div>
      </Button>

      <UpdateDialog
        open={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        latestVersion={latestVersion}
        publishDate={publishDate.split("T")[0]}
        releaseNotes={releaseNotes}
      />
    </>
  )
}
