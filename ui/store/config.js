import { invoke } from "@tauri-apps/api/core"
import { load } from "@tauri-apps/plugin-store"
import { create } from "zustand"

const DEFAULT_CONFIG = {
  // 通用
  window_theme: "system",
  window_vibrancy: true,
  remember_window: true,
}

let storeInstance = null

async function getStore() {
  if (!storeInstance) {
    storeInstance = await load("config.json", { autoSave: true })
  }
  return storeInstance
}

export const useConfigStore = create((set, get) => ({
  config: null,

  initConfig: async () => {
    const store = await getStore()
    for (const [key, value] of Object.entries(DEFAULT_CONFIG)) {
      if ((await store.get(key)) === undefined) {
        await store.set(key, value)
      }
    }
    return await get().refreshConfig()
  },

  getConfig: async () => {
    return get().config ?? (await get().refreshConfig())
  },

  refreshConfig: async () => {
    const store = await getStore()
    const entries = await Promise.all(
      Object.entries(DEFAULT_CONFIG).map(async ([key, value]) => [key, (await store.get(key)) ?? value]),
    )
    const config = Object.fromEntries(entries)
    set({ config })
    return config
  },

  saveConfig: async (key, value) => {
    set((state) => ({
      config: {
        ...state.config,
        [key]: value,
      },
    }))

    const store = await getStore()
    await store.set(key, value)

    if (key === "window_theme") {
      await invoke("set_theme", { theme: value })
    }
  },

  resetConfig: async () => {
    const store = await getStore()
    await store.clear()
    for (const [key, value] of Object.entries(DEFAULT_CONFIG)) {
      await store.set(key, value)
    }
    await get().refreshConfig()
  },
}))
