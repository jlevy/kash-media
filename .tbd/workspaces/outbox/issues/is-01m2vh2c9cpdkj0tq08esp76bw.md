---
type: is
id: is-01m2vh2c9cpdkj0tq08esp76bw
title: Verify uv tool install and uvx from an unpinned directory
kind: task
status: open
priority: 1
version: 1
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies: []
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
created_at: 2026-09-19T00:29:12.363Z
updated_at: 2026-09-19T00:29:12.363Z
---
From /tmp (no .python-version): uv tool install --force kash-media and uvx kash-shell@latest with no --python must succeed and must not build cydifflib. Also re-check --python 3.13. This can run as soon as 0.3.1 is on PyPI; re-run after consumer PRs merge.
