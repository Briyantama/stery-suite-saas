# AI-DLC Runbook: Stery Suite

Date: 2026-11-14

How to read: follow the sections top to bottom the first time; afterwards use "Commands, in order" and "Pre-answered confirmations" as a checklist. Current state per repo is in `docs/aidlc/AIDLC_Progress_Stery_Suite.en.md`.

## Prerequisites

| # | Check | Command (from the suite root `C:/Users/solui/moon-eye/stery-suite`) | Expected |
|---|---|---|---|
| 1 | Engine extension present | `ls ~/.omp/agent/extensions/aidlc-workflow.ts` | file exists |
| 2 | Clean tree per repo | `git -C SELA status --short`, same for `POS-Stery`, `HRIS-Stery`, `stery-kit` | empty; commit or stash the uncommitted design-system work first (counts are in the Progress doc, section Summary) |
| 3 | Quality gate green per product repo | `bash scripts/check.sh` inside `SELA/`, `POS-Stery/`, `HRIS-Stery/` | exit 0; needs `TEST_DATABASE_URL` and `TEST_REDIS_ADDR` |
| 4 | stery-kit pushed | `git -C stery-kit ls-remote origin` | non-empty (product CI checks the kit out) |
| 5 | Tracker builds | `python scripts/build_tracker.py --check` | exit 0 |

Engine facts (source: `~/.omp/agent/extensions/aidlc-engine/README.md`):

- Commands: `/aidlc start <task> [--scope X] [--run]`, `status`, `next`, `approve [note] [--hold]`, `reject <feedback>`, `resume`, `report`, `scope <name>`, `skip`, `help`.
- State lives in `<project>/.aidlc/`: `state.json`, `audit.jsonl` (hash chain), `attest/*.json`, `records/<phase>/<stage>/*.md`, `report.md`.
- A stage completes only when its artifacts exist, are at least 60 bytes, contain a `##` heading and contain no placeholders.
- Guards only act when `<cwd>/.aidlc` exists.

## Run topology

Two levels. Do not mix them in one session.

| Level | Start `omp` in | Use for | State folder |
|---|---|---|---|
| Suite | suite root | cross-repo intents: platform work, milestones S4-S5, FR-SUI requirements | `.aidlc/` (exists; id `aidlc-20261114051752-6a2ffc`, scope `classic`, 3 stages approved, 15 pending) |
| Product | `SELA/`, `POS-Stery/` or `HRIS-Stery/` | per-product FRs and Bolts | `<repo>/.aidlc/`, created by the first `/aidlc start` in that folder |

Rules:

- The hand-made intents under `<repo>/docs/aidlc/intents/` stay as the human-readable record. Engine records go to `.aidlc/records/`. Do not copy content between them: the engine's requirements-analysis record links to the intent folder.
- stery-kit has no intent. Cross-repo kit work runs at suite level; kit-only work may start `omp` in `stery-kit/` (a `.aidlc/` is created there).
- Add `.aidlc/` to the relevant `.gitignore` before the first commit if the records should stay local. At scan time the suite-root `.aidlc/` is untracked.

## Commands, in order

1. `omp` in the chosen folder. `/aidlc status`: at suite level it shows scope `classic`, 3 approved and 15 pending stages.
2. `/aidlc scope feature` (scope is not locked at suite level, `scopeLocked:false`). The `feature` scope marks all 33 stages EXECUTE (`~/.omp/agent/skills/aidlc-upstream/scopes/aidlc-feature.md`), so the pending list grows; run `/aidlc status` again and read the new list before continuing. Product-level runs: `/aidlc start "<task>" --scope feature`.
3. `/aidlc next`: runs the next pending stage. Answer each gate (see the table below).
4. Read the stage artifact under `.aidlc/records/<phase>/<stage>/`. Evidence paths must be listed.
5. `/aidlc approve [note]` when satisfied; `/aidlc reject <feedback>` to send the stage back for revision.
6. `/aidlc resume` after an interrupted turn (stage shows `interrupted`).
7. `/aidlc report` writes `.aidlc/report.md` when you want a summary.

Only the human can run `/aidlc approve`; the model cannot. Approval is refused with `STALE_ARTIFACTS` if gated artifacts changed after attestation. Rerun the stage to re-attest, then approve.

## Stage-by-stage entry points

Taken from the Progress doc stage maps.

