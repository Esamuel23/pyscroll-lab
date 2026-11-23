# Journal

One entry per working day: the change, the numbers, what I learned, open questions.

## 2026-11-23: Phase 0 skeleton

- **Change:** package layout, `lab info` / `lab serve`, settings from `LAB_` env vars, `/health` (reports whether the private data folder is set and complete), tests, ruff/mypy/pytest, CI.
- **Why `/health` checks the data:** CI and fresh clones run without the private data, so "degraded" is a valid, tested state, not a crash.
- **Next:** Phase 1, starting with the `reels` table and its data contract.
- **Questions to answer in review:** how does `Depends(get_settings)` let the tests swap settings? Why is the warehouse rebuilt rather than updated in place?
