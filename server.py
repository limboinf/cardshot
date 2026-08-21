#!/usr/bin/env python3
"""cardshot server — 本地 WebUI 服务器 (纯标准库, 零依赖).

打开 http://localhost:8765
"""
import json
import os
import subprocess
import sys
import threading
import urllib.parse
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from shooter import shoot, shoot_dir

ROOT = Path(__file__).parent
CARDS_DIR = ROOT / "cards"
OUT_DIR = ROOT / "output"
STATIC_DIR = ROOT / "static"
PORT = 8766


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):  # 安静点
        pass

    # ---------- helpers ----------
    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _safe_card(self, name: str) -> Path:
        """防目录穿越: 卡片名只允许文件名, 且必须落在 cards/ 内"""
        p = (CARDS_DIR / name).resolve()
        if not p.is_file() or CARDS_DIR.resolve() not in p.parents:
            raise ValueError(f"非法卡片: {name}")
        return p

    # ---------- GET ----------
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == "/api/cards":
            files = sorted([f.name for f in CARDS_DIR.glob("*.html")])
            self._json({"cards": files})

        elif path == "/api/open":
            # 在浏览器新标签打开卡片原件 (给 AI 调试或手动微调)
            name = qs.get("f", [""])[0]
            try:
                p = self._safe_card(name)
                webbrowser.open(p.resolve().as_uri())
                self._json({"ok": True})
            except ValueError as e:
                self._json({"error": str(e)}, 400)

        elif path == "/api/reveal":
            out = qs.get("path", [""])[0]
            # 只允许 reveal output/ 下的文件
            op = Path(out).expanduser().resolve()
            if OUT_DIR.resolve() not in op.parents:
                self._json({"error": "只允许 output/ 内的文件"}, 400)
                return
            if not op.exists():
                self._json({"error": f"文件不存在: {out}"}, 404)
                return
            subprocess.Popen(["open", "-R", str(op)])
            self._json({"ok": True})

        elif path == "/api/thumbnail":
            # 低倍率快照用于列表预览 (缓存到 output/.thumbs/)
            name = qs.get("f", [""])[0]
            try:
                p = self._safe_card(name)
            except ValueError as e:
                self._json({"error": str(e)}, 400)
                return
            thumb_dir = OUT_DIR / ".thumbs"
            thumb_dir.mkdir(parents=True, exist_ok=True)
            thumb = thumb_dir / f"{p.stem}.png"
            if not thumb.exists():
                try:
                    shoot(p, thumb, 270, 360, scale=1.0)
                except Exception as e:
                    self._json({"error": f"缩略图失败: {e}"}, 500)
                    return
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(thumb.stat().st_size))
            self.end_headers()
            self.wfile.write(thumb.read_bytes())

        elif path == "/api/outputs":
            files = []
            if OUT_DIR.exists():
                for f in sorted(OUT_DIR.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True):
                    files.append({"name": f.name, "path": str(f), "kb": round(f.stat().st_size / 1024)})
            self._json({"outputs": files[:50]})

        elif path.startswith("/cards/"):
            # 卡片原件: 供 iframe 预览
            name = urllib.parse.unquote(path[len("/cards/"):])
            try:
                p = self._safe_card(name)
            except ValueError as e:
                self._json({"error": str(e)}, 400)
                return
            body = p.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        else:
            # 静态文件: / -> static/index.html, 其余从 static/ 出
            if path == "/":
                path = "/index.html"
            self.directory = str(STATIC_DIR)
            super().do_GET()

    # ---------- POST ----------
    def do_POST(self):
        if self.path == "/api/shoot":
            req = self._read_body()
            try:
                p = self._safe_card(req["file"])
            except (KeyError, ValueError) as e:
                self._json({"error": f"参数错误: {e}"}, 400)
                return
            w = int(req.get("w", 1080))
            h = int(req.get("h", 1440))
            scale = float(req.get("scale", 1.0))
            out = OUT_DIR / f"{p.stem}_{int(w*scale)}x{int(h*scale)}.png"
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            try:
                shoot(p, out, w, h, scale)
                self._json({"ok": True, "path": str(out), "name": out.name})
            except Exception as e:
                self._json({"error": f"截图失败: {e}"}, 500)

        elif self.path == "/api/shoot_all":
            req = self._read_body()
            w = int(req.get("w", 1080))
            h = int(req.get("h", 1440))
            scale = float(req.get("scale", 1.0))
            OUT_DIR.mkdir(parents=True, exist_ok=True)

            def run():
                try:
                    outs = shoot_dir(CARDS_DIR, OUT_DIR, w, h, scale)
                    STATE["last_batch"] = [str(o) for o in outs]
                except Exception as e:
                    STATE["last_batch"] = []
                    STATE["last_error"] = str(e)

            threading.Thread(target=run, daemon=True).start()
            self._json({"ok": True, "msg": "批量截图已启动, 稍后到 output/ 查看"})

        else:
            self._json({"error": "not found"}, 404)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            return {}


STATE = {}


def main():
    CARDS_DIR.mkdir(exist_ok=True)
    OUT_DIR.mkdir(exist_ok=True)
    STATIC_DIR.mkdir(exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"cardshot 已启动: {url}  (cards/ 下 {len(list(CARDS_DIR.glob('*.html')))} 个卡片)")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
