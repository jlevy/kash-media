---
title: "Plan Spec: Unblock kash installs blocked by cydifflib on Python 3.14"
description: >-
  One flexdoc release from main that keeps PyPI cydifflib>=1.2.0,
  then one chopdiff pin, then kash-shell / kash-docs / kash-media.
  Published cydifflib 1.2.0 already builds on GIL 3.14. A CyDifflib
  fork is optional and not on the required train. Do not drop
  cydifflib. Freethreaded 3.14t stays unsupported as a kash-media
  target.
---
# Feature: Unblock kash Installs Blocked by cydifflib on Python 3.14

**Date:** 2026-09-18 (last updated 2026-09-18)

**Spike (2026-09-18):** GIL CPython 3.14.6 installs and imports the full published
kash-media graph, including frame capture (`cv2` + `skimage`). Freethreaded 3.14t does
not. See Background.

**Bench (2026-09-18):** On the production path, cydifflib 1.2.0 is 8.4× to 38.7× faster
than stdlib `difflib` (33–39× at WINDOW_2K). Keep the hard dependency.

**Build-debug (2026-09-18):** Published cydifflib 1.2.0 sdist **builds and imports on
GIL 3.14** in about 17s. The same `.cxx` **fails on 3.14t**. A fork is not required for
the release train. See Diagnosis.

**Author:** Joshua Levy

**Status:** Active (one-release topology, keep-cydifflib, and “no required fork” locked
2026-09-18; tags and GIL-3.14 product widening pending signoff)

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

flexdoc uses cydifflib in one place (`import cydifflib as difflib` for
`SequenceMatcher`). stdlib `difflib` is API-compatible there, but it is **not** the
release default. chopdiff’s README (commit `0e6f81d`) states cydifflib is significantly
faster than stdlib `difflib`. A production-path bench on CPython 3.13.7 arm64 confirmed
**8.4× at 59 tokens; 38.7× at 2048 (2.0 ms vs 77.8 ms); 32.5× at 10k; 35.2× at 20k**
(33–39× at WINDOW_2K). Opcodes matched stdlib.
**Keep the hard dependency on PyPI `cydifflib>=1.2.0`.** Do not drop it.

