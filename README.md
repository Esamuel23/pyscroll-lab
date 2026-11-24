# PyScroll Lab

A small, real, production-style ML system built on the data of a live short-form coding channel (PyScroll), grown one reviewed change at a time.

The channel posts 35 short Python videos a week. Each one has a script, a hook, render QA results and platform metrics (3-second hold, average watch time, views, saves). Lab turns that into:

- a **warehouse** that rebuilds from the raw files,
- a **hold predictor**: which hooks keep viewers past 3 seconds, and how sure we are,
- an **LLM layer**: score and rewrite hooks, answer questions with citations, with an eval suite that runs in CI,
- an **API** (FastAPI) and an **MCP server** so an AI pair programmer can query it directly,
- **weekly monitoring**: predicted vs actual on last week's posts, then retrain.

The channel's raw data is private and is never committed. The code reads it from `LAB_DATA_ROOT`.

## Status

Phase 0: skeleton, CI and a `/health` endpoint, reviewed.

- [System design](docs/SYSTEM_DESIGN.md): context, requirements, qualities, key decisions
- [Architecture](docs/ARCHITECTURE.md): layers, what exists now, request flow, repo map
- [Skills matrix](docs/SKILLS_MATRIX.md): ML / AI engineer job requirements → the phase that covers each, with evidence
- [Review framework](docs/REVIEW_FRAMEWORK.md): severity levels, 10 scored dimensions, sprint and phase reviews
- [Reviews](docs/reviews/): one file per reviewed change, with findings and decisions
- [Metrics history](metrics/HISTORY.md): a snapshot after every change (`python tools/snapshot.py "label"`)
- [ROADMAP.md](ROADMAP.md) for the plan, [JOURNAL.md](JOURNAL.md) for the daily log

## The loop

Code one small change → review it (`docs/reviews/`) → fix → `python tools/snapshot.py "<label>"` → commit → CI. Every phase also updates the architecture doc.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env              # set LAB_DATA_ROOT to the data folder
lab info                          # checks the data paths
lab serve                         # http://127.0.0.1:8077/health and /docs
pytest && ruff check . && mypy    # what CI runs
```

## Constraints, on purpose

- **Runs on a laptop with no CUDA GPU.** Models must train on CPU in minutes (scikit-learn, gradient boosting, small sentence embeddings). Large-model work goes through an API.
- **Small data.** About 60 labelled posts per platform to start, plus 35 a week. That means honest evaluation, time-aware cross-validation and intervals, not leaderboard scores.

## License

MIT
