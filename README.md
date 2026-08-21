# cardshot — HTML 卡片截图工作室

本地 WebUI：AI 生成一批 HTML 卡片 → 浏览器式预览缩放 → 按社交媒体比例（3:4 / 9:16 / 1:1 / 16:9 / 自定义）一键截图 / 批量截图。

**不生成图片内容，只负责"网页 → 图"的最后一公里。** 内容由 AI（Hermes / Claude / 任意 LLM）生成 HTML 放进 `cards/` 即可。

## 快速开始

```bash
cd ~/work/GitHub/cardshot
python3 server.py          # 打开 http://localhost:8765
```

CLI 单张 / 批量截图（不开界面）：

```bash
python3 shooter.py cards/demo-card.html                    # 默认 1080×1440
python3 shooter.py cards/demo-card.html -w 1080 -h 1920    # 9:16
python3 shooter.py cards/ -w 1080 -h 1440 --scale 2        # 整个目录批量, 2x 高清
```

## 工作流

1. 让 AI 按你的风格约定生成一系列 HTML 知识卡片，存到 `cards/`（一页一文件）
2. 打开 WebUI，左侧选卡片，中间实时预览
3. 顶部切换目标比例（小红书 3:4、抖音 9:16、微信封面 2.35:1、自定义…）
4. 缩放滑杆检查细节（25%–100% + 一键适配）
5. 「截图」出当前张，「全部截图」批量出图，图片落 `output/`
6. 输出分辨率 = 比例尺寸 × 倍率（2x = 视网膜高清）

## 目录

```
cardshot/
├── server.py        # 本地 Web 服务（stdlib，无依赖）
├── shooter.py       # 截图核心 + CLI（headless Chrome）
├── static/index.html# WebUI
├── cards/           # AI 生成的 HTML 卡片放这里
└── output/          # 截图输出（gitignore）
```

## 依赖

- Python 3.9+（仅标准库）
- macOS 上的 Google Chrome（`/Applications/Google Chrome.app`，即 headless 截图引擎）

## API（供 AI / 脚本调用）

- `GET  /api/cards` → 卡片列表
- `POST /api/shoot` `{file, w, h, scale}` → 截单张，返回输出路径
- `POST /api/shoot_all` `{w, h, scale}` → 批量截图
- `GET  /api/reveal?path=...` → Finder 中定位文件
