---
type: is
id: is-01m2vh2am6gq83k197wwcwkw8s
title: "flexdoc 0.4.1: drop cydifflib on origin/main and open PR"
kind: task
status: closed
priority: 1
version: 5
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies:
  - type: blocks
    target: is-01m2vh2ayn9vkmzkgbwmea9ngp
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
created_at: 2026-09-19T00:29:10.661Z
updated_at: 2026-09-19T01:05:29.310Z
closed_at: 2026-09-19T01:05:29.309Z
close_reason: "PR filed: https://github.com/jlevy/flexdoc/pull/25 (no tag until signoff)"
resolution: null
duplicate_of: null
---
Same one-file change on origin/main (v0.4.0 line) so non-kash flexdoc>=0.4.0 consumers are not stuck building cydifflib on 3.14. Parallel with the 0.3.1 PR.
