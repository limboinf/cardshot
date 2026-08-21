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
- 数据要有来源行（如"数据：火山引擎 2026.7 官方定价"）

## 各平台策略
| 平台 | 尺寸 | 底色/语言 | 信息密度 | 结构套路 |
|---|---|---|---|---|
| 小红书 | 1080×1440 | 米白 #faf6ef 暖底、荧光笔标记色 #ffd591、强调橙 #d4570e | 高：钩子标题+6格(3价格+3省钱)+2tips+结论框 | 胶囊tag → h1钩子 → 3列价格格 → 深色note格 → tips列表 → 深色结论框(吸底) |
| 抖音 | 1080×1920 | 纯黑 #0d0f14+紫光晕、主紫 #a58bff、金黄 #ffd166 | 低：大数字冲击为主 | tag → 超大h1 → ¥190px级大数字 → 4行价格row → 渐变CTA胶囊 → 小字来源 |
| X 卡 | 1600×900 | 推特黑 #000、品牌蓝 #1d9bf0、次级 #71767b | 中：英文hook+4数据卡 | 账号行(头像圆+@limbopeng) → 英文判断句hook带🧵 → 4个stat卡 → 左note右价格tag |
| 通用横图 | 1920×1080 | 深紫渐变 #0f1220→#1a1030 | 中：条形图可视化 | 左栏(tag+h1+desc+超大单价) 右栏(条形图行，宽度按数值比例) |
| 公众号封面 | 900×383 | 紫渐变+44px细网格质感 | 极低：封面级一句钩子 | 左(kicker+h1+sub) 右(¥108px大数字+口径小字) |

## 溢出检测（browser_exec，逐张跑）
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
curl -s -X POST http://localhost:8766/api/shoot -H 'Content-Type: application/json' \
  -d '{"file":"seedance-xhs.html","w":1080,"h":1440,"scale":1}'
```
高清版 scale=2（输出 2160×2880）。文件名自动 `{stem}_{w}x{h}.png` 落 output/。
