# Cat PUZZLE 四段简笔画动画

小帅最近下载了一个 App。四段童话式短故事分别演示偶遇广场、好友偶遇提醒、猫咪图鉴与 Cilly，以及用语音发布偶遇。

[合辑 MP4](<Cat PUZZLE-四段动画合辑.mp4>) · [合辑字幕](<Cat PUZZLE-四段动画合辑.srt>) · [初版剧本](<docs/初版剧本.md>)

| 合辑时间 | 内容 | 单段成片 |
| --- | --- | --- |
| 0:00 | 偶遇广场 | [第一段](<episode-01/output/第一段-偶遇广场-更新跑步台词.mp4>) |
| 0:19 | 好友偶遇提醒 | [第二段](<episode-02/output/第二段-好友偶遇提醒-更新跑步台词.mp4>) |
| 0:37 | 猫咪图鉴和 Cilly | [第三段](<episode-03/output/第三段-猫咪图鉴和Cilly-头像版.mp4>) |
| 0:58 | 给 Cilly 发语音 | [第四段](<episode-04/output/第四段-给Cilly发语音.mp4>) |
| 1:23 | 那么，这个 APP 是什么呢？ | [转场旁白](assets/transition-narration.mp3) |

合辑全长 1 分 25.7 秒，1280 × 720，30 fps。第二至第四段重复的开场和牵手结尾为 1.3 倍速，保留旁白音高。

![合辑末尾的转场画面](assets/transition-still.jpg)

## 制作素材

- 各段的 **source/** 保存角色动作、猫咪等原始插画和生图提示词。Cilly 的 [矢量头像](assets/cilly-avatar.svg) 另附在 **assets/**。
- **audio/** 保存逐句配音。**audio/drafts/** 中是有别于成片的早期录音。旁白用豆包「悠悠君子 2.0」，小帅的语音留言用「清爽男大 2.0」。
- **output/** 保存单段成片、分镜图、字幕、音效底轨和历史剪辑。
- 各段的 **render.py** 绘制画面并合成配音。**compose.py** 重剪合辑并渲染最后的提问分镜。插画已随仓库提供，重剪和渲染只使用本地文件。

## 本地重剪

在本目录运行以下命令。渲染脚本使用 Windows 的楷体和微软雅黑。运行前安装 Python 3.10 或更新版本、Pillow、NumPy，以及启用 H.264 编码的 FFmpeg。

~~~powershell
python -m pip install Pillow numpy
python compose.py --ffmpeg ffmpeg
~~~

重剪成片与字幕会写到 **build/**。修改某段后，可以先运行对应的渲染脚本，再重剪合辑。比如第四段使用以下命令。

~~~powershell
python episode-04/render.py --ffmpeg ffmpeg
~~~
