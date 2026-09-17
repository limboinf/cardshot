# 平台卡片规范（2026.8 首版，Seedance 5 卡实测定稿）

活体范例：`~/work/GitHub/cardshot/cards/seedance-*.html`。改规范时先看范例再动表。

## 共同骨架
```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  width: <平台宽>px; height: <平台高>px; overflow: hidden;
  font-family: "PingFang SC", -apple-system, "Helvetica Neue", sans-serif;
  /* 布局 + 固定 padding，贴边安全区 ≥40px */
}
```
- 内容边界距画布边最少留 ~40px（实测最紧一张 41px 仍安全）
- 中文字号下限：正文 ≥24px（900px 宽）/ ≥26px（1080px 宽），标题 60-96px
- 字体：通用卡用上面 system 栈；选用风格库样式时按 [`style-library.md`](style-library.md)「字体体系」在 `<head>` 加载 Google Fonts 白名单并保留此栈兜底
- 数据要有来源行（如"数据：火山引擎 2026.7 官方定价"）

## 各平台策略
| 平台 | 尺寸与物理像素 | 底色/语言 | 信息密度 | 结构套路 |
|---|---|---|---|---|
| 小红书 | 1080×1440（**出图强制 2x：2160×2880**） | 内容驱动选风格：暖米白、Editorial、Zen、Swiss（含轻瑞士）等 | 可变：封面低，内容页中到高，结尾低 | 封面钩子+语义承接 → 每页一个主结构 → 总结/互动 |
| 抖音 | 1080×1920（出图建议 2x） | 纯黑 #0d0f14+紫光晕、主紫 #a58bff、金黄 #ffd166 | 低：大数字冲击为主 | tag → 超大h1 → ¥190px级大数字 → 4行价格row → 渐变CTA胶囊 → 小字来源 |
| X 卡 | 1600×900 | 推特黑 #000、品牌蓝 #1d9bf0、次级 #71767b | 中：英文hook+4数据卡 | 账号行(头像圆+@limbopeng) → 英文判断句hook带🧵 → 4个stat卡 → 左note右价格tag |
| 通用横图 | 1920×1080 | 深紫渐变 #0f1220→#1a1030 | 中：条形图可视化 | 左栏(tag+h1+desc+超大单价) 右栏(条形图行，宽度按数值比例) |
| 公众号封面 | 900×383（出图建议 2x） | 紫渐变+44px细网格质感 | 极低：封面级一句钩子 | 左(kicker+h1+sub) 右(¥108px大数字+口径小字) |

## 小红书页面分工（内容驱动）

小红书 1080×1440 不应把整组卡片都做成同一密度。页面职责不同，留白和信息量也不同：

| 页面 | 首要任务 | 推荐密度 | 必须出现 | 不应出现 |
|---|---|---|---|---|
| 封面 | 停留、识别主题、制造继续阅读的理由 | 低：1 个主命题 + 1 个承接 | 中文钩子、一个语义锚点、内容型承接、CTA | 六个知识点总览、长段正文、随机装饰堆叠 |
| 铺垫页 | 建立问题和阅读语境 | 中低：2–4 个解释点 | 问题、范围、下一页悬念 | 把所有背景资料一次讲完 |
| 核心页 | 快速扫描并理解一个结构 | 中：3–6 个条目 | 一个主结构、一个辅助结构、一句结论 | 两个等权主结构、超过 7 个条目 |
| 高密度页 | 承载可收藏的短清单或框架 | 中高：最多 7 个短条目 | 统一行骨架、清晰分区、来源/证据 | 长段落、过小字号、装饰抢正文 |
| 结尾页 | 固化记忆并引导行动 | 低：1 个结论 + 1 个 CTA | 总结、行动或互动 | 引入新的事实和新概念 |

封面与内容页共享背景、字体、边框、强调色和编号语法，但不共享信息密度。具体内容诊断、风格匹配和拆页阈值见 [`content-driven-design.md`](content-driven-design.md)。

## 小红书封面检查

- 主标题常规 90–116px；字重按风格字体体系（Editorial/Zen/Swiss 越大越轻 300-500，其余 700-900）；不超过三行且装饰不竞争时才允许 128–130px。
- 中文钩子优先，英文术语只能辅助；标题强调词控制在 1–2 个。
- 下半屏必须出现阶段序列、目录、数据格、流程带或证据片段等内容型承接。
- 总视觉元素 ≤6 组；缩略图阅读顺序应为标题 → 内容范围 → CTA/承接 → 装饰/背书。
- 关键文本与装饰距画布边至少 40px，顶部右侧和底部 10% 避开平台 UI 安全区。

## 小红书内容页检查

- 一页一个阅读问题，采用“一个主结构 + 一个辅助结构 + 一句结论”。
- 常规每条使用“编号/名称/一句话机制/产物或证据 tag”，正文 22–25px，行距至少 1.4，每页最多 7 条。
- `flow`、`comparison`、`list/grid`、`editorial` 要由信息关系决定，不由风格名强行决定。
- flex 行只允许“图标 + 一个正文块”；行内 `<b>`、代码和链接必须包在 `.copy`/`.body` 内，避免匿名 flex item 破坏换行。
- 内容少时用真实案例、示例、流程或数据补足结构，不用 `margin-top:auto` 伪造阅读密度。

## 交付同步检查

1. 改 HTML 后重新生成对应 PNG（**出图强制 2x 视网膜采样 `--scale 2`**，物理分辨率 2160×2880，绝不用 1x 标清交付），不把旧 PNG 当作当前预览。
2. 核对 HTML `<title>`、主标题、品牌/来源文案与 PNG、`gallery.html` 中的预览是否一致。
3. 逐张运行 `scripts/check-overflow.py`，确认内容和绝对定位装饰都在 40px 安全区内。
4. 浅底卡用实际设计底色运行 `scripts/quality-check.py`；底部吸底结论框造成的条带 WARN 先用溢出检查和最底部纯色抽检判断，不因已知误报削减内容。
5. 最后做一次实际尺寸和缩略图目检：确认标题优先级、自然换行、装饰语义和页面间阅读顺序。

```python
goto_url(f"file://{base}/{name}.html"); wait_for_load()
m = js("""(() => {
  let maxR = 0, maxB = 0;
  for (const el of document.body.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    maxB = Math.max(maxB, r.bottom); maxR = Math.max(maxR, r.right);
  }
  return {maxBottom: Math.round(maxB), maxRight: Math.round(maxR)};
})()""")
ok = m['maxBottom'] <= H and m['maxRight'] <= W
```

## 像素质检（PIL，vision 不可用时的兜底）
```python
from PIL import Image
img = Image.open(f).convert('RGB'); w, h = img.size
corners = [img.getpixel(p) for p in [(3,3),(w-4,3),(3,h-4),(w-4,h-4)]]
white_edge = any(sum(c) > 700 for c in corners)   # 意外白边（设计就是浅底的卡除外）
strip = img.crop((0, int(h*0.95), w, h))           # 底条均值≈背景色=文字没被截
```
注意：小红书米白底(250,246,239)四角"偏白"是设计本意，质检时先对设计稿底色。

## 出图命令（走 cardshot，不另拼 Chrome）
```bash
python3 shooter.py cards/seedance-xhs.html --auto --scale 2
```
高清版 scale=2（输出 2160×2880）。文件名自动 `{stem}_{w}x{h}.png` 落 output/。