| Target | Start the run at | Then |
|---|---|---|
| SELA | Close the inception human review gate (intent `261014-closed-beta-readiness`, gate Open); record decisions in the engine's requirements-analysis record | Verify B1-B2 (built, unverified), then B7: real-device test, Midtrans webhook proof, T7.2 needs at least 3 rows in `SELA/docs/tracking/usability_sessions.csv` |
| POS-Stery | build-and-test: re-verify B6 locally and re-run `bash scripts/check.sh` | Work the 18 open High findings in `code-review-2026-11-08.md`; then fill user-stories and domain-design gaps; then contract-design (OpenAPI) |
| HRIS-Stery | build-and-test: re-verify B6 locally and re-run `bash scripts/check.sh` | Work the open High findings and the FSD-cited defects; then user-stories gap; then contract-design (RPC table is in the FSD, proto removed) |
| stery-kit | requirements-analysis and contract-design for KIT tasks (tracker S1.1 is the only KIT task) | Use the full-rescan reverse-engineering result as the basis; then build-and-test with the kit command (C3) |
| Suite | units-generation and delivery-planning for milestones S4-S5 | Link to `docs/00_Analisis_Dampak_Risiko.en.md` section 7 and the tracker milestones instead of rewriting them |

## Pre-answered confirmations

Defaults proposed in advance. Override any of them by answering differently at the gate.

| Gate | Where it appears | Default answer | Why |
|---|---|---|---|
| C1 Stage approval | Every stage end, `/aidlc approve` | Approve only when the artifact lists evidence paths; otherwise `/aidlc reject` | Artifact quality is checked structurally only, not semantically |
| C2 Code KB reuse or rescan | reverse-engineering, per repo | `Focused scan` for POS-Stery, HRIS-Stery, SELA; `Full rescan` for stery-kit | Intent scout maps exist for the three products but no Code KB; the kit has no map |
| C3 Verification command per Unit | build-and-test and each Bolt | SELA, POS-Stery, HRIS-Stery: `bash scripts/check.sh` (needs `TEST_DATABASE_URL`, `TEST_REDIS_ADDR`; narrow with `CHECK_STAGES=go` or `CHECK_STAGES=web`). stery-kit: `cd go && go build ./... && go vet ./... && go test ./... && cd ../web && npm run check && npm run test:unit`. Suite root: `python scripts/build_tracker.py --check` | Same gate the repos already use in CI |
| C4 Autonomy in construction | construction start | Stop after each Bolt for review. No merge, no push, no real credentials. Always ask before destructive migrations, pricing changes, production keys | Repos' rule: AI proposes, human decides |
| C5 Bolt failure | construction | Stop and ask; work on a throwaway branch, not `main` | Keeps the four repos' history clean |
| C6 Build failure | build-and-test | Accept the proposed loop-back, maximum 3 per stage | Bounded retries |
| C7 Plan approval before code-generation writes (`plan_approval`) | code-generation plan step | Keep on | Engine blocks writes outside `.aidlc/` until the plan is approved |
| C8 Scope | `/aidlc scope` | `feature` at suite level; product-level runs use `feature` too | Full lifecycle at practical depth |
| C9 Repo layout | suite repo | Recommended: add `.gitmodules` for `HRIS-Stery`, `POS-Stery`, `SELA`, `stery-kit` (URLs `git@github.com:Briyantama/<repo>.git`; SELA's current origin is `https://github.com/Briyantama/SELA.git`) and delete the empty stray `stery-suite/` folder in the suite root | The pushed suite commit stores the four repos as gitlinks (mode 160000) with no `.gitmodules`: a fresh clone gets four empty folders. This changes the repo, so it needs your explicit yes and is NOT done by this documentation task |

## Troubleshooting

| Symptom | Action |
|---|---|
| Stage stuck `interrupted` | `/aidlc resume` (or `/aidlc next`) reruns it |
| Artifact rejected for size, missing `##` heading or placeholder | Fix the record file under `.aidlc/records/`, then rerun the stage |
| `STALE_ARTIFACTS` on approve | Gated artifacts changed after attestation; rerun the stage to re-attest, then approve |
| Workflow frozen, audit-chain or state-digest mismatch | Do not hand-edit `.aidlc/state.json`. Restore `.aidlc/` from backup, or delete `<project>/.aidlc/` and restart (engine README, rollback) |
| Engine misbehaves everywhere | Disable with `omp --no-extensions`, or rename `aidlc-workflow.ts` |
| Port 8080 already in use on the dev box | An unrelated Apache holds it. e2e uses 8081, 9091, 5174, 5175, 2525, 2526 |
| `go test -race` fails or is skipped | `-race` needs cgo/gcc, absent on the Windows dev box; `scripts/check.sh` skips it, CI runs it |
| `omp -p` stops after one turn | Print mode ends when the command returns; chained stages need the TUI or RPC mode |
