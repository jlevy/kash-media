---
type: is
id: is-01m2vh5x6y1njh81mrtzbb7ts4
title: "chopdiff: tag and publish 0.4.1 (or 0.5.0 if surface changes)"
kind: task
status: open
priority: 1
version: 8
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
created_at: 2026-09-19T00:31:07.997Z
updated_at: 2026-09-19T01:22:09.308Z
---
Tag chopdiff v0.4.1 if TextUnit.words tests stay unchanged against keep-cydifflib flexdoc, else v0.5.0. Blocked on the one flexdoc tag from main (kashm-roqq). Retarget PR 33 off the hard-drop flexdoc branch. Do not tag until user signoff.

## Notes

Blocked on user signoff and flexdoc v0.4.1 on PyPI. Chopdiff PR is https://github.com/jlevy/chopdiff/pull/33. Tests passed; tag v0.4.1 not v0.5.0.
