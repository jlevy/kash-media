---
title: "Plan Spec: Unblock kash installs blocked by cydifflib on Python 3.14"
description: >-
  Coordinated flexdoc, chopdiff, kash-shell, kash-docs, and kash-media
  releases so uv tool install / uvx no longer fail building cydifflib on
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

flexdoc uses cydifflib in one place (`import cydifflib as difflib` for
`SequenceMatcher`).
stdlib `difflib` is a drop-in there.

Two releases make that fix selectable:

1. **flexdoc 0.3.1** from `v0.3.0` — published chopdiff 0.4.0 already allows
   any `0.3.x`, so this unblocks today’s kash graph the day it hits PyPI.
2. **flexdoc 0.4.1** on `main`, then **chopdiff** relaxes `flexdoc<0.4.0`,
   validates 0.4.x (especially `TextUnit.words`), and publishes.
   kash-shell, kash-docs, and kash-media then lock both new lower bounds.

jlevy first-party packages are exempt from the 14-day cool-off.
Consumers may depend on a tag the same day it is on PyPI.
chopdiff’s *dated* flexdoc exception (`2026-07-12`) is not that exemption and
must be updated, or 0.4.1 will not resolve in that repo.

## Goals

- Make `uv tool install kash-media` and `uvx kash-shell@latest` succeed from a
  directory with no `.python-version` pin (uv’s default latest Python, today
  3.14 / 3.14t)
- Ship flexdoc 0.3.1 so the *current* published graph (chopdiff 0.4.0 +
  kash-media 0.4.9) can drop cydifflib without waiting on chopdiff
- Move the first-party train onto flexdoc 0.4.1 by changing chopdiff, then
  relocking kash-shell, kash-docs, and kash-media
- Record the uv interpreter-selection trap in kash-media install docs
  (`--python 3.13` remains the safe pin while kash-media’s `requires-python`
  is `<3.14`)

## Non-Goals

- Adding Python 3.14 as a supported runtime for kash-media or kash-docs.
  Both already declare `requires-python = "<3.14"`.
  This plan unblocks *accidental* 3.14 resolution; it does not certify 3.14.
- Changing uv itself.
- Touching third-party flexdoc pins outside this train (ojoshe, practical-prose,
  and similar).
- Replacing cydifflib with another native accelerator.
- Reworking chopdiff windowing or chunk APIs except as required to accept
  flexdoc 0.4.x `TextUnit.words` semantics.

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
  |                      blocked for kash by chopdiff
chopdiff 0.4.0
  requires flexdoc>=0.3.0,<0.4.0
  lock exception: flexdoc cutoff 2026-07-12 (before flexdoc 0.4.0)
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
Publishing only `flexdoc 0.4.1` still does not fix kash until a new chopdiff
release allows `0.4.x`.

flexdoc 0.4.0 changed `TextUnit.words` from raw whitespace counts to logical
word metrics.
chopdiff windowing uses `wordtoks` / `paragraphs` / `bytes`.
`TextUnit.words` appears in div-chunk tests (`chunk_text_as_divs`).
That is the compatibility surface to re-run before relaxing `<0.4.0`.
If those tests fail only because sizes changed, prefer `TextUnit.raw_words`
at the call sites that want the old measure, or accept the new sizes and
bump chopdiff’s minor (pre-1.0 break).

### First-party cool-off

kash-shell, kash-docs, and kash-media list flexdoc and chopdiff at
`2099-12-31`, so a same-day tag resolves.

chopdiff itself still has:

```toml
[tool.uv.exclude-newer-package]
flexdoc = "2026-07-12T00:00:00Z"
```

flexdoc 0.4.0 was published 2026-07-20.
That cutoff must become a first-party exemption (`2099-12-31`) before
chopdiff can lock 0.4.1.

### Checkout notes

