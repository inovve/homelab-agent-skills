# crawl4ai server — full API reference

All paths are relative to your server base URL (`CRAWL4AI_BASE_URL`, default `http://localhost:11235`). All bodies JSON. Add `Authorization: Bearer <token>` only if the server has JWT enabled.

Ground truth for anything not covered here: `GET /openapi.json` (endpoint shapes) and `GET /schema` (exhaustive BrowserConfig + CrawlerRunConfig parameter schemas). Endpoint availability can vary slightly between crawl4ai versions — the OpenAPI spec of *your* server is authoritative.

## Contents

1. [Endpoint catalog](#endpoint-catalog)
2. [Simple endpoints](#simple-endpoints) — /md, /html, /screenshot, /pdf, /execute_js, /llm
3. [/crawl and config serialization](#crawl-and-config-serialization)
4. [CrawlerRunConfig parameters](#crawlerrunconfig-parameters)
5. [BrowserConfig parameters](#browserconfig-parameters)
6. [Extraction strategies](#extraction-strategies)
7. [Markdown generation and content filters](#markdown-generation-and-content-filters)
8. [Deep crawling](#deep-crawling)
9. [Streaming and the job queue](#streaming-and-the-job-queue)
10. [Sessions, hooks, monitoring, MCP](#sessions-hooks-monitoring-mcp)

## Endpoint catalog

| Method + path | Purpose |
|---|---|
| `GET /health` | Liveness + version |
| `POST /md` | URL → markdown with content filter |
| `POST /html` | URL → preprocessed HTML (for schema building) |
| `POST /screenshot` | URL → base64 PNG |
| `POST /pdf` | URL → base64 PDF |
| `POST /execute_js` | Run JS snippets on a page, returns full CrawlResult |
| `POST /crawl` | Full crawl of up to 100 URLs, blocking |
| `POST /crawl/stream` | Same, but NDJSON streamed per-result |
| `POST /crawl/job` / `GET /crawl/job/{task_id}` | Async crawl with polling + optional webhook |
| `POST /llm/job` / `GET /llm/job/{task_id}` | Async LLM extraction job |
| `GET /llm/{url}?q=...` | Synchronous LLM Q&A over a page |
| `POST /token` | Get a JWT (only when security is enabled) |
| `GET /schema` | Full BrowserConfig/CrawlerRunConfig schemas |
| `POST /config/dump` | Validate/normalize a config object |
| `GET /ask` | crawl4ai library docs/context for AI assistants |
| `GET /hooks/info` | Available hook points |
| `GET /monitor/health`, `/monitor/requests`, `/monitor/browsers`, `/monitor/endpoints/stats`, `/monitor/timeline`, `/monitor/logs/errors` | Server observability |
| `POST /monitor/actions/cleanup` | Force-kill idle pooled browsers |
| `GET /mcp/sse`, `GET /mcp/schema` | Built-in MCP server (SSE transport) |
| `GET /metrics` | Prometheus metrics |
| `GET /playground` | Interactive UI for building/testing requests |

## Simple endpoints

### POST /md

```json
{"url": "https://example.com", "f": "fit", "q": null, "c": "0"}
```

- `f` (filter): `raw` (full page markdown), `fit` (main-content pruning, default), `bm25` (rank blocks against `q`), `llm` (LLM-filtered against `q` — requires server-side LLM key).
- `q`: query string, used by `bm25`/`llm` only.
- `c`: cache-bust counter — bump it (or pass a random string) to force a re-fetch.
- Response: `{"url", "filter", "query", "cache", "markdown", "success"}`.

### POST /html

`{"url": "..."}` → `{"html", "url", "success"}`. The HTML is sanitized/preprocessed for building extraction schemas, not the raw page source (use `/crawl` and read `results[0].html` for raw).

### POST /screenshot

`{"url": "...", "screenshot_wait_for": 2}` → `{"success", "screenshot"}` (base64 PNG). `screenshot_wait_for` = seconds to wait before capture. Avoid `output_path` — it saves inside the server container, not on the client machine.

### POST /pdf

`{"url": "..."}` → `{"success", "pdf"}` (base64). Same `output_path` caveat.

### POST /execute_js

```json
{"url": "https://example.com", "scripts": ["return document.title", "return document.querySelectorAll('a').length"]}
```

Each script must be an expression/body that **returns** a value (they're wrapped as functions). Returns a full CrawlResult; per-script return values are in `js_execution_result` (`{"success": true, "results": [...]}`).

### GET /llm/{url}?q=...

URL-encode the target page URL in the path: `GET /llm/https%3A%2F%2Fexample.com?q=What is this page about`. Requires an LLM provider key configured on the server — if it errors, fall back to `/md` and answer from the markdown yourself.

## /crawl and config serialization

```json
{
  "urls": ["https://a.com", "https://b.com"],
  "browser_config": {"type": "BrowserConfig", "params": {...}},
  "crawler_config": {"type": "CrawlerRunConfig", "params": {...}}
}
```

Every config object — including nested strategies, filters, scorers — is serialized as `{"type": "<PythonClassName>", "params": {...constructor kwargs...}}`. Plain values (strings, numbers, lists, dicts-as-schemas) stay plain. Enum values are passed as strings (e.g. `"cache_mode": "BYPASS"`).

### CrawlResult (each element of `results`)

Key fields: `url`, `redirected_url`, `success`, `status_code`, `error_message`, `markdown` (dict: `raw_markdown`, `fit_markdown`, `markdown_with_citations`, `references_markdown`, `fit_html`), `cleaned_html`, `html`, `fit_html`, `links` (`{"internal": [...], "external": [...]}` with text/title per link), `media` (`images`, `videos`, `audios` with scores), `tables` (auto-detected data tables: headers + rows), `metadata` (page title, description, og:*), `extracted_content` (JSON **string** when an extraction strategy ran — `json.loads` it), `screenshot`/`pdf`/`mhtml` (base64, when requested), `js_execution_result`, `session_id`, `response_headers`, `ssl_certificate`.

## CrawlerRunConfig parameters

The most useful `params` (all optional):

**Content selection**
- `css_selector`: crop the page to matching elements before processing
- `target_elements`: list of selectors — markdown/extraction focus on these, but links/media still come from the whole page
- `excluded_tags`: e.g. `["nav", "footer", "aside", "form"]`
- `excluded_selector`: CSS selector to strip (e.g. `"#ads, .cookie-banner"`)
- `word_count_threshold`: min words per text block; lower it for sparse pages
- `exclude_external_links`, `exclude_social_media_links`, `exclude_external_images`: booleans
- `process_iframes`: include iframe content
- `remove_overlay_elements`: kill modals/popups

**Page interaction**
- `js_code`: string or list of JS snippets executed after load
- `js_only`: re-use the existing page in a session — run JS without re-navigating (needs `session_id`)
- `wait_for`: `"css:.selector"` or `"js:() => window.loaded === true"`
- `wait_until`: `"domcontentloaded"` (default) / `"networkidle"` / `"load"`
- `page_timeout`: ms, default 60000
- `delay_before_return_html`: seconds to linger before capture
- `scan_full_page` + `scroll_delay`: auto-scroll to trigger lazy loading
- `simulate_user`, `override_navigator`, `magic`: anti-bot-detection heuristics
- `virtual_scroll_config`: for virtualized feeds — `{"type": "VirtualScrollConfig", "params": {"container_selector": "#feed", "scroll_count": 10, "scroll_by": "container_height", "wait_after_scroll": 0.5}}`

**Caching & session**
- `cache_mode`: `"ENABLED"` / `"BYPASS"` / `"DISABLED"` / `"READ_ONLY"` / `"WRITE_ONLY"`
- `session_id`: string — reuse one browser page across sequential `/crawl` calls (multi-step flows)

**Output**
- `screenshot`, `pdf`, `capture_mhtml`: booleans — adds base64 payloads to the result
- `stream`: on `/crawl/stream`, controls per-result streaming
- `verbose`: server-side logging

**Strategies** (each a `{"type", "params"}` object): `extraction_strategy`, `markdown_generator`, `deep_crawl_strategy`, `proxy_config` (`{"type": "ProxyConfig", "params": {"server": "http://host:port", "username": "...", "password": "..."}}`)

## BrowserConfig parameters

- `headless` (default true), `browser_type` (`"chromium"`)
- `viewport_width` / `viewport_height` (e.g. 1920/1080 for desktop layouts)
- `user_agent`, or `user_agent_mode: "random"`
- `enable_stealth`: harder-to-detect browser
- `text_mode`: disables images — much faster for text scraping
- `light_mode`: disables background features for speed
- `java_script_enabled` (default true)
- `cookies`: `[{"name", "value", "domain", "path"}]`, `headers`: dict
- `extra_args`: list of Chromium flags

## Extraction strategies

### JsonCssExtractionStrategy (no LLM — fast, deterministic)

```json
"extraction_strategy": {"type": "JsonCssExtractionStrategy", "params": {
  "schema": {
    "name": "articles",
    "baseSelector": "article.post",
    "baseFields": [{"name": "data_id", "type": "attribute", "attribute": "data-id"}],
    "fields": [
      {"name": "title", "selector": "h2", "type": "text"},
      {"name": "url", "selector": "a.link", "type": "attribute", "attribute": "href"},
      {"name": "img", "selector": "img", "type": "attribute", "attribute": "src"},
      {"name": "body", "selector": ".content", "type": "html"},
      {"name": "tags", "selector": ".tag", "type": "list", "fields": [{"name": "tag", "type": "text"}]}
    ]
  }
}}
```

Field types: `text`, `attribute`, `html`, `regex` (+ `pattern`), `list` / `nested` / `nested_list` (with sub-`fields`). One result object per `baseSelector` match; result lands in `extracted_content` as a JSON string. `JsonXPathExtractionStrategy` is identical but with XPath selectors.

Workflow for an unfamiliar site: `POST /html` to get preprocessed HTML → inspect it → write the schema → test on one URL → run the batch.

### LLMExtractionStrategy

```json
"extraction_strategy": {"type": "LLMExtractionStrategy", "params": {
  "llm_config": {"type": "LLMConfig", "params": {"provider": "openai/gpt-4o-mini", "api_token": "env:OPENAI_API_KEY"}},
  "schema": {"type": "object", "properties": {"price": {"type": "number"}}},
  "extraction_type": "schema",
  "instruction": "Extract the product name and price"
}}
```

Depends on LLM keys available to the server (`api_token: "env:VAR"` reads the *server's* env). If it fails, prefer: crawl to markdown, then have the agent extract — the agent is an LLM.

## Markdown generation and content filters

```json
"markdown_generator": {"type": "DefaultMarkdownGenerator", "params": {
  "content_filter": {"type": "PruningContentFilter", "params": {"threshold": 0.48, "threshold_type": "dynamic"}},
  "options": {"ignore_links": true, "ignore_images": true, "body_width": 0}
}}
```

- `PruningContentFilter`: heuristic main-content pruning → populates `markdown.fit_markdown`
- `BM25ContentFilter`: `{"user_query": "...", "bm25_threshold": 1.0}` — keeps blocks relevant to a query
- `LLMContentFilter`: LLM-based, needs `llm_config`

For a quick single page, `/md` with `f=fit` does the same thing with less ceremony.

## Deep crawling

Crawl a whole site section from a seed URL. Set on `crawler_config.params.deep_crawl_strategy`:

```json
"deep_crawl_strategy": {"type": "BFSDeepCrawlStrategy", "params": {
  "max_depth": 2,
  "max_pages": 30,
  "include_external": false,
  "filter_chain": {"type": "FilterChain", "params": {"filters": [
    {"type": "DomainFilter", "params": {"allowed_domains": ["docs.example.com"]}},
    {"type": "URLPatternFilter", "params": {"patterns": ["*/guide/*"]}},
    {"type": "ContentTypeFilter", "params": {"allowed_types": ["text/html"]}}
  ]}}
}}
```

- Strategies: `BFSDeepCrawlStrategy` (breadth-first), `DFSDeepCrawlStrategy`, `BestFirstCrawlingStrategy` (add `url_scorer`: `{"type": "KeywordRelevanceScorer", "params": {"keywords": ["pricing", "api"], "weight": 0.7}}`)
- **Always bound `max_pages`** — an unbounded deep crawl can run for a very long time and hammer the target site.
- Each crawled page arrives as a separate CrawlResult with `metadata.depth` and `metadata.score`. Deep crawls are the main case for `/crawl/stream` or `/crawl/job` instead of blocking `/crawl`.

## Streaming and the job queue

### POST /crawl/stream

Same payload as `/crawl`; add `"stream": true` in `crawler_config.params`. Response is NDJSON — one CrawlResult per line as each finishes, terminated by `{"status": "completed"}`. With curl, use `-N` (no buffering) and append each line to a file.

### POST /crawl/job (fire and forget)

```json
{"urls": ["..."], "browser_config": {...}, "crawler_config": {...},
 "webhook_config": {"webhook_url": "https://...", "webhook_data_in_payload": false}}
```

→ `202 {"task_id": "..."}`. Poll `GET /crawl/job/{task_id}` → `{"status": "PENDING"|"PROCESSING"|"COMPLETED"|"FAILED", "result": ...}`. `webhook_config` is optional. `POST /llm/job` works the same for LLM extraction (`{"url", "q", "schema"?, "provider"?}`).

## Sessions, hooks, monitoring, MCP

- **Sessions**: pass the same `session_id` in `crawler_config` across sequential `/crawl` calls to keep one browser page alive — e.g. call 1 loads and clicks "next" via `js_code`, call 2 uses `js_only: true` to harvest without reloading.
- **Hooks**: `/crawl` accepts a `hooks` object (`{"code": {"<hook_point>": "python code"}, "timeout": 30}`); `GET /hooks/info` lists hook points. Rarely needed — prefer `js_code`/`wait_for`.
- **Monitoring**: `GET /monitor/health` (memory, browser pool), `GET /monitor/requests?status=error`, `GET /monitor/logs/errors` — check these when crawls hang or fail oddly.
- **MCP**: the server also exposes its tools over MCP at `GET /mcp/sse` — agents with MCP support can register it as an alternative to raw REST, but the REST API covered here needs no extra setup.
