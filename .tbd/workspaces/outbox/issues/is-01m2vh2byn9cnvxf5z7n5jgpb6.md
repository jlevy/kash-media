---
type: is
id: is-01m2vh2byn9cnvxf5z7n5jgpb6
title: "kash-media: require flexdoc>=0.4.1 and new chopdiff, allow GIL 3.14, open PR"
kind: task
status: closed
priority: 1
version: 8
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies: []
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
created_at: 2026-09-19T00:29:12.020Z
updated_at: 2026-09-19T02:47:06.786Z
closed_at: 2026-09-19T02:47:06.772Z
close_reason: PR 14 merged; v0.4.10 on PyPI with flexdoc[diff]>=0.4.1, chopdiff>=0.4.1, requires-python >=3.13,<3.15. GIL 3.14 metadata done; kash-docs 0.2.7 still <3.14.
resolution: null
duplicate_of: null
---
Pin the new flexdoc (keeps cydifflib) and the new chopdiff; relock. If signed off: requires-python >=3.13,<3.15; keep the 3.14 classifier. Install docs must pin a GIL 3.13 or GIL 3.14; uv venv -p 3.14 / --python 3.14 can resolve 3.14t. Do not claim 3.14t. Do not start until both tags are on PyPI.
