#!/usr/bin/env python3
"""副業詐欺録 サムネ保存用簡易HTTPサーバー
   POST /?slug=<slug>  bodyにPNGバイナリ→ /public/ogp/<slug>.png に保存
"""
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

OUT_DIR = "/Users/toppo/マイファイル/副業詐欺録/public/ogp"
os.makedirs(OUT_DIR, exist_ok=True)


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        try:
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            slug = qs.get("slug", ["unknown"])[0]
            length = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(length)
            out = os.path.join(OUT_DIR, f"{slug}.png")
            with open(out, "wb") as f:
                f.write(data)
            self.send_response(200)
            self._cors()
            self.end_headers()
            msg = f"OK {slug} {len(data)} bytes\n"
            self.wfile.write(msg.encode())
            print(f"[save] {out} ({len(data)} bytes)")
        except Exception as e:
            self.send_response(500)
            self._cors()
            self.end_headers()
            self.wfile.write(str(e).encode())
            print(f"[err] {e}")

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 7777), Handler).serve_forever()
