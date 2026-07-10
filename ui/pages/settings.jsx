import { Outlet } from "react-router-dom"

import { Page, PageBlock } from "@/components/page"
import { SettingsNav, SettingsNavButton } from "@/components/settings"

export function Settings() {
  return (
    <Page>
      <PageBlock className="flex-1 flex-col" last>
        <SettingsNav>
          <SettingsNavButton path="/settings/general" title="通用" />
          <SettingsNavButton path="/settings/developer" title="开发者选项" />
          <SettingsNavButton path="/settings/about" title="关于" />
        </SettingsNav>
        <Outlet />
      </PageBlock>
    </Page>
  )
}
