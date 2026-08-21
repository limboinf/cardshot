#!/usr/bin/env python3
"""cardshot shooter — headless Chrome 截图核心 + CLI.

用法:
  python3 shooter.py cards/demo.html                     # 1080x1440 (3:4)
  python3 shooter.py cards/ -w 1080 -h 1920 --scale 2    # 目录批量 9:16 2x
  python3 shooter.py cards/ --all-presets                # 每张卡出全部平台尺寸
  python3 shooter.py cards/ -p xhs douyin                # 只出指定预设
  python3 shooter.py cards/ --auto                       # 逐张读 HTML 自带尺寸
  python3 shooter.py cards/ -p xhs --grid 2x3            # 出图后拼网格长图
  python3 shooter.py --list-presets                      # 查看全部预设
"""
import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]

# 平台预设: name -> (width, height, 说明)
PRESETS = {
    "xhs":          (1080, 1440, "小红书 3:4"),
    "douyin":       (1080, 1920, "抖音/视频号 9:16"),
    "square":       (1080, 1080, "方图 1:1 (Ins/朋友圈)"),
    "twitter":      (1600, 900,  "X/Twitter 16:9"),
    "wide":         (1920, 1080, "通用横图 FHD"),
    "wechat-cover": (900, 383,   "公众号封面 2.35:1"),
    "zhihu":        (1080, 2340, "知乎/长图卡"),
}


def find_chrome() -> str:
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    found = shutil.which("chrome") or shutil.which("chromium") or shutil.which("google-chrome")
    if found:
        return found
    raise SystemExit("未找到 Chrome/Chromium，请安装 Google Chrome")


def render_adaptive_html(source: str, width: int, height: int, base_href=None) -> str:
    """运行时覆盖卡片画布尺寸，不修改源 HTML."""
    if width <= 0 or height <= 0:
        raise ValueError("画布宽高必须是正整数")

    base = ""
    if base_href:
        base = f'<base href="{html.escape(base_href, quote=True)}">\n'
    override = (
        '<style id="cardshot-adaptive-canvas">\n'
        'html, body {\n'
        f'  width: {width}px !important;\n'
        f'  height: {height}px !important;\n'
        '  min-width: 0 !important;\n'
        '  min-height: 0 !important;\n'
        '  margin: 0 !important;\n'
        '  overflow: hidden !important;\n'
        '}\n'
        '</style>\n'
    )
    head = re.search(r"<head(?:\s[^>]*)?>", source, re.IGNORECASE)
    if not head:
        return base + override + source
    closing_head = re.search(r"</head\s*>", source[head.end():], re.IGNORECASE)
    if not closing_head:
        return source[:head.end()] + "\n" + base + override + source[head.end():]
    close_at = head.end() + closing_head.start()
    return (
        source[:head.end()] + "\n" + base + source[head.end():close_at]
        + "\n" + override + source[close_at:]
    )


def shoot(html_path: Path, out_path: Path, width: int, height: int, scale: float = 1.0,
          timeout: int = 60) -> Path:
    """对单个 HTML 文件截图. out_path 已含扩展名(.png)."""
    chrome = find_chrome()
    source_path = html_path.resolve()
    source = source_path.read_text(encoding="utf-8")
    rendered = render_adaptive_html(
        source,
        width,
        height,
        source_path.parent.as_uri() + "/",
    )
    with tempfile.TemporaryDirectory(prefix="cardshot-") as temp_dir:
        render_path = Path(temp_dir) / source_path.name
        render_path.write_text(rendered, encoding="utf-8")
        # window-size 始终用 CSS 像素, 输出倍率交给 force-device-scale-factor
        # (两者都乘会导致 4x: 2160 窗口 × 2 倍率 = 4320px)
        cmd = [
            chrome,
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--window-size={width},{height}",
            f"--screenshot={out_path.resolve()}",
            "--virtual-time-budget=8000",   # 等 JS/字体/图片
            render_path.as_uri(),
        ]
        if scale != 1.0:
            cmd.insert(4, f"--force-device-scale-factor={scale}")
        subprocess.run(cmd, check=True, capture_output=True, timeout=timeout)
    if not out_path.exists():
        raise RuntimeError("Chrome 未产出文件")
    return out_path


