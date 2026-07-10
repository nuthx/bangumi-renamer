import "@/globals.css"

import { GearSixIcon, TextboxIcon } from "@phosphor-icons/react"
import { invoke } from "@tauri-apps/api/core"
import { listen } from "@tauri-apps/api/event"
import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { HashRouter, Navigate, Route, Routes } from "react-router-dom"
import { Toaster } from "sonner"

import { Nav, NavButton, NavSpace, NavUpgrade } from "@/components/nav.jsx"
import { AppWindow, MainContent, TitleBar } from "@/components/window.jsx"
import { Renamer } from "@/pages/renamer.jsx"
import { Settings } from "@/pages/settings.jsx"
import { AboutSetting } from "@/pages/settings-about.jsx"
import { DeveloperSetting } from "@/pages/settings-developer.jsx"
import { GeneralSetting } from "@/pages/settings-general.jsx"
import { useConfigStore } from "@/store/config"

// 初始化配置和主题模式
useConfigStore
  .getState()
  .initConfig()
  .then(async (config) => {
    await invoke("set_theme", { theme: config.window_theme })
  })

// 监听菜单跳转
listen("navigate", (event) => {
  window.location.hash = event.payload
})

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <HashRouter>
      <AppWindow>
        <Toaster
          position="top-center"
          offset={{ top: "32px" }}
          expand={true}
          gap={8}
          visibleToasts={5}
          className="flex justify-center"
        />
        <TitleBar />
        <MainContent>
          <Nav>
            <NavButton path="/" title="动画命名" icon={<TextboxIcon />} />
            <NavSpace />
            <NavUpgrade />
            <NavButton path="/settings" title="设置" icon={<GearSixIcon />} />
          </Nav>

          <Routes>
            <Route path="/" element={<Renamer />} />
            <Route path="/settings" element={<Settings />}>
              <Route index element={<Navigate to="general" replace />} />
              <Route path="general" element={<GeneralSetting />} />
              <Route path="developer" element={<DeveloperSetting />} />
              <Route path="about" element={<AboutSetting />} />
            </Route>
          </Routes>
        </MainContent>
      </AppWindow>
    </HashRouter>
  </StrictMode>,
)
