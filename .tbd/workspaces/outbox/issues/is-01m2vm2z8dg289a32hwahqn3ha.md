---
type: is
id: is-01m2vm2z8dg289a32hwahqn3ha
title: "flexdoc: new 0.4.1 PR from main (keep cydifflib; do not merge 24/25)"
kind: task
status: closed
priority: 1
version: 8
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies:
  - type: blocks
    target: is-01m2vh2ayn9vkmzkgbwmea9ngp
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
hold: null
hold_until: null
created_at: 2026-09-19T01:21:57.516Z
updated_at: 2026-09-19T01:30:37.395Z
closed_at: 2026-09-19T01:30:37.393Z
close_reason: Filed https://github.com/jlevy/flexdoc/pull/26 from origin/main. requires-python >=3.11,<3.15. Guard in flexdoc.util.cpython_build, called from token_diffs before import cydifflib. cydifflib kept. Commented on 24/25. Do not tag. Build/wheel-smoke CI passed including 3.14; audit fail is pre-existing pip 26.1.2 CVE on sibling PRs too.
resolution: null
duplicate_of: null
---
New PR from flexdoc main (not 24 or 25): https://github.com/jlevy/flexdoc/pull/26. Keep cydifflib>=1.2.0. requires-python >=3.11,<3.15 (GIL 3.14 yes, 3.14t no). Import-time Py_GIL_DISABLED guard before import cydifflib. Do not fork, vendor, merge 24/25, or tag. Blocks the single flexdoc tag (kashm-roqq).

## Notes

PR filed: https://github.com/jlevy/flexdoc/pull/26 from origin/main. requires-python >=3.11,<3.15. Guard in src/flexdoc/util/cpython_build.py, called from token_diffs before import cydifflib. cydifflib>=1.2.0 kept. Commented on #24 and #25. Do not tag. Waiting on flexdoc CI.
