---
type: is
id: is-01m2vh2byn9cnvxf5z7n5jgpb6
title: "kash-media: require flexdoc>=0.4.1 and new chopdiff, allow GIL 3.14, open PR"
kind: task
status: in_progress
priority: 1
version: 7
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies: []
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
created_at: 2026-09-19T00:29:12.020Z
updated_at: 2026-09-19T02:18:54.068Z
---
Pin the new flexdoc (keeps cydifflib) and the new chopdiff; relock. If signed off: requires-python >=3.13,<3.15; keep the 3.14 classifier. Install docs must pin a GIL 3.13 or GIL 3.14; uv venv -p 3.14 / --python 3.14 can resolve 3.14t. Do not claim 3.14t. Do not start until both tags are on PyPI.
