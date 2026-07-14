#!/usr/bin/env python3
"""Minimal crawl4ai server client. Python stdlib only — no dependencies.

Environment:
  CRAWL4AI_BASE_URL   Server base URL (default: http://localhost:11235)
  CRAWL4AI_API_TOKEN  Optional JWT, sent as Authorization: Bearer <token>

Commands:
  health                                  Check server liveness
  md <url> [--filter fit|raw|bm25|llm] [--query Q] [-o FILE]
  html <url> [-o FILE]                    Preprocessed HTML
  screenshot <url> [--wait SECS] [-o FILE.png]
  pdf <url> [-o FILE.pdf]
  js <url> <script> [<script> ...]        Each script must `return` a value
  crawl <url> [<url> ...] [--config FILE] [-o FILE]
  job <url> [<url> ...] [--config FILE]   Enqueue async crawl, print task_id
  status <task_id> [-o FILE]              Poll an async crawl job

--config FILE is a JSON file: {"browser_config": {...}, "crawler_config": {...}}
using crawl4ai's {"type": ..., "params": {...}} envelope.
"""
import argparse
import base64
import json
import os
import sys
import urllib.request

BASE = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235").rstrip("/")
TOKEN = os.environ.get("CRAWL4AI_API_TOKEN")


def request(path, payload=None, method=None, timeout=300):
    url = BASE + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"))
    req.add_header("Content-Type", "application/json")
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        sys.exit(f"HTTP {e.code} from {url}\n{body[:2000]}")
    except urllib.error.URLError as e:
        sys.exit(f"Cannot reach {url} ({e.reason}). Is the server running? "
                 f"Set CRAWL4AI_BASE_URL if it is not on localhost:11235.")


def output(data, path, label="result"):
    text = data if isinstance(data, str) else json.dumps(data, indent=2, ensure_ascii=False)
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"{label} written to {path}")
    else:
        print(text)


def load_config(path):
    if not path:
        return {}
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    return {k: cfg[k] for k in ("browser_config", "crawler_config") if k in cfg}


def save_b64(b64, path, label):
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64))
    print(f"{label} written to {path} ({os.path.getsize(path)} bytes)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("health")

    s = sub.add_parser("md")
    s.add_argument("url")
    s.add_argument("--filter", default="fit", choices=["fit", "raw", "bm25", "llm"])
    s.add_argument("--query")
    s.add_argument("-o", "--out")

    s = sub.add_parser("html")
    s.add_argument("url")
    s.add_argument("-o", "--out")

    s = sub.add_parser("screenshot")
    s.add_argument("url")
    s.add_argument("--wait", type=float, default=2)
    s.add_argument("-o", "--out", default="screenshot.png")

    s = sub.add_parser("pdf")
    s.add_argument("url")
    s.add_argument("-o", "--out", default="page.pdf")

    s = sub.add_parser("js")
    s.add_argument("url")
    s.add_argument("scripts", nargs="+")

    for name in ("crawl", "job"):
        s = sub.add_parser(name)
        s.add_argument("urls", nargs="+")
        s.add_argument("--config")
        if name == "crawl":
            s.add_argument("-o", "--out")

    s = sub.add_parser("status")
    s.add_argument("task_id")
    s.add_argument("-o", "--out")

    a = p.parse_args()

    if a.cmd == "health":
        output(request("/health"), None)
    elif a.cmd == "md":
        r = request("/md", {"url": a.url, "f": a.filter, "q": a.query})
        output(r.get("markdown", r), a.out, "markdown")
    elif a.cmd == "html":
        r = request("/html", {"url": a.url})
        output(r.get("html", r), a.out, "html")
    elif a.cmd == "screenshot":
        r = request("/screenshot", {"url": a.url, "screenshot_wait_for": a.wait})
        save_b64(r["screenshot"], a.out, "screenshot")
    elif a.cmd == "pdf":
        r = request("/pdf", {"url": a.url})
        save_b64(r["pdf"], a.out, "pdf")
    elif a.cmd == "js":
        r = request("/execute_js", {"url": a.url, "scripts": a.scripts})
        output(r.get("js_execution_result", r), None)
    elif a.cmd == "crawl":
        r = request("/crawl", {"urls": a.urls, **load_config(a.config)})
        output(r, a.out)
    elif a.cmd == "job":
        r = request("/crawl/job", {"urls": a.urls, **load_config(a.config)})
        output(r, None)
    elif a.cmd == "status":
        output(request(f"/crawl/job/{a.task_id}"), a.out)


if __name__ == "__main__":
    main()
