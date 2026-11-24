# Review framework

The same review every time, held to a senior bar. Three levels, each with a fixed template:

| Level | When | Scope | Output |
|---|---|---|---|
| **Change review** | every change (`P<phase>-<nn>`) | one diff | `docs/reviews/<date>-P<phase>-<nn>-<slug>.md` + snapshot |
| **Sprint review** | end of each week | everything merged that week | `docs/sprints/S<nn>.md` + new slides in the deck |
| **Phase review** | end of each phase | the whole system | `docs/reviews/<date>-P<phase>-phase.md` + deep-dive slides |

Naming: one id per change (`P1-03`) used in the review file, the snapshot label, the commit subject and the journal heading.

## IDE snapshots (VS Code)

Every review shows the code the way it looks in the editor, not just as `file:line` text. The IDE is **VS Code**, opened on this folder. It has a `code -g file:line` command that jumps any window to a line, and the workspace look is fixed in `.vscode/settings.json` (Dark Modern, 16 px, no minimap, ruler at 100), so every snapshot matches. PyCharm works for reading, but snapshots come from VS Code.

**Keep VS Code open on `pyscroll-lab` during a review.** Claude drives it:

| When | What Claude does | File |
|---|---|---|
| You blind-review | Nothing in the editor. You open the diff yourself | |
| Walkthrough | Opens each hop of the traced request in order, in your window | `docs/snapshots/<id>/00-trace-<n>.png` |
| Each finding | Opens the line, snapshots it **before** the fix | `docs/snapshots/<id>/<nn>-before.png` |
| After the fix | Same file and line, snapshotted again | `docs/snapshots/<id>/<nn>-after.png` |
| Sprint review | The best before/after pair goes on the deck's finding slide | |

```powershell
powershell -ExecutionPolicy Bypass -File tools/ide_snap.ps1 -File src/pyscroll_lab/config.py -Line 20 -Id P1-01 -Name 01-before
```

Rules:
- **Public repo:** never snapshot `.env*` (except `.env.example`), anything under `data/`, or a terminal showing paths or numbers from channel data. The script refuses `.env` and `data/` paths. Close the bottom panel before a snapshot.
- Findings in the review file link their snapshots: `![01 before](../snapshots/P1-01/01-before.png)`.
- The window must be visible on screen. The script brings it to the front, but anything drawn on top of it (a notification, another window) ends up in the image. Check each PNG before committing.

---

## 1. Change review

### Severity (every finding gets one)

| Level | Meaning | Rule |
|---|---|---|
| **S1 blocker** | wrong results, data loss, security hole, leakage, CI red | fix before merge |
| **S2 major** | will break under realistic use, missing test for a branch that matters, design that blocks the next phase | fix before merge, or a dated issue |
| **S3 minor** | works, but harder to read, change or operate than it should be | fix in this change if < 15 min, else issue |
| **S4 nit** | style, naming | optional |

### The 10 dimensions (score each 0–3)

0 = missing · 1 = junior (works on the happy path) · 2 = mid (handles realistic cases, tested) · 3 = senior (handles failure, measured, explained, simple)

| # | Dimension | Senior bar (what a 3 looks like) |
|---|---|---|
| 1 | **Problem & scope** | The change states the goal as a measurable criterion, and the diff does only that. |
| 2 | **Correctness** | Edge cases named and tested: empty, missing, duplicate, out of range, wrong type. No silent fallbacks. |
| 3 | **Design** | Each module has one job; dependencies point one way (api → services → data); no premature abstraction; a decision record for any trade-off. |
| 4 | **Tests** | Tests prove behaviour, not lines. Every branch that matters is covered; tests are isolated (no env, network or clock leaks); a failing test was seen to fail. |
| 5 | **Data & ML rigor** *(when data/models change)* | Contracts on inputs; no leakage (time-aware splits); baseline compared; uncertainty reported; error analysis by segment. |
| 6 | **AI rigor** *(when LLM code changes)* | Structured, validated output; prompt versioned; eval run before vs after; grounding/citations checked; cost and latency recorded; failure path (timeout, refusal, bad JSON) tested. |
| 7 | **Performance** | Big-O of the hot path stated; measured, not guessed (p50/p95 latency, memory, build time) against a budget; no N+1 queries or per-request reloads. |
| 8 | **Reliability & ops** | Errors are specific and logged with context; retries/timeouts on every external call; health reflects reality; idempotent jobs. |
| 9 | **Security** | No secrets in code or logs; inputs validated at the boundary; least privilege; private data never leaves `LAB_DATA_ROOT`. |
| 10 | **Readability & docs** | A newcomer can follow the flow; names say what, comments say why; ARCHITECTURE/README updated if the shape changed. |

**Pass bar:** no S1/S2 open, no dimension below 2, average ≥ 2.3. The average is tracked in the snapshot history; it should trend up.

### Template (copy for every change)

```markdown
# Review: P<phase>-<nn> <title> (<date>)

**Goal (measurable):**
**Scope:** commit(s) · files
**Baseline:** snapshot #<n>

## Walkthrough
One request or job traced from entry point to data/model and back.

## Findings
| # | Sev | Dimension | Where (file:line) | Finding | Decision | Snapshot (before → after) |

## Scores
| Dimension | Score | Why |
(1–10; mark N/A for 5/6 when not touched)

## Performance
| Measure | Before | After | Budget |

## Questions for you (answer out loud before moving on)
1. Why … (mechanism)
2. What breaks if … (failure)
3. What's the trade-off in … (decision)
4. Trace … (flow)

## After the fixes
Snapshot #<n> vs #<n+1>. Pass bar met: yes/no.
```

The four questions are always one of each kind: **mechanism, failure, trade-off, trace.**

---

## 2. Sprint review (weekly)

1. **Sprint goal vs result:** what was planned, what shipped, what slipped and why.
2. **Metrics:** last snapshot vs the sprint's first (tests, coverage, complexity, latency, model error, eval scores, cost per call). One chart.
3. **Demo:** call each new endpoint or run each new command live; paste the output.
4. **Skills matrix:** rows moved to 🟨 or ✅, with evidence links.
5. **Review scores:** the average score per dimension this week; the lowest dimension becomes next sprint's focus.
6. **Retro:** keep / stop / try (one each).
7. **Next sprint:** goal (one sentence, measurable) + the 3–5 changes planned.
8. **Deck:** add 3–5 slides (below).

---

## 3. Phase review (deep dive)

Everything in the sprint review, plus one section per layer, each with numbers:

| Layer | What gets revised | Measured by |
|---|---|---|
| **Algorithms** | complexity of builds, joins, feature code, retrieval; better data structures | Big-O + wall time on the full dataset |
| **Application speed** | startup, per-request work, caching | p50/p95 latency, memory |
| **API** | contract shape, errors, pagination, versioning | contract tests, OpenAPI diff |
| **Server** | workers, timeouts, concurrency, container size | load test (requests/s at p95 budget) |
| **ML** | model vs baseline, calibration, drift | MAE + interval coverage on held-out weeks |
| **AI integration** | prompt, retrieval, model choice | eval score, cost per call, p95 latency |

Ends with an architecture update and a decision record for every trade-off made.

---

## 4. The deck

One ongoing slide deck: the findings, in order, readable by someone non-technical. Updated at every sprint review.

Slides per sprint:
1. Sprint goal → result (one line each)
2. The metrics chart (snapshot history)
3. One architecture or flow diagram that changed
4. The most interesting finding (bug, leak, speedup) with before/after
5. Skills matrix progress

Each phase review adds a section divider and the layer-by-layer deep dive.
