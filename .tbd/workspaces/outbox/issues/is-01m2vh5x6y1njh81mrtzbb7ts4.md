---
type: is
id: is-01m2vh5x6y1njh81mrtzbb7ts4
title: "chopdiff: tag and publish 0.4.1 (or 0.5.0 if surface changes)"
kind: task
status: open
priority: 1
version: 9
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
updated_at: 2026-09-19T01:42:48.474Z
---
Tag chopdiff v0.4.1 if TextUnit.words tests stay unchanged against keep-cydifflib flexdoc, else v0.5.0. Blocked on the one flexdoc tag from main (kashm-roqq). Retarget PR 33 off the hard-drop flexdoc branch. Do not tag until user signoff.

## Notes

flexdoc v0.4.1 is on PyPI. Depend on flexdoc[diff]>=0.4.1,<0.5 (or flexdoc + cydifflib>=1.2.0). Retarget #33 off the hard-drop branch. Relock from PyPI. Do not tag until user signoff.
