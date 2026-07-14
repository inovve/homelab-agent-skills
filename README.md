# Homelab Agent Skills

[Agent Skills](https://agentskills.io) that let AI agents — Claude Code, Claude.ai, and any tool supporting the open `SKILL.md` format — operate the **self-hosted apps running on your local server**: services in Docker containers, Proxmox VMs and LXCs, or bare metal on your homelab.

Self-hosted apps rarely get official AI integrations. But most of them expose solid REST APIs — and a skill is all it takes to make an agent fluent in one: where the API lives, how auth works, which endpoints matter, and what not to touch without asking. These skills capture that knowledge once, so any agent can use your apps like a power user from the first prompt.

## Skills

| Skill | App | What the agent can do |
|---|---|---|
| [outline](outline/) | [Outline](https://www.getoutline.com) wiki (self-hosted or cloud) | Search, read, create, update, move, and export documents and collections; comments, attachments, public shares, users and groups. |
| [crawl4ai](crawl4ai/) | [crawl4ai](https://github.com/unclecode/crawl4ai) crawler (Docker) | Turn any URL into clean LLM-ready markdown; screenshots, PDFs, JavaScript execution on live pages, structured CSS/LLM extraction, batch and deep site crawls. |

More skills for common homelab services are planned. PRs welcome — the [outline](outline/) skill is a good template: a `SKILL.md` with conventions and common operations, a full API reference in `references/`, and a zero-dependency helper script.

## Design principles

- **Credentials never live in a skill.** Each skill reads its URL and API key from environment variables or a local `.env` file that stays on your machine — the skills are safe to share and commit.
- **Bring your own instance.** Every skill's README explains how to spin up the app (typically Docker) and generate an API key.
- **Private networks welcome.** Instances behind Tailscale, WireGuard, or a LAN-only reverse proxy work fine — the agent calls them from your machine.
- **Destructive actions ask first.** Permanent deletes, public shares, and permission changes are flagged for user confirmation in every skill.

## Installing a skill

**Claude Code (personal, all projects):**

```bash
git clone https://github.com/inovve/homelab-agent-skills.git
cp -r homelab-agent-skills/outline ~/.claude/skills/outline
```

**Claude.ai / Claude Desktop:** zip the skill's folder and upload it under **Settings → Capabilities → Skills**.

**Anything else:** each skill works as plain documentation and standalone tooling too — see the skill's README.

## License

MIT — see individual skill folders.
