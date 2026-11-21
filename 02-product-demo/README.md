# 02 手机界面产品展示

[当前 30 秒成片](out/Only-Cats-UI-Launch-30s-Catalog-Swipe.mp4) · [可编辑 HTML 时间线](index.html) · [分镜与节奏](treatment.md) · [素材来源与配乐授权](materials.md)

画布为 1920 × 1080，30 fps。手机里的画面来自 Only Cats 网页端录屏和本地试玩数据。当前版用配乐和音效带节奏，配合开场的产品定位和结尾品牌文案。

| 时间 | 展示内容 | 时间线使用的剪辑 |
| --- | --- | --- |
| 0–4 秒 | 欢迎页、品牌和产品定位 | [欢迎页](materials/01-welcome.mp4) |
| 4–10 秒 | Cilly 助手、选猫照片、填写地点和预览 | [助手](materials/02-assistant.mp4) |
| 10–16 秒 | 浏览偶遇广场、打开贴贴的帖子 | [广场](materials/03-square.mp4) |
| 16–22 秒 | 顶部头像条连划六次，停在第 26 条「兰花」 | [图鉴横滑](materials/04-catalog-swipe.mp4) |
| 22–28 秒 | 打开阿禾的聊天并发送邀约 | [消息](materials/05-messages.mp4) |
| 28–30 秒 | 保留聊天画面，收回品牌字标和结语 | 同一段消息剪辑 |

## 接着剪

- 改布局、品牌文案或切换时点，编辑 [index.html](index.html)。GSAP 的场景标记对应上表。更换手机内容时，同时核对 video 元素的素材、首帧和起止时间。
- [materials/](materials/) 保存时间线直接使用的 MP4、首帧、品牌字标、贴贴照片和 Cilly 头像。[recordings/](recordings/) 保存可重新裁切的 WebM 录屏和图鉴横滑的操作记录。图鉴当前采用暖色录屏对应的剪辑。
- [assets/](assets/) 保存现用配乐、原曲、混音前版本、早期合成配乐和网页字体。公开分发时保留原作者、CC BY 4.0 与改动说明，详见[配乐授权](materials.md)。
- [history/](history/) 保存九份早期 HTML 时间线，素材路径已调整为从该目录读取。要用花叔 Motion 继续编辑旧版，可复制到单独工程，再按时间线中的相对路径放置素材。
- [legacy-20s/](legacy-20s/) 保存最早的 20 秒纯手机展示、五段原片、手机框、音乐和 Python 合成脚本。在仓库根目录运行「python 02-product-demo/legacy-20s/assemble.py legacy-recut.mp4 ffmpeg」可以重剪，需要 Pillow、NumPy 和 FFmpeg。

## 预览与导出

在仓库根目录运行。需要 Node.js、Chrome，以及 PATH 里的 FFmpeg 和 ffprobe。

~~~sh
npx -y huashu-motion@0.5.1 studio 02-product-demo
npx -y huashu-motion@0.5.1 check 02-product-demo
npx -y huashu-motion@0.5.1 render 02-product-demo --fps 30
~~~

新导出写入 **out/**。0.5.1 可能提示 no soundtrack，这里使用时间线里指定的 WAV，重导出已确认包含配乐。改图鉴时可先检查 16–22 秒，对照 [6 秒图鉴单段](out/Only-Cats-Catalog-6s.mp4)。

## 版本与导出素材

| 文件 | 用途 |
| --- | --- |
| [30 秒图鉴横滑版](out/Only-Cats-UI-Launch-30s-Catalog-Swipe.mp4) | 当前单独成片 |
| [Playful](out/Only-Cats-UI-Launch-30s-Playful.mp4)、[Groove](out/Only-Cats-UI-Launch-30s-Groove.mp4)、[30 秒初版](out/Only-Cats-UI-Launch-30s.mp4) | 之前的配乐和节奏剪辑 |
| [早期导出](out/drafts/) | v1–v3、早期乐谱和曾用过的动画插段 |
| [分享包](out/share/) | GIF 和发布文案 |
| [审片截图](out/sheets/) | 对照各版的画面和切换 |
