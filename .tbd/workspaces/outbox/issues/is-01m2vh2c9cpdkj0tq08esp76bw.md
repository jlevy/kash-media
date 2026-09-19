---
type: is
id: is-01m2vh2c9cpdkj0tq08esp76bw
title: Verify uv tool install and uvx with --python 3.13 and 3.14
kind: task
status: open
priority: 1
version: 3
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies: []
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
created_at: 2026-09-19T00:29:12.363Z
updated_at: 2026-09-19T01:08:07.385Z
---
After flexdoc 0.3.1, from /tmp: uv tool install --force --python 3.13 kash-media and --python 3.14 must succeed and must not build cydifflib. Same for uvx --python 3.13|3.14 kash-shell@latest. Do not expect a bare install with no --python to succeed if uv selects 3.14t. Re-run after chopdiff + flexdoc 0.4.1 are on PyPI.
