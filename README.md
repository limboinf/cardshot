# cardshot — HTML 卡片截图工作室

**AI 生成 HTML 卡片 → 一键出各平台尺寸 PNG。** 本地 WebUI + CLI 双模式，零依赖（Python 标准库 + 你机器上已有的 Chrome）。同时是一个可复用的 **Agent Skill**（本仓库自带 `SKILL.md`，见下）。

核心流程：AI（Claude / Hermes / 任意 LLM）按你的风格约定生成一批 HTML 知识卡片放进 `cards/` → 你在 WebUI 里预览、切比例、用内置代码编辑器实时微调 → CLI 或网页按钮批量出图。**不生成内容，只负责“网页 → 图”的最后一公里。**

```
AI 写卡 → cards/*.html → WebUI 预览/编辑 → shooter.py → output/*.png → 发小红书/抖音/X/公众号
```

## 快速开始

```bash
cd ~/work/GitHub/cardshot
python3 server.py                # WebUI: http://localhost:8766
```

CLI 直接出图（不开界面）：

```bash
python3 shooter.py cards/demo-card.html              # 单张 1080×1440
python3 shooter.py cards/ -w 1080 -h 1920            # 整目录 9:16
python3 shooter.py cards/ --auto                     # 按每张卡自带尺寸出图
python3 shooter.py cards/ -p xhs douyin              # 指定平台预设批量
python3 shooter.py cards/ --all-presets --scale 2    # 全预设 × 2x 高清
python3 shooter.py cards/ -p xhs --grid 2x3          # 出图后拼网格长图
```

## CLI 参数（shooter.py）

| 参数 | 说明 |
|---|---|
| `target` | HTML 文件或目录（目录 = 批量） |
| `-W/-H` | 画布宽高（默认 1080×1440） |
| `-p, --preset <name>...` | 平台预设，可多个（见下表） |
| `--all-presets` | 每张卡按全部预设各出一张 |
| `--auto` | 自动读每张卡自带尺寸（`<meta name="card-size">` 或 body CSS 宽高） |
| `--scale <n>` | 输出倍率（2 = 视网膜高清） |
| `--grid CxR` | 出图后拼接网格长图（需 `pip3 install Pillow`） |
| `-o, --out <dir>` | 输出目录（默认 `./output`） |
| `--list-presets` | 列出全部预设 |

### 平台预设

| name | 尺寸 | 平台 |
|---|---|---|
| `xhs` | 1080×1440 | 小红书 3:4 |
| `douyin` | 1080×1920 | 抖音/视频号 9:16 |
| `square` | 1080×1080 | 方图 1:1（Ins/朋友圈） |
| `twitter` | 1600×900 | X/Twitter 16:9 |
| `wide` | 1920×1080 | 通用横图 FHD |
| `wechat-cover` | 900×383 | 公众号封面 2.35:1 |
| `zhihu` | 1080×2340 | 知乎长图卡 |

```bash
python3 shooter.py cards/ -p xhs douyin square        # 一张卡 → 3 个平台
python3 shooter.py cards/ --auto                      # 卡片写什么尺寸就出什么
python3 shooter.py cards/ --grid 2x3                  # 6 图拼 2 列长图
```

### 场景速查

- **一批调研 → 全平台发布**：AI 一次写 5 张卡（每张自带 `card-size` meta）→ `python3 shooter.py cards/ --auto`
- **同卡多平台**：`python3 shooter.py cards/foo.html --all-presets`
- **高清印刷**：`--scale 2`（1080 宽卡 → 2160px 输出）
- **多图并一图**：`--grid 2x3` 拼长图，省平台九宫格手拼

## WebUI

```bash
python3 server.py    # 自动开浏览器 → http://localhost:8766
```

- 左侧卡片列表，中间实时预览，顶部比例 chip 一键切换（3:4 / 9:16 / 1:1 / 16:9 / 2.35:1 / 自定义）
- **内置代码编辑器**（⌘E）：改 HTML 停手 900ms 自动保存，预览实时刷新；⌘S 手动保存；首次修改自动备份原件（`cards/.backups/`），一键恢复
- **新建卡片**：自带 1080×1440 暗色模板
- 「截图」当前张 / 「全部截图」批量，图片落 `output/`
- 缩放滑杆 25%–100% 检查细节，输出分辨率 = 画布 × 倍率

## 给 AI 的写卡约定

卡片是自包含 HTML（内联 CSS，无外部依赖），尺寸二选一：

1. `<meta name="card-size" content="1080x1440">`（推荐，`--auto` 直接识别）
2. `body { width: 1080px; height: 1440px; }`（CSS 固定宽高，也能被识别）

要点：所有样式内联在 `<style>`；不引外链字体/图片（headless 截图不等待网络）；深浅底自定，但内容别贴边（留 ≥40px 边距，防溢出裁切）。

## API（供 AI / 脚本调用）

| 端点 | 说明 |
|---|---|
| `GET /api/cards` | 卡片列表 |
| `POST /api/shoot {file,w,h,scale}` | 截单张 |
| `POST /api/shoot_all {w,h,scale}` | 整目录批量 |
| `GET /api/source?f=` | 读卡片源码 |
| `POST /api/save {file,content}` | 保存卡片（首次自动备份原件） |
| `GET /api/backup?f=` | 读首次修改前的原件 |
| `GET /api/outputs` | 输出列表 |

## 目录结构

```
cardshot/
├── server.py        # WebUI 服务 (stdlib, 零依赖)
├── shooter.py       # 截图核心 + CLI (headless Chrome)
├── static/index.html# WebUI 前端
├── SKILL.md         # Agent Skill 入口 (见下节)
├── references/      # 平台规范: 配色/信息密度/结构套路 (skill 引用文件)
├── scripts/         # check-overflow / shoot / quality-check (skill 脚本)
├── cards/           # AI 生成的 HTML 卡片 (含 seedance 5 卡范例)
└── output/          # PNG 输出 (gitignore)
```

## 作为 Agent Skill 使用

本仓库同时是一个标准 Agent Skill（`SKILL.md` + `references/` + `scripts/`），供任何 LLM agent（Claude Code / Hermes / Cursor…）直接加载：agent 读 `SKILL.md` 获得五步工作流，按 `references/platform-conventions.md` 的平台规范写卡，用 `scripts/` 里的脚本做溢出检测、批量出图和质检。脚本路径全部相对仓库，clone 到哪都能跑。

两种接法：

```bash
# 1. Claude Code 风格: clone 后直接作为项目 skill
git clone https://github.com/limboinf/cardshot ~/cardshot

# 2. Hermes: 软链到 skills 目录
ln -s ~/cardshot ~/.hermes/skills/creative/cardshot
```

人说的话：把内容发全平台时让 agent 加载本 skill；agent 的说法：触发词为“知识卡片 / 社媒配图 / 多平台出图”。

## 许可

未设置开源许可证，保留所有权利（All rights reserved）。个人使用、fork 学习请自便；商用或转载请先联系作者。

## 依赖

- Python 3.9+（标准库；`--grid` 拼图需 `pip3 install Pillow`）
- Google Chrome（`/Applications/Google Chrome.app`；Chromium/Edge 亦可）

## 已实测场景

- 6 张卡 × `--auto` 全自动出图（各按自带尺寸）✓
- 指定预设批量 `-p xhs douyin` ✓
- 网格拼接 `--grid 1x1` ✓
- WebUI 端到端：编辑器改码 → 自动保存 → 预览刷新 → 截图落盘 ✓
- 2x/4x 高清 `--scale` ✓
