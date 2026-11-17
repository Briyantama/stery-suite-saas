# AI-DLC Progress: Stery Suite

Date: 2026-11-14

How to read: the Summary gives one row per repo; the Stage map shows, per repo, which AI-DLC stage has evidence on disk; Requirements and tasks holds the counts; Open blockers lists what stops a clean AI-DLC run. Paths are relative to the suite root `C:/Users/solui/moon-eye/stery-suite`. How to run the engine is in `docs/aidlc/AIDLC_Runbook_Stery_Suite.en.md`.

## Summary

All four product modules are on `go 1.27.3` and all four repos are on branch `chore/go-1.27-pg-18.6`. "Uncommitted" counts `git status --short` lines; the figure after the plus sign is this documentation task's own edits (section Doc drift fixed on 2026-11-14).

| Repo | Branch | Last commit | Uncommitted files | Intent and phase | Requirement counts | Tracker counts | Top blocker |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SELA | `chore/go-1.27-pg-18.6` | 2026-11-09 | 14 (11 + 3) | `261014-closed-beta-readiness`: Inception, human review gate Open; B0 done, B1-B2 built but unverified, B3-B5 merged (PRs #8-#10), B6 moved to B7, B7 not started, Operation not started | 66 FSD requirements: 45 Completed / 21 Partial | 105 tasks (as_of 2026-10-25): 76 Completed / 20 Pending Verification / 9 Not Started | Inception review gate Open; B7 real-device and Midtrans webhook proof pending |
| POS-Stery | `chore/go-1.27-pg-18.6` | 2026-11-09 | 23 (20 + 3) | `261108-stack-align-sela`: Construction; B1-B5 done, B6 build/test done locally, U8 CI written | 68 FSD rows: 11 Done / 32 Partial / 1 Pending Verification / 24 Not started | 22 suite-tracker tasks: 7 Completed / 3 In Progress / 5 Pending Verification / 7 Not Started | 18 open High review findings repo-wide (verdict BLOCK); the `unit_price` finding looks resolved in current code (blocker a), re-verify the rest |
| HRIS-Stery | `chore/go-1.27-pg-18.6` | 2026-11-09 | 15 (9 + 6) | `261108-stack-align-sela`: Construction; B1-B5 done, B6 build/test done locally, U8 CI written | 75 FSD rows: 1 Done / 40 Partial / 1 Pending Verification / 33 Not started | 20 suite-tracker tasks: 10 Completed / 2 In Progress / 3 Pending Verification / 5 Not Started | Same 18 High findings (HRIS: non-atomic refresh rotation, document access, leave); FSD defects not re-verified |
| stery-kit | `chore/go-1.27-pg-18.6` | 2026-11-09 | 25 (design-system work) | none (no `docs/aidlc`, no intent) | n/a (no FSD) | 1 suite-tracker task (S1.1 extract kit): Completed | No intent or requirements record; design-system changes uncommitted |
| Suite root | `master` | 2026-11-14 | 9 entries (4 product gitlinks, 3 tracker files, `.aidlc/`, `docs/aidlc/`) | engine run `aidlc-20261114051752-6a2ffc`: scope `classic` (fallback, `scopeLocked:false`), brownfield, 3 stages approved, 15 pending | 102 FR-SUI rows: 0 Done / 5 Partial / 0 Pending Verification / 97 Not started | 64 tasks: 19 Completed / 7 In Progress / 12 Pending Verification / 26 Not Started | Gitlinks without `.gitmodules`; scope still `classic` until `/aidlc scope feature` |

## Stage map

Stage order follows the engine (`.aidlc/state.json`, `order`) without the three auto-approved initialization stages (workspace-scaffold, state-init, practices-discovery) and refined-mockups; `operation` is listed because the `feature` scope includes it. Status: `Done` = artifact with evidence exists; `Partial` = evidence exists but not as a dedicated artifact or incomplete; `Missing` = nothing on disk.

### SELA

| Stage | Status | Evidence path |
| --- | --- | --- |
| workspace-detection | Done | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/01-context.md` |
| reverse-engineering | Missing | - |
| requirements-analysis | Done | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/03-requirements.md` |
| user-stories | Missing | - |
| domain-design | Done | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/04-design-impact.md` |
| units-generation | Done | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/05-units-of-work.md` |
| contract-design | Partial | `SELA/docs/FSD_Sela.md` (section 6; no contract file) |
| delivery-planning | Done | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/06-bolt-plan.md` |
| functional-design | Done | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/02-decisions.md` (D1-D9) |
| nfr-requirements | Partial | `SELA/docs/FSD_Sela.md` (no dedicated file) |
| nfr-design | Missing | - |
| infrastructure-design | Partial | `SELA/deploy`, `SELA/.github/workflows/ci.yml` |
| code-generation | Partial | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/aidlc-state.md` (B0-B5; B7 not started) |
| build-and-test | Partial | `SELA/scripts/check.sh`, `SELA/.github/workflows/ci.yml` (B1-B2 unverified) |
| operation | Missing | - |

### POS-Stery

| Stage | Status | Evidence path |
| --- | --- | --- |
| workspace-detection | Done | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/01-context.md` |
| reverse-engineering | Done | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/aidlc-state.md` (intent scout maps; no Code KB) |
| requirements-analysis | Done | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/01-context.md`, `POS-Stery/PRD.md`, `POS-Stery/docs/BRD_POS.en.md`, `POS-Stery/docs/FSD_POS.en.md` |
| user-stories | Missing | - |
| domain-design | Missing | - |
| units-generation | Done | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/05-units-of-work.md` (U1-U10) |
| contract-design | Partial | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/05-units-of-work.md` (route table; no OpenAPI) |
| delivery-planning | Done | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/06-bolt-plan.md` (B0-B6) |
| functional-design | Done | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/02-decisions.md`, `POS-Stery/docs/adr` |
| nfr-requirements | Partial | `POS-Stery/docs/FSD_POS.en.md` (NFR sections) |
| nfr-design | Missing | - |
| infrastructure-design | Partial | `POS-Stery/deploy`, `POS-Stery/apps/api/Dockerfile`, `POS-Stery/.github/workflows/ci.yml` |
| code-generation | Done | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/aidlc-state.md` (B1-B5; 18 High review findings open repo-wide, see `code-review-2026-11-08.md`) |
| build-and-test | Partial | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/aidlc-state.md` (B6 done locally; evidence only in the state file) |
| operation | Missing | - |

### HRIS-Stery

| Stage | Status | Evidence path |
| --- | --- | --- |
| workspace-detection | Done | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/01-context.md` |
| reverse-engineering | Done | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/aidlc-state.md` (intent scout maps; no Code KB) |
| requirements-analysis | Done | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/01-context.md`, `HRIS-Stery/docs/BRD_HRIS.en.md`, `HRIS-Stery/docs/PRD_HRIS.en.md`, `HRIS-Stery/docs/FSD_HRIS.en.md` |
| user-stories | Missing | - |
| domain-design | Partial | `HRIS-Stery/docs/adr/0005-single-module-go-api-on-sela-stack.md`, `HRIS-Stery/docs/adr/0006-dragonfly-streams-replace-nats-jetstream.md` |
| units-generation | Done | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/05-units-of-work.md` (U1-U10) |
| contract-design | Partial | `HRIS-Stery/docs/FSD_HRIS.en.md` (RPC table; proto removed) |
| delivery-planning | Done | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/06-bolt-plan.md` (B0-B6) |
| functional-design | Done | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/02-decisions.md`, `HRIS-Stery/docs/adr` |
| nfr-requirements | Partial | `HRIS-Stery/docs/FSD_HRIS.en.md` (NFR sections) |
| nfr-design | Missing | - |
| infrastructure-design | Partial | `HRIS-Stery/deploy`, `HRIS-Stery/apps/api/Dockerfile`, `HRIS-Stery/.github/workflows/ci.yml` |
| code-generation | Done | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/aidlc-state.md` (B1-B5; 18 High review findings open repo-wide) |
| build-and-test | Partial | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/aidlc-state.md` (B6 done locally; evidence only in the state file) |
| operation | Partial | `HRIS-Stery/docs/deployment/production.md`, `HRIS-Stery/.github/workflows/cd-staging.yml` |

### stery-kit

No intent and no `docs/aidlc`. Requirements and design evidence is limited to the tracker task S1.1 (`docs/tracking/tracker.json`), `stery-kit/DESIGN.md` and `stery-kit/PRODUCT.md`.

| Stage | Status | Evidence path |
| --- | --- | --- |
| workspace-detection | Missing | - |
| reverse-engineering | Missing | - |
| requirements-analysis | Partial | `docs/tracking/tracker.json` (KIT task S1.1), `stery-kit/PRODUCT.md` |
| user-stories | Missing | - |
| domain-design | Missing | - |
| units-generation | Missing | - |
| contract-design | Missing | - |
| delivery-planning | Missing | - |
| functional-design | Partial | `stery-kit/DESIGN.md` |
| nfr-requirements | Missing | - |
| nfr-design | Missing | - |
| infrastructure-design | Missing | - |
| code-generation | Missing | - |
| build-and-test | Missing | - |
| operation | Missing | - |

### Suite

| Stage | Status | Evidence path |
| --- | --- | --- |
| workspace-detection | Done | `.aidlc/state.json` |
| reverse-engineering | Missing | - |
| requirements-analysis | Done | `docs/BRD_Stery_Suite.en.md`, `docs/PRD_Stery_Suite.en.md`, `docs/FSD_Stery_Suite.en.md` |
| user-stories | Missing | - |
| domain-design | Partial | `docs/00_Analisis_Dampak_Risiko.en.md` |
| units-generation | Partial | `docs/tracking/tracker.json` (milestones S0-S5) |
| contract-design | Missing | - |
| delivery-planning | Partial | `docs/00_Analisis_Dampak_Risiko.en.md` (section 7) |
| functional-design | Missing | - |
| nfr-requirements | Missing | - |
| nfr-design | Missing | - |
| infrastructure-design | Missing | - |
| code-generation | Missing | - |
| build-and-test | Missing | - |
| operation | Missing | - |

## Requirements and tasks

Recomputed on 2026-11-14. FSD tallies count the first Status cell of each unique `FR-` row in the English FSD; `python scripts/build_tracker.py --check` passes (64 tasks, 315 requirements).

### FSD requirement rows

| FSD | Rows | Done | Partial | Pending Verification | Not started | Deferred |
| --- | --- | --- | --- | --- | --- | --- |
| Suite (`docs/FSD_Stery_Suite.en.md`, FR-SUI) | 102 | 0 | 5 | 0 | 97 | 0 |
| POS (`POS-Stery/docs/FSD_POS.en.md`) | 68 | 11 | 32 | 1 | 24 | 0 |
| HRIS (`HRIS-Stery/docs/FSD_HRIS.en.md`) | 75 | 1 | 40 | 1 | 33 | 0 |

POS moved from 30 Partial / 26 Not started to 32 / 24 on 2026-11-14: FR-POS-04.4 and FR-POS-SEC.6 are now Partial, matching the `requirement_overrides` in `docs/tracking/tracker.json`. SELA requirements live in `SELA/docs/tracking/tracker.json` (66 rows: 45 Completed / 21 Partial).

### Suite tracker tasks per milestone (`docs/tracking/tracker.json`, 64 tasks)

| Milestone | Tasks | Completed | In Progress | Pending Verification | Not Started |
| --- | --- | --- | --- | --- | --- |
| S0 | 6 | 1 | 2 | 3 | 0 |
| S1 | 5 | 1 | 0 | 1 | 3 |
| S2 | 21 | 7 | 3 | 5 | 6 |
| S3 | 19 | 10 | 2 | 3 | 4 |
| S4 | 9 | 0 | 0 | 0 | 9 |
| S5 | 4 | 0 | 0 | 0 | 4 |
| Total | 64 | 19 | 7 | 12 | 26 |

### SELA tracker tasks (`SELA/docs/tracking/tracker.json`, as_of 2026-10-25)

| Scope | Tasks | Completed | Pending Verification | Not Started |
|---|---|---|---|---|
| All milestones M1-M8 and BL | 105 | 76 | 20 | 9 |

## Open blockers

| # | Blocker | Evidence |
| --- | --- | --- |
| a | Local code review verdict is BLOCK with 18 High findings open. Examples: HRIS refresh rotation is a non-atomic `Exists` then `Del`; POS sale trusts client `unit_price` and discounts; POS stock can go negative; POS supplier `receive_stock` double counts; POS customer loyalty points can be minted by a cashier; POS `category_id` can point to another tenant. Note: the POS FSD (as updated 2026-11-14) records server-side unit price as present in `POS-Stery/apps/api/services/sales/infrastructure/price_port.go`, so re-verify that finding first | `code-review-2026-11-08.md` |
| b | SELA inception human review gate is still Open; real-device and Midtrans webhook tests are pending (B7); T7.2 needs at least 3 rows in `SELA/docs/tracking/usability_sessions.csv` | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/aidlc-state.md`, `SELA/docs/tracking/usability_sessions.csv` |
| c | POS secrets (FR-POS-SEC.6, Partial): `POS-Stery/ecosystem.config.cjs` now reads secrets from `.env`; the old `deploy/docker/init-postgres.sql` and `scripts/migrate-helper.sh` no longer exist. Still open: git history was not rewritten and rotation of the old values is not evidenced (tracker task S2.5, In Progress) | `POS-Stery/ecosystem.config.cjs`, `docs/tracking/tracker.json` |
| d | Defects cited by the HRIS FSD sections 3-4 (pre-consolidation text; about 250 old-layout evidence paths were not re-verified on 2026-11-14): attendance migration `UNIQUE ... WHERE` syntax, RLS without FORCE on attendance, leave and notification, `hris_app` lacks INSERT on `auth.tenants`, CI integration job connects as `hris_admin` | `HRIS-Stery/docs/FSD_HRIS.en.md` |
| e | A1-A8 in the POS and HRIS intent decisions are "Assumed" (status Open), not owner-confirmed | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/02-decisions.md`, `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/02-decisions.md` |
| f | Four repos carry uncommitted design-system changes (SELA 11, POS-Stery 20, HRIS-Stery 9, stery-kit 25 files before this task's edits) | `git -C <repo> status --short` |
| g | Gitlink gap: in the pushed suite commit (`Briyantama/stery-suite-saas`) `HRIS-Stery`, `POS-Stery`, `SELA`, `stery-kit` are gitlinks (mode 160000) with no `.gitmodules`, so a fresh clone gets four empty folders. An untracked, empty stray folder `stery-suite/` (containing `HRIS-Stery/`) sits in the suite root. Decision C9 is in the Runbook; nothing was changed | `docs/aidlc/AIDLC_Runbook_Stery_Suite.en.md` |

## Doc drift fixed on 2026-11-14

| File | Change |
| --- | --- |
| `POS-Stery/CLAUDE.md` | `Go 1.25.1` to `Go 1.27.3` |
| `POS-Stery/docs/FSD_POS.en.md`, `POS-Stery/docs/FSD_POS.id.md` | Status note under the title; about 180 as-is evidence paths and the as-is prose for gRPC, NATS, gateway, client-trusted price and PO receive rewritten to the current single-module code (`apps/api/services/<x>/`, `cmd/api/{main,routes}.go`, `stery-kit/go/*`); removed components point to ADR-0001/0002; target-state text untouched; FR-POS-04.4 and FR-POS-SEC.6 set to Partial (server-side unit price and negative-total rejection exist; no role-limited discount, D-POS-07 still `tbd`); EN and ID parity (12 `##` headings, 486 table rows each) |
| `HRIS-Stery/CLAUDE.md` | `Go 1.25.1` to `Go 1.27.3` |
| `HRIS-Stery/docs/PHASE5_SUMMARY.md`, `PHASE5_DEEP_CODE_REVIEW.md`, `PHASE5_ARCHITECTURE_REVIEW.md` | `Superseded (2026-11-14)` banner prepended; bodies untouched |
| `HRIS-Stery/docs/FSD_HRIS.en.md`, `HRIS-Stery/docs/FSD_HRIS.id.md` | Status note and a path-mapping sentence under the evidence convention; sections 2.2-2.5 and rows FR-HRS-01.2, FR-HRS-SEC.6, NFR-HRS-08, `/login` reconciled with ADR-0005/0006; defects "web login is a mock", "No HTTP mux is mounted" and "gateway client does not pass the token" marked resolved (login now posts to `/api/v1/auth/login` and writes the `hris_session` cookie); FR-HRS-01.2 stays Partial (JWT, not opaque session); English legend normalised to `Done / Partial / Not started / Pending Verification / Deferred`; the Indonesian FSD gained the "Implementation status 2026-11-08" block it lacked |
| `SELA/CLAUDE.md` | FSD version `v2.21` to `v2.55` (BRD and PRD stay v2.5); `min Go 1.25.1` to `Go 1.27.3` |
| `SELA/AGENTS.md` | `Go >= 1.25.1` to `Go 1.27.3` |
| `SELA/docs/aidlc/intents/261014-closed-beta-readiness/aidlc-state.md` | Basis row: `FSD v2.39` to `FSD v2.55`, tracker `as_of 2026-10-25` |
| `docs/tracking/README.md` | "no commits yet" line replaced with the current repo statement; heading sentence points to `SELA/docs/tracking/README.md` and states the SELA rollup reads `SELA/docs/tracking/tracker.json` live |
| `docs/tracking/Stery_Suite_Progress_Tracker.xlsx`, `docs/tracking/traceability.csv` | Regenerated by `python scripts/build_tracker.py`; `tracker.json` unchanged (the FR-POS-04.4 override already equals the FSD value) |

Drift deliberately left:

- `docs/tracking/tracker.json` and `SELA/docs/tracking/tracker.json`: rows about gitignored docs are historical task text.
- HRIS FSD sections 3-4 and the traceability tables: about 250 old-layout evidence paths (`services/<x>-service/...`, `apps/api-gateway/...`) are marked as history by the path-mapping sentence, not rewritten.
- `HRIS-Stery/docs/FSD_HRIS.id.md`: legend and rows keep the Indonesian status words (`Selesai / Sebagian / Belum / Ditunda`, English equivalents in parentheses); `scripts/build_tracker.py` reads only the `.en.md` files.
- `Go >= 1.25.1` in the target STACK-SPEC row of the HRIS FSD (target-state row).
- POS FSD section 2.7 (as-is to to-be delta) and row K17 still name `services/api-gateway` and `X-Service-Token` on purpose, as the old side of the delta.
