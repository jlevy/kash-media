---
type: is
id: is-01m2vh2a96wenjbh1ew3wb1z9d
title: "flexdoc: tag and publish v0.3.1"
kind: task
status: open
priority: 1
version: 6
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies:
  - type: blocks
    target: is-01m2vh2b9bt6p8ygrnhx1eata4
  - type: blocks
    target: is-01m2vh2bkwetfmrv7bj191nye4
  - type: blocks
    target: is-01m2vh2byn9cnvxf5z7n5jgpb6
  - type: blocks
    target: is-01m2vh2c9cpdkj0tq08esp76bw
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
created_at: 2026-09-19T00:29:10.309Z
updated_at: 2026-09-19T01:07:47.424Z
---
After the 0.3.1 PR is merged and CI is green: make build, confirm wheel Requires-Dist has no cydifflib, tag v0.3.1 via GitHub Release/publish.yml. This is the version the kash graph can resolve (chopdiff pins flexdoc<0.4.0).

## Notes

Blocked on user signoff. Flexdoc 0.3.1 PR: https://github.com/jlevy/flexdoc/pull/24
