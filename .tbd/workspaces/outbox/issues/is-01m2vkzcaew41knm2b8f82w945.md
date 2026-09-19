---
type: is
id: is-01m2vkzcaew41knm2b8f82w945
title: "flexdoc: keep cydifflib and apply GIL 3.14 install fix"
kind: task
status: closed
priority: 1
version: 6
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies:
  - type: blocks
    target: is-01m2vh2ayn9vkmzkgbwmea9ngp
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
hold: null
hold_until: null
created_at: 2026-09-19T01:19:59.821Z
updated_at: 2026-09-19T01:21:57.375Z
closed_at: 2026-09-19T01:21:57.374Z
close_reason: "Build-debug: GIL 3.14 already builds and imports published cydifflib 1.2.0 sdist (~17s). No fork, vendor, or stdlib drop required. 3.14t fail is Cython 3.0.x + freethreaded. Fork is optional later only if we want 3.14t to install cydifflib."
resolution: null
duplicate_of: null
---
Rewrite or replace flexdoc PR 25 so it keeps the cydifflib hard dep and the cydifflib import. Apply whatever GIL 3.14 install fix sibling debugging recommends (wheel, vendor, or fallback only if required). Do not drop to stdlib. Do not merge the current hard-drop patch. Blocks the single flexdoc tag from main (kashm-roqq).

## Notes

Sibling is still debugging GIL 3.14 install. Keep cydifflib. PR 25 is the intended vehicle and must not drop. PR 24 will not ship.