def detect_size(html_path: Path):
    """读卡片自带尺寸: <meta name="card-size" content="1080x1440"> 或 body CSS.

    返回 (w, h) 或 None.
    """
    try:
        html = html_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    m = re.search(r'<meta\s+name="card-size"\s+content="(\d+)\s*[x×]\s*(\d+)"', html)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"body\s*\{[^}]*?width:\s*(\d+)px[^}]*?height:\s*(\d+)px", html, re.S)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"body\s*\{[^}]*?height:\s*(\d+)px[^}]*?width:\s*(\d+)px", html, re.S)
    if m:
        return int(m.group(2)), int(m.group(1))
    return None


def collect_htmls(target: Path):
    if target.is_dir():
        return sorted(p for p in target.iterdir() if p.suffix.lower() == ".html")
    return [target]


def shoot_one_tagged(p: Path, out: Path, w: int, h: int, scale: float, tag: str, results: list):
    t0 = time.time()
    try:
        shoot(p, out, w, h, scale)
        print(f"{tag} {p.name} [{w}x{h}] -> {out.name}  ({time.time()-t0:.1f}s)")
        results.append(out)
    except Exception as e:
        print(f"{tag} {p.name} [{w}x{h}] FAILED: {e}", file=sys.stderr)


def shoot_dir(directory: Path, out_dir: Path, width: int, height: int, scale: float = 1.0):
    """整目录统一尺寸出图 (server.py 也在用)."""
    htmls = collect_htmls(directory)
    if not htmls:
        print(f"[skip] {directory} 下没有 .html 文件")
        return []
    results = []
    for i, p in enumerate(htmls, 1):
        out = out_dir / f"{p.stem}_{int(width*scale)}x{int(height*scale)}.png"
        shoot_one_tagged(p, out, width, height, scale, f"[{i}/{len(htmls)}]", results)
    return results


def shoot_presets(target: Path, out_dir: Path, presets: list, scale: float = 1.0, auto: bool = False):
    """每个 HTML × 每个预设尺寸出图.

    auto=True 时忽略预设, 逐张读 HTML 自带尺寸, 读不到就跳过.
    """
    htmls = collect_htmls(target)
    if not htmls:
        print("[skip] 没有 .html 文件")
        return []
    results = []
    jobs = []  # (html, label, w, h)
    if auto:
        for p in htmls:
            size = detect_size(p)
            if size is None:
                print(f"[skip] {p.name}: 未识别尺寸 (需 meta card-size 或 body 固定宽高)")
                continue
            jobs.append((p, f"auto", size[0], size[1]))
    else:
        for p in htmls:
            for preset in presets:
                w, h, _ = PRESETS[preset]
                jobs.append((p, preset, w, h))
    for i, (p, label, w, h) in enumerate(jobs, 1):
        out = out_dir / f"{p.stem}_{label}_{int(w*scale)}x{int(h*scale)}.png"
        shoot_one_tagged(p, out, w, h, scale, f"[{i}/{len(jobs)}]", results)
    return results


def make_grid(images: list, cols: int, out_path: Path, gap: int = 0, bg: str = "#ffffff"):
    """把多张 PNG 拼成网格长图 (需 Pillow)."""
    from PIL import Image
    imgs = [Image.open(p) for p in images]
    w0 = min(i.width for i in imgs)
    scaled = []
    for im in imgs:
        if im.width != w0:
            im = im.resize((w0, round(im.height * w0 / im.width)))
        scaled.append(im)
    rows = (len(scaled) + cols - 1) // cols
    row_hs = []
    for r in range(rows):
        row = scaled[r*cols:(r+1)*cols]
        row_hs.append(max(i.height for i in row))
    W = w0 * cols + gap * (cols - 1)
    H = sum(row_hs) + gap * (rows - 1)
    canvas = Image.new("RGB", (W, H), bg)
    y = 0
    for r in range(rows):
        x = 0
        for im in scaled[r*cols:(r+1)*cols]:
            canvas.paste(im, (x, y))
            x += im.width + gap
        y += row_hs[r] + gap
    canvas.save(out_path)
    return out_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="cardshot 截图 CLI — HTML 卡片 → 各平台尺寸 PNG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
