---
type: is
id: is-01m2vh2bkwetfmrv7bj191nye4
title: "kash-docs: require flexdoc>=0.4.1 and new chopdiff, relock, open PR"
kind: task
status: closed
priority: 2
version: 7
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies: []
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
created_at: 2026-09-19T00:29:11.675Z
updated_at: 2026-09-19T02:57:56.483Z
closed_at: 2026-09-19T02:57:56.483Z
close_reason: "Shipped kash-docs 0.2.8: PR https://github.com/jlevy/kash-docs/pull/9 merged, tag v0.2.8, PyPI requires-python >=3.11,<3.15 with kash-shell>=0.4.12,<0.5, flexdoc[diff]>=0.4.1, chopdiff>=0.4.1,<0.5. GIL 3.14 default graph only; extras still blocked by onnxruntime."
resolution: null
duplicate_of: null
---
From GitHub main at 0.2.7. Pin the new flexdoc (keeps cydifflib) and the new chopdiff. Do not start until both tags are on PyPI.

## Notes

Preparing kash-docs from GitHub main (4cf7b06 / 0.2.7 line) on build/flexdoc-041-gil-314. Waiting on chopdiff 0.4.1 and a kash-shell patch tag before the final lock.
