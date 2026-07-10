use tauri::menu::{Menu, MenuBuilder, MenuItemBuilder, PredefinedMenuItem, SubmenuBuilder};
use tauri::{App, Emitter};

pub fn create_menu(app: &App) -> Result<Menu<tauri::Wry>, Box<dyn std::error::Error>> {
    let app_menu = SubmenuBuilder::new(app, "Bangumi Renamer")
        .item(&MenuItemBuilder::with_id("about", "关于").build(app)?)
        .separator()
        .item(
            &MenuItemBuilder::with_id("settings", "设置")
                .accelerator("Cmd+,")
                .build(app)?,
        )
        .item(&MenuItemBuilder::with_id("developer", "开发者选项").build(app)?)
        .separator()
        .item(&PredefinedMenuItem::quit(
            app,
            Some("退出 Bangumi Renamer"),
        )?)
        .build()?;

    let func_menu = SubmenuBuilder::new(app, "功能")
        .item(
            &MenuItemBuilder::with_id("renamer", "动画命名")
                .accelerator("Cmd+1")
                .build(app)?,
        )
        .build()?;

    let edit_menu = SubmenuBuilder::new(app, "编辑")
        .item(&PredefinedMenuItem::undo(app, Some("撤销"))?)
        .item(&PredefinedMenuItem::redo(app, Some("重做"))?)
        .separator()
        .item(&PredefinedMenuItem::cut(app, Some("剪切"))?)
        .item(&PredefinedMenuItem::copy(app, Some("复制"))?)
        .item(&PredefinedMenuItem::paste(app, Some("粘贴"))?)
        .item(&PredefinedMenuItem::select_all(app, Some("全选"))?)
        .build()?;

    let window_menu = SubmenuBuilder::new(app, "窗口")
        .item(&PredefinedMenuItem::minimize(app, Some("最小化"))?)
        .item(&PredefinedMenuItem::maximize(app, Some("最大化"))?)
        .separator()
        .item(&PredefinedMenuItem::close_window(app, Some("关闭窗口"))?)
        .build()?;

    let menu = MenuBuilder::new(app)
        .item(&app_menu)
        .item(&edit_menu)
        .item(&func_menu)
        .item(&window_menu)
        .build()?;

    app.on_menu_event(|app, event| match event.id().as_ref() {
        "about" => {
            let _ = app.emit("navigate", "/settings/about");
        }
        "settings" => {
            let _ = app.emit("navigate", "/settings");
        }
        "developer" => {
            let _ = app.emit("navigate", "/settings/developer");
        }
        "renamer" => {
            let _ = app.emit("navigate", "/");
        }
        _ => {}
    });

    Ok(menu)
}
