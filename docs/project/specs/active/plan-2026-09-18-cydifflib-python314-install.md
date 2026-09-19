---
title: "Plan Spec: Unblock kash installs blocked by cydifflib on Python 3.14"
description: >-
  Coordinated flexdoc, chopdiff, kash-shell, kash-docs, and kash-media
  releases so uv tool install / uvx no longer fail building cydifflib on
  GIL Python 3.14. Freethreaded 3.14t stays unsupported.
---
# Feature: Unblock kash Installs Blocked by cydifflib on Python 3.14

**Date:** 2026-09-18 (last updated 2026-09-18)

**Spike (2026-09-18):** GIL CPython 3.14.6 installs and imports the full
published kash-media graph, including frame capture (`cv2` + `skimage`).
Freethreaded 3.14t does not. See Background.

**Author:** Joshua Levy

**Status:** Active (decisions locked 2026-09-18)

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

jlevy first-party packages are exempt from the 14-day cool-off
(`2099-12-31` per-package exemptions).
Consumers may depend on a tag the same day it is on PyPI.
chopdiff’s *dated* flexdoc exception (`2026-07-12`) is not that exemption and
must be updated, or 0.4.1 will not resolve in that repo.

PRs land first.
Release tags wait for explicit user signoff.

## Decisions

Locked 2026-09-18:

- **GIL Python 3.14 is allowed for kash-media.** The vision stack works
  (opencv-python 5.0.0.93 `abi3`, scikit-image).
  Use `requires-python = ">=3.13,<3.15"` and keep the 3.14 classifier.
- **Python 3.14t (freethreaded) is unsupported.** Bare `uv tool install` /
  `uvx` still pick the latest managed Python, which can be 3.14t.
  Install docs must keep `--python 3.13` or `--python 3.14` (GIL).
  Do not claim 3.14t.
- **PRs now; tags only after user signoff.** Do not cut `v0.3.1`, `v0.4.1`,
  or later consumer tags until the user says so.
- **Lower-level libraries first.** File the flexdoc 0.3.1 and 0.4.1 PRs in
  parallel.
  Immediate unblock is flexdoc `v0.3.1` from tag `v0.3.0` (chopdiff 0.4.0
  already allows `0.3.x`).
- **Coordinated train:** flexdoc `v0.4.1` on `main` (same cydifflib drop);
  then chopdiff `flexdoc>=0.4.1,<0.5` and cool-off `2099-12-31`.
- **jlevy first-party repos have no cool-off restriction.** Use
  `2099-12-31` exemptions.

These close the earlier questions about whether 3.14 is a supported kash-media
runtime, whether a bare unpinned `uv tool install` must succeed, and whether
this pass should tag as well as open PRs.

## Goals

- Ship flexdoc 0.3.1 so the *current* published graph (chopdiff 0.4.0 +
  kash-media 0.4.9) can drop cydifflib without waiting on chopdiff
- Make `uv tool install --python 3.13 kash-media` and
  `uv tool install --python 3.14 kash-media` succeed without building
  cydifflib, and the same for `uvx --python 3.13|3.14 kash-shell@latest`
- Move the first-party train onto flexdoc 0.4.1 by changing chopdiff, then
  relocking kash-shell, kash-docs, and kash-media
- Allow GIL 3.14 on kash-media (`requires-python >=3.13,<3.15`)
- Record the uv interpreter-selection trap in kash-media install docs:
  `--python 3.13` or `--python 3.14` remains required because a bare
  `uv tool install` / `uvx` can still select 3.14t

## Non-Goals

- Supporting freethreaded Python 3.14t, or claiming that a bare
  `uv tool install` / `uvx` with no `--python` will succeed when uv picks
  3.14t
- Changing uv itself
- Touching third-party flexdoc pins outside this train (ojoshe, practical-prose,
  and similar)
- Replacing cydifflib with another native accelerator
- Reworking chopdiff windowing or chunk APIs except as required to accept
  flexdoc 0.4.x `TextUnit.words` semantics
- Cutting release tags in this pass

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

### Spike: GIL 3.14 vs Freethreaded 3.14t

Tested 2026-09-18 on macOS arm64.

**CPython 3.14.6 (GIL, uv-managed)** — works for kash-media as published.

- `uv pip install kash-media` completed (cydifflib 1.2.0 built a
  `_initialize.cpython-314-darwin.so`; opencv-python 5.0.0.93 used its
  `cp37-abi3` wheel).
- Frame path imported and ran a tiny SSIM: `cv2` 5.0.0, `skimage` 0.26.0,
  `structural_similarity` self-score 1.0, `VideoCapture` constructs,
  backends include `AVFOUNDATION` and `FFMPEG`.
- Also imported `kash.kits.media.video.video_frames` and
  `image_similarity`, plus `tokenizers`, `curl_cffi`, `yt_dlp`.
