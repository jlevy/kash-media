---
type: is
id: is-01m2vkv6bqp05yh1zdgya9pkbr
title: Decide flexdoc cydifflib approach (keep, drop, or optional-fallback)
kind: task
status: closed
priority: 1
version: 4
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies:
  - type: blocks
    target: is-01m2vh2ayn9vkmzkgbwmea9ngp
  - type: blocks
    target: is-01m2vkzcaew41knm2b8f82w945
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
created_at: 2026-09-19T01:17:42.646Z
updated_at: 2026-09-19T01:19:59.821Z
closed_at: 2026-09-19T01:19:59.670Z
close_reason: "Keep cydifflib as a hard dependency. Written reason: chopdiff 0e6f81d / README. Bench on CPython 3.13.7 arm64, cydifflib 1.2.0, production path: 8.4x at 59 tokens; 38.7x at 2048 (2.0 ms vs 77.8 ms); 32.5x at 10k; 35.2x at 20k; opcodes matched stdlib. Vendor/fallback only if GIL 3.14 install requires it. Do not drop."
resolution: null
duplicate_of: null
---
Parallel analysis (do not implement in the topology pass). Choose keep cydifflib, drop it for stdlib difflib, or optional-fallback. Exact flexdoc version is planned 0.4.1 and TBD if this changes the bump. Do not edit flexdoc source until this lands. Blocks the single flexdoc tag from main (kashm-roqq / PR 25).
