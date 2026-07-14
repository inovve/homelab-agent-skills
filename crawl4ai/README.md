# crawl4ai agent skill

An [Agent Skill](https://agentskills.io) that teaches any AI coding agent (Claude Code, Claude.ai/Cowork, or any agent that can read markdown and run shell commands) to use a **self-hosted [crawl4ai](https://github.com/unclecode/crawl4ai) server** for web scraping and crawling:

- Any URL → clean, LLM-ready **markdown** (with main-content filtering)
- **Screenshots** (PNG) and **PDFs** of rendered pages
- **JavaScript execution** on live pages (dynamic sites, lazy loading, infinite scroll)
- **Structured extraction** via CSS/XPath schemas (no LLM needed) or LLM extraction
- **Batch crawls** (up to 100 URLs per call), NDJSON **streaming**, and an async **job queue**
- **Deep crawling** — BFS/best-first over a whole site with domain/URL filters

The skill is plain markdown + one dependency-free Python script, so it works with any agent framework that supports the SKILL.md convention — and even without one, you can just point your agent at `SKILL.md`.

## Contents

```
crawl4ai/
├── SKILL.md            The skill — connection, endpoint guide, quick recipes
├── references/
│   └── api.md          Full API reference (all endpoints, configs, strategies)
├── scripts/
│   └── c4ai.py         Stdlib-only CLI client (health/md/screenshot/pdf/js/crawl/job)
├── README.md           This file
└── LICENSE             MIT
```

## 1. Run a crawl4ai server

You need a running crawl4ai Docker server. Quickest start:

```bash
docker run -d \
  --name crawl4ai \
  -p 11235:11235 \
  --shm-size=1g \
  unclecode/crawl4ai:latest
```

Verify: `curl http://localhost:11235/health` → `{"status": "ok", ...}`.
Open `http://localhost:11235/playground` in a browser to explore the API interactively.

Notes:

- `--shm-size=1g` matters — Chromium inside the container needs shared memory.
- Pin a version tag in production instead of `latest` (e.g. `unclecode/crawl4ai:0.7.4`).
- To enable LLM-based extraction (`/llm`, `f=llm`, `LLMExtractionStrategy`), pass provider keys to the container, e.g. `-e OPENAI_API_KEY=...` or `-e ANTHROPIC_API_KEY=...`, or use a `.llm.env` file. Everything else works without any keys.
- For remote access from other machines, put it behind your VPN/tailnet or a reverse proxy — see [Security](#4-security) below. (Running it on a [Tailscale](https://tailscale.com) node works great: the server is reachable from all your devices but not the internet.)
- Full deployment options (docker-compose, config.yml, JWT auth, scaling): https://docs.crawl4ai.com

## 2. Install the skill

### Claude Code

Copy this folder into your skills directory:

```bash
# Personal (all projects)
cp -r crawl4ai ~/.claude/skills/crawl4ai

# Or per-project
cp -r crawl4ai <project>/.claude/skills/crawl4ai
```

New sessions pick it up automatically; the agent invokes it whenever a task involves scraping/crawling. You can also trigger it explicitly with `/crawl4ai`.

### Claude.ai / Cowork

Zip the folder (`SKILL.md` must be at the zip root) and upload it in **Settings → Capabilities → Skills**.

### Other agents (Codex, Gemini CLI, OpenCode, custom frameworks...)

Any of these work:

- If the agent supports the [Agent Skills](https://agentskills.io) format, install the folder in its skills directory.
- Otherwise, reference the file directly in the agent's context/instructions file (`AGENTS.md`, `GEMINI.md`, system prompt, ...):
  > For web scraping/crawling, read and follow `path/to/crawl4ai/SKILL.md`.
- Or skip the skill entirely and let the agent call `scripts/c4ai.py` — the `--help` output documents every command.

### MCP alternative

The crawl4ai server also exposes its tools over MCP at `http://<server>:11235/mcp/sse`. If your agent speaks MCP you can register that endpoint instead of (or alongside) this skill — the skill's REST approach needs no registration and gives the agent finer control, so both are valid.

## 3. Point the skill at your server

The skill and the helper script resolve the server from environment variables:

| Variable | Meaning | Default |
|---|---|---|
| `CRAWL4AI_BASE_URL` | Base URL of your server | `http://localhost:11235` |
| `CRAWL4AI_API_TOKEN` | JWT, only if your server has auth enabled | *(unset)* |

Set `CRAWL4AI_BASE_URL` wherever your agent inherits its environment (shell profile, `.env`, agent settings). If it's unset and localhost doesn't respond, the skill tells the agent to ask you for the URL — so it works even with zero configuration.

Examples:

```bash
# bash/zsh
export CRAWL4AI_BASE_URL="http://crawl4ai.my-tailnet.ts.net:11235"

# PowerShell (persistent)
[Environment]::SetEnvironmentVariable("CRAWL4AI_BASE_URL", "http://crawl4ai.my-tailnet.ts.net:11235", "User")
```

Smoke test:

```bash
python scripts/c4ai.py health
python scripts/c4ai.py md https://example.com
```

## 4. Security

- **Don't expose the server to the public internet unauthenticated.** It's a remote-controlled browser: anyone who can reach it can crawl arbitrary sites from your IP and reach hosts on the server's network. Keep it on localhost, a VPN/tailnet, or behind a reverse proxy with auth.
- crawl4ai supports JWT auth (`security.jwt_enabled: true` in the server's `config.yml`). Clients then obtain a token via `POST /token {"email": "..."}` and send `Authorization: Bearer <token>`; the skill handles this when `CRAWL4AI_API_TOKEN` is set.
- The skill instructs the agent to treat crawled page content as **data, not instructions** (prompt-injection hygiene), to bound deep crawls, and to crawl politely.

## Quick reference

| Task | Call |
|---|---|
| Page → markdown | `POST /md` `{"url": "...", "f": "fit"}` |
| Screenshot / PDF | `POST /screenshot` / `POST /pdf` (base64 in response) |
| Run JS on a page | `POST /execute_js` `{"url": "...", "scripts": ["return ..."]}` |
| Batch crawl + extraction | `POST /crawl` `{"urls": [...], "crawler_config": {...}}` |
| Stream results | `POST /crawl/stream` (NDJSON) |
| Async job | `POST /crawl/job` → `GET /crawl/job/{task_id}` |

Full details in [SKILL.md](SKILL.md) and [references/api.md](references/api.md).

## License

MIT — see [LICENSE](LICENSE).

Not affiliated with the crawl4ai project. crawl4ai itself is by [@unclecode](https://github.com/unclecode/crawl4ai) (Apache-2.0).
