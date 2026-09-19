---
title: "Plan Spec: Unblock kash installs blocked by cydifflib on Python 3.14"
description: >-
  Flexdoc 0.4.1 and chopdiff 0.4.1 are on PyPI. Chopdiff depends on
  `flexdoc[diff]>=0.4.1,<0.5` (cydifflib kept). Next is kash-shell /
  kash-docs / kash-media. Do not drop cydifflib. Do not merge flexdoc
  24/25. Do not tag kash from this pass.
---
# Feature: Unblock kash Installs Blocked by cydifflib on Python 3.14

**Date:** 2026-09-18 (last updated 2026-09-19)

**Spike (2026-09-18):** GIL CPython 3.14.6 installs and imports the full published
kash-media graph, including frame capture (`cv2` + `skimage`). Freethreaded 3.14t does
not. See Background.

**Bench (2026-09-18):** On the production path, cydifflib 1.2.0 is 8.4× to 38.7× faster
than stdlib `difflib` (33–39× at WINDOW_2K). Keep cydifflib for token diffs.

**Build-debug (2026-09-18):** Published cydifflib 1.2.0 sdist **builds and imports on
GIL 3.14** in about 17s. The same `.cxx` **fails on 3.14t**. A fork is not required for
the release train. See Diagnosis.

**Author:** Joshua Levy

