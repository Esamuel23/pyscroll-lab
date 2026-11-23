# Architecture

The inside view: packages, how a request moves through them, and what exists today. Updated every phase. For the outside view see [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md).

## 1. Target layers (end of Phase 4)

Each layer may only import from the layers below it. Grey boxes are not built yet.

```mermaid
flowchart TB
  subgraph interface[Interface]
    cli[cli.py<br/>lab info · serve · build]
    api[api.py<br/>FastAPI routes]
    mcp[mcp/<br/>tools wrapping the API]:::todo
  end
  subgraph service[Services]
    reels_s[reels / metrics queries]:::todo
    predict_s[predict]:::todo
    hooks_s[hooks: score · rewrite]:::todo
    ask_s[ask: retrieval + answer]:::todo
    evals_s[evals]:::todo
  end
  subgraph core[Core]
    ingest[ingest/<br/>parse + validate raw files]:::todo
    wh[warehouse/<br/>DuckDB schema + queries]:::todo
    feats[features/]:::todo
    models[models/<br/>train · registry · load]:::todo
    llm[llm/<br/>client · prompts · cost log]:::todo
  end
  config[config.py<br/>Settings, LAB_ env, .env]

  cli --> api
  mcp --> api
  api --> service
  cli --> service
  service --> core
  interface --> config
  service --> config
  core --> config

  classDef todo fill:#eee,stroke:#999,color:#777,stroke-dasharray:4 3
```

## 2. What exists now (Phase 0)

```mermaid
flowchart LR
  user([you]) -->|lab info| cli[cli.py<br/>main → cmd_info]
  user -->|lab serve| cli2[cli.py<br/>cmd_serve → uvicorn]
  cli2 --> app[api.py<br/>app = FastAPI]
  client([HTTP client]) -->|GET /health| app
  cli --> gs[config.get_settings]
  app -->|Depends| gs
  gs --> S[Settings<br/>data_root · warehouse_path]
  S -->|data_sources / missing_sources| fs[(LAB_DATA_ROOT<br/>reels · analytics · QA_LEDGER · STANDARDS)]
  S -->|exists?| whf[(data/warehouse.duckdb)]
```

| Module | Responsibility | Depends on |
|---|---|---|
| `config.py` | Load settings; list the expected data sources; report missing ones | pydantic-settings |
| `api.py` | HTTP app; `GET /health` returns `ok` or `degraded` with details | config, FastAPI |
| `cli.py` | `lab info` (diagnostics, exit 1 if data is missing) and `lab serve` | config, uvicorn |
| `tests/` | Health states (no data, complete, missing source); CLI exit codes | pytest, TestClient |
| `tools/snapshot.py` | Metrics snapshot after each reviewed change | pytest-cov, radon, ruff, mypy |

## 3. Request flow: `GET /health`

```mermaid
sequenceDiagram
  participant C as Client
  participant U as uvicorn
  participant F as FastAPI app
  participant G as get_settings()
  participant S as Settings
  participant FS as Filesystem
  C->>U: GET /health
  U->>F: ASGI request
  F->>G: resolve Depends(get_settings)
  G->>S: Settings() reads LAB_* env, then .env
  F->>S: missing_sources()
  S->>FS: exists() on 4 source paths
  F->>FS: warehouse_path.exists()
  F-->>U: Health(status, version, data_root_set, missing_sources, warehouse_built)
  U-->>C: 200 JSON
```

## 4. Repository map

```
pyscroll-lab/
├─ src/pyscroll_lab/     the package (config, api, cli; later ingest, warehouse, features, models, llm, mcp)
├─ tests/                one test file per module
├─ tools/snapshot.py     metrics snapshot → metrics/snapshots/*.json + metrics/HISTORY.md
├─ metrics/              committed snapshot history (engineering metrics now, model metrics later)
├─ docs/                 SYSTEM_DESIGN, ARCHITECTURE, reviews/<date>-<topic>.md
├─ .github/workflows/    CI: ruff, format, mypy (strict), pytest
├─ ROADMAP.md · JOURNAL.md · README.md
└─ data/                 (gitignored) warehouse and derived files
```

## 5. Rules that keep it reviewable

- Interface code (`cli`, `api`, `mcp`) holds no business logic: it parses input, calls a service and formats output.
- All configuration goes through `get_settings()`, so there's one seam for tests.
- Every endpoint has a Pydantic request/response model, and those are the contract.
- Every change ships with tests and a snapshot row; every phase updates this file.
