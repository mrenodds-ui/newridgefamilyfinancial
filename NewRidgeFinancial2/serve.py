"""Serve NewRidgeFinancial 2.0 mock pages (static files only) on port 1966."""

import http.server
import socketserver
from pathlib import Path

HOST = "127.0.0.1"
PORT = 1966
SITE_DIR = Path(__file__).resolve().parent / "site"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SITE_DIR), **kwargs)

    def end_headers(self):
        if self.path.endswith(".html") or self.path in ("/", ""):
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        super().end_headers()


if __name__ == "__main__":
    if not (SITE_DIR / "index.html").is_file():
        raise SystemExit(f"Site not found: {SITE_DIR / 'index.html'}")

    with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
        print(f"NewRidgeFinancial 2.0 mock pages: http://{HOST}:{PORT}/")
        httpd.serve_forever()