**Status:** Active (flexdoc `v0.4.1` on PyPI at `cbe2f5d`; chopdiff `v0.4.1` on
PyPI at `728e46b`, `flexdoc[diff]>=0.4.1,<0.5`; cydifflib is the `diff` extra;
spec PR [kash-media#13](https://github.com/jlevy/kash-media/pull/13) merged;
kash-media pyproject prepared on `build/gil-python-314`; lock can now use
published chopdiff `0.4.1`; a kash-docs that allows GIL 3.14 is still required)

## Overview

`uv tool install kash-media` and `uvx kash-shell@latest` fail on machines where uv’s
default interpreter is **freethreaded** CPython 3.14t. On this machine
`uv python find 3.14` resolves `cpython-3.14.7+freethreaded`. `uv tool install` / `uvx`
keep that interpreter and do not re-select from the root package’s `requires-python`.
`uv venv -p 3.14` is not enough if that pin still resolves 3.14t.

The resolver pulls `flexdoc` 0.3.0 → `cydifflib` 1.2.0. cydifflib ships wheels for
cp39–cp313 only (no cp314 / cp314t). On **3.14t** the sdist’s shipped Cython 3.0.12
`_initialize.cxx` fails (`__pyx_vectorcallfunc`, `PyTuple_GetSlice` on FASTCALL args).
On **GIL 3.14** that same sdist **builds and imports** (CMake compiles the shipped
`.cxx` in about 17s; `SequenceMatcher` works).

flexdoc uses cydifflib in one place (`token_diffs.SequenceMatcher`, `autojunk=False`).
stdlib `difflib` is API-compatible there, but it is **not** the release default.
chopdiff’s README (commit `0e6f81d`) states cydifflib is significantly
faster than stdlib `difflib`. A production-path bench on CPython 3.13.7 arm64 confirmed
**8.4× at 59 tokens; 38.7× at 2048 (2.0 ms vs 77.8 ms); 32.5× at 10k; 35.2× at 20k**
(33–39× at WINDOW_2K). Opcodes matched stdlib.
**Keep `cydifflib>=1.2.0` for token diffs.** Do not drop it for stdlib.
Core flexdoc does not depend on it: install `flexdoc[diff]`.

**One flexdoc release from `main` is done:** `v0.4.1` (`cbe2f5d`), on PyPI.
Token diffs keep `cydifflib>=1.2.0` on the `diff` extra. **Supported = GIL 3.14.
Unsupported = 3.14t.**
`requires-python` includes 3.14 (`>=3.11,<3.15`) but cannot exclude 3.14t; a version
specifier is not a GIL vs freethreaded flag. Enforcement is an import-time
`sysconfig.get_config_var("Py_GIL_DISABLED")` guard before `import cydifflib`, plus
docs. flexdoc supports CPython 3.11–3.14 with the GIL, not free-threaded 3.14t; use
`--python 3.13` or a GIL 3.14 (`uv python find 3.14` may resolve to 3.14t).
Do **not** fork CyDifflib as part of this train.
Do **not** vendor cydifflib into flexdoc.
Do **not** merge [jlevy/flexdoc#24](https://github.com/jlevy/flexdoc/pull/24) or
[jlevy/flexdoc#25](https://github.com/jlevy/flexdoc/pull/25) (closed: stdlib drop;
wrong default; superseded by #26 and #27). Do not also ship a 0.3.1 patch.

Published chopdiff 0.4.0 pinned `flexdoc>=0.3.0,<0.4.0`. Chopdiff `0.4.1` now
depends on `flexdoc[diff]>=0.4.1,<0.5` and is on PyPI. Do not add a second
flexdoc tag later as a “quick unblock.”

A CyDifflib fork (Cython 3.2 regenerate, cp314 / optional cp314t wheels under a new PyPI
name) is **optional**, only if we later want 3.14t to *install* cydifflib.
Even then, a 3.14t compile re-enables the GIL, and kash-media’s next wall is an OpenCV
source build. 3.14t remains **not** a kash-media install target.
An upstream ping can run in parallel.
Do not start a fork in this pass.

jlevy first-party packages are exempt from the 14-day cool-off (`2099-12-31` per-package
exemptions). Chopdiff now uses `flexdoc = "2099-12-31T00:00:00Z"`.

Flexdoc and chopdiff are tagged. Chopdiff `v0.4.1` depends on
`flexdoc[diff]>=0.4.1,<0.5` and is on PyPI. kash-media pyproject is prepared
(`requires-python = ">=3.13,<3.15"`, `flexdoc[diff]>=0.4.1`, `chopdiff>=0.4.1`).
Relock from the published packages. kash-docs 0.2.7 still declares
`requires-python <3.14`, so a GIL 3.14 `uv tool install` stays blocked until a
new kash-docs is published.

## Decisions

Locked 2026-09-18, updated the same day after bench, options analysis, and build-debug:

- **Keep PyPI `cydifflib>=1.2.0` for token diffs, as `flexdoc[diff]`.** Do not drop it
  for stdlib `difflib`. Core flexdoc does not depend on cydifflib. Written reason:
  chopdiff `0e6f81d` / README. Bench: 8.4×–38.7× (33–39× at WINDOW_2K); opcodes matched.
- **No required native install fix for GIL 3.14.** Published 1.2.0 sdist builds and
  imports on GIL 3.14 if CMake and a C++ compiler are present.
  No cp314 wheel exists; the sdist is enough for GIL 3.14.
- **Do not fork CyDifflib on the required train.** Fork / Cython regenerate is optional
  and only for “3.14t can install cydifflib.”
  Do not start a fork in this pass.
  Vendoring into flexdoc is rejected (would make flexdoc a native cibuildwheel package).
  Stdlib fallback is rejected. Token diffs require the `diff` extra (cydifflib).
- **Do not claim 3.14t-safe.** A regenerate-and-compile on 3.14t re-enables the GIL.
  Aiming for 3.14t to *install* cydifflib is optional later work, not this train.
  kash-media on 3.14t still dies on OpenCV.
- **One flexdoc release, from `main`.** Shipped as `v0.4.1`. Token diffs keep
  cydifflib on `flexdoc[diff]`.
  Declare GIL 3.14 (`requires-python = ">=3.11,<3.15"`, keep the 3.14 classifier).
  Do not claim 3.14t. There is no Trove classifier for “free-threading unsupported”
  (the published levels are Unstable / Beta / Stable / Resilient); omit it.
  Do not ship 0.3.1. Do not merge #24 or #25.
- **Enforce 3.14t at import, not only in metadata.** `requires-python` cannot express
  GIL vs freethreaded. `uv tool install` / `uvx` can still pick
  `3.14.7+freethreaded` even when a package says `<3.14`. Before `import cydifflib`,
  check the **build** flag `sysconfig.get_config_var("Py_GIL_DISABLED")` (not live
  GIL state: a 3.14t cydifflib import re-enables the GIL, so
  `sys._is_gil_enabled()` after import is a lie). Raise a short error naming 3.14t
  and `--python 3.13` / GIL 3.14.
- **0.3.1 is cancelled** (one release, less release-branch surface).
  chopdiff 0.4.0 cannot select flexdoc `>=0.4.0`, so **chopdiff must publish before kash
  consumers see the new flexdoc.**
- **GIL Python 3.14 is allowed for kash-media**
  (`requires-python = ">=3.13,<3.15"`, keep the 3.14 classifier).
  The vision stack works (opencv-python 5.0.0.93 `abi3`, scikit-image).
- **Python 3.14t is unsupported as a kash-media install target.** Install docs must say
  `--python 3.13` or a **GIL** 3.14. `uv venv -p 3.14` / `--python 3.14` is not enough
  if uv resolves 3.14t. Be explicit (for example pin a GIL build, not the freethreaded
  one).
- **Flexdoc and chopdiff are tagged.** Kash tags still wait on sibling consumer
  PRs. kash-media may tag `v0.4.10` after a green merge if publish is tag-driven
  (`uvx kash-media@latest`).
- **Lower-level libraries first:** flexdoc `v0.4.1` and chopdiff `v0.4.1` are on
  PyPI; next is kash consumers.
- **jlevy first-party repos have no cool-off restriction.** Use `2099-12-31` exemptions.

These close dual-track 0.3.1 and 0.4.1, dropping cydifflib, vendoring into flexdoc,
stdlib fallback as default, and “must fork for GIL 3.14.”

## Goals

- Ship **one** flexdoc release from `main` that **keeps** `cydifflib>=1.2.0` on the
  `diff` extra, declares GIL 3.14 (`>=3.11,<3.15`), and rejects 3.14t at import via
  `Py_GIL_DISABLED` (done: `v0.4.1`)
- Publish a new chopdiff that depends on `flexdoc[diff]>=0.4.1,<0.5` (done:
  `v0.4.1`; chopdiff 0.4.0 cannot)
- Then lock kash-shell, kash-docs, and kash-media onto the new flexdoc and chopdiff
  lower bounds
- Make `uv tool install` / `uvx` succeed on **GIL** 3.13 and **GIL** 3.14 with cydifflib
  present, using an explicit interpreter pin that cannot resolve 3.14t
- Allow GIL 3.14 on kash-media (`requires-python >=3.13,<3.15`)
- Document the uv interpreter trap: bare `uv tool install` / `uvx` and a naive
  `--python 3.14` can still select 3.14t

## Non-Goals

- Dropping cydifflib, or treating stdlib `difflib` as the default accelerator
- Merging or tagging flexdoc #24 or #25
- Shipping flexdoc 0.3.1, or any second flexdoc tag to unblock chopdiff 0.4.0
- Forking CyDifflib, publishing a new PyPI name, or vendoring cydifflib into flexdoc as
  part of this train
- Claiming 3.14t-safe, or making 3.14t a kash-media install target
- Changing uv itself
- Touching third-party flexdoc pins outside this train (ojoshe, practical-prose, and
  similar)
- Reworking chopdiff windowing or chunk APIs except as required to accept flexdoc 0.4.x
  `TextUnit.words` semantics
- Starting kash-shell or kash-docs PRs from this repo (sibling agents own those)
- Cutting a kash-media tag before the lock resolves on PyPI and CI is green

## Background

### Failure

From a non-project directory (for example tbd), `uv python find` selects the newest
managed interpreter.
On this machine `uv python find 3.14` is `cpython-3.14.7+freethreaded`.
`uv tool install` / `uvx` keep that interpreter.
kash-media 0.4.9 already declares `>=3.13,<3.14`; the install still ran on 3.14t.

`--python 3.13` installs cleanly today (kash-media 0.4.9, kash-shell 0.4.11, flexdoc
0.3.0, cydifflib wheel).

### Diagnosis (Build-Debug, 2026-09-18)

Confirmed locally:

| Interpreter | cydifflib 1.2.0 | Result |
| --- | --- | --- |
| CPython 3.13 (wheel) | cp313 wheel | Installs; production path as today |
| CPython 3.14 GIL | sdist, shipped Cython 3.0.12 `_initialize.cxx` | **Builds and imports in ~17s.** `SequenceMatcher` works. No cp314 wheel. |
| CPython 3.14t | same shipped `.cxx` | **Fails:** `__pyx_vectorcallfunc`, `PyTuple_GetSlice` on FASTCALL args. Freethreaded + Cython 3.0.x, not a GIL 3.14 ABI break. |

Further 3.14t notes (not on the required train):

- Adding `Cython>=3.1` **without** deleting `_initialize.cxx` does **not** fix 3.14t
  (CMake never regenerates).
- Delete `.cxx` and build with Cython 3.1.8 or 3.3.0: 3.14t **compiles**; import then
  **re-enables the GIL**. Do not claim 3.14t-safe.
- Even after a 3.14t cydifflib compile, kash-media’s next wall is an OpenCV source-build
  (`opencv-python` 5.0.0.93 has no `cp314t` wheel; `abi3` is not used).

**Implication:** the original “cydifflib does not compile on 3.14” report mixed GIL 3.14
with 3.14t. GIL 3.14 does not need a fork, a vendor, or a stdlib drop.
Bare `uv tool install` died because uv picked 3.14t.

### Rejected Alternatives

- **Drop cydifflib (#24 / #25):** wrong default.
  33–39× slower at WINDOW_2K. Do not merge.
- **Vendor into flexdoc:** would make flexdoc a native cibuildwheel package.
  Not necessary; GIL 3.14 already builds the published sdist.
- **Optional extra / stdlib fallback as default:** rejected (same bench).
- **Must-fork CyDifflib for this train:** overridden by build-debug.
  Optional later if we want 3.14t to *install* cydifflib.
  Upstream ping is fine in parallel.

### Why Keep cydifflib

flexdoc’s only cydifflib use is `SequenceMatcher` in `token_diffs`.

**Written reason** (chopdiff commit `0e6f81d`, README): LCS-style token diffs use
[cydifflib](https://github.com/rapidfuzz/cydifflib), which is significantly faster than
Python’s built-in [difflib](https://docs.python.org/3.10/library/difflib.html).

**Bench** (2026-09-18), production path, CPython 3.13.7 arm64, cydifflib 1.2.0:
`wordtoks`, `SequenceMatcher(autojunk=False)`, `get_opcodes`. Opcodes matched stdlib.

| Tokens | Speedup vs stdlib | Notes |
| --- | --- | --- |
| 59 | 8.4× |  |
| 2048 | 38.7× | 2.0 ms vs 77.8 ms; WINDOW_2K 33–39× |
| 10k | 32.5× |  |
| 20k | 35.2× |  |

### Spike: GIL 3.14 vs Freethreaded 3.14t (kash-media)

Tested 2026-09-18 on macOS arm64.

**CPython 3.14.6 (GIL, uv-managed)** — works for kash-media as published.

- `uv pip install kash-media` completed (cydifflib 1.2.0 built a
  `_initialize.cpython-314-darwin.so`; opencv-python 5.0.0.93 used its `cp37-abi3`
  wheel).
- Frame path imported and ran a tiny SSIM: `cv2` 5.0.0, `skimage` 0.26.0,
  `structural_similarity` self-score 1.0, `VideoCapture` constructs, backends include
  `AVFOUNDATION` and `FFMPEG`.
- Also imported `kash.kits.media.video.video_frames` and `image_similarity`, plus
  `tokenizers`, `curl_cffi`, `yt_dlp`.
- The pyproject comment that onnxruntime lacks 3.14 wheels is stale.
  Neither onnxruntime nor torch is on the default media graph (`kash-docs` without
  `[full]`). A probe install of current wheels succeeded: onnxruntime 1.29.0, torch
  2.14.0.

**CPython 3.14.7+freethreaded** — not a kash-media install target.

- This is what `uv python find 3.14` / bare `uv tool install` pick as “latest” from a
  directory with no pin.
- cydifflib sdist fails to compile (Cython 3.0.x + freethreaded).
- After a hypothetical regenerate, OpenCV source-build is the next wall.

**Docs:** tell tool users `--python 3.13` or a **GIL** 3.14. Spell out that
`--python 3.14` / `uv venv -p 3.14` can still resolve 3.14t on this toolchain.
Do not document 3.14t as supported.

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
Published chopdiff `0.4.1` now allows flexdoc `0.4.x`. Consumer locks must bump
to `chopdiff>=0.4.1`.

flexdoc 0.4.0 changed `TextUnit.words` from raw whitespace counts to logical word
metrics. chopdiff windowing uses `wordtoks` / `paragraphs` / `bytes`. `TextUnit.words`
appears in div-chunk tests (`chunk_text_as_divs`). Phase 2 against PyPI
`flexdoc[diff]` 0.4.1: sizes unchanged; tagged chopdiff `v0.4.1`.

### Why 0.3.1 Was Cancelled

A 0.3.1 patch would have been selectable by published chopdiff 0.4.0 without a chopdiff
release. That dual-track is cancelled: one release from `main`, less `release/0.3.x`
surface. **chopdiff must ship before kash sees the new flexdoc.** Do not revive 0.3.1.

#24 and #25 are closed (rejected: stdlib drop is a 30–40× regression; superseded by
#26 and #27). Do not merge or tag them.

### First-Party Cool-Off

kash-shell, kash-docs, and kash-media list flexdoc and chopdiff at `2099-12-31`.
Chopdiff now uses `flexdoc = "2099-12-31T00:00:00Z"` and depends on
`flexdoc[diff]>=0.4.1,<0.5`. [chopdiff#33](https://github.com/jlevy/chopdiff/pull/33)
merged; [chopdiff#34](https://github.com/jlevy/chopdiff/pull/34) locked `pip==26.2.1`
so the publish audit gate could pass (PYSEC-2026-3721; not an ignore).

### Checkout Notes

| Repo | GitHub | Local note |
| --- | --- | --- |
| flexdoc | [jlevy/flexdoc](https://github.com/jlevy/flexdoc) | `v0.4.1` on PyPI (`cbe2f5d`): GIL 3.14; refuse 3.14t; `cydifflib` is extra `diff`. [26](https://github.com/jlevy/flexdoc/pull/26) and [27](https://github.com/jlevy/flexdoc/pull/27) merged. [24](https://github.com/jlevy/flexdoc/pull/24) and [25](https://github.com/jlevy/flexdoc/pull/25) closed. |
| chopdiff | [jlevy/chopdiff](https://github.com/jlevy/chopdiff) | `v0.4.1` on PyPI (`728e46b`): `flexdoc[diff]>=0.4.1,<0.5`; cool-off `2099-12-31`; cydifflib via extra `diff`. [33](https://github.com/jlevy/chopdiff/pull/33) and [34](https://github.com/jlevy/chopdiff/pull/34) merged. |
| kash-shell | [jlevy/kash](https://github.com/jlevy/kash) | Latest tag `v0.4.11`. Can lock `flexdoc[diff]>=0.4.1` and `chopdiff>=0.4.1` from PyPI. |
| kash-docs | [jlevy/kash-docs](https://github.com/jlevy/kash-docs) | Work from GitHub `main` / published 0.2.7. Same pins; still needs GIL 3.14 (`<3.14` today). |
| kash-media | [jlevy/kash-media](https://github.com/jlevy/kash-media) | Spec PR #13 merged. Package branch `build/gil-python-314`: `requires-python >=3.13,<3.15`, `flexdoc[diff]>=0.4.1`, `chopdiff>=0.4.1`. Chopdiff `0.4.1` is on PyPI; relock can proceed. |

## Design

### Approach

Keep published `cydifflib>=1.2.0` for token diffs (`flexdoc[diff]`). Do not drop,
vendor, or fork for this train.

**One coordinated train:**

1. One flexdoc release from `main` (not #24 or #25): **done** (`v0.4.1`). Token diffs
   keep cydifflib on extra `diff`; `requires-python = ">=3.11,<3.15"`; import-time
   `Py_GIL_DISABLED` guard before `cydifflib`; do not claim 3.14t.
2. One chopdiff pin: **done** (`v0.4.1`). `flexdoc[diff]>=0.4.1,<0.5`, cool-off
   `2099-12-31`, relocked from PyPI. `TextUnit.words` tests unchanged (45 passed).
3. kash-shell, kash-docs, kash-media: new lower bounds; kash-media `requires-python` and
   install docs (explicit GIL pin).
   kash-media pyproject is prepared; relock from published chopdiff `0.4.1` and a
   kash-docs that allows GIL 3.14.

Optional later, not this train: fork CyDifflib, regenerate with Cython 3.2, publish
cp314 (and cp314t if cheap) under a new PyPI name so 3.14t can *install* cydifflib.
Upstream ping can start without a fork.

### Backward Compatibility

- **cydifflib import path:** MAINTAIN for token diffs via `_cydifflib()` and
  `flexdoc[diff]` (`cydifflib>=1.2.0`). No stdlib fallback.
- **Library APIs (flexdoc token_diffs):** no public flexdoc API exposes `cydifflib`.
- **chopdiff ↔ flexdoc 0.4.x:** VERSION and FAIL FAST on the pin
  (`flexdoc[diff]>=0.4.1,<0.5`). Confirmed against PyPI `flexdoc[diff]` 0.4.1:
  sizes unchanged; shipped as chopdiff `v0.4.1`.
- **Server APIs / plugins / file formats / persisted state / schemas:** N/A.

### API Changes

flexdoc: none at `token_diffs` besides the import-time `Py_GIL_DISABLED` guard and
the lazy `flexdoc[diff]` import. `requires-python` is `>=3.11,<3.15`. 3.14
classifier stays. No free-threading classifier (no “unsupported” Trove level exists).

chopdiff: none unless 0.4.x forces `TextUnit.raw_words` or new expected sizes.

### Components

| Package | Change | New tag |
| --- | --- | --- |
| flexdoc | One release from `main`; `cydifflib` on extra `diff`; `>=3.11,<3.15`; `Py_GIL_DISABLED` guard | **shipped** `v0.4.1` |
| chopdiff | `flexdoc[diff]>=0.4.1,<0.5`; first-party cool-off; relock; tests | **shipped** `v0.4.1` |
| kash-shell | new flexdoc and chopdiff lower bounds; relock | optional `v0.4.12` |
| kash-docs | same pins; allow GIL 3.14 (`<3.14` today); relock from GitHub `main` | optional 0.2.8 |
| kash-media | same pins; relock; GIL 3.14 and explicit `--python` docs | optional `v0.4.10` |

## Implementation Plan

There is no 0.3.1 phase, no drop-cydifflib phase, and no required fork phase.
Flexdoc and chopdiff are tagged. Kash tags wait on sibling consumer PRs.

### Done: Diagnosis

- [x] Keep cydifflib (bench 33–39× at WINDOW_2K)
- [x] GIL 3.14: published 1.2.0 sdist builds and imports (~17s)
- [x] 3.14t: Cython 3.0.x + freethreaded; not a GIL 3.14 ABI break
- [x] Fork / vendor / stdlib-drop are not required for this train
- [x] Do not merge #24 or #25

### Phase 1: One Flexdoc Release From Main

- [x] Hard-drop PRs opened and rejected for merge:
  [jlevy/flexdoc#24](https://github.com/jlevy/flexdoc/pull/24),
  [jlevy/flexdoc#25](https://github.com/jlevy/flexdoc/pull/25)
- [x] New PR from `main` (not #24/#25): [jlevy/flexdoc#26](https://github.com/jlevy/flexdoc/pull/26).
  GIL 3.14; `Py_GIL_DISABLED` guard; does not claim 3.14t
- [x] Follow-up [jlevy/flexdoc#27](https://github.com/jlevy/flexdoc/pull/27): `cydifflib`
  is extra `diff` only
- [x] After signoff: merge #26 and #27, tag **one** flexdoc version from `main`
  (`v0.4.1` at `cbe2f5d`)
- [x] Confirm PyPI `flexdoc==0.4.1`: default `Requires-Dist` has no `cydifflib`;
  extra `diff` requires `cydifflib>=1.2.0`
- [x] Do **not** tag `v0.3.1`. #24 and #25 closed, not merged

### Phase 2: One Chopdiff Pin

Repo: [jlevy/chopdiff](https://github.com/jlevy/chopdiff).

- [x] Cool-off `flexdoc = "2099-12-31T00:00:00Z"`
- [x] Dep `flexdoc[diff]>=0.4.1,<0.5` (no git source)
- [x] PR [jlevy/chopdiff#33](https://github.com/jlevy/chopdiff/pull/33) retargeted off
  #25; relocked from PyPI `flexdoc==0.4.1`; `TextUnit.words` tests unchanged
- [x] [chopdiff#34](https://github.com/jlevy/chopdiff/pull/34): lock `pip==26.2.1`
  (PYSEC-2026-3721 remediation; publish.yml runs `pip-audit`)
- [x] Tag `v0.4.1` at `728e46b`; PyPI `chopdiff==0.4.1` requires
  `flexdoc[diff]<0.5,>=0.4.1`

### Phase 3: kash-shell, kash-docs, kash-media

Flexdoc and chopdiff `v0.4.1` are on PyPI. Consumer PRs can lock now.
kash-media pyproject and install docs are prepared on `build/gil-python-314`.

**kash-shell** ([jlevy/kash](https://github.com/jlevy/kash))

- [ ] New flexdoc and chopdiff lower bounds; relock; PR; optional `v0.4.12`

**kash-docs** ([jlevy/kash-docs](https://github.com/jlevy/kash-docs))

- [ ] From GitHub `main` at 0.2.7; same pins; allow GIL 3.14
  (`requires-python` today is `<3.14`); relock; PR; optional 0.2.8

**kash-media** (this repo)

- [x] Same pins in pyproject (`flexdoc[diff]>=0.4.1`, `chopdiff>=0.4.1`)
- [ ] Relock from PyPI `chopdiff==0.4.1` (and kash-docs if a new version exists)
- [x] `requires-python = ">=3.13,<3.15"`; keep the 3.14 classifier
- [x] Drop the stale onnxruntime 3.14-wheels comment
- [x] README / installation: `--python 3.13` or an explicit **GIL** 3.14. State that
  `uv venv -p 3.14` / `--python 3.14` can resolve 3.14t. Do not document 3.14t as
  supported
- [ ] PR; optional `v0.4.10` after a green merge if publish is tag-driven

**Verify** from `/tmp` after Phase 2 tags:

- [ ] `uv tool install --force` with an explicit **GIL** 3.13 and **GIL** 3.14 succeeds
  and still includes cydifflib (only after chopdiff allows 0.4.x)
- [ ] `uvx` with the same GIL pins succeeds
- [ ] Do not expect a bare install, or `--python 3.14` that resolves 3.14t, to succeed

## Testing Strategy

**flexdoc (`main` line only)**

- `token_diffs` tests and golden docs
- Guard: `is_gil_disabled_build()` is False on a GIL runner and True when
  `Py_GIL_DISABLED` is mocked
- Built wheel `Requires-Dist` must list `cydifflib` **only** as
  `extra == "diff"` (confirmed on PyPI 0.4.1)

**cydifflib (done)**

- Bench vs stdlib; keep cydifflib on `flexdoc[diff]`
- GIL 3.14 sdist build and import (~17s)
- 3.14t sdist fail (Cython 3.0.x)

**chopdiff**

- Div / transform / token-diff tests against `flexdoc[diff]` 0.4.1
- `uv tree -p flexdoc -p cydifflib` shows both (via the extra)

**kash consumers**

- `make lint` and `make test` after the lock change
- Resolver: new flexdoc, new chopdiff, cydifflib present
- GIL 3.14 tool install with an explicit GIL pin

**release smoke (required, packaged artifact)**

After both tags are on PyPI, from a directory with no Python pin, use **GIL**
interpreters (not 3.14t):

```shell
uv tool uninstall kash-media || true
uv tool install --force --python 3.13 kash-media
# Pin a GIL 3.14, not 3.14t — `--python 3.14` can resolve freethreaded
uvx --python 3.13 kash-shell@latest --help
```

Do not treat `make test` in a 3.13 project venv as evidence the tool install works.
Do not treat a bare `uv tool install` as the success criterion.
Do not treat a flexdoc-only publish as enough (published `chopdiff 0.4.0` still
selects flexdoc 0.3.0; use `chopdiff>=0.4.1`). Do not treat “no cydifflib in the
tree” as success.

## Rollout Plan

Release identity is the git tag (`vX.Y.Z`). Flexdoc `v0.4.1` and chopdiff `v0.4.1`
are tagged. This pass does not tag kash, fork CyDifflib, or merge #24/#25.

1. Keep `cydifflib>=1.2.0` for token diffs (decided). Extra `diff`, not a default dep.
   No required fork or vendor.
2. Flexdoc PRs from `main` (not #24/#25): #26 GIL guard; #27 `flexdoc[diff]`. Drop PRs
   closed.
3. User signoff, then one flexdoc tag from `main` (**done:** `v0.4.1`).
4. One chopdiff pin of `flexdoc[diff]>=0.4.1,<0.5` from PyPI (**done:** `v0.4.1`).
5. kash-shell / kash-docs / kash-media PRs the same day as the chopdiff tag.
6. Optional kash tags.
7. Smoke-test GIL 3.13 and GIL 3.14 from `/tmp`. Confirm cydifflib is in the graph.

Chopdiff `0.4.1` is on PyPI. Consumer locks can require `flexdoc[diff]>=0.4.1`
and `chopdiff>=0.4.1`.

Rehearse with `make build` and inspect `Requires-Dist` (`cydifflib` only on extra
`diff`).

## Open Questions

- **Optional later:** fork CyDifflib so 3.14t can *install* cydifflib (not 3.14t-safe;
  not a kash-media target).
  Not this train.

Closed: dual-track 0.3.1 and 0.4.1. Closed: drop cydifflib.
Closed: vendor into flexdoc.
Closed: stdlib fallback as default.
Closed: must-fork for GIL 3.14.
Closed: GIL 3.14 vs `<3.14`. **Supported = GIL 3.14; unsupported = 3.14t.**
flexdoc `requires-python = ">=3.11,<3.15"` (includes 3.14, cannot exclude 3.14t).
Enforcement is import-time `Py_GIL_DISABLED` plus docs, not metadata alone.
Closed: flexdoc 0.4.1 contents and tag. GIL 3.14; `cydifflib` on extra `diff`; no
stdlib fallback. Tagged `v0.4.1` (`cbe2f5d`); on PyPI.
Closed: chopdiff 0.4.1 vs 0.5.0. Tests unchanged against PyPI `flexdoc[diff]`
0.4.1; tagged `v0.4.1` (`728e46b`); on PyPI.

## References

- flexdoc call site: `src/flexdoc/docs/token_diffs.py`
- flexdoc 3.14t guard: `src/flexdoc/util/cpython_build.py` (`Py_GIL_DISABLED`), called
  from `token_diffs` before `import cydifflib`
- chopdiff rationale: commit `0e6f81d`,
  [README.md](https://github.com/jlevy/chopdiff/blob/main/README.md)
- chopdiff pin and dated exception: `pyproject.toml`
- Published pins: PyPI `kash-media` 0.4.9, `kash-shell` 0.4.11, `kash-docs` 0.2.7,
  `chopdiff` 0.4.1, `flexdoc` 0.4.1 (`diff` extra), `cydifflib` 1.2.0
- Flexdoc release: [v0.4.1](https://github.com/jlevy/flexdoc/releases/tag/v0.4.1),
  [publish run](https://github.com/jlevy/flexdoc/actions/runs/35413395310)
- Flexdoc PRs: [26](https://github.com/jlevy/flexdoc/pull/26) (GIL 3.14 / 3.14t guard);
  [27](https://github.com/jlevy/flexdoc/pull/27) (`diff` extra);
  [24](https://github.com/jlevy/flexdoc/pull/24) and
  [25](https://github.com/jlevy/flexdoc/pull/25) (closed; stdlib drop)
- Chopdiff release: [v0.4.1](https://github.com/jlevy/chopdiff/releases/tag/v0.4.1),
  [publish run](https://github.com/jlevy/chopdiff/actions/runs/35415631527)
- Chopdiff PRs: [33](https://github.com/jlevy/chopdiff/pull/33) (`flexdoc[diff]` from
  PyPI); [34](https://github.com/jlevy/chopdiff/pull/34) (`pip==26.2.1`)
- Plan PR: [kash-media#13](https://github.com/jlevy/kash-media/pull/13)
- Install docs: [README.md](../../../README.md),
  [installation.md](../../installation.md), [publishing.md](../../publishing.md)
- uv interpreter selection: `uv tool install --python` / `UV_PYTHON`; `uv python find
  3.14` can be 3.14t

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
