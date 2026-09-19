---
type: is
id: is-01m2vh2ayn9vkmzkgbwmea9ngp
title: "flexdoc: tag and publish one release from main (keep cydifflib)"
kind: task
status: open
priority: 1
version: 10
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies:
  - type: blocks
    target: is-01m2vh5wwc3bfdbf5h5mretjyq
  - type: blocks
    target: is-01m2vh5x6y1njh81mrtzbb7ts4
  - type: blocks
    target: is-01m2vh2c9cpdkj0tq08esp76bw
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
hold: blocked
hold_until: null
created_at: 2026-09-19T00:29:10.996Z
updated_at: 2026-09-19T01:22:08.381Z
---
One flexdoc release from main that keeps PyPI cydifflib>=1.2.0 (planned v0.4.1). Vehicle is a new PR (kashm-qbj5), not 24 or 25. Do not tag until that PR lands and the user signs off. This tag does not reach kash until chopdiff is published (kashm-0po5).

## Notes

Blocked on kashm-qbj5 and user signoff. Do not tag. Do not merge PR 24 or 25. No required fork.
