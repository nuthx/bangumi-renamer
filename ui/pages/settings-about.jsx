import { ChatsIcon, FileTextIcon, GithubLogoIcon } from "@phosphor-icons/react"
import { openUrl } from "@tauri-apps/plugin-opener"

import packageJson from "#/package.json"
import { Button } from "@/components/button.jsx"
import { SettingsCard, SettingsContent, SettingsItem } from "@/components/settings"

export function AboutSetting() {
  return (
    <SettingsContent>
      <div className="flex-center flex-col gap-3 py-10">
        <img src="/logo/icon.svg" alt="logo" className="size-24 rounded-2xl shadow-md" draggable="false" />
        <img src="/logo/text.svg" alt="logo" className="w-58 pt-4" draggable="false" />
        <p className="text-secondary">这个有点厉害的动画重命名工具竟然不知不觉就更新到了 {packageJson.version}</p>
      </div>

      <SettingsCard>
        <SettingsItem title="Github" subtitle="看看作者今天 Work 了没，顺手来个 Star 吧" icon={<GithubLogoIcon />}>
          <Button onClick={() => openUrl("https://github.com/nuthx/bangumi-renamer")}>打开</Button>
        </SettingsItem>
      </SettingsCard>

      <SettingsCard>
        <SettingsItem title="反馈" subtitle="欢迎反馈软件问题，或提出功能建议" icon={<ChatsIcon />}>
          <Button onClick={() => openUrl("https://github.com/nuthx/bangumi-renamer/issues")}>反馈</Button>
        </SettingsItem>
      </SettingsCard>

      <SettingsCard>
        <SettingsItem title="更新记录" subtitle="查看 Bangumi Renamer 的更新日志" icon={<FileTextIcon />}>
          <Button onClick={() => openUrl("https://github.com/nuthx/bangumi-renamer/releases")}>查看</Button>
        </SettingsItem>
      </SettingsCard>
    </SettingsContent>
  )
}