| Repo | GitHub | Local note |
| --- | --- | --- |
| flexdoc | [jlevy/flexdoc](https://github.com/jlevy/flexdoc) | `origin/main` is the 0.4.0 line (`v0.4.0`). 0.3.1 must branch from `v0.3.0`. |
| chopdiff | [jlevy/chopdiff](https://github.com/jlevy/chopdiff) | `../chopdiff`. `main` matches origin; published 0.4.0. Pin `flexdoc>=0.3.0,<0.4.0`. |
| kash-shell | [jlevy/kash](https://github.com/jlevy/kash) | One commit behind `origin/main`; latest tag `v0.4.11`. |
| kash-docs | [jlevy/kash-docs](https://github.com/jlevy/kash-docs) | Local main is stale (last local tag `v0.1.20`). Work from GitHub `main` / published 0.2.7. |
| kash-media | [jlevy/kash-media](https://github.com/jlevy/kash-media) | This repo. Lock has flexdoc 0.3.0 and kash-shell 0.4.10. |

## Design

### Approach

**Immediate unblock (no chopdiff release required):** tag flexdoc `v0.3.1`.
Published chopdiff 0.4.0 already accepts it.
Published kash-media 0.4.9 already says `flexdoc>=0.3.0`.

**Coordinated train (chopdiff in the set):**

1. Same cydifflib drop on flexdoc `main` → `v0.4.1`.
2. chopdiff: point at `flexdoc>=0.4.1,<0.5`, fix the dated cool-off exception,
   run the suite (div chunking with `TextUnit.words`, sliding windows,
   token diffs), PR, tag.
3. kash-shell, kash-docs, kash-media: `flexdoc>=0.4.1` and
   `chopdiff>=<new chopdiff tag>`; relock; kash-media classifier + README.

Work on the chopdiff PR can start against a path or git dep on the flexdoc
0.4.1 branch; the lock and tag wait for PyPI 0.4.1.

### Backward compatibility

- **Internal code (flexdoc cydifflib):** DO NOT MAINTAIN.
- **Library APIs (flexdoc):** DO NOT MAINTAIN for the import path.
  No public flexdoc API exposes `cydifflib`.
- **chopdiff ↔ flexdoc 0.4.x:** VERSION + FAIL FAST on the pin
  (`>=0.4.1,<0.5`).
  If `TextUnit.words` chunk sizes change in a user-visible way, that is a
  pre-1.0 minor bump of chopdiff (0.5.0), not a silent patch.
  If tests pass unchanged, chopdiff 0.4.1 is enough.
- **Server APIs / plugins / file formats / persisted state / schemas:** N/A.

Do not keep an optional cydifflib extra.

### API Changes

flexdoc: none at the `token_diffs` surface.

chopdiff: none unless 0.4.x forces `TextUnit.words` call sites to
`TextUnit.raw_words` or new expected sizes.

### Components

| Package | Change | New tag |
| --- | --- | --- |
| flexdoc | Drop `cydifflib`; stdlib `difflib` | `v0.3.1` and `v0.4.1` |
| chopdiff | `flexdoc>=0.4.1,<0.5`; first-party cool-off; relock; tests | `v0.4.1` or `v0.5.0` |
| kash-shell | `flexdoc>=0.4.1`; `chopdiff>=` new tag; relock | optional `v0.4.12` |
| kash-docs | same pins; relock from GitHub `main` | optional 0.2.8 |
| kash-media | same pins; relock; classifier + README | optional `v0.4.10` |

## Implementation Plan

Three phases.
Phase 1 unblocks the already-published kash packages.
Phase 2 is chopdiff.
Phase 3 is the three kash PRs (one each; do not land 0.3.1-only consumer PRs
and then redo them).

### Phase 1: Flexdoc patches and releases

- [ ] From `v0.3.0`, replace `import cydifflib as difflib` with `import difflib`
      and remove `cydifflib>=1.2.0` from `pyproject.toml`
- [ ] Relock; run lint and the token-diff / golden tests
- [ ] PR on a `release/0.3.1` (or equivalent) branch; merge
- [ ] Tag `v0.3.1` (GitHub Release → `publish.yml` → PyPI)
- [ ] Repeat the same change on `origin/main` for `v0.4.1`
- [ ] Confirm PyPI metadata for 0.3.1 and 0.4.1 has no `cydifflib`
- [ ] From `/tmp`, `uv tool install --force kash-media` with no `--python`
      (proves 0.3.1 unblocks the current graph)

### Phase 2: Chopdiff adopts flexdoc 0.4.1

Repo: [jlevy/chopdiff](https://github.com/jlevy/chopdiff) (`../chopdiff`).

- [ ] Set `[tool.uv.exclude-newer-package] flexdoc = "2099-12-31T00:00:00Z"`
      (or delete the dated 2026-07-12 override if the global first-party
      exemption already covers it)
- [ ] Change the dep to `flexdoc>=0.4.1,<0.5`
- [ ] `uv lock --upgrade-package flexdoc`
- [ ] Run `make lint` and `make test`, including
      `tests/divs/test_div_elements.py` and transform / `token_diffs` tests
- [ ] If `TextUnit.words` sizes change: either switch those call sites to
      `TextUnit.raw_words` (keep 0.4.1) or accept the new sizes and tag 0.5.0
- [ ] PR; tag after merge and green CI

### Phase 3: kash-shell, kash-docs, kash-media

These three PRs wait on flexdoc 0.4.1 **and** the new chopdiff tag.
They are independent of each other.

**kash-shell** ([jlevy/kash](https://github.com/jlevy/kash))

- [ ] Update `main`
- [ ] `flexdoc>=0.4.1` and `chopdiff>=` the new chopdiff tag
- [ ] Relock; PR; optional `v0.4.12`

**kash-docs** ([jlevy/kash-docs](https://github.com/jlevy/kash-docs))

Needed for lock and lower-bound hygiene on the 0.2.7 line, not for the first
install fix after flexdoc 0.3.1.

- [ ] Start from GitHub `main` at 0.2.7, not the stale local tree
- [ ] Same flexdoc and chopdiff pins; relock; PR; optional 0.2.8

**kash-media** (this repo)

- [ ] Same flexdoc and chopdiff pins; relock
- [ ] Remove the `Programming Language :: Python :: 3.14` classifier
- [ ] README: `uv tool install --python 3.13 kash-media ...`
      Keep `requires-python = ">=3.13,<3.14"`
- [ ] PR; optional `v0.4.10`

**Verify again** from `/tmp` after Phase 3 tags (or after PyPI has 0.4.1 +
new chopdiff, even before kash consumer tags):

- [ ] `uv tool install --force kash-media` (no `--python`) does not build
      cydifflib and resolves flexdoc >=0.3.1 (and 0.4.1 once chopdiff allows it)
- [ ] `uvx kash-shell@latest` with no `--python` succeeds
- [ ] `--python 3.13` still succeeds

## Testing Strategy

**flexdoc (each line)**

- `token_diffs` tests and golden docs
- Built wheel `Requires-Dist` must not list `cydifflib`

**chopdiff**

- Existing div / transform / token-diff tests against flexdoc 0.4.1
- `uv tree -p flexdoc -p cydifflib` shows flexdoc 0.4.1 and no cydifflib
- Decide 0.4.1 vs 0.5.0 from whether `TextUnit.words` results change

**kash consumers**

- `make lint` and `make test` after the lock change
- Resolver check: flexdoc >=0.4.1, new chopdiff, no cydifflib

**release smoke (required, packaged artifact)**

After flexdoc 0.3.1, and again after chopdiff + flexdoc 0.4.1:

```shell
uv tool uninstall kash-media || true
uv tool install --force kash-media
uvx kash-shell@latest --help
```

Run from a directory with no Python pin.
Do not treat `make test` in a 3.13 project venv as evidence the tool install
works.

## Rollout Plan

Release identity is the git tag (`vX.Y.Z`).
Each package uses that repo’s `docs/publishing.md` (`publish.yml` trusted
publisher).

| Order | Tag | Why this order |
| --- | --- | --- |
| 1 | flexdoc `v0.3.1` | Unblocks published kash-media / kash-shell / kash-docs immediately |
| 2 | flexdoc `v0.4.1` | Same fix on the 0.4 line; chopdiff’s target |
| 3 | chopdiff `v0.4.1` or `v0.5.0` | Opens `flexdoc` 0.4.x for the kash graph |
| 4 | kash-shell / kash-docs / kash-media PRs | Same day as the chopdiff tag (no cool-off) |
| 5 | Optional kash tags | Published lower bounds; not required once 0.3.1 exists |

Do not tag a consumer before its PR is merged and CI is green on `main`.
Do not publish a kash release that requires `flexdoc>=0.4.1` before the new
chopdiff is on PyPI, or the resolver will conflict (`chopdiff 0.4.0` still
says `<0.4.0`).

Rehearse flexdoc and chopdiff with `make build` and inspect wheel
`Requires-Dist` before tagging.

## Open Questions

- **Optional kash consumer tags in this pass, or PRs only?**
  flexdoc 0.3.1 plus the later chopdiff tag are enough for installs.
  Recommend tagging flexdoc and chopdiff; kash tags only if we want the new
  lower bounds on PyPI immediately.
- **chopdiff 0.4.1 vs 0.5.0** is decided by the Phase 2 test run, not in
  advance.

## References

- flexdoc call site: `src/flexdoc/docs/token_diffs.py`
- chopdiff pin and dated exception: `pyproject.toml`
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
