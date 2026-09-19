---
title: "Plan Spec: Unblock kash installs blocked by cydifflib on Python 3.14"
description: >-
  Coordinated flexdoc releases and consumer PRs so uv tool install / uvx of
  kash-shell, kash-docs, and kash-media no longer fail building cydifflib on
  Python 3.14.
---
# Feature: Unblock kash Installs Blocked by cydifflib on Python 3.14

**Date:** 2026-09-18 (last updated 2026-09-18)

**Author:** Joshua Levy

**Status:** Draft

## Overview

`uv tool install kash-media` and `uvx kash-shell@latest` fail on machines where
uv’s default interpreter is CPython 3.14 (including the freethreaded 3.14t
build).
The resolver pulls `flexdoc` 0.3.0, which depends on `cydifflib` 1.2.0.
That package has wheels only through 3.13; the sdist’s vendored Cython does not
compile on 3.14.

The fix is to drop `cydifflib` from flexdoc (stdlib `difflib` is a drop-in for
the one call site) and ship a **0.3.1** release that existing kash packages can
actually resolve.
Consumer PRs then raise the lower bound, relock, and align Python-version
claims.
jlevy first-party packages are exempt from the 14-day cool-off, so consumers
can depend on `flexdoc==0.3.1` the same day it hits PyPI.

## Goals

- Make `uv tool install kash-media` and `uvx kash-shell@latest` succeed from a
  directory with no `.python-version` pin (uv’s default latest Python, today
  3.14 / 3.14t)
- Keep the published kash resolver on a flexdoc version it is allowed to pick
  (`0.3.x`, because chopdiff pins `flexdoc>=0.3.0,<0.4.0`)
- Also ship the same cydifflib removal on the flexdoc `0.4.x` line, so
  non-kash consumers of `flexdoc>=0.4.0` are not left on a broken 3.14 build
- Relock and raise lower bounds in kash-shell, kash-docs, and kash-media
- Record the uv interpreter-selection trap in install docs (`--python 3.13`
  remains the safe pin while kash-media’s `requires-python` is `<3.14`)

## Non-Goals

- Adding Python 3.14 as a supported runtime for kash-media or kash-docs.
  Both already declare `requires-python = "<3.14"`.
  This plan unblocks *accidental* 3.14 resolution; it does not certify 3.14.
- Relaxing chopdiff’s `flexdoc<0.4.0` pin or moving kash onto flexdoc 0.4.x.
  That is a separate, API-breaking adoption (logical word metrics / TextRef).
- Changing uv itself.
- Touching third-party flexdoc pins outside this train (ojoshe, practical-prose,
  and similar can pick up 0.3.1 or 0.4.1 on their own cadence).
- Replacing cydifflib with another native accelerator.

## Background

### Failure

From a non-project directory (for example tbd), `uv python find` selects the
newest managed interpreter.
On this machine that is `cpython-3.14.7+freethreaded`.
`uv tool install` / `uvx` keep that interpreter and do **not** re-select from
the root package’s `requires-python`.
kash-media 0.4.9 already declares `>=3.13,<3.14`; the install still ran on
3.14t.

`cydifflib` 1.2.0 (April 2025) ships `cp313` wheels and an sdist.
There is no `cp314` / `cp314t` wheel.
The sdist build fails with unknown `__pyx_vectorcallfunc` and a
`PyTuple_GetSlice` type error.

`--python 3.13` installs cleanly today (kash-media 0.4.9, kash-shell 0.4.11,
flexdoc 0.3.0, cydifflib wheel).

### Published dependency graph

```
cydifflib 1.2.0
  ^
flexdoc 0.3.0          flexdoc 0.4.0
  ^                      ^
  |                      (no kash package can select this)
chopdiff 0.4.0
  requires flexdoc>=0.3.0,<0.4.0
  ^
kash-shell 0.4.11
  flexdoc>=0.3.0
  chopdiff>=0.4.0
  requires-python >=3.11,<4.0   (claims 3.14)
  ^
kash-docs 0.2.7
  flexdoc>=0.3.0
  chopdiff>=0.4.0
  kash-shell>=0.4.9,<0.5
  requires-python >=3.11,<3.14
  ^
kash-media 0.4.9
  flexdoc>=0.3.0
  chopdiff>=0.4.0
  kash-shell>=0.4.10,<0.5
  kash-docs>=0.2.7,<0.3
  requires-python >=3.13,<3.14
  classifier incorrectly lists 3.14
```

chopdiff’s upper bound is why the install log said `flexdoc 0.3.0`, not 0.4.0.
Publishing only `flexdoc 0.4.1` would **not** fix kash installs.
The release that the current kash resolver can take is **flexdoc 0.3.1**.

