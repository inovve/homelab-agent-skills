# Outline Skill for AI Agents

An [Agent Skill](https://agentskills.io) that gives AI agents full read/write access to your [Outline](https://www.getoutline.com) wiki — cloud or self-hosted — through its REST API. It follows the open `SKILL.md` format, so it works with **Claude Code, Claude.ai, and any agent that supports Agent Skills** — and degrades gracefully for agents that don't (see [Other agents](#other-agents)).

Ask your agent things like:

- *"Search my wiki for the onboarding checklist and summarize it"*
- *"Save this analysis as a new page in the Engineering collection"*
- *"Append today's meeting notes to the Weekly Sync doc"*
- *"Export the Handbook collection as markdown"*
- *"Import these .docx files into a new collection"*

## Features

- **Documents** — search (full-text and title), read, create, update/append, duplicate, move, archive, trash/restore, publish/unpublish, templates, revision history and rollback
- **Collections** — list, browse tree structure, create, update, export (markdown/HTML/JSON), import
- **Comments** — read, create (threaded), update, delete
- **Attachments** — upload files/images and embed them in documents
- **Shares** — create and revoke public links (with confirmation)
- **Users & groups** — list, invite, manage memberships (admin actions require confirmation)
- **Activity** — events feed, audit log, document views, stars
- Ships with a zero-dependency Python helper (`scripts/outline_api.py`) so calls work identically on macOS, Linux, and Windows

Your instance URL and API key are **never stored in the skill** — they live in a local `.env` file that stays on your machine.

## Setup

### 1. Get an Outline instance

Pick one:

- **Cloud (easiest)** — sign up at [getoutline.com](https://www.getoutline.com). Your URL is `https://app.getoutline.com`.
- **Self-hosted** — Outline is open source ([outline/outline](https://github.com/outline/outline)). Follow the [official hosting guide](https://docs.getoutline.com/s/hosting/) to run it with Docker. A minimal path:
  1. Provision a host with Docker and a Postgres + Redis instance.
  2. Use the provided `docker-compose` setup from the hosting guide, set `URL`, `SECRET_KEY`, `UTILS_SECRET`, and an auth provider (Slack, Google, OIDC, or email magic links).
  3. Put it behind HTTPS (reverse proxy, or something like Tailscale/Cloudflare Tunnel for private access).

### 2. Create an API key

In Outline: click your avatar → **Settings** → **API Keys** (under "Account") → **New API key…**. Copy the `ol_api_...` token — it's shown once.

The key inherits *your* permissions. If you only need read access, consider creating it from a viewer-role account.

### 3. Store your credentials

Create the file `~/.config/outline/.env` (Windows: `%USERPROFILE%\.config\outline\.env`):

```
OUTLINE_URL=https://app.getoutline.com
OUTLINE_API_KEY=ol_api_your_key_here
```

Use your own domain for `OUTLINE_URL` if self-hosting. A template is provided in [.env.example](.env.example). Alternatively, set `OUTLINE_URL` and `OUTLINE_API_KEY` as environment variables — they take precedence over the file.

> **Never commit this file.** It is not part of the skill and the skill never copies the key anywhere.

### 4. Install the skill

**Claude Code (personal, all projects):**

```bash
git clone https://github.com/inovve/skills.git
cp -r skills/outline ~/.claude/skills/outline
```

**Claude Code (single project):** copy the `outline/` folder to `.claude/skills/outline` inside the project.

**Claude.ai / Claude Desktop:** zip the `outline/` folder and upload it under **Settings → Capabilities → Skills**.

**Other skill-capable agents** (any tool implementing the [Agent Skills format](https://agentskills.io)): place the `outline/` folder in that tool's skills directory. The skill uses only the standard `name` + `description` frontmatter, so no adaptation is needed.

#### Other agents

No skill support at all? The skill still works as plain documentation and tooling:

- Point the agent at [SKILL.md](SKILL.md) ("read this file, then do X with my wiki") — everything it needs is in there and in [references/api.md](references/api.md).
- Or use [scripts/outline_api.py](scripts/outline_api.py) directly — it's a standalone, dependency-free CLI for the whole Outline API, usable by any agent with shell access, or by you.

### 5. Verify

Ask your agent: *"Check my Outline connection"* — or run it yourself:

```bash
python scripts/outline_api.py auth.info
```

You should see your user and team info.

## How it works

Outline's API is RPC-style: every operation is a `POST {url}/api/<resource>.<method>` with a JSON body and a Bearer token. [SKILL.md](SKILL.md) teaches the agent the conventions and the common operations; [references/api.md](references/api.md) is the complete endpoint reference loaded on demand.

The skill is deliberately conservative with destructive or outward-facing actions: permanent deletes, public share links, permission changes, and user invites always get confirmed with you first.

## Alternative: MCP server

Outline instances also expose an MCP endpoint at `{OUTLINE_URL}/mcp` (streamable HTTP), which any MCP client can connect to. For Claude Code:

```bash
claude mcp add --transport http outline https://YOUR_OUTLINE_URL/mcp
```

The two approaches coexist fine; this skill needs no MCP setup and works in agents that have no MCP support.

## Troubleshooting

- **401 Unauthorized** — key is wrong, revoked, or the `.env` wasn't found. Run the verify step above; the script tells you where it looked.
- **Cannot reach host** — self-hosted instances on private networks (VPN/Tailscale) are only reachable when you're connected to that network.
- **404 on an endpoint** — self-hosted versions can lag the cloud API. Check your version against the [official API docs](https://www.getoutline.com/developers).

## License

MIT — see [LICENSE](LICENSE).
