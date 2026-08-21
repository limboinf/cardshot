#!/usr/bin/env python3
"""check-overflow.py — cardshot 卡片溢出检测（零依赖，headless Chrome）.

原理: 复制卡片到临时文件, 在 </body> 前注入测量脚本(把结果写进 document.title),
headless Chrome --dump-dom 渲染后从 DOM 里解析 title, 与画布尺寸比对。

用法:
  python3 check-overflow.py <卡片.html 或目录>          # 全部检测
  python3 check-overflow.py cards/ --margin 40          # 要求内容距边 ≥40px
退出码: 0=全部 OK, 1=有溢出/失败
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]

INJECT = """<script>
window.addEventListener('load', () => {
  setTimeout(() => {
    let maxR = 0, maxB = 0, cnt = 0;
    for (const el of document.body.querySelectorAll('*')) {
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) continue;
      cnt++;
      if (r.bottom > maxB) maxB = r.bottom;
      if (r.right > maxR) maxR = r.right;
    }
    document.title = 'OV:' + Math.round(maxB) + ',' + Math.round(maxR)
      + ':' + document.body.clientWidth + 'x' + document.body.clientHeight
      + ':' + cnt;
  }, 300);
});
</script>"""


def find_chrome() -> str:
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    found = shutil.which("chrome") or shutil.which("chromium") or shutil.which("google-chrome")
    if found:
        return found
    raise SystemExit("未找到 Chrome/Chromium")


def read_card_size(html: str):
    m = re.search(r'<meta\s+name="card-size"\s+content="(\d+)\s*[x×]\s*(\d+)"', html)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"body\s*\{[^}]*?width:\s*(\d+)px[^}]*?height:\s*(\d+)px", html, re.S)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def check_card(chrome: str, card: Path, margin: int) -> bool:
    html = card.read_text(encoding="utf-8", errors="ignore")
    size = read_card_size(html)
    if size is None:
        print(f"[SKIP] {card.name}: 未识别尺寸 (缺 meta card-size / body 固定宽高)")
        return True  # 不算失败, 但提示
    w, h = size
    injected = html.replace("</body>", INJECT + "\n</body>")
    if injected == html:  # 没有 </body> 就追加
        injected = html + INJECT
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(injected)
        tmp = Path(f.name)
    try:
        r = subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
             f"--window-size={w},{h}", "--virtual-time-budget=6000",
             "--dump-dom", tmp.resolve().as_uri()],
            capture_output=True, timeout=90, text=True)
        m = re.search(r"<title>(OV:[^<]+)</title>", r.stdout)
        if not m:
            print(f"[FAIL] {card.name}: 未能取到测量结果 (title 未注入)")
            return False
        payload = m.group(1)[3:]           # maxB,maxR:WxH:cnt
        parts = payload.split(":")
        maxb, maxr = (int(x) for x in parts[0].split(","))
        cnt = parts[2] if len(parts) > 2 else "?"
        ok = (maxb <= h - margin) and (maxr <= w - margin)
        status = "OK  " if ok else "OVERFLOW"
        detail = f"内容底线{maxb}/{h} 右界{maxr}/{w} 元素{cnt}"
        if not ok:
            detail += f"  → 要求距边 ≥{margin}px"
        print(f"[{status}] {card.name:40s} {detail}")
        return ok
    except subprocess.TimeoutExpired:
        print(f"[FAIL] {card.name}: Chrome 超时")
        return False
    finally:
        tmp.unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser(description="cardshot 卡片溢出检测")
    ap.add_argument("target", help="HTML 文件或目录")
    ap.add_argument("--margin", type=int, default=40, help="内容距画布边最小像素 (默认 40)")
    args = ap.parse_args()

    target = Path(args.target).expanduser().resolve()
    cards = sorted(target.glob("*.html")) if target.is_dir() else [target]
    if not cards:
        print(f"没有找到 .html: {target}")
        sys.exit(1)

    chrome = find_chrome()
    results = [check_card(chrome, c, args.margin) for c in cards]
    passed = sum(results)
    print(f"\n{passed}/{len(results)} 通过 (margin={args.margin}px)")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
