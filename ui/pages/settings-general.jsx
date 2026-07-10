import { AppWindowIcon, FrameCornersIcon, SunIcon } from "@phosphor-icons/react"

import { Select } from "@/components/select"
import { SettingsCard, SettingsContent, SettingsItem, SettingsTitle } from "@/components/settings"
import { Switch } from "@/components/switch"
import { useConfigStore } from "@/store/config"

export function GeneralSetting() {
  const config = useConfigStore((state) => state.config)
  const saveConfig = useConfigStore((state) => state.saveConfig)

  // 等待配置加载完成后再出页面，否则 Switch 的动画会闪一下
  if (!config) return null

  return (
    <SettingsContent>
      <SettingsTitle title="个性化" />

      <SettingsCard>
        <SettingsItem title="主题模式" subtitle="选择界面的显示风格" icon={<SunIcon />}>
          <Select
            options={[
              { value: "system", label: "跟随系统" },
              { value: "light", label: "浅色" },
              { value: "dark", label: "深色" },
            ]}
            value={config?.window_theme}
            onChange={(value) => saveConfig("window_theme", value)}
            className="w-48"
          />
        </SettingsItem>
      </SettingsCard>

      <SettingsTitle title="窗口" />

      <SettingsCard>
        <SettingsItem
          title="启用窗口材质"
          subtitle="启用系统的 Mica 或 Vibrancy 等窗口效果。修改后需重启生效"
          icon={<AppWindowIcon />}
        >
          <Switch
            checked={config?.window_vibrancy ?? true}
            onChange={(checked) => saveConfig("window_vibrancy", checked)}
          />
        </SettingsItem>
      </SettingsCard>

      <SettingsCard>
        <SettingsItem
          title="记住窗口尺寸"
          subtitle="程序启动时恢复上次关闭时的窗口大小和位置"
          icon={<FrameCornersIcon />}
        >
          <Switch checked={config?.remember_window} onChange={(checked) => saveConfig("remember_window", checked)} />
        </SettingsItem>
      </SettingsCard>
    </SettingsContent>
  )
}
