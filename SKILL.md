---
name: cardshot
description: 内容→多平台社媒卡片出图。做小红书/抖音/X/公众号配图、知识卡片批量出图时用。
---

# cardshot — 内容 → 多平台知识卡片流水线

一份调研/内容 → N 张平台适配卡片图。AI 写 HTML 卡片，本工具（`shooter.py` + `server.py`）负责"网页 → 图"的最后一公里：按平台比例预览、实时改码、一键批量出图。

## 何时用
- 要把内容做成知识卡片 / 社媒配图，一份内容发多个平台（小红书 / 抖音 / X / 公众号 / 知乎…）
- 已有一批 HTML 卡片，需要各平台尺寸的 PNG
- 单平台小红书图文（HTML + Chrome 截图，不调生图 API）

## 工具速查
- **WebUI**：`python3 server.py` → http://localhost:8766 （预览 / 比例切换 / 代码编辑器实时改码）
- **CLI**（`shooter.py`）：
  - `python3 shooter.py cards/ --auto` — 逐张读卡片自带尺寸出图（主路径）
  - `python3 shooter.py cards/ -p xhs douyin` — 平台预设批量；`--all-presets` 全预设
  - `python3 shooter.py --list-presets` — 查全部预设（xhs / douyin / square / twitter / wide / wechat-cover / zhihu）
  - `--scale 2` 高清 ｜ `--grid 2x3` 拼网格长图（需 Pillow）｜ `-o` 输出目录
  - 宽高参数是大写 `-W/-H`（`-h` 与 argparse help 冲突）
- **skill 脚本**（本目录 `scripts/`）：
  - `scripts/check-overflow.py <卡/目录> [--margin 40]` — 溢出检测，退出码 0/1
  - `scripts/shoot.sh auto|all|presets <名...>|one <参数>` — 出图封装（路径相对仓库）
  - `scripts/quality-check.py <png/目录> [--bg faf6ef]` — 像素质检（浅底卡必须传 `--bg`）
- **API**（server.py 起着时）：`POST /api/shoot {file,w,h,scale}` ｜ `POST /api/shoot_all` ｜ `GET /api/cards`、`/api/outputs`、`/api/source?f=`、`POST /api/save`、`GET /api/backup?f=`
- 零依赖：Python 标准库 + Chrome/Chromium/Edge（quality-check 和 --grid 需 Pillow）

## 标准流程（五步）
1. **写卡**：每平台一个 HTML 放 `cards/`，命名 `{topic}-{platform}.html`。必须带 `<meta name="card-size" content="WxH">`（`--auto` 靠它识别）+ `body{width/height 固定; overflow:hidden}`。风格按平台分治——**写前必读 `references/platform-conventions.md`**（各平台配色语言/信息密度/结构套路/字号下限）；视觉风格选型见 **`references/style-library.md`**（11 套实测风格 + 封面/内容页分工约定）
2. **溢出检测**：`python3 scripts/check-overflow.py cards/` — 全 OK 才出图；报 OVERFLOW 修布局再检
3. **出图**：`scripts/shoot.sh auto`（主路径）或 `presets xhs douyin`；不要自己另拼 Chrome 命令
4. **像素质检**：`python3 scripts/quality-check.py output/*.png --bg <底色hex>`；浅底卡必须传 `--bg` 否则误报。有视觉模型则加目检，没有则 DOM + 像素即兜底
5. **交付**：发送前 `ls` 验证文件存在；只发卡片本体 PNG（别把 WebUI 界面截图当成品交付）

## 平台速览（细节见 references/platform-conventions.md）
| 平台 | 尺寸 | 设计语言 | 信息密度 |
|---|---|---|---|
| 小红书 | 1080×1440 | 米白暖底 / 荧光笔标记 / 价格格+结论框 | 高 |
| 抖音 | 1080×1920 | 黑底光晕 / 超大数字视觉锤 / CTA | 低 |
| X 卡 | 1600×900 | 推特黑 / 品牌蓝 / 账号头衔 / 🧵 | 中（英文 hook） |
| 通用横图 | 1920×1080 | 深紫渐变 / 条形图对比 | 中 |
| 公众号封面 | 900×383 | 左钩子右大数字 / 网格质感 | 极低 |

活体范例：`cards/seedance-*.html`（一份视频模型价格调研 → 5 平台卡片）。

## 坑（都踩过）
- **Chrome 双重放大**：`--window-size` 永远用 CSS 像素，倍率只交给 `--force-device-scale-factor`；两者都乘 → 4x 尺寸错误
- **卡片必须自包含**：内联 CSS、无外链字体/图片（headless 截图不等网络），字体用 system 栈
- **内容贴边**：距画布边 ≥40px（check-overflow 的默认 margin），否则视觉上像被裁
- **测试数据污染**：编辑器/测试改过卡片后要恢复原件（`/api/backup` 或 `cards/.backups/`），别把测试文案交付出去
- **quality-check 浅底误报**：米白/浅色底卡必须传 `--bg`，否则四角检查把设计底色当白边报 WARN
- **quality-check 底部条带误报（更隐蔽）**：浅底卡带深色吸底结论框时，底部条带方差检查会报 `底部条带杂色(方差XXXX, 可能截字)` 的 WARN。这是误报——结论框是圆角且 body 留了 ~56px 底边距，所以真正画布最底 56px 仍是纯净设计底色。确认方法：check-overflow 通过（内容底线 ≤ 高且 ≥ 安全边距）即权威；再用像素抽检最底 56px 均值≈底色即可，不必理会该 WARN。不要因为 WARN 就去削内容。
- **check-overflow 只收单个 target**：参数为单个目录或单个文件，传多个文件（`cards/a.html cards/b.html`）会报 `unrecognized arguments`。批量检查把同批卡片放子目录（如 `cards/steer/`）后传目录；出图同理 `python3 shooter.py cards/steer/ --auto -o output/steer`。
- **改完记得 commit**：本 skill 软链到 github.com/limboinf/cardshot 仓库，编辑 SKILL.md / 卡片 / 脚本后需 `git commit` 推送（memory: 改skill=改仓库+commit）。

## 目录
```
cardshot/
├── server.py / shooter.py / static/   # 工具本体
├── cards/           # HTML 卡片（含 seedance 5 卡范例）
├── references/
│   └── platform-conventions.md        # 平台规范：配色/密度/结构/字号/质检代码
├── scripts/         # check-overflow.py / shoot.sh / quality-check.py
└── output/          # PNG 输出（gitignore）
```
