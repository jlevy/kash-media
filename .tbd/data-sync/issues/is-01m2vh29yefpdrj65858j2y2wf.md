---
type: is
id: is-01m2vh29yefpdrj65858j2y2wf
title: "flexdoc 0.3.1: drop cydifflib on the v0.3.0 line and open PR"
kind: task
status: closed
priority: 1
version: 4
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies:
  - type: blocks
    target: is-01m2vh2a96wenjbh1ew3wb1z9d
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
created_at: 2026-09-19T00:29:09.965Z
updated_at: 2026-09-19T01:05:28.957Z
closed_at: 2026-09-19T01:05:28.956Z
close_reason: "PR filed: https://github.com/jlevy/flexdoc/pull/24 (no tag until signoff)"
resolution: null
duplicate_of: null
---
Branch from v0.3.0 (not origin/main). Replace import cydifflib as difflib with stdlib difflib; remove the pyproject dep; relock; lint/test token_diffs and goldens; open PR.
