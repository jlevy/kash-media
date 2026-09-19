---
type: is
id: is-01m2vh5wwc3bfdbf5h5mretjyq
title: "chopdiff: adopt flexdoc>=0.4.1,<0.5, fix cool-off exception, open PR"
kind: task
status: closed
priority: 1
version: 4
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies:
  - type: blocks
    target: is-01m2vh5x6y1njh81mrtzbb7ts4
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
created_at: 2026-09-19T00:31:07.659Z
updated_at: 2026-09-19T01:07:46.553Z
closed_at: 2026-09-19T01:07:46.550Z
close_reason: "PR filed: https://github.com/jlevy/chopdiff/pull/33 (do not tag until flexdoc 0.4.1 is on PyPI and user signs off). Tests passed unchanged; plan chopdiff v0.4.1 not v0.5.0."
resolution: null
duplicate_of: null
---
Repo ../chopdiff (jlevy/chopdiff). Replace flexdoc>=0.3.0,<0.4.0 with >=0.4.1,<0.5. Change exclude-newer-package flexdoc from 2026-07-12 to 2099-12-31. Relock. Run lint/test including TextUnit.words chunking. If word sizes change, use raw_words (stay 0.4.1) or accept and plan 0.5.0. Can start against a path dep on the flexdoc 0.4.1 branch; lock/tag wait for PyPI.