- The pyproject comment that onnxruntime lacks 3.14 wheels is stale.
  Neither onnxruntime nor torch is on the default media graph
  (`kash-docs` without `[full]`). A probe install of current wheels
  succeeded: onnxruntime 1.29.0, torch 2.14.0.

**CPython 3.14.7+freethreaded** — not a supported install target.

- This is what `uv python find` / `uv tool install` pick as “latest”
  from a directory with no pin (tbd, `/tmp`, `$HOME`).
- `cydifflib` sdist fails to compile (`__pyx_vectorcallfunc`,
  `PyTuple_GetSlice`).
- `opencv-python` 5.0.0.93 has no `cp314t` wheel; the `abi3` wheel is
  not used. uv starts a full OpenCV source build (still compiling after
  two minutes; not a viable `uv tool install` path).

**Implication for `requires-python`:** kash-media can allow GIL 3.14
(`>=3.13,<3.15` plus a 3.14 classifier) for project venvs and
`--python 3.14`. That does not make bare `uv tool install kash-media`
work, because uv still selects 3.14t. Dropping cydifflib is not enough
for 3.14t either; opencv would then be the next source-build wall.
Keep telling tool users `--python 3.13` or `--python 3.14` (not
`3.14t`). Do not claim 3.14t support.

### Published Dependency Graph

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
  classifier already lists 3.14
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

### First-Party Cool-Off

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

### Checkout Notes