示例:
  %(prog)s cards/demo.html                        单张 1080x1440
  %(prog)s cards/ -w 1080 -h 1920                 目录批量 9:16
  %(prog)s cards/ -p xhs                          小红书尺寸整目录
  %(prog)s cards/ --all-presets --scale 2         每张卡 × 全部预设 × 2x
  %(prog)s cards/ --auto                          按 HTML 自带尺寸出图
  %(prog)s cards/ -p xhs --grid 2x3               出图后拼 2 列网格长图
  %(prog)s --list-presets                         查看全部平台预设
""")
    ap.add_argument("target", nargs="?", help="HTML 文件或包含 HTML 的目录")
    ap.add_argument("-W", "--width", type=int, default=1080, help="画布宽 (默认 1080)")
    ap.add_argument("-H", "--height", type=int, default=1440, help="画布高 (默认 1440)")
    ap.add_argument("--scale", type=float, default=1.0, help="输出倍率, 2 = 2x 高清")
    ap.add_argument("-o", "--out", default=None, help="输出目录 (默认 ./output)")
    ap.add_argument("-p", "--preset", nargs="+", choices=list(PRESETS), metavar="PRESET",
                    help="平台预设, 可多个: " + ", ".join(PRESETS))
    ap.add_argument("--all-presets", action="store_true", help="对所有预设逐一出图")
    ap.add_argument("--auto", action="store_true",
                    help="自动读 HTML 自带尺寸 (meta card-size / body CSS)")
    ap.add_argument("--grid", metavar="CxR", help="出图后拼接网格长图, 如 2x3 (需 Pillow)")
    ap.add_argument("--list-presets", action="store_true", help="列出全部预设并退出")
    args = ap.parse_args()

    if args.list_presets:
        print(f"{'name':<14} {'size':>11}  desc")
        for k, (w, h, d) in PRESETS.items():
            print(f"{k:<14} {w:>5}x{h:<5}  {d}")
        sys.exit(0)

    if not args.target:
        ap.error("需要 target (HTML 文件/目录), 或用 --list-presets")

    target = Path(args.target).expanduser().resolve()
    if not target.exists():
        ap.error(f"路径不存在: {target}")
    out_dir = Path(args.out).expanduser().resolve() if args.out else Path(__file__).parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    presets = list(PRESETS) if args.all_presets else (list(args.preset) if args.preset else [])

    results = []
    if presets or args.auto:
        results = shoot_presets(target, out_dir, presets, args.scale, auto=args.auto)
    elif target.is_dir():
        results = shoot_dir(target, out_dir, args.width, args.height, args.scale)
    else:
        out = out_dir / f"{target.stem}_{int(args.width*args.scale)}x{int(args.height*args.scale)}.png"
        shoot_one_tagged(target, out, args.width, args.height, args.scale, "[1/1]", results)

    if args.grid and results:
        m = re.fullmatch(r"(\d+)[x×](\d+)", args.grid.strip())
        if m:
            cols = max(1, int(m.group(1)))
            grid_out = out_dir / f"grid_{cols}cols_{int(time.time())}.png"
            try:
                make_grid(results, cols, grid_out)
                print(f"网格图: {grid_out.name}")
            except ImportError:
                print("[warn] 网格拼接需要 Pillow: pip3 install Pillow", file=sys.stderr)
        else:
            print(f"[warn] --grid 应为 CxR 如 2x3, 收到: {args.grid}", file=sys.stderr)

    if results:
        print(f"\n完成: {len(results)} 张 -> {out_dir}")
    else:
        sys.exit(1)