flexdoc uses cydifflib in one place:
`src/flexdoc/docs/token_diffs.py` does `import cydifflib as difflib` and calls
`difflib.SequenceMatcher`.
stdlib `difflib.SequenceMatcher` is the same API.

### First-party cool-off

jlevy packages are exempt from the rolling `exclude-newer` window
(`flexdoc`, `kash-shell`, `kash-docs`, `kash-media`, `chopdiff`, and the rest
of the first-party list in each `pyproject.toml` and in
`~/.config/uv/uv.toml`).
Consumer PRs may require `flexdoc>=0.3.1` immediately after the tag publishes.
Do not wait 14 days.

### Checkout notes

| Repo | GitHub | Local note |
| --- | --- | --- |
| flexdoc | [jlevy/flexdoc](https://github.com/jlevy/flexdoc) | `origin/main` is the 0.4.0 line (`v0.4.0`). 0.3.1 must branch from `v0.3.0`, not from current main. |
| kash-shell | [jlevy/kash](https://github.com/jlevy/kash) | One commit behind `origin/main`; latest tag `v0.4.11`. |
| kash-docs | [jlevy/kash-docs](https://github.com/jlevy/kash-docs) | Local main is stale (last local tag `v0.1.20`, kash-shell pinned to 0.3.37). Work from GitHub `main` / published 0.2.7. |
| kash-media | [jlevy/kash-media](https://github.com/jlevy/kash-media) | This repo. Lock has flexdoc 0.3.0 and kash-shell 0.4.10. |

chopdiff stays out of this train.
It already accepts any `0.3.x` flexdoc.

## Design

### Approach

Two flexdoc patch releases, same code change (delete the cydifflib dependency;
`import difflib`):

1. **`v0.3.1` from `v0.3.0`** — this is the release kash will resolve.
2. **`v0.4.1` from `origin/main` (`v0.4.0`)** — same removal so the 0.4 line
   is installable on 3.14 for everyone else.

Then three consumer PRs that do not need to wait on each other once 0.3.1 is
on PyPI:

- kash-shell: `flexdoc>=0.3.1`, relock
- kash-docs: `flexdoc>=0.3.1`, relock (from up-to-date `main`)
- kash-media: `flexdoc>=0.3.1`, relock; drop the false 3.14 classifier; mention
  `--python 3.13` in the README install snippet

Consumer *releases* are optional for the first successful `uv tool install`.
Published kash-media 0.4.9 already says `flexdoc>=0.3.0`, so 0.3.1 is eligible
the moment it exists.
Lower-bound bumps are defense against anyone who still has 0.3.0 cached or
pinned, and they make the lockfiles match production.

### Backward compatibility

- **Internal code:** DO NOT MAINTAIN.
  `cydifflib` is an implementation detail of `token_diffs.py`.
- **Library APIs:** DO NOT MAINTAIN for the import path.
  No public flexdoc API exposes `cydifflib`.
  Opcode results from `SequenceMatcher` stay the same for this call pattern
  (`autojunk=False`).
- **Server APIs / plugins / file formats / persisted state / schemas:** N/A.

Named consumer of the *flexdoc version range*: published chopdiff 0.4.0, which
cannot take 0.4.x.
That is why 0.3.1 exists.
Do not add a shim to keep cydifflib optional.

### API Changes

None.
`flexdoc.docs.token_diffs.diff_wordtoks` still returns the same `TokenDiff`.

### Components

| Package | Change | New tag if we publish |
| --- | --- | --- |
| flexdoc | Drop `cydifflib`; stdlib `difflib` | `v0.3.1` and `v0.4.1` |
| kash-shell | `flexdoc>=0.3.1`; relock | optional `v0.4.12` |
| kash-docs | `flexdoc>=0.3.1`; relock | optional patch on 0.2.x |
| kash-media | `flexdoc>=0.3.1`; relock; classifier + README | optional `v0.4.10` |

## Implementation Plan

Use two phases.
Phase 1 is the only gate for the user-visible install.
Phase 2 is lockfiles, docs, and optional consumer tags.

### Phase 1: Flexdoc patches and releases

- [ ] From `v0.3.0`, replace `import cydifflib as difflib` with `import difflib`
      and remove `cydifflib>=1.2.0` from `pyproject.toml`
- [ ] Relock flexdoc 0.3.1; run lint and the token-diff / golden tests
- [ ] PR against a `release/0.3.1` (or equivalent) branch; merge
- [ ] Tag `v0.3.1` per [publishing.md](../../../docs/publishing.md) (GitHub
      Release → `publish.yml` → PyPI)
- [ ] Repeat the same one-file change on `origin/main` for `v0.4.1`
- [ ] Confirm PyPI metadata for 0.3.1 and 0.4.1 has no `cydifflib`

### Phase 2: Consumer PRs (after 0.3.1 is on PyPI)

These three PRs are independent of each other.

**kash-shell** ([jlevy/kash](https://github.com/jlevy/kash))

- [ ] Update `main`
- [ ] `flexdoc>=0.3.1` (keep the existing unscoped upper bound)
- [ ] `uv lock` / `make upgrade` only as needed for flexdoc; commit `uv.lock`
- [ ] PR; optional tag `v0.4.12` so `uvx kash-shell@latest` advertises the
      bound (not required for 3.14 install once 0.3.1 exists)

**kash-docs** ([jlevy/kash-docs](https://github.com/jlevy/kash-docs))

Needed for lock and lower-bound hygiene, not for the first PyPI install fix.
Published 0.2.7 already depends on `flexdoc>=0.3.0`.

- [ ] Do not use the stale local checkout as the base; start from GitHub `main`
      at 0.2.7
- [ ] `flexdoc>=0.3.1`; relock
- [ ] PR; optional 0.2.8 tag

**kash-media** (this repo)

- [ ] `flexdoc>=0.3.1`; relock (kash-shell may stay `>=0.4.10` or move to
      `>=0.4.12` if we tag it)
- [ ] Remove the `Programming Language :: Python :: 3.14` classifier
- [ ] README install snippet: `uv tool install --python 3.13 kash-media ...`
      kash-media remains `requires-python = ">=3.13,<3.14"`
- [ ] PR; optional `v0.4.10` tag

**Verify** (from `/tmp` or any dir without a Python pin)

- [ ] `uv tool install --force kash-media` with no `--python` (3.14 default)
      succeeds after 0.3.1 and does not build cydifflib
- [ ] `uvx kash-shell@latest` with no `--python` succeeds
- [ ] `uv tool install --python 3.13 --force kash-media` still succeeds
- [ ] kash-docs: `uvx kash-docs@latest` only if we care about that entry point;
      same flexdoc path

## Testing Strategy

**flexdoc (each line)**

- Existing `token_diffs` tests and golden docs that exercise
  `diff_wordtoks` / alignment
- `uv tree` / the built wheel metadata must not list `cydifflib`
- No new performance test.
  stdlib `SequenceMatcher` is acceptable for this path.

**consumers**

- `make lint` and `make test` after the lock change
- Resolver check: `uv tree -p flexdoc -p cydifflib` shows flexdoc >=0.3.1 and
  no cydifflib

**release smoke (required, packaged artifact)**

After each flexdoc tag, in a clean directory with no pin:

```shell
uv tool uninstall kash-media || true
uv tool install --force kash-media
uvx kash-shell@latest --help
```

That is the user-visible contract.
Do not treat `make test` in a 3.13 project venv as evidence the tool install
works.

## Rollout Plan

Release identity is the git tag (`vX.Y.Z`).
Each package uses the simple-modern-uv `publish.yml` trusted-publisher path
documented in that repo’s `docs/publishing.md`.

| Order | Tag | Why this order |
| --- | --- | --- |
| 1 | flexdoc `v0.3.1` | Only version the current kash graph can select |
| 2 | flexdoc `v0.4.1` | Same fix on the line already on PyPI as 0.4.0; can proceed in parallel with 0.3.1 once the 0.3.1 PR is up |
| 3 | Consumer PRs | Same day as 0.3.1 on PyPI (no cool-off) |
| 4 | Optional consumer tags | Only if we want published lower bounds; not on the critical path |

Do not tag a consumer before its PR is merged and CI is green on `main`.
Do not bump kash-media’s flexdoc lower bound in a published release until 0.3.1
exists, or the consumer release cannot resolve.

Rehearse flexdoc locally with `make build` and inspect the wheel
`Requires-Dist` before tagging.

## Open Questions

- **Optional consumer tags in this pass, or PRs only?**
  PRs plus the flexdoc 0.3.1 tag are enough for `uv tool install kash-media`
  to succeed.
  Recommend tagging flexdoc only, unless we want the lower bounds on PyPI
  immediately.
- **Relax chopdiff in a follow-up** so kash can move to flexdoc 0.4.x later?
  Out of scope here.
  Track separately if we want TextRef / logical-word metrics in kash.

## References

- flexdoc call site: `src/flexdoc/docs/token_diffs.py`
- Published pins: PyPI `kash-media` 0.4.9, `kash-shell` 0.4.11,
  `kash-docs` 0.2.7, `chopdiff` 0.4.0, `flexdoc` 0.3.0 and 0.4.0
- Install docs: [README.md](../../../README.md),
  [installation.md](../../installation.md),
  [publishing.md](../../publishing.md)
- uv interpreter selection: `uv tool install --python` / `UV_PYTHON`; default
  is latest managed CPython when no project pin exists

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
