#!/usr/bin/env python3
"""Call the Outline API.

Usage:
    python outline_api.py <endpoint> [json-body | @file.json]

Examples:
    python outline_api.py auth.info
    python outline_api.py documents.search '{"query": "roadmap"}'
    python outline_api.py documents.create @body.json

Configuration is resolved in order:
    1. OUTLINE_URL and OUTLINE_API_KEY environment variables
    2. ~/.config/outline/.env  (KEY=value lines)

Exits 0 on success, 1 on API error or misconfiguration. Prints the JSON
response (pretty) to stdout; errors go to stderr. Requires only the Python
standard library.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ENV_FILE = Path.home() / ".config" / "outline" / ".env"


def load_config():
    url = os.environ.get("OUTLINE_URL")
    key = os.environ.get("OUTLINE_API_KEY")
    if not (url and key) and ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip("'\"")
            if k == "OUTLINE_URL" and not url:
                url = v
            elif k == "OUTLINE_API_KEY" and not key:
                key = v
    if not (url and key):
        sys.exit(
            "Missing configuration. Set OUTLINE_URL and OUTLINE_API_KEY as "
            f"environment variables, or create {ENV_FILE} with those two lines. "
            "Create an API key in Outline under Settings > API Keys."
        )
    return url.rstrip("/"), key


def main():
    # Windows consoles default to a legacy codepage that cannot print
    # emoji (common in Outline icons); force UTF-8 output.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0 if len(sys.argv) >= 2 else 1)

    endpoint = sys.argv[1].lstrip("/")
    if endpoint.startswith("api/"):
        endpoint = endpoint[4:]

    raw = sys.argv[2] if len(sys.argv) > 2 else "{}"
    if raw.startswith("@"):
        raw = Path(raw[1:]).read_text(encoding="utf-8")
    try:
        body = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"Body is not valid JSON: {e}")

    url, key = load_config()
    req = urllib.request.Request(
        f"{url}/api/{endpoint}",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as e:
        try:
            payload = json.load(e)
        except Exception:
            sys.exit(f"HTTP {e.code}: {e.reason}")
        print(json.dumps(payload, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        sys.exit(f"Cannot reach {url}: {e.reason}")

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if payload.get("ok") is False:
        sys.exit(1)


if __name__ == "__main__":
    main()
