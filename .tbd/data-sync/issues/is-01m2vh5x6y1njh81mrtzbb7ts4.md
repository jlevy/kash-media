---
type: is
id: is-01m2vh5x6y1njh81mrtzbb7ts4
title: "chopdiff: tag and publish 0.4.1 (or 0.5.0 if surface changes)"
kind: task
status: closed
priority: 1
version: 11
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
updated_at: 2026-09-19T02:28:24.639Z
closed_at: 2026-09-19T02:28:24.637Z
close_reason: chopdiff v0.4.1 on PyPI (728e46b). PR 33 retargeted to flexdoc[diff] from registry; PR 34 locked pip 26.2.1 so publish audit passed. https://github.com/jlevy/chopdiff/pull/33 https://pypi.org/project/chopdiff/0.4.1/
resolution: null
duplicate_of: null
---
Tag chopdiff v0.4.1 if TextUnit.words tests stay unchanged against keep-cydifflib flexdoc, else v0.5.0. Blocked on the one flexdoc tag from main (kashm-roqq). Retarget PR 33 off the hard-drop flexdoc branch. Do not tag until user signoff.

## Notes

Retargeting PR 33: flexdoc[diff]>=0.4.1,<0.5 from PyPI; keep cydifflib; tag v0.4.1 after green required CI.
