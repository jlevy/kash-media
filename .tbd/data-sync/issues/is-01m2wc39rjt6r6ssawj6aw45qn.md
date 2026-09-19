---
type: is
id: is-01m2wc39rjt6r6ssawj6aw45qn
title: Bump kash-media to kash-shell>=0.4.13 and release v0.4.12
kind: task
status: closed
priority: 1
version: 3
labels: []
dependencies: []
created_at: 2026-09-19T08:21:34.097Z
updated_at: 2026-09-19T08:28:24.423Z
closed_at: 2026-09-19T08:28:24.422Z
close_reason: "Merged PR 18 and published kash-media v0.4.12. PyPI requires kash-shell>=0.4.13. Smoke test: kash-media 0.4.12 + kash-shell 0.4.13 + mcp 1.30.0."
resolution: null
duplicate_of: null
---
Raise the kash-shell floor so published kash-media installs cannot resolve the 0.4.12 startup crash. Relock, PR, tag v0.4.12.
