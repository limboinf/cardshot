#!/usr/bin/env python3
"""扫描 templates/ 下的样卡, 重新生成根目录 gallery.html (风格库预览墙).

生成的是纯静态页: 双击即可在浏览器打开, 无需任何服务器.
每个风格一节, 展示其封面 + 内容页 + 结尾页三张. 风格在 STYLES 里登记, 缺卡会报警.
用法: python3 scripts/build-gallery.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = ROOT / "templates"
OUT = ROOT / "gallery.html"

# 风格登记表: (文件名前缀, 展示名). 新增风格在这里加一行.
STYLES = [
    ("editorial", "Editorial 杂志编辑"),
    ("zen", "Zen 日式极简"),
    ("swiss", "Swiss 瑞士网格"),
    ("swiss-editorial", "Swiss Editorial 轻瑞士"),
]

KINDS = ["cover", "page", "end"]  # 每个风格固定三页: 封面 + 内容页 + 结尾页
KIND_LABELS = {"cover": "封面", "page": "内容页", "end": "结尾页"}


def scan() -> list:
    files = {}  # "editorial-cover" -> "templates/editorial-cover.html"
    for f in TEMPLATES_DIR.glob("*.html"):
        files[f.stem] = f"templates/{f.name}"
    groups = []
    for stem, label in STYLES:
        cards = []
        for k in KINDS:
            rel = files.get(f"{stem}-{k}")
            if rel:
                cards.append({"file": rel, "name": f"{stem}-{k}",
                              "k": k, "label": KIND_LABELS[k]})
        missing = [k for k in KINDS if not any(c["name"] == f"{stem}-{k}" for c in cards)]
        if missing:
            print(f"⚠ {label}({stem}) 缺: {', '.join(missing)}")
        if cards:
            groups.append({"style": label, "cards": cards})
    return groups


TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>cardshot — 风格库</title>
<style>
  :root {
    --bg: #0f1115; --panel: #171a21; --panel2: #1d212b; --line: #2a2f3c;
    --text: #e8eaf0; --muted: #8b93a7; --accent: #5b8cff; --accent2: #7c5bff; --radius: 10px;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }
  header {
    display: flex; align-items: center; gap: 14px; padding: 12px 20px;
    background: var(--panel); border-bottom: 1px solid var(--line);
    position: sticky; top: 0; z-index: 10;
  }
  .logo { font-weight: 700; font-size: 15px; }
  .logo span { color: var(--accent); }
  .count { font-size: 13px; color: var(--muted); }
  .spacer { flex: 1; }
  .cmd { font-size: 12px; color: var(--muted); background: var(--panel2); border: 1px solid var(--line); border-radius: 8px; padding: 6px 12px; font-family: ui-monospace, Menlo, monospace; }
  main { max-width: 1440px; margin: 0 auto; padding: 24px 20px 60px; }
  .group { margin-bottom: 44px; }
  .group-head { display: flex; align-items: baseline; gap: 12px; margin-bottom: 16px; }
  .group-head h2 { font-size: 17px; font-weight: 700; }
  .group-head .n { font-size: 13px; color: var(--muted); }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 18px; }
  .tile { background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; transition: border-color .15s; }
  .tile:hover { border-color: var(--accent); }
  .thumb { position: relative; width: 100%; aspect-ratio: 3 / 4; background: #22262f; overflow: hidden; }
  .thumb iframe { border: 0; pointer-events: none; transform-origin: 0 0; position: absolute; top: 0; left: 0; width: 1080px; height: 1440px; background: #fff; }
  .meta { padding: 10px 12px; display: flex; align-items: center; gap: 8px; border-top: 1px solid var(--line); }
  .meta .name { font-size: 13px; font-weight: 600; word-break: break-all; }
  .chip { font-size: 11px; padding: 2px 8px; border-radius: 999px; flex-shrink: 0; }
  .chip.cover { background: rgba(124,91,255,.18); color: #b7a4ff; }
  .chip.page { background: rgba(94,140,255,.16); color: #9db9ff; }
  .chip.end { background: rgba(255,171,64,.18); color: #ffc078; }
  .acts { padding: 0 12px 12px; display: flex; gap: 8px; }
  .acts a { flex: 1; text-align: center; font-size: 12px; padding: 5px 10px; background: var(--panel2); color: var(--text); border: 1px solid var(--line); border-radius: 8px; text-decoration: none; }
  .acts a:hover { border-color: var(--accent); }
</style>
</head>
<body>
<header>
  <div class="logo">🎨 风格<span>库</span></div>
  <div class="count" id="count"></div>
  <div class="spacer"></div>
  <div class="cmd">出图: python3 shooter.py templates/ --auto</div>
</header>
<main id="main"></main>
<script>
const GROUPS = __GROUPS__;
const main = document.getElementById('main');
let total = 0;
for (const g of GROUPS) {
  total += g.cards.length;
  const sec = document.createElement('div');
  sec.className = 'group';
  sec.innerHTML = `<div class="group-head"><h2>${g.style}</h2><span class="n">${g.cards.length} 页</span></div><div class="grid"></div>`;
  const grid = sec.querySelector('.grid');
  for (const c of g.cards) {
    const tile = document.createElement('div');
    tile.className = 'tile';
    tile.innerHTML = `
      <div class="thumb"><iframe loading="lazy" src="${c.file}" scrolling="no"></iframe></div>
      <div class="meta"><span class="chip ${c.k}">${c.label}</span><span class="name">${c.name}</span></div>
      <div class="acts"><a href="${c.file}" target="_blank">↗ 原件</a></div>`;
    grid.appendChild(tile);
  }
  main.appendChild(sec);
}
document.getElementById('count').textContent = `${GROUPS.length} 个风格 · ${total} 页`;
function fit() {
  document.querySelectorAll('.thumb').forEach(thumb => {
    const f = thumb.querySelector('iframe');
    if (f) f.style.transform = `scale(${thumb.clientWidth / 1080})`;
  });
}
window.addEventListener('resize', fit);
fit();
</script>
</body>
</html>
"""


def main():
    groups = scan()
    if not groups:
        raise SystemExit("templates/ 下没有找到样卡")
    OUT.write_text(TEMPLATE.replace("__GROUPS__", json.dumps(groups, ensure_ascii=False)), encoding="utf-8")
    n = sum(len(g["cards"]) for g in groups)
    print(f"已生成 {OUT.relative_to(ROOT)}: {len(groups)} 个风格 {n} 页 (双击即可在浏览器打开)")


if __name__ == "__main__":
    main()
