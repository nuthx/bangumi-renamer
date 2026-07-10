import { ArrowClockwiseIcon, BellRingingIcon, FolderOpenIcon } from "@phosphor-icons/react"
import { appDataDir } from "@tauri-apps/api/path"
import { openPath } from "@tauri-apps/plugin-opener"

import { Button } from "@/components/button.jsx"
import { SettingsCard, SettingsContent, SettingsItem, SettingsTitle } from "@/components/settings"
import { toast } from "@/components/toast.jsx"
import { useConfigStore } from "@/store/config"

export function DeveloperSetting() {
  const resetConfig = useConfigStore((state) => state.resetConfig)

  const handleOpenConfig = async () => {
    try {
      await openPath(await appDataDir())
    } catch (error) {
      toast.error({ title: "文件夹打开失败", description: error.message })
    }
  }

  const handleResetConfig = async () => {
    try {
      await resetConfig()
      toast.success({ title: "配置已重置" })
    } catch (error) {
      toast.error({ title: "重置配置失败", description: error.message })
    }
  }

  return (
    <SettingsContent>
      <SettingsTitle title="配置管理" />

      <SettingsCard>
        <SettingsItem
          title="浏览配置文件"
          subtitle="请勿随意修改配置项。若遇软件启动失败，请完全删除文件夹内全部内容"
          icon={<FolderOpenIcon />}
        >
          <Button onClick={handleOpenConfig}>打开</Button>
        </SettingsItem>
      </SettingsCard>

      <SettingsCard>
        <SettingsItem
          title="重置配置文件"
          subtitle="点击后立即重置所有配置项，没有二次弹窗确认。部分配置需重启后生效"
          icon={<ArrowClockwiseIcon />}
        >
          <Button onClick={handleResetConfig}>重置</Button>
        </SettingsItem>
      </SettingsCard>

      <SettingsTitle title="软件测试" />

      <SettingsCard>
        <SettingsItem title="发送通知" subtitle="点击后立即发送 Toast 通知" icon={<BellRingingIcon />}>
          <div className="flex gap-2">
            <Button onClick={() => toast.success({ title: "单行标题" })}>成功</Button>
            <Button onClick={() => toast.warning({ title: "单行标题" })}>警告</Button>
            <Button onClick={() => toast.error({ title: "多行标题", description: "多行多行多行多行多行多行多行内容" })}>
              错误
            </Button>
            <Button
              onClick={() =>
                toast.promise(new Promise((r) => setTimeout(r, 1500)), {
                  loading: { title: "加载中..." },
                  success: { title: "加载完成" },
                })
              }
            >
              加载
            </Button>
          </div>
        </SettingsItem>
      </SettingsCard>
    </SettingsContent>
  )
}
