#[cfg(target_os = "macos")]
mod menu;
mod theme;

use tauri::{generate_context, generate_handler, Builder, Manager, Window};
use tauri_plugin_store::StoreExt;
use tauri_plugin_window_state::{StateFlags, WindowExt};
#[cfg(target_os = "windows")]
use window_vibrancy::{apply_acrylic, apply_blur, apply_mica};
#[cfg(target_os = "macos")]
use window_vibrancy::{apply_vibrancy, NSVisualEffectMaterial};

#[tauri::command]
fn set_theme(window: Window, theme: String) -> Result<(), String> {
    theme::set_theme_inner(window, theme).map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    Builder::default()
        .plugin(
            tauri_plugin_window_state::Builder::default()
                .skip_initial_state("main")
                .build(),
        )
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_os::init())
        .plugin(tauri_plugin_store::Builder::default().build())
        .invoke_handler(generate_handler![set_theme])
        .setup(|app| {
            let window = app.get_webview_window("main").unwrap();

            // 获取配置
            let store = app.store("config.json").ok();
            let remember_window = store
                .as_ref()
                .and_then(|s| s.get("remember_window"))
                .and_then(|v| v.as_bool())
                .unwrap_or(false);
            let enable_vibrancy = store
                .as_ref()
                .and_then(|s| s.get("window_vibrancy"))
                .and_then(|v| v.as_bool())
                .unwrap_or(true);

            // 恢复窗口状态
            if remember_window {
                let _ = window.restore_state(StateFlags::all());
            }

            // 应用窗口材质
            if enable_vibrancy {
                #[cfg(target_os = "windows")]
                {
                    let _ = apply_mica(&window, None)
                        .or_else(|_| apply_acrylic(&window, None))
                        .or_else(|_| apply_blur(&window, None));
                }

                #[cfg(target_os = "macos")]
                {
                    let _ = apply_vibrancy(&window, NSVisualEffectMaterial::HudWindow, None, None);
                }
            }

            // 创建 macOS 菜单
            #[cfg(target_os = "macos")]
            if let Ok(menu) = menu::create_menu(app) {
                let _ = app.set_menu(menu);
            }

            // 初始化完成后再显示窗口
            let _ = window.show();

            Ok(())
        })
        .run(generate_context!())
        .expect("error while running tauri application");
}
