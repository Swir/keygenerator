# Changelog

## 1.1.0 — 2026-10-19

- Fix the missing pattern-validation method that prevented adding custom patterns.
- Validate pattern shape, length, stored JSON schema and collection size.
- Keep bounded ten-code generation and all widget updates on the Tk main thread.
- Save patterns atomically under the current user's local application-data folder; preserve corrupt input in a backup before recovery.
- Read legacy working-directory patterns without modifying the original file.
- Show generation results in a resizable table with similarity highlighting and clipboard error handling.
- Add regression and packaged-runtime tests for pattern creation, persistence and generation.

This application produces synthetic pattern-shaped test strings, not valid software licenses, credentials or cryptographic secrets.
