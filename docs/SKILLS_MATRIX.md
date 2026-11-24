# Skills matrix

**What this project is:** an end-to-end **production ML system with an LLM application layer**, built on real data. The ML engineering track (data → features → model → serving → monitoring) comes first. The AI engineering track (LLM features, RAG, evals, agents/MCP) is layered on top of it. A platform track (containers, cloud, observability) ships both.

This file is the checklist: every requirement below comes from real postings (sampled 2026-11-24, listed at the bottom). Each row names the phase where Lab gives you a real rep, and the evidence a reviewer could open. A row is ✅ only when the evidence exists and has been reviewed.

Status: ⬜ not started · 🟨 in progress · ✅ done with evidence

## ML engineering track

| Requirement (how postings say it) | Seen in | Lab phase | Evidence it's done | Status |
|---|---|---|---|---|
| Strong Python: packaging, testing, type hints | all 6 | P0 | `pyproject.toml`, mypy strict, pytest, CI | ✅ |
| Git + code review through PRs, clean history | 3 | P0 → every change | PRs with review docs linked | 🟨 (commits on main, no PRs yet) |
| SQL, pandas, messy real-world data | 3 | P1 | warehouse build + data contracts | ⬜ |
| Data pipelines: ingestion, validation, schema checks, freshness | 2 | P1 | `lab build`, contract tests, unmatched-rows report | ⬜ |
| Versioned, reproducible datasets | 2 | P1 | rebuild-from-scratch, data hash in each snapshot | ⬜ |
| NumPy / pandas / scikit-learn | 2 | P2 | features + baseline → ridge → GBM | ⬜ |
| ML fundamentals: validation, generalization, leakage | 3 | P2 | leave-one-week-out CV, leakage test | ⬜ |
| Statistics: confidence intervals, experiment design | 1 | P2, P4 | prediction intervals, "is the gain real" test | ⬜ |
| Error analysis across segments | 1 | P2 | per-format / per-platform error table | ⬜ |
| Experiment tracking + model registry (MLflow / W&B) | 3 | P2 | MLflow runs + registered model | ⬜ |
| PyTorch | 2 | P6 | small CPU model (text classifier) trained in PyTorch | ⬜ |
| Fine-tuning (LoRA/PEFT), when to fine-tune vs prompt | 2 | P6 | LoRA on a small model (Colab GPU) vs prompt baseline, same eval | ⬜ |
| Model monitoring: drift, calibration, predicted vs actual | 3 | P4 | `GET /monitor/weekly` + report | ⬜ |
| Orchestration (Airflow / Dagster / Prefect) | 1 | P4 | weekly job as a scheduled flow | ⬜ |

## AI engineering track

| Requirement | Seen in | Lab phase | Evidence | Status |
|---|---|---|---|---|
| APIs serving ML/AI (FastAPI) | 4 | P0 → P3 | `/health` now; `/reels`, `/predict`, `/hooks/*`, `/ask` | 🟨 |
| Async Python | 2 | P3 | async LLM calls with timeouts and retries | ⬜ |
| Prompt design, structured/validated output | 2 | P3 | `/hooks/rewrite` with Pydantic-validated output | ⬜ |
| Tool calling | 2 | P3 | Claude tool-use loop over warehouse queries | ⬜ |
| Embeddings + vector DB (FAISS / Chroma / Qdrant) | 3 | P2 (embeddings), P3 (vector store) | index + retrieval tests | ⬜ |
| RAG **from scratch**, then with a framework | 3 | P3 | `/ask` hand-built; LangChain or LlamaIndex version compared | ⬜ |
| IR basics: BM25, dense, reranking | 1 | P3 | hybrid retrieval vs dense-only, measured | ⬜ |
| Evals: golden set, LLM-as-judge, regression tests in CI | 4 | P3 | eval suite running in CI, judge calibrated on real holds | ⬜ |
| Eval tooling (RAGAS / DeepEval / Langfuse) | 1 | P3 | one tool wired in, compared to the hand-built evals | ⬜ |
| Guardrails, grounding (never invent numbers) | 3 | P3 | citation checker + refusal tests | ⬜ |
| MCP servers/clients | 2 | P1 (read tools), P3 | Lab MCP server used by Claude Code | ⬜ |
| Agents / multi-agent (LangGraph or similar) | 3 | P3+ | one agent workflow (e.g. weekly analyst) | ⬜ |
| Cost, latency, quality trade-offs | 3 | P3 | cost-per-call and p95 table per model | ⬜ |
| AI coding tools with a workflow you can explain | 1 | every day | this repo's review docs + journal | ✅ |

## Platform track

| Requirement | Seen in | Lab phase | Evidence | Status |
|---|---|---|---|---|
| CI/CD | 3 | P0 | GitHub Actions | ✅ |
| Docker | 4 | P5 | Dockerfile, image under a size budget, CI build | ⬜ |
| Cloud (AWS preferred: S3, EC2/ECS/Lambda) | 4 | P5 | deployed demo with synthetic data | ⬜ |
| Infrastructure as code (Terraform / CDK) | 1 | P5 | Terraform for the deploy | ⬜ |
| Logging, monitoring, observability | 3 | P5 | structured logs, request ids, latency metrics | ⬜ |
| Load testing, p50/p95 latency | (senior) | P5 | load test report per endpoint | ⬜ |
| Security: secrets, input validation, auth | 2 | P3, P5 | API key auth, no secrets in repo, scan in CI | ⬜ |
| Front end (React) for an AI feature | 2 | optional P5 | small dashboard over the API | ⬜ (optional) |

## Senior-level skills (not tools)

These are what separate a senior posting from a junior one. Every review scores them (see [REVIEW_FRAMEWORK.md](REVIEW_FRAMEWORK.md)).

- Turning a vague goal into measurable quality criteria.
- Trade-off decisions written down (cost, latency, accuracy, simplicity) — each in a decision record.
- Saying what the system *can't* do: limits, failure modes, data gaps.
- Explaining a technical decision to a non-technical reader (the deck).
- Keeping complex systems simple.

## Phases added by this matrix

The roadmap covers P0–P4. The postings ask for two things it lacked, so:
- **P5: Ship it** — Docker, AWS deploy with synthetic data, Terraform, structured logging, load tests.
- **P6: Deep ML** — PyTorch model and a LoRA fine-tune (Colab GPU; the laptop has none), each compared on the same eval as the CPU baseline.

## Postings sampled (Indeed, remote US, 2026-11-24)

- Optum, Sr AI/ML Engineer ($120–214K): FastAPI, RAG, vector DBs, MCP, agents, MLOps, cloud, Docker, CI/CD.
- Mpathic, ML Engineer, Evaluation ($150–175K): evaluation datasets, regression tests, statistics, leakage, error analysis.
- Mpathic, ML Engineer, Data Products ($150–175K): pipelines, versioned datasets, data quality checks, AWS, Terraform/CDK, orchestration.
- FindDepth, AI Software Engineer ($90–120K): RAG, agents, evals, async Python, FastAPI, IR (BM25, dense, reranking).
- Awesome Motive, AI Engineer ($77–130K): structured output, tool calling, RAG from scratch, vector DBs, evals, Docker, cloud, MLflow, LoRA, MCP.
- Capital One, Sr. Staff AI Engineer ($286–392K): cost/latency/throughput trade-offs, inference optimization, guardrails, governance (the senior ceiling).

Re-sample every phase; add rows that show up in 2+ postings.
