---
type: is
id: is-01m2vh29mhfpyb261xnxvkd6tm
title: Unblock kash installs blocked by cydifflib on Python 3.14
kind: epic
status: closed
priority: 1
version: 29
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
  - is-01m2vszxvbbvb8c6xqec8ycqgb
created_at: 2026-09-19T00:29:09.647Z
updated_at: 2026-09-19T04:43:11.647Z
closed_at: 2026-09-19T04:41:45.174Z
close_reason: "Train complete: flexdoc 0.4.1, chopdiff 0.4.1, kash-shell 0.4.12, kash-docs 0.2.8, kash-media 0.4.11 on PyPI. GIL 3.13/3.14 resolve works; 3.14t unsupported. cydifflib kept."
resolution: null
duplicate_of: null
---
One flexdoc release from main that keeps PyPI cydifflib>=1.2.0, then one chopdiff pin, then kash-shell / kash-docs / kash-media. GIL 3.14 already builds published cydifflib; a CyDifflib fork is optional and not on this train. 0.3.1 is cancelled. Do not drop cydifflib. Do not merge flexdoc 24/25.

## Notes

kash-shell 0.4.12 and kash-docs 0.2.8 are on PyPI (>=3.11,<3.15; flexdoc[diff]>=0.4.1; chopdiff>=0.4.1). cydifflib stays via flexdoc[diff]. kash-media 0.4.10 still locks kash-docs==0.2.7 and kash-shell==0.4.10 — sibling must relock to 0.2.8 / 0.4.12. GIL 3.14 only; not 3.14t.
