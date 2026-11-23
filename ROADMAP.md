# Roadmap

Each phase ends with something running that can be called. Work lands as one small, tested change per day, reviewed in full (see "Review routine").

## Phase 0: Skeleton ✅ in progress
- Package (`src/pyscroll_lab`), `lab` CLI, settings from env, `/health`.
- ruff, mypy (strict), pytest, pre-commit, GitHub Actions CI.

## Phase 1: Warehouse and read API
- DuckDB tables built from the raw files: `reels`, `rows` (script lines), `posts` (reel × platform × date), `metrics`, `qa_events`.
- Data contracts (types, ranges, uniqueness); `lab build` is idempotent and rebuilds from scratch.
- A tested matcher joining platform exports to reels, with an explicit report of unmatched rows.
- Endpoints: `GET /reels`, `GET /reels/{id}`, `GET /metrics/summary`, `POST /ingest/metrics`.
- MCP server exposing the same reads as tools.

## Phase 2: Features and the hold predictor
- Hook features (word count, opener type, person plus number, code words, question), format, length, slot, platform.
- Text features: TF-IDF, then small sentence embeddings on CPU, cached in the warehouse.
- Mean baseline → ridge → gradient boosting; leave-one-week-out validation; MAE plus intervals.
- MLflow (local) for runs and a model registry; `POST /predict/hold`.

## Phase 3: LLM layer
- `POST /hooks/score`: rule checks, model score and the nearest past posts with their real hold.
- `POST /hooks/rewrite`: LLM candidates (structured output) that must pass the rules, then are ranked.
- `POST /ask`: retrieval over standards, scripts and results, with citations.
- Eval suite (golden set, rule-pass rate, judge calibrated against real outcomes, cost and latency) running in CI when prompts change.

## Phase 4: Close the loop
- Weekly: ingest new metrics, compare predicted vs actual, check calibration and drift, retrain, and promote only on held-out weeks.
- `GET /monitor/weekly` plus a markdown report.

## Review routine
1. What changed and why.
2. Contracts and tests first.
3. Walk one request from endpoint to SQL or model and back.
4. What breaks it: empty inputs, missing metrics, leakage, API failures.
5. The numbers vs yesterday.
6. Explain the flow back in your own words; gaps become tomorrow's first task. Log it in `JOURNAL.md`.
