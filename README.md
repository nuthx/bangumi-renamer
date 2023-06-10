<p align="center">
    <img src="icon/icon.png" width=25%/ alt="">
</p>

## 介绍

本项目是基于 AniList 与 Bangumi 极为先进的自动化命名工具。只需要拖入下载完成的动画文件夹，即可根据自定义规则重新命名，避免手动整理费神又费力。

## 示例

命名格式（支持自定义）：

```
{b_initial_name}/[{b_typecode}] [{b_release_date}] {b_jp_name}
```

拖入文件：

```
[Moozzi2] Tokyo Revengers [ x265-10Bit Ver. ] - TV + SP
[VCB-Studio] Kage no Jitsuryokusha ni Naritakute! [Ma10p_1080p]
```

命名结果：

```
东京复仇者/[01] [230107] 東京リベンジャーズ 聖夜決戦編
想要成为影之实力者！/[01] [221005] 陰の実力者になりたくて！
```

## 使用

Bangumi Renamer 具备简单 GUI 界面，批量拖入需要更名的文件夹，先点击`开始识别`进行数据分析，确认内容后，点击`重命名`即可完成命名操作。

请在`重命名`开始前确保结果准确无误，`重命名`开始后，**操作不可撤销**。

若出现一个或多个结果错误，需要`清空列表`后排除错误项目，重新拖入识别。后续版本会支持单项调整。

##### 注意事项：

- 该工具仅为整季动画提供命名支持（即支持文件夹命名，不支持文件命名）
- 兼容常见的整季动画格式，规则为匹配首个`]`开始到后面第一个`[`间的内容为完整罗马名，并排除其中的`BD`与`BD-BOX`。
- 若出现无法兼容的情况，可手动修改文件夹名为`[]Tokyo Revengers[]`的格式再次尝试。

##### 数据来源：

- `AniList`：对动画罗马名的第一搜索结果较为准确
- `Bangumi`：命名数据的主要来源

### TODO

- 更优雅的方式实现图片展示
- 删除列表中指定行的动画文件夹
- 增加复选框，仅重命名选中的动画文件夹
- 输出更准确的行为日志到窗口左下角
- 进度条展示

### 致谢

[[AniList APIv2]](https://anilist.github.io/ApiV2-GraphQL-Docs/) 官方接口

[[Bangumi API]](https://github.com/bangumi/api) 官方接口

[[ChatGPT]](https://chat.openai.com/) 为我解答了诸多困惑

### 免责

本项目代码仅供学习交流，不得用于商业用途，若侵权请联系
