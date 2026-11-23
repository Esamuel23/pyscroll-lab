# Journal

One entry per working day: the change, the numbers, what I learned, open questions.

## 2026-11-23: Phase 0 skeleton

- **Change:** package layout, `lab info` / `lab serve`, settings from `LAB_` env vars, `/health` (reports whether the private data folder is set and complete), tests, ruff/mypy/pytest, CI.
- **Why `/health` checks the data:** CI and fresh clones run without the private data, so "degraded" is a valid, tested state, not a crash.
- **Next:** Phase 1, starting with the `reels` table and its data contract.
- **Questions to answer in review:** how does `Depends(get_settings)` let the tests swap settings? Why is the warehouse rebuilt rather than updated in place?

## 2026-11-23: Phase 0 review, system design and architecture maps

- **Change:** first full review ([docs/reviews/2026-11-23-phase-0.md](docs/reviews/2026-11-23-phase-0.md)), 9 findings. The big one: tests read the developer's own `.env`, so a test failed on the laptop and passed in CI. Fixed with an autouse fixture that isolates every test. Settings are now cached and their paths absolute; deps pinned in `constraints.txt`; pre-commit aligned with CI.
- **Added:** `docs/SYSTEM_DESIGN.md`, `docs/ARCHITECTURE.md` (Mermaid), `tools/snapshot.py`, `metrics/HISTORY.md`.
- **Numbers:** tests 4/1 → 9/0, coverage 91.7% → 98.6%, warnings 1 → 0.
- **Learned:** "passes in CI" isn't "correct". Environment leaking into tests is a real class of bug. Measuring first (snapshot #1) is what exposed it.
- **Open:** answer the four review questions out loud before starting Phase 1.
