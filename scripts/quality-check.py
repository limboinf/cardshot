#!/usr/bin/env python3
"""quality-check.py — cardshot 出图像素质检（四角+底条, PIL, 零外部依赖）.

检查项:
  1. 文件可打开且非空图 (纯色图警告: 方差≈0 可能渲染失败)
  2. 四角色值 vs 设计底色 (意外白边检测)
  3. 底部条带均值 (文字被截断时底条会出现异常亮/杂色)

用法:
  python3 quality-check.py output/*.png
  python3 quality-check.py output/ --bg faf6ef     # 指定设计底色(浅底卡用)
退出码: 0=全部通过, 1=有可疑项
"""
import argparse
import glob
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("需要 Pillow: pip3 install Pillow"); sys.exit(2)


def variance(px):
    if not px:
        return 0
    n = len(px)
    means = [sum(p[i] for p in px) / n for i in range(3)]
    return sum((p[i] - means[i]) ** 2 for p in px for i in range(3)) / (n * 3)


def check(img_path: Path, bg_hex: str) -> bool:
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    bg = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))

    corners = [img.getpixel(p) for p in [(3, 3), (w-4, 3), (3, h-4), (w-4, h-4)]]
    corner_off = [c for c in corners if sum(abs(a-b) for a, b in zip(c, bg)) > 90]
    strip = img.crop((0, int(h*0.95), w, h))
    spx = list(strip.getdata())[::7]
    strip_var = variance(spx)
    allpx = list(img.getdata())[::31]
    img_var = variance(allpx)

    issues = []
    if img_var < 12:
        issues.append(f"疑似空图/纯色 (方差{img_var:.0f})")
    if corner_off:
        issues.append(f"四角与设计底色#{bg_hex}不符: {corner_off}")
    if strip_var > 900:
        issues.append(f"底部条带杂色 (方差{strip_var:.0f}, 可能截字)")

    status = "OK  " if not issues else "WARN"
    print(f"[{status}] {img_path.name:44s} {w}x{h}")
    for i in issues:
        print(f"        ↳ {i}")
    return not issues


def main():
    ap = argparse.ArgumentParser(description="cardshot 出图像素质检")
    ap.add_argument("targets", nargs="+", help="PNG 文件或目录")
    ap.add_argument("--bg", default="000000", help="设计底色 hex (默认 000000, 浅底卡传实际底色)")
    args = ap.parse_args()

    files = []
    for t in args.targets:
        p = Path(t).expanduser()
        files += sorted(p.glob("*.png")) if p.is_dir() else [p]
    if not files:
        print("没有找到 PNG"); sys.exit(1)

    results = [check(f, args.bg) for f in files]
    passed = sum(results)
    print(f"\n{passed}/{len(results)} 通过")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
