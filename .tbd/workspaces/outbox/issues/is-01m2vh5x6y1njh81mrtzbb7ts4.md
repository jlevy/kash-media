---
type: is
id: is-01m2vh5x6y1njh81mrtzbb7ts4
title: "chopdiff: tag and publish 0.4.1 or 0.5.0"
kind: task
status: open
priority: 1
version: 5
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies:
  - type: blocks
    target: is-01m2vh2b9bt6p8ygrnhx1eata4
  - type: blocks
    target: is-01m2vh2bkwetfmrv7bj191nye4
  - type: blocks
    target: is-01m2vh2byn9cnvxf5z7n5jgpb6
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
created_at: 2026-09-19T00:31:07.997Z
updated_at: 2026-09-19T01:07:46.867Z
---
After the chopdiff PR merges and CI is green: tag v0.4.1 if TextUnit.words tests pass unchanged, else v0.5.0. publish.yml. This opens flexdoc 0.4.x for kash. Do not skip: kash PRs that require flexdoc>=0.4.1 will conflict with published chopdiff 0.4.0.

## Notes

Blocked on user signoff and flexdoc v0.4.1 on PyPI. Chopdiff PR is https://github.com/jlevy/chopdiff/pull/33. Tests passed; tag v0.4.1 not v0.5.0.
