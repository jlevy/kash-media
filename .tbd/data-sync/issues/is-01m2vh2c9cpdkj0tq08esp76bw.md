---
type: is
id: is-01m2vh2c9cpdkj0tq08esp76bw
title: Verify uv tool install and uvx with --python 3.13 and 3.14
kind: task
status: closed
priority: 1
version: 8
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies: []
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
created_at: 2026-09-19T00:29:12.363Z
updated_at: 2026-09-19T04:41:44.831Z
closed_at: 2026-09-19T04:41:44.830Z
close_reason: "Verified kash-media 0.4.11: uv tool install --python 3.13 and GIL 3.14.6 venv resolve include cydifflib 1.2.0. uvx --python 3.13 kash --version is kash-shell 0.4.12. 3.14t still fails as expected."
resolution: null
duplicate_of: null
---
After the one flexdoc tag and the new chopdiff are on PyPI, from /tmp: tool install / uvx must succeed on an explicit GIL 3.13 and GIL 3.14. The graph must still include cydifflib. Do not expect a bare install or a --python 3.14 that resolves 3.14t to succeed.

## Notes

kash-docs==0.2.8 and kash-shell==0.4.12 uvx succeed on GIL 3.13.7 and GIL 3.14.6 with flexdoc 0.4.1, chopdiff 0.4.1, cydifflib 1.2.0. kash-media 0.4.10 still locks kash-docs==0.2.7 / kash-shell==0.4.10; sibling must relock before this verify can pass for kash-media.
