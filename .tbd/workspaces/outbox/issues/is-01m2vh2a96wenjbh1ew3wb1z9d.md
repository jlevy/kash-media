---
type: is
id: is-01m2vh2a96wenjbh1ew3wb1z9d
title: "flexdoc: tag and publish v0.3.1"
kind: task
status: closed
priority: 1
version: 11
spec_path: docs/project/specs/active/plan-2026-09-18-cydifflib-python314-install.md
labels: []
dependencies: []
parent_id: is-01m2vh29mhfpyb261xnxvkd6tm
created_at: 2026-09-19T00:29:10.309Z
updated_at: 2026-09-19T01:17:58.000Z
closed_at: 2026-09-19T01:17:57.999Z
close_reason: "Cancelled: one flexdoc release from main only. Do not tag v0.3.1. PR https://github.com/jlevy/flexdoc/pull/24 is superseded for release (leave open; comment only). chopdiff must publish before kash can resolve the new flexdoc."
resolution: canceled
duplicate_of: null
---
After the 0.3.1 PR is merged and CI is green: make build, confirm wheel Requires-Dist has no cydifflib, tag v0.3.1 via GitHub Release/publish.yml. This is the version the kash graph can resolve (chopdiff pins flexdoc<0.4.0).

## Notes

Blocked on user signoff. Flexdoc 0.3.1 PR: https://github.com/jlevy/flexdoc/pull/24
