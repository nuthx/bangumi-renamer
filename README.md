# bangumi-autorenamer

### 介绍

为了解决每次下载完动画，都要先搜索中文译名，然后去 网站上手动复制番名，再改名的痛苦

怒啃 Pathon 三天，写下了第一个小版本

一键将下载的番剧文件夹，通过 Bangumi 和 AniList 查询，重命名为指定名称

### GUI：开发中

- 批量处理
- 自定义时间格式
- 自定义重命名格式
- 支持获取当前动画第一季度的名字（用于放入父文件夹）
- 展示动画封面及更多详细信息
- And more...

### 示例

在 Nyaa 上下载了 `[VCB-Studio] Yuusha Party o Tsuihou Sareta Beast Tamer, Saikyoushu no Nekomimi Shoujo to Deau [Ma10p_1080p]`，想整理成 “时间+日文名”的形式

需要先搜索`Yuusha Party o Tsuihou Sareta Beast Tamer, Saikyoushu no Nekomimi Shoujo to Deau`中文叫啥，再去 Bangumi 上复制放送时间

最后拼成`[1.TV] [20221002] 勇者パーティーを追放されたビーストテイマー、最強種の猫耳少女と出会う`形式的文件夹名

这个程序可以一键完成上述操作，信息源来自 Bangumi 与 AniList

### 使用

```
python3 renamer.py
```

拖入文件即可完成更名

### 致谢

[[Bangumi API]](https://github.com/bangumi/api) 官方接口

[[AniList APIv2]](https://anilist.github.io/ApiV2-GraphQL-Docs/) 官方接口

[[ChatGPT]](https://chat.openai.com/) 帮我解答了诸多困惑

### 免责

本项目代码仅供学习交流，不得用于商业用途，若侵权请联系
