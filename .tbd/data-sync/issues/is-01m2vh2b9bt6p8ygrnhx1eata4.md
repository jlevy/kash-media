---
type: is
id: is-01m2vh2b9bt6p8ygrnhx1eata4
title: "kash-shell: require flexdoc>=0.4.1 and new chopdiff, relock, open PR"
kind: task
status: closed
priority: 1
version: 8
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies: []
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
created_at: 2026-09-19T00:29:11.338Z
updated_at: 2026-09-19T02:57:56.173Z
closed_at: 2026-09-19T02:57:56.171Z
close_reason: "Shipped kash-shell 0.4.12: PR https://github.com/jlevy/kash/pull/24 merged, tag v0.4.12, PyPI requires-python >=3.11,<3.15 with flexdoc[diff]>=0.4.1 and chopdiff>=0.4.1,<0.5. GIL 3.14 only; cydifflib stays via flexdoc[diff]."
resolution: null
duplicate_of: null
---
Pin the new flexdoc (planned >=0.4.1, keeps cydifflib) and the new chopdiff. Relock. PR on jlevy/kash. Do not start until both tags are on PyPI.

## Notes

Unblocked: chopdiff 0.4.1 is on PyPI with flexdoc[diff].