**One flexdoc release from current `main`.** Planned tag is 0.4.1. Keep
`cydifflib>=1.2.0`. Widen declared Python to include GIL 3.14 if that is the product
decision. Do **not** claim 3.14t. Do **not** fork CyDifflib as part of this train.
Do **not** vendor cydifflib into flexdoc.
Do **not** merge [jlevy/flexdoc#24](https://github.com/jlevy/flexdoc/pull/24) or
[jlevy/flexdoc#25](https://github.com/jlevy/flexdoc/pull/25) (stdlib drop; wrong
default). Do not also ship a 0.3.1 patch.

Published chopdiff 0.4.0 pins `flexdoc>=0.3.0,<0.4.0`. One flexdoc 0.4.x release does
**not** reach kash until a new chopdiff is published that allows `0.4.x`. That sequence
is required. Do not add a second flexdoc tag later as a “quick unblock.”

A CyDifflib fork (Cython 3.2 regenerate, cp314 / optional cp314t wheels under a new PyPI
name) is **optional**, only if we later want 3.14t to *install* cydifflib.
Even then, a 3.14t compile re-enables the GIL, and kash-media’s next wall is an OpenCV
source build. 3.14t remains **not** a kash-media install target.
An upstream ping can run in parallel.
Do not start a fork in this pass.

jlevy first-party packages are exempt from the 14-day cool-off (`2099-12-31` per-package
exemptions). chopdiff’s dated flexdoc exception (`2026-07-12`) is not that exemption and
must be updated, or the new flexdoc will not resolve in that repo.

PRs land first. Release tags wait for explicit user signoff.
Do not start kash-shell / kash-docs / kash-media PRs until the flexdoc and chopdiff tags
are on PyPI.

## Decisions

Locked 2026-09-18, updated the same day after bench, options analysis, and build-debug:

- **Keep PyPI `cydifflib>=1.2.0` as a hard dependency.** Do not drop it for stdlib
  `difflib`. Written reason: chopdiff `0e6f81d` / README. Bench: 8.4×–38.7× (33–39× at
  WINDOW_2K); opcodes matched.
- **No required native install fix for GIL 3.14.** Published 1.2.0 sdist builds and
  imports on GIL 3.14 if CMake and a C++ compiler are present.
  No cp314 wheel exists; the sdist is enough for GIL 3.14.
- **Do not fork CyDifflib on the required train.** Fork / Cython regenerate is optional
  and only for “3.14t can install cydifflib.”
  Do not start a fork in this pass.
  Vendoring into flexdoc is rejected (would make flexdoc a native cibuildwheel package).
  Optional extra / stdlib fallback is rejected as the default.
- **Do not claim 3.14t-safe.** A regenerate-and-compile on 3.14t re-enables the GIL.
  Aiming for 3.14t to *install* cydifflib is optional later work, not this train.
  kash-media on 3.14t still dies on OpenCV.
- **One flexdoc release, from `main`.** Keep cydifflib.
  Widen Python to include GIL 3.14 if that is the product decision.
  Planned 0.4.1. Do not ship 0.3.1. Do not merge #24 or #25.
- **0.3.1 is cancelled** (one release, less release-branch surface).
  chopdiff 0.4.0 cannot select flexdoc `>=0.4.0`, so **chopdiff must publish before kash
  consumers see the new flexdoc.**
- **GIL Python 3.14 is allowed for kash-media** if the product decision is to widen
  (`requires-python = ">=3.13,<3.15"`, keep the 3.14 classifier).
  The vision stack works (opencv-python 5.0.0.93 `abi3`, scikit-image).
- **Python 3.14t is unsupported as a kash-media install target.** Install docs must say
  `--python 3.13` or a **GIL** 3.14. `uv venv -p 3.14` / `--python 3.14` is not enough
  if uv resolves 3.14t. Be explicit (for example pin a GIL build, not the freethreaded
  one).
- **PRs now; tags only after user signoff.**
- **Lower-level libraries first:** one flexdoc from `main`, then one chopdiff pin, then
  kash consumers.
- **jlevy first-party repos have no cool-off restriction.** Use `2099-12-31` exemptions.

These close dual-track 0.3.1 and 0.4.1, dropping cydifflib, vendoring into flexdoc,
optional-extra as default, and “must fork for GIL 3.14.”

## Goals

- Ship **one** flexdoc release from `main` that **keeps** `cydifflib>=1.2.0` and, if
  signed off, declares GIL 3.14 (planned 0.4.1)
- Publish a new chopdiff that allows that flexdoc (chopdiff 0.4.0 cannot)
- Then lock kash-shell, kash-docs, and kash-media onto the new flexdoc and chopdiff
  lower bounds
- Make `uv tool install` / `uvx` succeed on **GIL** 3.13 and **GIL** 3.14 with cydifflib
  present, using an explicit interpreter pin that cannot resolve 3.14t
- Allow GIL 3.14 on kash-media (`requires-python >=3.13,<3.15`) if signed off
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
- Starting kash consumer PRs before the flexdoc and chopdiff tags are on PyPI
- Cutting release tags in this pass

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
Publishing only a flexdoc 0.4.x release still does not fix kash until a new chopdiff
release allows `0.4.x`.

flexdoc 0.4.0 changed `TextUnit.words` from raw whitespace counts to logical word
metrics. chopdiff windowing uses `wordtoks` / `paragraphs` / `bytes`. `TextUnit.words`
appears in div-chunk tests (`chunk_text_as_divs`). Phase 2 already ran against the 0.4.1
drop PR: sizes unchanged, so chopdiff 0.4.1 is the planned tag.
Re-run against a keep-cydifflib `main` (not #25) before tagging.

### Why 0.3.1 Was Cancelled

A 0.3.1 patch would have been selectable by published chopdiff 0.4.0 without a chopdiff
release. That dual-track is cancelled: one release from `main`, less `release/0.3.x`
surface. **chopdiff must ship before kash sees the new flexdoc.** Do not revive 0.3.1.

#24 and #25 remain open for the record.
Do not merge or tag them.
Their hard-drop is the wrong default, and GIL 3.14 does not need a drop.

### First-Party Cool-Off

kash-shell, kash-docs, and kash-media list flexdoc and chopdiff at `2099-12-31`.
chopdiff still has `flexdoc = "2026-07-12T00:00:00Z"`. That cutoff must become
`2099-12-31` before chopdiff can lock the new flexdoc.
[chopdiff#33](https://github.com/jlevy/chopdiff/pull/33) already makes that change
(against the hard-drop flexdoc branch; retarget to keep-cydifflib `main` / PyPI).

### Checkout Notes

| Repo | GitHub | Local note |
| --- | --- | --- |
| flexdoc | [jlevy/flexdoc](https://github.com/jlevy/flexdoc) | `origin/main` is the 0.4.0 line and already depends on cydifflib. One release from `main` (planned 0.4.1): keep the dep; optionally declare GIL 3.14. [PR 24](https://github.com/jlevy/flexdoc/pull/24) and [PR 25](https://github.com/jlevy/flexdoc/pull/25) will not merge. |
| chopdiff | [jlevy/chopdiff](https://github.com/jlevy/chopdiff) | Published 0.4.0 pins `flexdoc>=0.3.0,<0.4.0`. [PR 33](https://github.com/jlevy/chopdiff/pull/33) targets `flexdoc>=0.4.1,<0.5`; drop the git source on the hard-drop branch and relock from keep-cydifflib flexdoc. |
| kash-shell | [jlevy/kash](https://github.com/jlevy/kash) | Latest tag `v0.4.11`. Do not start a consumer PR yet. |
| kash-docs | [jlevy/kash-docs](https://github.com/jlevy/kash-docs) | Work from GitHub `main` / published 0.2.7. Do not start a consumer PR yet. |
| kash-media | [jlevy/kash-media](https://github.com/jlevy/kash-media) | Lock has flexdoc 0.3.0. Do not start the consumer PR yet. |

## Design

### Approach

Keep published `cydifflib>=1.2.0`. Do not drop, vendor, or fork for this train.

**One coordinated train:**

1. One flexdoc release from `main` (a **new** PR, not #24 or #25): keep cydifflib; widen
   declared Python to GIL 3.14 if signed off; do not claim 3.14t. Tag after user
   signoff.
2. One chopdiff pin: `flexdoc>=0.4.1,<0.5`, cool-off `2099-12-31`, relock from PyPI,
   re-confirm `TextUnit.words` tests.
   Tag only after the flexdoc tag is on PyPI and the user signs off.
3. kash-shell, kash-docs, kash-media: new lower bounds; kash-media `requires-python` and
   install docs (explicit GIL pin).
   File only after both tags are on PyPI.

Optional later, not this train: fork CyDifflib, regenerate with Cython 3.2, publish
cp314 (and cp314t if cheap) under a new PyPI name so 3.14t can *install* cydifflib.
Upstream ping can start without a fork.

### Backward Compatibility

- **cydifflib import path:** MAINTAIN. Keep `import cydifflib as difflib` and
  `cydifflib>=1.2.0`.
- **Library APIs (flexdoc token_diffs):** no public flexdoc API exposes `cydifflib`.
- **chopdiff ↔ flexdoc 0.4.x:** VERSION and FAIL FAST on the pin (`>=0.4.1,<0.5`). Phase
  2 against the drop PR: sizes unchanged → chopdiff 0.4.1. Re-confirm against
  keep-cydifflib `main`.
- **Server APIs / plugins / file formats / persisted state / schemas:** N/A.

### API Changes

flexdoc: none at `token_diffs`. Possible `requires-python` / classifier widening only.

chopdiff: none unless 0.4.x forces `TextUnit.raw_words` or new expected sizes.

### Components

| Package | Change | New tag |
| --- | --- | --- |
| flexdoc | One release from `main`; keep `cydifflib>=1.2.0`; optionally declare GIL 3.14 | planned `v0.4.1` |
| chopdiff | `flexdoc>=0.4.1,<0.5`; first-party cool-off; relock; tests | `v0.4.1` (tests passed; else `v0.5.0`) |
| kash-shell | new flexdoc and chopdiff lower bounds; relock | optional `v0.4.12` |
| kash-docs | same pins; relock from GitHub `main` | optional 0.2.8 |
| kash-media | same pins; relock; GIL 3.14 and explicit `--python` docs | optional `v0.4.10` |

## Implementation Plan

There is no 0.3.1 phase, no drop-cydifflib phase, and no required fork phase.
Tags wait for user signoff.

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
- [ ] New PR from `main` (not #24/#25): keep `cydifflib>=1.2.0`; widen `requires-python`
  / classifiers for GIL 3.14 if signed off; do not claim 3.14t
- [ ] After signoff: merge that PR, tag **one** flexdoc version from `main`
- [ ] Confirm PyPI metadata still requires `cydifflib`
- [ ] Do **not** tag `v0.3.1`. Do **not** merge #24 or #25

### Phase 2: One Chopdiff Pin

Repo: [jlevy/chopdiff](https://github.com/jlevy/chopdiff).

- [x] Cool-off `flexdoc = "2099-12-31T00:00:00Z"`
- [x] Dep `flexdoc>=0.4.1,<0.5`
- [x] PR [jlevy/chopdiff#33](https://github.com/jlevy/chopdiff/pull/33) (currently
  locked to the hard-drop flexdoc branch)
- [ ] Retarget off #25; lock keep-cydifflib flexdoc; re-run `TextUnit.words` tests
- [ ] After flexdoc is on PyPI and signoff: relock from PyPI, tag chopdiff 0.4.1

### Phase 3: kash-shell, kash-docs, kash-media

Wait on the flexdoc tag **and** the new chopdiff tag.
Do not start these PRs in this pass.

**kash-shell** ([jlevy/kash](https://github.com/jlevy/kash))

- [ ] New flexdoc and chopdiff lower bounds; relock; PR; optional `v0.4.12`

**kash-docs** ([jlevy/kash-docs](https://github.com/jlevy/kash-docs))

- [ ] From GitHub `main` at 0.2.7; same pins; relock; PR; optional 0.2.8

**kash-media** (this repo)

- [ ] Same pins; relock
- [ ] `requires-python = ">=3.13,<3.15"`; keep the 3.14 classifier (if signed off)
- [ ] Drop the stale onnxruntime 3.14-wheels comment
- [ ] README / installation: `--python 3.13` or an explicit **GIL** 3.14. State that
  `uv venv -p 3.14` / `--python 3.14` can resolve 3.14t. Do not document 3.14t as
  supported
- [ ] PR; optional `v0.4.10` after signoff

**Verify** from `/tmp` after Phase 2 tags:

- [ ] `uv tool install --force` with an explicit **GIL** 3.13 and **GIL** 3.14 succeeds
  and still includes cydifflib (only after chopdiff allows 0.4.x)
- [ ] `uvx` with the same GIL pins succeeds
- [ ] Do not expect a bare install, or `--python 3.14` that resolves 3.14t, to succeed

## Testing Strategy

**flexdoc (`main` line only)**

- `token_diffs` tests and golden docs
- Built wheel `Requires-Dist` **must list** `cydifflib`

**cydifflib (done)**

- Bench vs stdlib; keep the hard dep
- GIL 3.14 sdist build and import (~17s)
- 3.14t sdist fail (Cython 3.0.x)

**chopdiff**

- Div / transform / token-diff tests against keep-cydifflib flexdoc
- `uv tree -p flexdoc -p cydifflib` shows both

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
Do not treat a flexdoc-only publish as enough (`chopdiff 0.4.0` still selects flexdoc
0.3.0). Do not treat “no cydifflib in the tree” as success.

## Rollout Plan

Release identity is the git tag (`vX.Y.Z`). This pass updates the plan and comments; it
does not tag, fork, or merge #24/#25.

1. Keep `cydifflib>=1.2.0` (decided).
   No required fork or vendor.
2. New flexdoc PR from `main` (not #24/#25): keep the dep; widen GIL 3.14 if signed off.
   Do not merge the drop PRs.
3. User signoff, then one flexdoc tag from `main`.
4. One chopdiff pin from that PyPI version; user signoff; tag chopdiff (planned 0.4.1).
   This is the step that makes the new flexdoc visible to kash.
5. kash-shell / kash-docs / kash-media PRs the same day as the chopdiff tag.
6. Optional kash tags.
7. Smoke-test GIL 3.13 and GIL 3.14 from `/tmp`. Confirm cydifflib is in the graph.

Do not publish a kash release that requires `flexdoc>=0.4.1` before the new chopdiff is
on PyPI.

Rehearse with `make build` and inspect `Requires-Dist` (`cydifflib` must be present).

## Open Questions

- **Widen flexdoc and kash-media to GIL 3.14?** Product decision.
  Build-debug says GIL 3.14 already works with published cydifflib.
  Needs user signoff before the flexdoc PR’s `requires-python` change.
- **flexdoc 0.4.1 contents** besides keeping cydifflib: classifiers / `requires-python`
  only, or also install-doc notes.
  Needs signoff.
- **chopdiff 0.4.1 vs 0.5.0:** currently 0.4.1 from the drop-PR test run.
  Re-confirm against keep-cydifflib `main`.
- **Optional later:** fork CyDifflib so 3.14t can *install* cydifflib (not 3.14t-safe;
  not a kash-media target).
  Not this train.

Closed: dual-track 0.3.1 and 0.4.1. Closed: drop cydifflib.
Closed: vendor into flexdoc.
Closed: optional-extra as default.
Closed: must-fork for GIL 3.14.

## References

- flexdoc call site: `src/flexdoc/docs/token_diffs.py`
- chopdiff rationale: commit `0e6f81d`,
  [README.md](https://github.com/jlevy/chopdiff/blob/main/README.md)
- chopdiff pin and dated exception: `pyproject.toml`
- Published pins: PyPI `kash-media` 0.4.9, `kash-shell` 0.4.11, `kash-docs` 0.2.7,
  `chopdiff` 0.4.0, `flexdoc` 0.3.0 and 0.4.0, `cydifflib` 1.2.0
- Flexdoc PRs: [24](https://github.com/jlevy/flexdoc/pull/24) and
  [25](https://github.com/jlevy/flexdoc/pull/25) (do not merge; stdlib drop)
- Chopdiff PR: [33](https://github.com/jlevy/chopdiff/pull/33)
- Plan PR: [kash-media#13](https://github.com/jlevy/kash-media/pull/13)
- Install docs: [README.md](../../../README.md),
  [installation.md](../../installation.md), [publishing.md](../../publishing.md)
- uv interpreter selection: `uv tool install --python` / `UV_PYTHON`; `uv python find
  3.14` can be 3.14t

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