| Repo | GitHub | Local note |
| --- | --- | --- |
| flexdoc | [jlevy/flexdoc](https://github.com/jlevy/flexdoc) | `origin/main` is the 0.4.0 line (`v0.4.0`). 0.3.1 must branch from `v0.3.0`. |
| chopdiff | [jlevy/chopdiff](https://github.com/jlevy/chopdiff) | `../chopdiff`. `main` matches origin; published 0.4.0. Pin `flexdoc>=0.3.0,<0.4.0`. |
| kash-shell | [jlevy/kash](https://github.com/jlevy/kash) | One commit behind `origin/main`; latest tag `v0.4.11`. |
| kash-docs | [jlevy/kash-docs](https://github.com/jlevy/kash-docs) | Local main is stale (last local tag `v0.1.20`). Work from GitHub `main` / published 0.2.7. |
| kash-media | [jlevy/kash-media](https://github.com/jlevy/kash-media) | This repo. Lock has flexdoc 0.3.0 and kash-shell 0.4.10. |

## Design

### Approach

**Immediate unblock (no chopdiff release required):** tag flexdoc `v0.3.1`
after user signoff.
Published chopdiff 0.4.0 already accepts it.
Published kash-media 0.4.9 already says `flexdoc>=0.3.0`.

**Coordinated train (chopdiff in the set):**

1. Same cydifflib drop on flexdoc `main` → PR, then `v0.4.1` after signoff.
2. chopdiff: point at `flexdoc>=0.4.1,<0.5`, set cool-off to `2099-12-31`,
   run the suite (div chunking with `TextUnit.words`, sliding windows,
   token diffs), PR.
   Tag only after flexdoc 0.4.1 is on PyPI and the user signs off.
3. kash-shell, kash-docs, kash-media: `flexdoc>=0.4.1` and
   `chopdiff>=<new chopdiff tag>`; relock; kash-media `requires-python` +
   README.

Work on the chopdiff PR can start against a path or git dep on the flexdoc
0.4.1 branch; the lock and tag wait for PyPI 0.4.1.

### Backward Compatibility

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
| kash-media | same pins; relock; GIL 3.14 + README `--python` | optional `v0.4.10` |

## Implementation Plan

Three phases.
Phase 1 unblocks the already-published kash packages.
Phase 2 is chopdiff.
Phase 3 is the three kash PRs (one each; do not land 0.3.1-only consumer PRs
and then redo them).
Tags are a later step, after user signoff.

### Phase 1: Flexdoc Patches

- [x] From `v0.3.0`, replace `import cydifflib as difflib` with `import difflib`
      and remove `cydifflib>=1.2.0` from `pyproject.toml`
- [x] Relock; run lint and the token-diff / golden tests
- [x] PR: [jlevy/flexdoc#24](https://github.com/jlevy/flexdoc/pull/24) (`release/0.3.x`)
- [x] Repeat the same change on `origin/main` for the 0.4.1 PR
      ([jlevy/flexdoc#25](https://github.com/jlevy/flexdoc/pull/25))
- [ ] After signoff: tag `v0.3.1` and `v0.4.1` (GitHub Release → `publish.yml` →
      PyPI)
- [ ] Confirm PyPI metadata for 0.3.1 and 0.4.1 has no `cydifflib`
- [ ] From `/tmp`, `uv tool install --force --python 3.13 kash-media` and
      `--python 3.14` (proves 0.3.1 unblocks the current graph on GIL Pythons)

### Phase 2: Chopdiff Adopts Flexdoc 0.4.1

Repo: [jlevy/chopdiff](https://github.com/jlevy/chopdiff) (`../chopdiff`).

- [x] Set `[tool.uv.exclude-newer-package] flexdoc = "2099-12-31T00:00:00Z"`
- [x] Change the dep to `flexdoc>=0.4.1,<0.5`
- [x] Lock against the flexdoc 0.4.1 PR branch (git source). Relock from PyPI
      after 0.4.1 is tagged
- [x] Run `make lint` and `make test`, including
      `tests/divs/test_div_elements.py` and transform / `token_diffs` tests
      (`TextUnit.words` sizes unchanged → chopdiff 0.4.1, not 0.5.0)
- [x] PR: [jlevy/chopdiff#33](https://github.com/jlevy/chopdiff/pull/33)
      (cannot release until flexdoc 0.4.1 is tagged)
- [ ] After signoff: drop the git source, relock from PyPI, tag once CI is
      green

### Phase 3: kash-shell, kash-docs, kash-media

These three PRs wait on flexdoc 0.4.1 **and** the new chopdiff tag.
They are independent of each other.

**kash-shell** ([jlevy/kash](https://github.com/jlevy/kash))

- [ ] Update `main`
- [ ] `flexdoc>=0.4.1` and `chopdiff>=` the new chopdiff tag
- [ ] Relock; PR; optional `v0.4.12` after signoff

**kash-docs** ([jlevy/kash-docs](https://github.com/jlevy/kash-docs))

Needed for lock and lower-bound hygiene on the 0.2.7 line, not for the first
install fix after flexdoc 0.3.1.

- [ ] Start from GitHub `main` at 0.2.7, not the stale local tree
- [ ] Same flexdoc and chopdiff pins; relock; PR; optional 0.2.8 after
      signoff

**kash-media** (this repo)

- [ ] Same flexdoc and chopdiff pins; relock
- [ ] Set `requires-python = ">=3.13,<3.15"`; keep the 3.14 classifier
- [ ] Drop the stale onnxruntime 3.14-wheels comment
- [ ] README / installation: `uv tool install --python 3.13 kash-media` or
      `--python 3.14` (GIL). Do not document 3.14t
- [ ] PR; optional `v0.4.10` after signoff

**Verify again** from `/tmp` after Phase 3 tags (or after PyPI has 0.4.1 +
new chopdiff, even before kash consumer tags):

- [ ] `uv tool install --force --python 3.13 kash-media` and
      `--python 3.14` do not build cydifflib and resolve flexdoc >=0.3.1
      (and 0.4.1 once chopdiff allows it)
- [ ] `uvx --python 3.13 kash-shell@latest` and `--python 3.14` succeed
- [ ] Do not expect a bare install with no `--python` to succeed if uv
      selects 3.14t

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

After flexdoc 0.3.1, and again after chopdiff + flexdoc 0.4.1, from a
directory with no Python pin:

```shell
uv tool uninstall kash-media || true
uv tool install --force --python 3.13 kash-media
uv tool install --force --python 3.14 kash-media
uvx --python 3.13 kash-shell@latest --help
uvx --python 3.14 kash-shell@latest --help
```

Do not treat `make test` in a 3.13 project venv as evidence the tool install
works.
Do not treat a bare `uv tool install` with no `--python` as the success
criterion.

## Rollout Plan

Release identity is the git tag (`vX.Y.Z`).
Each package uses that repo’s `docs/publishing.md` (`publish.yml` trusted
publisher).
This pass files PRs only.

| Order | Step | Why this order |
| --- | --- | --- |
| 1 | flexdoc 0.3.1 PR | Cherry-pickable patch from `v0.3.0`; unblocks published kash the day it is tagged |
| 2 | flexdoc 0.4.1 PR | Same fix on the 0.4 line; chopdiff’s target; parallel with (1) |
| 3 | chopdiff PR | Opens `flexdoc` 0.4.x; cannot tag until flexdoc 0.4.1 is on PyPI |
| 4 | User signoff, then tags | `v0.3.1`, `v0.4.1`, then chopdiff `v0.4.1` or `v0.5.0` |
| 5 | kash-shell / kash-docs / kash-media PRs | Same day as the chopdiff tag (no cool-off) |
| 6 | Optional kash tags | Published lower bounds; not required once 0.3.1 exists |

Do not tag a consumer before its PR is merged and CI is green on `main`.
Do not publish a kash release that requires `flexdoc>=0.4.1` before the new
chopdiff is on PyPI, or the resolver will conflict (`chopdiff 0.4.0` still
says `<0.4.0`).

Rehearse flexdoc and chopdiff with `make build` and inspect wheel
`Requires-Dist` before tagging.

## Open Questions

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
