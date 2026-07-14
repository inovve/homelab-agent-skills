# Outline API — full endpoint reference

All endpoints: `POST {OUTLINE_URL}/api/<name>` with a JSON body and `Authorization: Bearer <key>`.
Canonical spec: https://www.getoutline.com/developers · OpenAPI source: https://github.com/outline/openapi

## Contents

- [Documents](#documents)
- [Revisions](#revisions)
- [Collections](#collections)
- [Comments](#comments)
- [Attachments (upload flow)](#attachments)
- [Shares](#shares)
- [Users](#users)
- [Groups](#groups)
- [Stars](#stars)
- [Events & audit](#events--audit)
- [File operations (import/export)](#file-operations)
- [Auth & misc](#auth--misc)

## Documents

| Endpoint | Parameters | Notes |
|---|---|---|
| `documents.info` | `id` (UUID or urlId), optional `shareId` | Full doc incl. `text` markdown |
| `documents.export` | `id` | Returns `data` as a markdown string |
| `documents.list` | `collectionId`, `parentDocumentId`, `userId`, `backlinkDocumentId`, `template` (bool), `sort` (`updatedAt`, `title`, `index`, ...), `direction` (`ASC`/`DESC`), `limit`, `offset` | All filters optional |
| `documents.search` | `query`, optional `collectionId`, `documentId`, `userId`, `dateFilter` (`day`/`week`/`month`/`year`), `statusFilter` (array: `draft`/`archived`/`published`), `limit`, `offset` | Returns `[{ranking, context, document}]`; `context` is a highlighted snippet |
| `documents.search_titles` | `query` | Title-only match — fastest way to find a doc by name |
| `documents.viewed` | `limit`, `offset` | Recently viewed by the auth user |
| `documents.drafts` | `collectionId`, `dateFilter`, `limit`, `offset` | Own unpublished drafts |
| `documents.create` | `title`, `text`, `collectionId`, `parentDocumentId`, `templateId`, `template` (bool), `publish` (bool) | Without `publish: true` it's a draft |
| `documents.duplicate` | `id`, optional `title`, `collectionId`, `parentDocumentId`, `recursive` (bool), `publish` | Copy a doc (optionally with children) |
| `documents.import` | multipart form: `file`, `collectionId`, optional `parentDocumentId`, `publish` | Accepts .md, .docx, .html, .txt. Use `curl -F "file=@notes.md" -F "collectionId=..." -F "publish=true"` (no JSON content-type) |
| `documents.update` | `id`, `title`, `text`, `append` (bool), `publish`, `done` | `text` replaces the whole doc unless `append: true` |
| `documents.templatize` | `id` | Turn a doc into a template |
| `documents.move` | `id`, `collectionId`, `parentDocumentId`, `index` | |
| `documents.archive` | `id` | Reversible |
| `documents.restore` | `id`, optional `revisionId` | Un-archive / un-trash / revert to a past revision |
| `documents.delete` | `id`, `permanent` (bool) | Default = trash (reversible). `permanent: true` is irreversible — confirm with user |
| `documents.unpublish` | `id` | Back to draft |
| `documents.users` | `id`, `query` | Users with access to the doc |
| `documents.memberships` | `id`, `query`, `permission` | Direct user memberships |
| `documents.add_user` / `documents.remove_user` | `id`, `userId`, `permission` (`read`/`read_write`) | Sharing change — confirm with user |
| `documents.add_group` / `documents.remove_group` | `id`, `groupId`, `permission` | Sharing change — confirm with user |

## Revisions

| Endpoint | Parameters | Notes |
|---|---|---|
| `revisions.info` | `id` | A single revision (full text) |
| `revisions.list` | `documentId`, `sort`, `direction`, `limit`, `offset` | History of a document |

Revert with `documents.restore` + `revisionId`.

## Collections

| Endpoint | Parameters | Notes |
|---|---|---|
| `collections.list` | `limit`, `offset`, `query` | |
| `collections.info` | `id` | |
| `collections.documents` | `id` | Nested tree of `{id, title, url, children}` — best way to see structure |
| `collections.create` | `name`, `description`, `icon`, `color` (hex), `permission` (`read`/`read_write`/`null`), `private` (bool), `sharing` (bool) | `permission: null` = invite-only visibility |
| `collections.update` | `id` + any create field | |
| `collections.archive` / `collections.restore` | `id` | Reversible |
| `collections.delete` | `id` | Deletes all docs within — confirm with user |
| `collections.export` | `id`, `format` (`outline-markdown`/`json`/`html`) | Async — returns a `fileOperation`; poll then download (see File operations) |
| `collections.export_all` | `format` | Whole workspace export |
| `collections.add_user` / `remove_user` | `id`, `userId`, `permission` | Permission change — confirm with user |
| `collections.add_group` / `remove_group` | `id`, `groupId`, `permission` | Permission change — confirm with user |
| `collections.memberships` | `id`, `query`, `permission` | User memberships |
| `collections.group_memberships` | `id`, `query`, `permission` | Group memberships |

## Comments

| Endpoint | Parameters | Notes |
|---|---|---|
| `comments.list` | `documentId`, `collectionId`, `parentCommentId`, `limit`, `offset` | |
| `comments.info` | `id` | |
| `comments.create` | `documentId`, `text` (markdown) or `data` (ProseMirror JSON), optional `parentCommentId` | `text` is easiest; `parentCommentId` makes it a threaded reply |
| `comments.update` | `id`, `text` or `data` | |
| `comments.delete` | `id` | |

## Attachments

Uploading a file (e.g. an image to embed in a doc) is a two-step flow:

1. `attachments.create` with `{name, contentType, size, documentId}` → returns `data.uploadUrl`, `data.form` (a map of form fields), and `data.attachment` (with the final `url`).
2. POST the file to `uploadUrl` as multipart form-data: include every key/value from `form`, then the file itself as the `file` field (last).
3. Reference it in Markdown: `![name](<attachment.url>)`.

| Endpoint | Parameters | Notes |
|---|---|---|
| `attachments.create` | `name`, `contentType`, `size` (bytes), optional `documentId` | Step 1 above |
| `attachments.redirect` | `id` | 302 to the file — use `curl -L` to download |
| `attachments.delete` | `id` | |

## Shares

| Endpoint | Parameters | Notes |
|---|---|---|
| `shares.list` | `limit`, `offset`, `query`, `sort`, `direction` | |
| `shares.info` | `id` or `documentId` | |
| `shares.create` | `documentId` | Creates a **public** link — publishing action, confirm with user |
| `shares.update` | `id`, `published` (bool), `includeChildDocuments` (bool) | |
| `shares.revoke` | `id` | |

## Users

| Endpoint | Parameters | Notes |
|---|---|---|
| `users.list` | `query`, `emails` (array), `filter` (`all`/`invited`/`active`/`suspended`), `role` (`admin`/`member`/`viewer`/`guest`), `sort`, `limit`, `offset` | |
| `users.info` | `id` (omit for self) | |
| `users.invite` | `invites: [{email, name, role}]` | Sends emails — confirm with user |
| `users.update` | optional `id` (admins only for others), `name`, `avatarUrl`, `language`, `preferences` | |
| `users.update_role` | `id`, `role` | Admin action — confirm with user |
| `users.suspend` / `users.activate` | `id` | Admin action — confirm with user |
| `users.delete` | `id` | Irreversible — confirm with user |

## Groups

| Endpoint | Parameters | Notes |
|---|---|---|
| `groups.list` | `query`, `userId`, `limit`, `offset` | |
| `groups.info` | `id` | |
| `groups.create` | `name` | |
| `groups.update` | `id`, `name` | |
| `groups.delete` | `id` | Confirm with user |
| `groups.memberships` | `id`, `query`, `limit`, `offset` | |
| `groups.add_user` / `groups.remove_user` | `id`, `userId` | |

## Stars

| Endpoint | Parameters | Notes |
|---|---|---|
| `stars.list` | `limit`, `offset` | Starred docs/collections |
| `stars.create` | `documentId` or `collectionId`, optional `index` | |
| `stars.update` | `id`, `index` | Reorder |
| `stars.delete` | `id` | |

## Events & audit

| Endpoint | Parameters | Notes |
|---|---|---|
| `events.list` | `name` (e.g. `documents.create`), `actorId`, `documentId`, `collectionId`, `auditLog` (bool, admin), `sort`, `direction`, `limit`, `offset` | Activity feed / audit trail |
| `searches.list` | `limit`, `offset` | Recent search queries by the team |
| `searches.delete` | `id` | |
| `views.list` | `documentId` | Who viewed a doc |
| `views.create` | `documentId` | Record a view |

## File operations

Exports/imports are asynchronous. `collections.export`, `collections.export_all`, and workspace imports return a `fileOperation` object:

1. Poll `fileOperations.info` with `{id}` until `data.state == "complete"`.
2. Download with `fileOperations.redirect` (`curl -L -o export.zip`).

| Endpoint | Parameters |
|---|---|
| `fileOperations.info` | `id` |
| `fileOperations.list` | `type` (`import`/`export`), `limit`, `offset` |
| `fileOperations.redirect` | `id` |
| `fileOperations.delete` | `id` |

## Auth & misc

| Endpoint | Parameters | Notes |
|---|---|---|
| `auth.info` | — | Current user, team, and policy abilities — best connectivity/permissions test |
| `auth.config` | — | Configured auth providers |
| `apiKeys.list` | `limit`, `offset` | |
| `apiKeys.create` | `name` | Confirm with user |
| `apiKeys.delete` | `id` | Confirm with user |

Note: available endpoints can vary slightly by Outline version (self-hosted) and plan (cloud). If an endpoint 404s, check the instance version against https://www.getoutline.com/developers.
