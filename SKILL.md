---
name: cardshot
description: 内容→多平台社媒卡片出图。做小红书/抖音/X/公众号配图、知识卡片批量出图时用。
---

# cardshot — 内容驱动的多平台知识卡片流水线

一份调研/内容 → N 张平台适配卡片图。AI 写 HTML 卡片，本工具（`shooter.py`）负责“网页 → 图”的最后一公里：风格库预览、批量出图与质量检查。

小红书卡片的核心流程不是“选一个好看的模板”，而是：**先读懂内容，再决定用户怎么读；先确定信息结构，再选择最能承载它的视觉风格。** 具体规则见 [`references/content-driven-design.md`](references/content-driven-design.md)。

## 何时用
- 要把内容做成知识卡片 / 社媒配图，一份内容发多个平台（小红书 / 抖音 / X / 公众号 / 知乎…）
- 已有一批 HTML 卡片，需要各平台尺寸的 PNG
- 单平台小红书图文（HTML + Chrome 截图，不调生图 API）

## 设计入口
- **内容驱动规范**：先写内容契约，再定信息拓扑、风格、封面 brief 和内容页 outline
- **风格库**：`gallery.html`（纯静态，浏览器直接打开，无需服务器）— 每个风格一节（封面 + 内容页）；新增风格在 `scripts/build-gallery.py` 的 STYLES 表登记后重新生成
- **风格匹配**：`references/style-library.md` — 当前 3 套样卡的语义适配、承载边界和 token
- **平台规范**：`references/platform-conventions.md` — 尺寸、字号、密度和验收口径

## 工具速查
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
- 零依赖：Python 标准库 + Chrome/Chromium/Edge（quality-check 和 --grid 需 Pillow）

## 标准流程（内容优先，六步）
1. **内容诊断**：阅读完整源文，写出内容契约（主张、受众、阅读动作、内容类型、证据形态、信息拓扑、情绪温度、收藏理由、不可删信息）。先判断用户要怎么读，不先选风格。
2. **结构拆解**：确定卡片序列的阅读弧线（封面 → 铺垫 → 核心 → 收获 → 结尾），为每页指定一个阅读问题、一个主结构和一个结论。详细模板见 `references/content-driven-design.md`。
3. **风格匹配**：按“信息拓扑 > 证据形态 > 阅读动作 > 受众语气 > 主题名词”选首选、备选和排除项，并记录理由。再为每页选择 sparse / balanced / dense / list / comparison / flow 等结构，不让一个关键词直接决定整组卡片。
4. **封面与内容页 brief**：封面只保留中文钩子、必要范围、副标题、一个语义主锚点和内容型承接；内容页遵循“一个主结构 + 一个辅助结构 + 一句结论”，超过密度阈值就拆页。封面与内容页的装饰必须来自内容语义，不用随机图形填空。
5. **写卡与验收**：每平台一个 HTML 放 `cards/`，必须带 `<meta name="card-size" content="WxH">`、固定画布尺寸和 `overflow:hidden`。写前必读 `references/platform-conventions.md` 与 `references/style-library.md`；正文行内强调必须包在 `.copy`/`.body` 中，避免匿名 flex item 破坏换行。
6. **出图与交付**：先跑 `python3 scripts/check-overflow.py <目录或文件> --margin 40`，再出图和像素质检；浅底卡传真实底色。HTML 改动后重新生成对应 PNG，并核对源 HTML、gallery、PNG 的标题和品牌文案；最后同时做实际尺寸和缩略图目检。

## 平台速览（细节见 references/platform-conventions.md）
| 平台 | 尺寸 | 设计语言 | 信息密度 |
|---|---|---|---|
| 小红书 | 1080×1440 | 米白暖底 / 荧光笔标记 / 按内容匹配视觉语言 | 封面低密度，内容页中到高密度，结尾低密度 |
| 抖音 | 1080×1920 | 黑底光晕 / 超大数字视觉锤 / CTA | 低 |
| X 卡 | 1600×900 | 推特黑 / 品牌蓝 / 账号头衔 / 🧵 | 中（英文 hook） |
| 通用横图 | 1920×1080 | 深紫渐变 / 条形图对比 | 中 |
| 公众号封面 | 900×383 | 左钩子右大数字 / 网格质感 | 极低 |

活体范例：`cards/seedance-*.html`（一份视频模型价格调研 → 5 平台卡片）。

## 坑（都踩过）
- **Chrome 双重放大**：`--window-size` 永远用 CSS 像素，倍率只交给 `--force-device-scale-factor`；两者都乘 → 4x 尺寸错误
- **卡片必须自包含**：内联 CSS、无外链图片；字体走 Google Fonts 白名单（Noto Serif SC / Playfair Display / Noto Sans SC / Inter / IBM Plex Mono，见 `references/style-library.md` 字体体系表），`<head>` 加载链接后必须保留 system 字体栈兜底（断网/离线自动降级）。shooter 的 `--virtual-time-budget=8000` 会等字体加载，截图字体异常先查网络
- **内容贴边**：距画布边 ≥40px（check-overflow 的默认 margin），否则视觉上像被裁
- **测试数据污染**：测试改过卡片后要恢复原件（`cards/.backups/`），别把测试文案交付出去
- **quality-check 浅底误报**：米白/浅色底卡必须传 `--bg`，否则四角检查把设计底色当白边报 WARN
- **quality-check 底部条带误报（更隐蔽）**：浅底卡带深色吸底结论框时，底部条带方差检查会报 `底部条带杂色(方差XXXX, 可能截字)` 的 WARN。这是误报——结论框是圆角且 body 留了 ~56px 底边距，所以真正画布最底 56px 仍是纯净设计底色。确认方法：check-overflow 通过（内容底线 ≤ 高且 ≥ 安全边距）即权威；再用像素抽检最底 56px 均值≈底色即可，不必理会该 WARN。不要因为 WARN 就去削内容。
- **check-overflow 只收单个 target**：参数为单个目录或单个文件，传多个文件（`cards/a.html cards/b.html`）会报 `unrecognized arguments`。批量检查把同批卡片放子目录（如 `cards/steer/`）后传目录；出图同理 `python3 shooter.py cards/steer/ --auto -o output/steer`。
- **改完记得 commit**：本 skill 软链到 github.com/limboinf/cardshot 仓库，编辑 SKILL.md / 卡片 / 脚本后需 `git commit` 推送（memory: 改skill=改仓库+commit）。

## 目录
```
cardshot/
├── shooter.py / gallery.html        # 工具本体 + 风格库预览墙
├── cards/           # HTML 卡片（含 seedance 5 卡范例）
├── references/
│   ├── content-driven-design.md         # 内容契约、风格匹配、封面与内容页结构
│   └── platform-conventions.md          # 平台规范：配色/密度/结构/字号/质检代码
├── scripts/         # check-overflow.py / shoot.sh / quality-check.py
└── output/          # PNG 输出（gitignore）
```
