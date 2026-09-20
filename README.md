# bilibili_video_crawing
哔哩哔哩，B站视频和封面原图爬取
主要界面
![image](https://user-images.githubusercontent.com/66453249/213915578-11a9a11f-3db3-4d85-b726-c2cf8a1e3791.png)
![image](https://user-images.githubusercontent.com/66453249/213915628-304bb653-4ef1-4ab2-b39e-2cc833c0a8c7.png)

现使用时发现还是得有个预览封面的功能，已增添上去。

其中about_test 的文件为测试文件夹，可供思路研究
如果要直接使用，把里面的jm_cmd_B站视频封面爬取.exe文件 + info.json + ffmpeg.exe，
这三个文件拿出来放到一个文件夹里面就可以正常使用

三个 exe 的区别（都已按 2026 的新接口重新打包）：

| exe | 说明 |
| --- | --- |
| `jm_B站视频封面爬取.exe` | 界面版，双击就能用，推荐给普通用户 |
| `jm_cmd_B站视频封面爬取.exe` | 界面版 + 控制台窗口，出问题时能看到详细报错 |
| `dist/jm_cli.exe` | 纯命令行版，参数见下面的「命令行版」 |

具体的代码思路可以看看这篇文章：
https://www.bilibili.com/read/cv21098039

---

## 更新记录

### 2026-09-20：适配 B 站 WBI 强制签名（本次变更）

**问题**：B 站升级后 `player/playurl` 接口把 WBI 签名变成了强制项，
而旧代码是「请求网页 → 正则抠 `window.__playinfo__`」，
网页里已经不再稳定带播放地址，因此老爬虫直接失效（解析不出音视频流）。

**修复**：把取流逻辑整体换成官方 API + WBI 签名，并补齐了几个不补就会被风控 / 403 的细节。

改动清单：

| 文件 | 本次变动 |
| --- | --- |
| `wbi.py` | **新增**。WBI 签名实现（取密钥 / 生成 mixin_key / 算 w_rid），以及带请求头、buvid 指纹、重试的会话与接口封装 |
| `ffmpegTool.py` | **新增**。定位 ffmpeg 并执行命令，避免模块之间循环 import |
| `jmCommon.py` | **新增**。读取 cookie、文件名过滤等公共小工具 |
| `jm_cli.py` | **新增**。命令行版下载器 |
| `jm_wbi_check.py` | **新增**。WBI 自检 / 排查脚本 |
| `getVideo.py` | **重写**。改为 view + playurl(wbi) 取流；流式下载；`-c:v copy` 合成；地址过期自动刷新重试；支持整条链接、`?p=`、b23 短链、av 号 |
| `getVideoPicture.py` | **重写**。封面 / UP主 / 标题改从 view 接口取，不再靠正则抠网页 |
| `VideoToAudio.py` | **重写**。不再依赖 `ffmpy` 和 PATH 里的 ffmpeg，统一走 `ffmpegTool`；新增 `extractAudio()` 直接由音频流转 mp3 |
| `CookieOperation.py` | **重写**。由「只留 SESSDATA」改为保留整条 cookie 的所有字段（SESSDATA、buvid3、bili_jct 等），更不容易被风控 |
| `jm_bilibil_video.py` | 小改。链接支持整条粘贴、输出目录校验、封面按钮加异常提示、cookie 弹窗加说明文案 |
| `getPreviewPictures.py` | 小改。兼容高版本 Pillow（`Image.ANTIALIAS` 已移除） |
| `jm_bilibil_video.spec` | 打包界面版 exe（本次未改动，沿用） |
| `jm_bilibil_video_cmd.spec` | **新增**。打包「界面 + 控制台」版 exe |
| `jm_cli.spec` | **新增**。打包命令行版 exe |
| `jm_B站视频封面爬取.exe` | **重新打包**（覆盖旧版） |
| `jm_cmd_B站视频封面爬取.exe` | **重新打包**（覆盖旧版，界面 + 控制台） |
| `dist/jm_bilibil_video.exe`、`dist/jm_cli.exe` | **重新打包** |

重新打包后每个 exe 约 59.5MB（旧版约 33MB），变大是因为 Python 3.11 + tkinter + requests 打进了单文件，
功能上没有影响。

> 备注：`bilibili_video_install.spec`（引用了一个已经不存在的 `bilibili_video_install.py`）和
> `jm_bilibili_video.spec`（与 `jm_bilibil_video.spec` 内容重复）都是历史遗留文件，可以忽略或删掉。

### 历史版本

* 增加「只爬取音频」的选项，界面新增预览 / 保存封面按钮，下载的视频如果已存在则覆盖。

---

## 接口与 WBI 签名说明

本次修订把取流逻辑整个换成官方 API：

| 用途 | 接口 |
| --- | --- |
| 视频标题 / UP主 / 封面 / 各分P的 cid | `api.bilibili.com/x/web-interface/view` |
| 音视频流地址（需 WBI 签名） | `api.bilibili.com/x/player/wbi/playurl` |
| 获取 wbi 密钥 | `api.bilibili.com/x/web-interface/nav` |
| 匿名指纹（buvid3 / buvid4） | `api.bilibili.com/x/frontend/finger/spi` |

**WBI 签名的三步逻辑**（实现见 `wbi.py`）：

1. 从 `nav` 接口取 `img_key`、`sub_key`（就是 wbi 图片文件名的 MD5）；
2. 两个 key 拼接后按固定混淆表 `MIXIN_KEY_ENC_TAB` 重排，取前 32 位得到 `mixin_key`；
3. 请求参数按 key 的字典序排序、过滤 `!'()*` 这几个字符，拼上时间戳 `wts` 与 `mixin_key` 做 MD5，得到 `w_rid`。

除了签名，还补齐了这些必要细节，否则很容易被风控（`-352`）或 CDN `403`：

* 请求头带 `Referer: https://www.bilibili.com/` 与真实浏览器 UA；
* 未登录时先向 `x/frontend/finger/spi` 要一个 `buvid3/buvid4` 匿名指纹；
* 音视频流改成流式边下边写盘（老代码把整个文件读进内存，大视频容易炸）；
* 视频流 `-c:v copy` 直接封装，不再重新编码（老代码重编码又慢又掉画质），音频转 AAC 保证 mp4 兼容；
* 播放地址有效期很短，下载失败会自动刷新地址重试一次；
* wbi 密钥缓存 30 分钟，签名失败时自动强制刷新重签。

## 文件说明

| 文件 | 作用 |
| --- | --- |
| `jm_bilibil_video.py` | tkinter 界面主程序（入口） |
| `jm_cli.py` | 命令行版本，不想开界面时用 |
| `jm_wbi_check.py` | WBI 自检脚本：打印 mixin_key、标题、封面、可选画质，排查问题时先跑它 |
| `wbi.py` | WBI 签名 + 官方 API 封装 |
| `getVideo.py` | 解析链接、取流、下载、ffmpeg 合成 |
| `getVideoPicture.py` | 封面原图地址获取与保存（也改走 API 了） |
| `VideoToAudio.py` | 提取音频为 mp3 |
| `ffmpegTool.py` | 定位 ffmpeg 并执行命令 |
| `jmCommon.py` | 读取 cookie、文件名过滤等小工具 |
| `CookieOperation.py` | cookie 字符串转字典（保留 SESSDATA、buvid3 等全部字段） |
| `getPreviewPictures.py` | 界面里的封面预览 |
| `info.json` | 配置：输出目录 + cookie，界面里改 |
| `ffmpeg.exe` | 音视频合成 / 转 mp3 用，要和 exe 放同一目录 |

## 使用方式

界面版：双击 `jm_B站视频封面爬取.exe`（看报错用 `jm_cmd_B站视频封面爬取.exe`，源码运行则是 `python jm_bilibil_video.py`）。

命令行版：

```bash
python jm_cli.py "https://www.bilibili.com/video/BV1B8rPBCELm/" -o D:/视频
python jm_cli.py BV1BDk2YCEHF -p 2 -o D:/视频      # 下载第2个分P
python jm_cli.py BV1B8rPBCELm -o D:/音频 --audio    # 只导出 mp3
```

视频 URL 可以直接粘贴浏览器地址栏里的整条链接，带 `?p=2` 时会自动识别分P
（链接里的分P 优先于界面上填的「集数」）；b23.tv 短链、`av` 号也能识别。

使用时，如果不添加cookie，则下载的视频质量最高只有480P，
添加cookie的方法，打开B站网页，登陆账号，然后F12，点到“网络”，再刷新网页，随便点一条获取到的请求，都有cookie：
![8ca1e6e24159a5427e9961a42e93f77f_74c5e54eae46d197a32370629e692c108a79400e](https://user-images.githubusercontent.com/66453249/211441821-2e0b58ce-8c15-4886-b3b6-068e3a75ebcb.png)

把整条 cookie 直接粘进界面里的「添加Cookie」即可，SESSDATA / buvid3 等字段会一起保存，
带上越多越不容易被风控，也能下载自己账号有权观看的画质。

## 打包 exe

```bash
python -m PyInstaller jm_bilibil_video.spec --noconfirm       # 界面版 -> dist/jm_bilibil_video.exe
python -m PyInstaller jm_bilibil_video_cmd.spec --noconfirm   # 界面+控制台版 -> dist/jm_cmd_B站视频封面爬取.exe
python -m PyInstaller jm_cli.spec --noconfirm                 # 命令行版 -> dist/jm_cli.exe
```

打包后把 exe 与 `info.json`、`ffmpeg.exe` 放在同一目录即可使用（根目录那两个 exe 就是 dist 里构建结果的副本）。

## 常见问题

* **最高只有 480P**：没带 cookie，或 cookie 已过期。带上有效的 SESSDATA 后再试；4K / HDR / 杜比这些还要账号本身有大会员。
* **提示「账号未登录 / 请求过于频繁」(-352)**：被风控了，等一会儿重试、换个网络，或者补上 cookie。
* **封面 / 标题显示不出来**：稿件可能已失效或被删除，界面会直接提示接口返回的错误码。
* **找不到 ffmpeg**：项目里的 `ffmpeg.exe` 要和 exe 放在同一目录，或者把 ffmpeg 加到 PATH。

拿不准问题出在哪时，先在项目根目录执行：

```bash
python jm_wbi_check.py BV1B8rPBCELm
```

它会依次打印 wbi 密钥、视频标题、封面地址、该稿件的全部可选画质，以及当前账号实际能拿到的画质，
一眼就能看出是签名问题、cookie 问题还是权限问题。

## 本次修改的验证情况

* 用 `BV1B8rPBCELm` 实测：正确拿到 `mixin_key`、playurl 返回 480P(匿名) 视频流与 192K 音频流，
  下载并合成出 `[UP主] - 标题_jm.mp4`，ffprobe 确认含 H.264 视频 + AAC 音频；只下音频得到 mp3。
* 用一个 150 分P 的稿件实测 `?p=2`：分P 名与文件都正确。
* 封面原图保存成功（走 view 接口的 `pic` 字段）。
* 分P 越界、输出目录不存在、链接非法等情况都会在输出台给出明确提示。
* 打包后的 `jm_cli.exe` 实际联网下载过一次；根目录两个 exe 均已重新打包并启动验证。
