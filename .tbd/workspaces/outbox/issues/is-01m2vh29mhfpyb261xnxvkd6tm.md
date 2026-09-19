---
type: is
id: is-01m2vh29mhfpyb261xnxvkd6tm
title: Unblock kash installs blocked by cydifflib on Python 3.14
kind: epic
status: in_progress
priority: 1
version: 25
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies: []
child_order_hints:
  - is-01m2vh29yefpdrj65858j2y2wf
  - is-01m2vh2a96wenjbh1ew3wb1z9d
  - is-01m2vh2am6gq83k197wwcwkw8s
  - is-01m2vkv6bqp05yh1zdgya9pkbr
  - is-01m2vkzcaew41knm2b8f82w945
  - is-01m2vm2z8dg289a32hwahqn3ha
  - is-01m2vh2ayn9vkmzkgbwmea9ngp
  - is-01m2vh5wwc3bfdbf5h5mretjyq
  - is-01m2vh5x6y1njh81mrtzbb7ts4
  - is-01m2vh2b9bt6p8ygrnhx1eata4
  - is-01m2vh2bkwetfmrv7bj191nye4
  - is-01m2vh2byn9cnvxf5z7n5jgpb6
  - is-01m2vh2c9cpdkj0tq08esp76bw
created_at: 2026-09-19T00:29:09.647Z
updated_at: 2026-09-19T01:42:48.791Z
---
One flexdoc release from main that keeps PyPI cydifflib>=1.2.0, then one chopdiff pin, then kash-shell / kash-docs / kash-media. GIL 3.14 already builds published cydifflib; a CyDifflib fork is optional and not on this train. 0.3.1 is cancelled. Do not drop cydifflib. Do not merge flexdoc 24/25.

## Notes

flexdoc v0.4.1 released (cbe2f5d, extra=diff). #24/#25 closed. Next: chopdiff pin of flexdoc[diff] (kashm-0po5). Do not tag chopdiff or kash yet.
