use anyhow::{Context, Result};
use tauri::{Theme, Window};

pub fn set_theme_inner(window: Window, theme: String) -> Result<()> {
    let theme_value = match theme.as_str() {
        "light" => Some(Theme::Light),
        "dark" => Some(Theme::Dark),
        _ => None,
    };
    window.set_theme(theme_value).context("设置主题失败")
}
