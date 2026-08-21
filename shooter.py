#!/usr/bin/env python3
"""cardshot shooter — headless Chrome 截图核心 + CLI.

用法:
  python3 shooter.py cards/demo.html                 # 1080x1440 (3:4)
  python3 shooter.py cards/ -w 1080 -h 1920 --scale 2 # 目录批量 9:16 2x
"""
import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]


def find_chrome() -> str:
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    found = shutil.which("chrome") or shutil.which("chromium") or shutil.which("google-chrome")
    if found:
        return found
    raise SystemExit("未找到 Chrome/Chromium，请安装 Google Chrome")


def shoot(html_path: Path, out_path: Path, width: int, height: int, scale: float = 1.0,
          timeout: int = 60) -> Path:
    """对单个 HTML 文件截图. out_path 已含扩展名(.png)."""
    chrome = find_chrome()
    # window-size 始终用 CSS 像素, 输出倍率交给 force-device-scale-factor
    # (两者都乘会导致 4x: 2160 窗口 × 2 倍率 = 4320px)
    real_w, real_h = width, height
    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={real_w},{real_h}",
        f"--screenshot={out_path}",
        "--virtual-time-budget=8000",   # 等 JS/字体/图片
        html_path.resolve().as_uri(),
    ]
    if scale != 1.0:
        cmd.insert(4, f"--force-device-scale-factor={scale}")
    subprocess.run(cmd, check=True, capture_output=True, timeout=timeout)
    return out_path


def shoot_dir(directory: Path, out_dir: Path, width: int, height: int, scale: float = 1.0):
    htmls = sorted([p for p in directory.iterdir() if p.suffix.lower() == ".html"])
    if not htmls:
        print(f"[skip] {directory} 下没有 .html 文件")
        return []
    results = []
    for i, p in enumerate(htmls, 1):
        out = out_dir / f"{p.stem}_{int(width*scale)}x{int(height*scale)}.png"
        t0 = time.time()
        try:
            shoot(p, out, width, height, scale)
            dt = time.time() - t0
            print(f"[{i}/{len(htmls)}] {p.name} -> {out.name}  ({dt:.1f}s)")
            results.append(out)
        except Exception as e:
            print(f"[{i}/{len(htmls)}] {p.name} FAILED: {e}", file=sys.stderr)
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="cardshot 截图 CLI")
    ap.add_argument("target", help="HTML 文件或包含 HTML 的目录")
    ap.add_argument("-W", "--width", type=int, default=1080)
    ap.add_argument("-H", "--height", type=int, default=1440)
    ap.add_argument("--scale", type=float, default=1.0, help="输出倍率, 2 = 2x 高清")
    ap.add_argument("-o", "--out", default=None, help="输出目录 (默认 ./output)")
    args = ap.parse_args()

    target = Path(args.target).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve() if args.out else Path(__file__).parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    if target.is_dir():
        outs = shoot_dir(target, out_dir, args.width, args.height, args.scale)
        print(f"\n完成: {len(outs)} 张 -> {out_dir}")
    else:
        out = out_dir / f"{target.stem}_{int(args.width*args.scale)}x{int(args.height*args.scale)}.png"
        shoot(target, out, args.width, args.height, args.scale)
        print(f"完成: {out}")
