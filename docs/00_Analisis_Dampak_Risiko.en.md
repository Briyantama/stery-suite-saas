# Impact and Risk Analysis

*Analysis of impact, risk, and architecture options for selling HRIS-Stery, POS-Stery, and SELA as Stery Suite packages*

|                         |                                                                                                                                                                  |
|-------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Document Name**       | Impact and Risk Analysis - Stery Suite                                                                                                                           |
| **Version**             | 1.0 (Draft)                                                                                                                                                      |
| **Date**                | 6 November 2026                                                                                                                                                  |
| **Prepared by**         | Product & Engineering Team                                                                                                                                       |
| **Status**              | Draft for review                                                                                                                                                 |
| **Related Documents**   | BRD_Stery_Suite, PRD_Stery_Suite, FSD_Stery_Suite, BRD_HRIS, PRD_HRIS, FSD_HRIS, BRD_POS, FSD_POS, `POS-Stery/PRD.md`, BRD/PRD/FSD Sela (v2.5 / v2.5 / v2.55)    |
| **Changes from previous** | Changes from previous: First issue                                                                                                                             |

## 1. Summary and recommendation

The owner wants to sell three products (HRIS-Stery, POS-Stery, SELA) as packages: all three, any two of three, or just one; each product can run standalone or integrated; new products can be added later. The owner has already decided three things: (1) structure = polyrepo plus a new platform repo `stery-suite`; (2) the stack, patterns, system design, and architecture of the whole suite = SELA's; (3) all new documents are available in Indonesian and English. The scope of this work is **documents only**: no source code is changed in any repo.

**Recommendation (verdict): compose, do not consolidate; SELA stack as the standard.** The three products remain three deployables with separate databases (D-SUI-01). The fourth deployable, the `stery-suite` platform, owns organisation/identity, entitlement, billing, notification hub, audit sink, and console. Shared Go code lives in `stery-suite/kit`, lifted from SELA's `internal/` packages. Each product has two modes, `STERY_MODE=standalone|suite` (D-SUI-02), so selling a single product does not change its behaviour. HRIS and POS are re-specified onto the SELA stack through the phased workstream S0-S5 (D-SUI-12); all decisions D-SUI-01 through D-SUI-12 are defined in BRD_Stery_Suite section 9.1.

Findings that drive the recommendation (details and evidence in sections 3-6):

- **No shared foundation.** None of the repos has SSO, entitlement, licensing, suite subscription/billing, or shared tables/code/events (RISK-SUI-01). SELA has no concept of tenant/organisation, does not use RLS, and has no external identity path; SELA's entitlement is the column `events.package` -> table `plans`, with no entitlement for bundles.
- **The three repos are not equal in condition.** SELA is the most mature (427 commits, 76 of 105 tasks Completed per the tracker as of 2026-10-25) but has not passed the closed-beta gate; POS has six real gRPC services but several integration defects; HRIS has defects that make the system unusable in practice (invalid attendance migration, HTTP gateway never mounted, web login still mocked).
- **Stack alignment = rewrite of the infrastructure/interface layers** of HRIS and POS (gRPC microservices + NATS + JWT + sqlc/zap/golang-migrate become one Go module + outbox + opaque session + pgx/slog/goose). The domain and application layers are kept (section 6).
- **Limited team capacity**: one alignment at a time (RISK-SUI-08), and each alignment is closed by its product's stabilisation gate (section 7).

## 2. Method and evidence

**Sources.** Static reading of the three repos and existing documents: `SELA` (branch `feat/strip-templates`, 427 commits, last commit 2026-10-26), `POS-Stery` (branch `development`, 21 commits, last 2026-06-30), `HRIS-Stery` (branch `development`, 33 commits, last 2026-06-10). Commit counts and dates were read from `git` on 6 November 2026. Principle: **code is the truth**; status documents that contradict code are recorded as "Contradiction" (section 3), not repeated as fact.

**Claim provenance.** Baseline claims from the planner are marked [V] (verified by the planner) or [S] (scout-reported). The author of this document re-read every cited path before asserting it. [S] claims that turned out to be wrong are corrected in section 3.4.

**Evidence rule.** Every statement about the current state carries a status from the set {Done, Partial, Not started, Pending Verification, Deferred} and a relative repo path in the `Evidence` column. Business values not found in a repo (prices, SLAs, quotas, market size, competitor data, KPI targets) are written as the literal `tbd` and become open questions (section 8). Only SELA package prices may be numbers. Estimates are marked `[INFERENCE]`. Committed secrets are referenced by path only, never by value.

**What was not run.** See Appendix B: no build, test, linter, migration, or service was run; all numbers are the result of static reading.

## 3. Progress per repo

The readiness estimates below are not measurements; all are `[INFERENCE]` and used only for sequencing work.

### 3.1 SELA

Readiness estimate toward closed beta: about 75% `[INFERENCE]` (basis: 76 of 105 tasks Completed, but 20 Pending Verification tasks include the payment path, and public serving is not yet proven).

| Area | Status | Findings | Evidence |
| --- | --- | --- | --- |
| Module structure | Done | One Go module `apps/api` (go 1.25.1); `services/{auth,event,media,payment,instant,rbac}`; `internal/{audit,piicrypt,objstore,httpx,config,db,testdb,health}`; 29 goose migrations (`0001`..`0029`) | `SELA/apps/api/go.mod`, `SELA/apps/api/services`, `SELA/apps/api/internal`, `SELA/apps/api/internal/db/migrations` |
| Transport | Done | REST `/api/v1` and gRPC for auth and event (`auth.proto`, `event.proto`) | `SELA/apps/api/api/proto/v1/auth.proto`, `SELA/apps/api/api/proto/v1/event.proto` |
| Async | Done | In-process ticker workers; DB outbox `notifications` and `instant_outbox` | `SELA/apps/api/internal/db/migrations/0008_notifications.sql`, `SELA/apps/api/internal/db/migrations/0029_instant_mode.sql`, `SELA/apps/api/services/instant/jobs.go` |
| Tracker | Partial | 105 tasks: 76 Completed, 20 Pending Verification, 9 Not Started (6 milestone markers M2.1-M7.1 and BL.1 notifications, BL.2 Hall of Fame, BL.3 instant); data as of 2026-10-25 | `SELA/docs/tracking/tracker.json` |
| Identity | Done | Email OTP and `sela_session` cookie only; no external identity/SSO path | `SELA/apps/api/services/auth/http.go`, `SELA/apps/api/services/auth/service.go` |
| Tenant / organisation | Not started | No concept of tenant, organisation, or RLS: searching `tenant` and `ROW LEVEL SECURITY` in the migrations yields no findings | `SELA/apps/api/internal/db/migrations` |
| Entitlement | Partial | Entitlement = `events.package` -> `plans`, written by the payment webhook (`UPDATE events ... FROM plans`); per-event only, no organisation or bundle entitlement | `SELA/apps/api/services/payment/postgres.go`, `SELA/apps/api/internal/db/migrations/0011_plans_transactions.sql` |
| Packages and prices | Done | `plans`: Gratis guest_cap 30 / retention 7; Hemat 80 / 30; Standar 200 / 365 (video, zip_full_resolution); Premium unlimited guests / 730; partner unlimited / never expires. Prices only in env `PLAN_PRICE_IDR_{HEMAT,STANDAR,PREMIUM}` = 39000 / 129000 / 350000 (Rp39.000 / Rp129.000 / Rp350.000; Gratis Rp0) | `SELA/.env.example`, `SELA/apps/api/internal/config/config.go`, `SELA/apps/api/internal/db/migrations/0011_plans_transactions.sql`, `SELA/apps/api/internal/db/migrations/0015_plan_retention_policy.sql` |
| `guest_cap` enforcement | Done | Corrected from the baseline: `CreateSession` accepts `guestCap` and rejects at the limit (`n >= *guestCap`) | `SELA/apps/api/services/media/postgres.go` |
| `video` enforcement | Done | Corrected from the baseline: `upload.go` rejects video with `ErrVideoNotInPlan` when the package does not include video | `SELA/apps/api/services/media/upload.go`, `SELA/apps/api/services/media/service.go` |
| `zip_full_resolution` enforcement | Not started | The flag is only read in the payment service (package list); ZIP export always streams the original object and does not read the flag | `SELA/apps/api/services/media/export.go`, `SELA/apps/api/services/payment/http.go` |
| Payment | Pending Verification | Providers `sandbox` and `midtrans` (QRIS Core API); Xendit was removed on 14 October 2026; the Midtrans webhook has never been tested with a real account over a public URL (owner sheet C3, T29.1) | `SELA/apps/api/services/payment/midtrans.go`, `SELA/apps/api/services/payment/provider.go`, `SELA/docs/verification/owner-decisions.md`, `SELA/docs/aidlc/intents/261014-closed-beta-readiness/10-lembar-jawaban-pemilik.md` |
| Retention | Partial | Conflict: owner-decisions A8 states `plans`-based retention is active in all environments, while tracker T18.3 states "Retention is opt-in" (no deletion unless `RETENTION_DAYS_*` is set); the code uses `plans.retention_days` | `SELA/docs/verification/owner-decisions.md`, `SELA/docs/tracking/tracker.json`, `SELA/CLAUDE.md` |
| Separate media origin | Pending Verification | The `MEDIA_ORIGIN_REQUIRED` configuration guard exists (FSD FR-SEC.1, v2.49) but origin separation on a real deployment is not yet proven | `SELA/docs/FSD_Sela.md`, `SELA/apps/api/internal/config/config.go` |
| Instant mode | Pending Verification | T38.1 is built (migration 0029, `services/instant`) but has status Pending Verification; T38.1 paid retention and FR-10.7 upgrade are not yet built | `SELA/docs/tracking/tracker.json`, `SELA/apps/api/services/instant/service.go` |
| Hosting | Pending Verification | The API runs on a development machine through an ngrok tunnel; not yet run end-to-end with real guests | `SELA/deploy/README.md` |
| Infrastructure | Partial | `deploy/docker-compose.yml` uses `:latest` images for Dragonfly, RustFS, aws-cli (ClamAV `stable`); PostgreSQL is not in the compose file | `SELA/deploy/docker-compose.yml` |
| Quality gate | Done | `scripts/check.sh` (stages `go web e2e`, `CHECK_STAGES`), workflow `ci.yml`; 774 Go `Test*` functions (static count); however T18.1 records that not a single full `check.sh` run has exited 0 | `SELA/scripts/check.sh`, `SELA/.github/workflows/ci.yml`, `SELA/docs/tracking/tracker.json` |

**Pending Verification tasks (20, per tracker 2026-10-25):** T11.3, T15.1, T16.1, T17.1, T18.1, T18.2, T18.3, T19.1, T19.2, T19.3, T19.4, T20.1, T23.1, T25.1, T26.1, T27.1, T28.1, T29.1, T37.1, T38.1 (evidence: `SELA/docs/tracking/tracker.json`).

**Contradictions of status documents vs code/other documents (SELA):**

| # | Contradiction | What the code / documents show | Evidence |
| --- | --- | --- | --- |
| K-1 | Owner sheet D2 mentions "56 Pending Verification tasks" | The tracker contains 20 Pending Verification tasks (76 Completed, 9 Not Started) | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/10-lembar-jawaban-pemilik.md`, `SELA/docs/tracking/tracker.json` |
| K-2 | Owner-decisions A8 (retention active) vs tracker T18.3 (retention opt-in) | The code uses `plans.retention_days`; the owner's decision has not been recorded as a single statement | `SELA/docs/verification/owner-decisions.md`, `SELA/docs/tracking/tracker.json` |
| K-3 | Stale version references in the FSD: lines 67, 1351, 1444 mention "v2.1" | The FSD is now v2.55, BRD v2.5 | `SELA/docs/FSD_Sela.md` |
| K-4 | PRD line 208 mentions "BRD v2.1"; the PRD header refers to FSD v2.54 | The FSD is now v2.55 | `SELA/docs/PRD_Sela.md` |
| K-5 | The vault note `Projects/SELA.md` still mentions Xendit | Xendit was removed on 14 October 2026; that note is outside the repo and was not re-read (reported by the planner) | `SELA/docs/verification/owner-decisions.md` |

### 3.2 POS

Readiness estimate: about 55% `[INFERENCE]` (six real gRPC services and 79 `Test*` functions, but cross-service integration and CI are not yet healthy).

| Area | Status | Findings | Evidence |
| --- | --- | --- | --- |
| gRPC services | Done | Six real services: auth, product, inventory, sales, supplier, customer; 79 `Test*` functions in 12 files (static count) | `POS-Stery/services/auth-service`, `POS-Stery/services/product-service`, `POS-Stery/services/inventory-service`, `POS-Stery/services/sales-service`, `POS-Stery/services/supplier-service`, `POS-Stery/services/customer-service` |
| HTTP gateway | Partial | The gateway is Go `chi` (not Laravel); the REST surface is a subset of proto operations: no `GetSale`, `ReceiveStock`, PO list, loyalty, threshold, auth refresh | `POS-Stery/services/api-gateway/cmd/server/main.go` |
| Loyalty | Not started | `AddLoyaltyPoints` is defined in customer-service but **has no caller** in any service | `POS-Stery/services/customer-service/internal/application/commands/add_loyalty_points.go`, `POS-Stery/services/sales-service` |
| NATS events | Not started | A shared NATS package exists (envelope, stream, JetStream) but there is no subscriber in any service; `AI.OrderForecasted` has no publisher | `POS-Stery/services/_shared/nats/streams.go`, `POS-Stery/services/_shared/nats/jetstream.go` |
| Sale flow | Partial | Synchronous saga: validate -> deduct stock (with compensation) -> save -> publish; no idempotency key; no PPN storage in the sales domain | `POS-Stery/services/sales-service/internal/application/commands/create_sale.go` |
| Admin dashboard | Partial | The payment mix is faked as 55/30/15 (cash/qris/debit) as a fallback when the API does not return `payment_mix` | `POS-Stery/apps/admin/src/routes/(app)/dashboard/+page.svelte` |
| CI | Partial | `ci.yml` is stale: Laravel gateway job, Go 1.24 although the service modules use go 1.25.0, calls `scripts/migrate-validate.sh` (file exists), pnpm-style `npm --filter` | `POS-Stery/.github/workflows/ci.yml`, `POS-Stery/scripts/migrate-validate.sh`, `POS-Stery/services/Dockerfile.base` |
| Committed secrets | Partial | Committed files contain secret values/weak credentials (values not quoted): PM2 configuration and Postgres init script | `POS-Stery/ecosystem.config.cjs`, `POS-Stery/deploy/docker/init-postgres.sql` |
| RLS | Partial | 15 RLS policies; `FORCE ROW LEVEL SECURITY` is present in every service migration; 7 policies without `WITH CHECK`: `customer.loyalty_points`, `inventory.stock_thresholds`, `product.categories`, `sales.sale_items`, `sales.receipts`, `supplier.purchase_orders`, `supplier.purchase_order_items` (static regex count) | `POS-Stery/services/customer-service/migrations/000001_create_customer_schema.up.sql`, `POS-Stery/services/inventory-service/migrations/000001_create_inventory_schema.up.sql`, `POS-Stery/services/product-service/migrations/000001_create_product_schema.up.sql`, `POS-Stery/services/sales-service/migrations/000001_create_sales_schema.up.sql`, `POS-Stery/services/supplier-service/migrations/000001_create_supplier_schema.up.sql` |
| Postgres integration tests | Not started | No test references `TEST_DATABASE`/testcontainers (static search) | `POS-Stery/services` |
| Authentication | Done | bcrypt login, JWT with claims `tid`, `sid`, `role`; the gateway applies JWT -> Tenant -> Store; roles `admin`, `cashier`, `stock_manager` | `POS-Stery/services/auth-service/internal/application/commands/login.go`, `POS-Stery/services/api-gateway/cmd/server/main.go` |
| Web | Partial | Two SvelteKit apps: `apps/admin` (dashboard, products, inventory, suppliers, customers, reports) and `apps/cashier` (cashier, receipts) with `service-worker.ts`; both use BFF proxies `+server.ts` under `routes/api` that keep the token in a server-side httpOnly cookie; `X-Store-ID` for admin is only mentioned in a proxy comment and no client code sets it (admin store selector not yet present, static search) | `POS-Stery/apps/admin/src/routes`, `POS-Stery/apps/cashier/src/routes`, `POS-Stery/apps/cashier/src/service-worker.ts` |
| gRPC transport | Done | Plaintext by design, documented | `POS-Stery/docs/security/grpc-transport-security.md` |

**Contradictions of status documents vs code (POS):**

| # | Contradiction | What the code shows | Evidence |
| --- | --- | --- | --- |
| K-6 | `PRD.md` section 10 (line 195) mentions "Laravel gateway for auth and HTTP API" | The gateway is Go `chi` | `POS-Stery/PRD.md`, `POS-Stery/services/api-gateway/cmd/server/main.go` |
| K-7 | `ci.yml` still contains a Laravel job and Go 1.24 | The gateway is Go `chi`; the service modules use go 1.25.0 | `POS-Stery/.github/workflows/ci.yml`, `POS-Stery/services/api-gateway/go.mod` |
| K-8 | The dashboard shows the payment mix as if it were data | The 55/30/15 figures are an artificial fallback | `POS-Stery/apps/admin/src/routes/(app)/dashboard/+page.svelte` |

### 3.3 HRIS

Readiness estimate: about 40% `[INFERENCE]` (in line with the score of 45/100 in `docs/PHASE5_SUMMARY.md` dated 2026-06-08, which was not re-verified here). Reason: plenty of domain/application code, but no running flow from browser to database.

| Area | Status | Findings | Evidence |
| --- | --- | --- | --- |
| gRPC services | Partial | 47 RPCs across 8 protos; 39 have real handlers. employee 8 of 10 (`UpdateEmployee`, `GetOrgChart` missing); document 5 of 7 (`DownloadDocument` returns an empty URL, `GetPresignedUrl` and `RollbackDocumentVersion` empty); ai-service: proto has 3 RPCs, directory `cmd/server` is empty | `HRIS-Stery/proto/hris/employee/v1/employee.proto`, `HRIS-Stery/services/employee-service/internal/interfaces/grpc/employee_service.go`, `HRIS-Stery/services/document-service/internal/interfaces/grpc/document_service.go`, `HRIS-Stery/proto/hris/ai/v1/ai.proto`, `HRIS-Stery/services/ai-service/cmd/server` |
| Attendance migration | Not started | `001_create_attendance_schema.up.sql` line 25: `CONSTRAINT attendance_unique_per_day UNIQUE (...) WHERE NOT is_override` is **invalid in PostgreSQL** (a UNIQUE constraint cannot use a WHERE clause; it must be a partial unique index); lines 45-46 `GRANT ... TO app` use role `app` (not `hris_app` as in the auth migration); RLS is only `ENABLE` without `FORCE`, policy without `WITH CHECK` | `HRIS-Stery/services/attendance-service/migrations/001_create_attendance_schema.up.sql`, `HRIS-Stery/services/auth-service/migrations/001_create_auth_schema.up.sql` |
| HTTP path | Not started | No `http.ListenAndServe`/`NewServeMux` in `services/**` outside `*.pb.gw.go`; the grpc-gateway path called by the Laravel gateway is never mounted | `HRIS-Stery/services`, `HRIS-Stery/docs/adr/0001-grpc-gateway-over-grpc-php.md` |
| Web login | Not started | `+page.server.ts` lines 38-40 call `http://localhost:3000/api/auth/login` with the comment "mocked for now" | `HRIS-Stery/apps/web/src/routes/(auth)/login/+page.server.ts` |
| Laravel gateway | Partial | Only `auth/*` and leave routes (`leaves`, `leave-balance`, `leave-types`); employee/attendance/document/audit routes are only placeholder comments; no `throttle` usage in `routes/api.php` | `HRIS-Stery/apps/api-gateway/routes/api.php` |
| Web | Partial | Pages: `/`, `(auth)/login`, `(app)/dashboard`, `(app)/leaves/apply`, `(app)/admin/leaves`; the token is also stored client-side (`stores/auth.ts` uses `localStorage`) | `HRIS-Stery/apps/web/src/routes`, `HRIS-Stery/apps/web/src/lib/stores/auth.ts` |
| Leave domain | Partial | `Cancel` only rejects REJECTED and CANCELLED, so PENDING can be cancelled even though `ErrCannotCancelPending` is declared; `ErrInsufficientLeaveBalance` is enforced in `leave_balance.go`; `ErrLeaveOverlapExists` is declared, enforcement not found outside `errors.go` | `HRIS-Stery/services/leave-service/internal/domain/leave_request.go`, `HRIS-Stery/services/leave-service/internal/domain/errors.go`, `HRIS-Stery/services/leave-service/internal/domain/leave_balance.go` |
| Personal data | Not started | `national_id` (NIK) and `tax_id` (NPWP) are type `TEXT`, `birth_date` is type `DATE`; the schema comment says "stored encrypted" but there is no encryption code in employee-service; no UU PDP statement in the repo | `HRIS-Stery/services/employee-service/migrations/001_create_employee_schema.up.sql` |
| Notification | Partial | The email adapter is created but not wired (`_ = emailAdapter // Placeholder`) | `HRIS-Stery/services/notification-service/cmd/server/main.go` |
| Auth | Partial | bcrypt login; `extractIPAddr` always returns `0.0.0.0` | `HRIS-Stery/services/auth-service/internal/domain/user.go`, `HRIS-Stery/services/auth-service/internal/interfaces/grpc/auth_service.go` |
| CI/CD | Partial | `cd-staging.yml` builds api-gateway, web, auth, employee, attendance, leave, notification, audit, ai but **not** document-service; `deploy/k8s/base` is empty | `HRIS-Stery/.github/workflows/cd-staging.yml`, `HRIS-Stery/deploy` |
| Tests | Partial | 131 `Test*` functions (static); no Postgres/testcontainers-based tests | `HRIS-Stery/services` |
| Deferred work | Deferred | Payroll, tax rules, recruitment, performance deferred to Phase 2 (ADR-0004, dated 2026-05-30) because of PPh 21, BPJS, THR regulations | `HRIS-Stery/docs/adr/0004-defer-payroll-to-phase2.md` |
| Events | Partial | NATS events (`hris.identity.user.registered` -> employee; `hris.workforce.employee.created` -> leave) are designed; other consumers are limited | `HRIS-Stery/docs/adr/0003-nats-jetstream-event-backbone.md` |
| Binaries in the working tree | Partial | Eight `server.exe` (root and seven services) exist on disk; **not committed** because `.gitignore` contains `*.exe` | `HRIS-Stery/.gitignore`, `HRIS-Stery/server.exe` |

**Contradictions of status documents vs code (HRIS):**

| # | Contradiction | What the code shows | Evidence |
| --- | --- | --- | --- |
| K-9 | `PROJECT_PROGRESS.md` states Auth/Employee/Attendance/Leave/Notification are "100% COMPLETE" and "Production-ready"; `PHASE1_RELEASE.md` and `IMPLEMENTATION_COMPLETE.md` are similar | Invalid attendance migration (line 25), no HTTP mux mounted, web login mocked to `localhost:3000`, `UpdateEmployee`/`GetOrgChart` missing; `PHASE5_SUMMARY.md` (2026-06-08) gives 45/100 | `HRIS-Stery/PROJECT_PROGRESS.md`, `HRIS-Stery/PHASE1_RELEASE.md`, `HRIS-Stery/IMPLEMENTATION_COMPLETE.md`, `HRIS-Stery/docs/PHASE5_SUMMARY.md` |
| K-10 | Schema comment: NIK/NPWP "stored encrypted via application-level encryption" | Plain `TEXT` columns; no encryption code in employee-service | `HRIS-Stery/services/employee-service/migrations/001_create_employee_schema.up.sql` |

### 3.4 Corrections to baseline [S] claims

The following claims were re-read and turned out to differ from the baseline; derived documents use the corrected version.

| # | Baseline claim [S] | What the code shows | Evidence |
| --- | --- | --- | --- |
| C-1 | "`guest_cap`/`video`/`zip_full_resolution` enforcement not found in the media path" | `guest_cap` and `video` are enforced; only `zip_full_resolution` is not read in the export path | `SELA/apps/api/services/media/postgres.go`, `SELA/apps/api/services/media/upload.go`, `SELA/apps/api/services/media/export.go` |
| C-2 | "`server.exe` committed" (HRIS) | Not committed (ignored by git); eight binaries exist in the working tree | `HRIS-Stery/.gitignore` |
| C-3 | "CD (`cd-staging.yml`) does not include audit/document/notification/ai" | The CD matrix includes audit, notification, and ai; only document-service is missing | `HRIS-Stery/.github/workflows/cd-staging.yml` |
| C-4 | "`birth_date` is type TEXT" | `birth_date` is type `DATE`; only NIK and NPWP are type `TEXT` | `HRIS-Stery/services/employee-service/migrations/001_create_employee_schema.up.sql` |
| C-5 | "grpc POS 1.65" | The POS service modules use grpc v1.80.0; v1.65.0 only in the `_shared` module | `POS-Stery/services/sales-service/go.mod`, `POS-Stery/services/_shared/go.mod` |
| C-6 | "Owner sheet mentions 56 Pending Verification" | Confirmed (D2), differs from the 20 in the tracker | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/10-lembar-jawaban-pemilik.md` |

**Cross-repo gaps (re-read):** grpc dependency versions 1.80.0 (POS, service modules) / 1.81.1 (HRIS) / 1.84.0 (SELA); pgx 5.6.0 / 5.9.2 / 5.11.0; nats.go 1.36.0 / 1.52.0 / not used by SELA; jwt/v5 5.2.1 (POS) / 5.3.1 (HRIS) / not used by SELA. Migrations: golang-migrate (HRIS `Makefile`), script `migrate-helper.sh` (POS), goose 3.26.0 (SELA). sqlc only in HRIS (`sqlc.yaml`). Logging zap (HRIS, POS) vs slog (SELA). Redis `redis:7-alpine` (HRIS `docker-compose.production.yml`) vs Dragonfly (SELA). HRIS carries OpenTelemetry and Prometheus in `go.mod`; the SELA baseline does not (RISK-SUI-15). Evidence: `HRIS-Stery/services/auth-service/go.mod`, `HRIS-Stery/services/employee-service/go.mod`, `POS-Stery/services/auth-service/go.mod`, `SELA/apps/api/go.mod`, `HRIS-Stery/Makefile`, `POS-Stery/scripts/migrate-helper.sh`, `HRIS-Stery/services/auth-service/sqlc.yaml`, `HRIS-Stery/docker-compose.production.yml`.

## 4. Risk register

Probability and impact: H (high), M (medium), L (low), all `[INFERENCE]`. The Evidence column only contains paths that exist today; forward-looking risks without code evidence are written "forward-looking risk".

| ID | Risk | Evidence | Probability | Impact | Mitigation | Trigger |
| --- | --- | --- | --- | --- | --- | --- |
| RISK-SUI-01 | No shared foundation for tenancy, identity, entitlement, and billing; the suite cannot be sold as a package without a new platform | `SELA/apps/api/services/auth/http.go`, `SELA/apps/api/services/payment/postgres.go`, `HRIS-Stery/services/auth-service`, `POS-Stery/services/auth-service` | H | H | Build the `stery-suite` platform (IAM, ENT, BIL) as step S1; products delegate through ports | First package sale is scheduled before S4 is finished |
| RISK-SUI-02 | SELA has no tenant/organisation concept and no external identity path; adding organisations may break the current host model | `SELA/apps/api/internal/db/migrations/0001_hosts.sql` | H | M | Only add nullable `hosts.org_id` and `hosts.external_subject` in suite mode; no RLS (D-SUI-08); standalone mode unchanged | Feature request for multi-user per organisation in SELA |
| RISK-SUI-03 | Aligning HRIS/POS to the SELA stack is a rewrite of the infrastructure/interface layers and takes time | `HRIS-Stery/services/employee-service/internal/interfaces/grpc/employee_service.go`, `POS-Stery/services/sales-service/internal/application/commands/create_sale.go` | H | H | Keep domain/application; phased rewrite S2 (POS) then S3 (HRIS) with stabilisation gates | The section 6 estimate is off by more than one level (S/M/L) |
| RISK-SUI-04 | RLS regression when moving to `kit/tenantdb` (cross-tenant isolation leaks) | `POS-Stery/services/sales-service/migrations/000001_create_sales_schema.up.sql`, `HRIS-Stery/services/attendance-service/migrations/001_create_attendance_schema.up.sql` | M | H | Require `ENABLE`+`FORCE`, `USING`+`WITH CHECK`, NOBYPASSRLS application role, cross-tenant tests per module | A cross-tenant test fails or is missing for a new module |
| RISK-SUI-05 | Conversion of HRIS/POS web from SSR to static SPA (SvelteKit `ssr=false`, `adapter-static`) | `HRIS-Stery/apps/web/src/routes/(auth)/login/+page.server.ts`, `POS-Stery/apps/cashier/src/hooks.server.ts` | M | M | One `apps/web` per product; POS merged into route groups `(admin)` and `(cashier)`; PWA scope per area | A feature depends on `+page.server.ts`/hooks with no client-side equivalent |
| RISK-SUI-06 | NATS -> Postgres outbox semantics change (ordering, redelivery, idempotent consumers) | `HRIS-Stery/docs/adr/0003-nats-jetstream-event-backbone.md`, `POS-Stery/services/_shared/nats/streams.go` | M | M | Outbox `FOR UPDATE SKIP LOCKED`, idempotent consumers (`processed_events`), at-least-once delivery (D-SUI-06) | Duplicate or lost events in integration tests |
| RISK-SUI-07 | Blast radius and UU PDP: SELA public uploads sit alongside HRIS NIK/NPWP data on shared infrastructure | `HRIS-Stery/services/employee-service/migrations/001_create_employee_schema.up.sql` | M | H | Separate database and role per product, separate bucket and access key, `kit/piicrypt` for NIK/NPWP/birth_date, UU PDP legal review | One cluster/host shared without credential separation |
| RISK-SUI-08 | Small (solo) team: too much work in progress at once | `SELA/docs/tracking/tracker.json` | H | H | One alignment at a time (D-SUI-12); gates S0/S2/S3 must be closed before moving on | Two workstreams running in parallel for more than one sprint |
| RISK-SUI-09 | Status document drift: documents claim done but the code does not | `HRIS-Stery/PROJECT_PROGRESS.md`, `HRIS-Stery/docs/PHASE5_SUMMARY.md`, `SELA/docs/aidlc/intents/261014-closed-beta-readiness/10-lembar-jawaban-pemilik.md` | H | M | Truth = code; `Evidence` column mandatory; contradictions recorded in FSD 11.3 | A new status document without an evidence path |
| RISK-SUI-10 | HRIS/POS/bundle prices are not yet set; without prices no business model can be tested | `SELA/.env.example` | H | M | Set prices as an owner decision (section 8); documents use `tbd` | First offer to a prospective customer without a price |
| RISK-SUI-11 | The platform becomes a single point of failure for suite mode | forward-looking risk | M | H | Signed entitlement snapshot with grace period (24 hours, `tbd`), 30-second introspection cache, standalone mode does not depend on the platform (D-SUI-03, D-SUI-04) | A platform incident that halts product login |
| RISK-SUI-12 | Secrets and binaries committed or left in the working tree | `POS-Stery/ecosystem.config.cjs`, `POS-Stery/deploy/docker/init-postgres.sql`, `HRIS-Stery/server.exe` | H | H | Rotate and purge POS secrets from git history; remove binaries from the HRIS working tree; gate S2/S3 | A secret scan finds values that are still live |
| RISK-SUI-13 | `:latest` images and hosting on a development machine prevent reproducible builds and availability | `SELA/deploy/docker-compose.yml`, `SELA/deploy/README.md` | H | M | Pin image tags/digests; choose production hosting (open decision, section 8) | Closed-beta release to real guests |
| RISK-SUI-14 | Midtrans is only proven in sandbox; the public webhook is untested | `SELA/apps/api/services/payment/midtrans.go`, `SELA/docs/aidlc/intents/261014-closed-beta-readiness/10-lembar-jawaban-pemilik.md` | H | H | Gate S0: webhook proven on a public URL; suite billing uses the same `payment.Provider` abstraction | The first real payment fails to activate |
| RISK-SUI-15 | Observability gap: the SELA baseline is only `slog` and `/healthz`, while HRIS/POS use OpenTelemetry/Prometheus | `HRIS-Stery/services/auth-service/go.mod`, `SELA/apps/api/internal/health` | M | M | Open owner decision (D-SUI-11); optional `kit` module | A production incident without sufficient metrics/traces |

## 5. Architecture options

| Option | Description | Pros | Cons | Decision |
| --- | --- | --- | --- | --- |
| A. Polyrepo + platform | The three product repos stay intact; the new repo `stery-suite` holds the platform and shared `kit`; products have `STERY_MODE` | Standalone sales unchanged; limited blast radius; new products added through the Product Contract; the team can move in phases | Cost of syncing `kit` across repos; the platform is a new component that must be built and operated | **Chosen** (D-SUI-01) |
| B. Monorepo | One repo for all products and the platform | Easy code sharing; uniform dependency versions | Moving three git histories; a single CI pipeline for a small team; blurs the boundaries of products sold separately | Not chosen; can be revisited if `kit` is too costly to sync |
| C. Single codebase/runtime | One application and one database for the whole suite | Simplest shared foundation | Violates per-product standalone sales; blast radius and UU PDP (RISK-SUI-07); one failure takes down all products | **Rejected** |

## 6. Stack alignment impact

Effort estimates S/M/L are all `[INFERENCE]`; an ordinal scale, not person-days. The `Evidence` column points to the current state. The target path is written in each FSD (section 2.7), not here.

### 6.1 SELA (already on the standard stack; change = `kit` adoption and suite mode)

| Current state -> mapping | Reusable | Effort | Evidence |
| --- | --- | --- | --- |
| `internal/{httpx,config,db,testdb,audit,piicrypt,objstore,health}` lifted into `stery-suite/kit` and re-imported by SELA (behaviour preserved) | All packages as the `kit` source | M | `SELA/apps/api/internal` |
| Ports `Identity`, `Entitlement`, `Notification`, `Audit`, `Events` with a local adapter (standalone) and a platform adapter (suite) | `services/auth`, `services/payment`, `internal/audit` as local adapters | M | `SELA/apps/api/services/auth/service.go`, `SELA/apps/api/services/payment/provider.go` |
| Nullable `hosts.org_id` and `hosts.external_subject` in suite mode | Table `hosts` | S | `SELA/apps/api/internal/db/migrations/0001_hosts.sql` |
| Completing gate S0 (webhook, retention, 20 Pending Verification, media origin, `zip_full_resolution`) | The whole codebase | M | `SELA/docs/tracking/tracker.json` |

### 6.2 POS

| Current state -> SELA mapping | Reusable | Effort | Evidence |
| --- | --- | --- | --- |
| Six gRPC services + chi gateway -> one Go module with packages `services/<nama>`, REST `/api/v1` on `net/http` ServeMux | Domain and application of each service | L | `POS-Stery/services/api-gateway/cmd/server/main.go`, `POS-Stery/services/sales-service` |
| gRPC sale saga -> one DB transaction; loyalty called in-process after commit | `create_sale.go` (rules), `add_loyalty_points.go` | M | `POS-Stery/services/sales-service/internal/application/commands/create_sale.go`, `POS-Stery/services/customer-service/internal/application/commands/add_loyalty_points.go` |
| NATS -> Postgres outbox + idempotent consumers | Event envelope (`event_envelope.go`) as a schema reference | M | `POS-Stery/services/_shared/nats/event_envelope.go` |
| JWT (`tid`, `sid`, `role`) -> opaque session cookie; `store_id` becomes a session attribute; bcrypt hash kept | Login command and roles | M | `POS-Stery/services/auth-service/internal/application/commands/login.go` |
| golang-migrate -> embedded goose; zap -> slog; Redis -> Dragonfly | SQL schema (RLS already `FORCE`) after adding `WITH CHECK` | M | `POS-Stery/services/customer-service/migrations/000001_create_customer_schema.up.sql` |
| Two SPAs (`apps/admin`, `apps/cashier`) -> one `apps/web` with route groups `(admin)` and `(cashier)`; cashier PWA | UI components and cashier service worker | M | `POS-Stery/apps/admin/src/routes`, `POS-Stery/apps/cashier/src/service-worker.ts` |
| CI -> `check.sh` pattern; secret rotation; remove fake dashboard data | `Makefile` and migration scripts as a reference | S | `POS-Stery/.github/workflows/ci.yml`, `POS-Stery/scripts/migrate-validate.sh` |

### 6.3 HRIS

| Current state -> SELA mapping | Reusable | Effort | Evidence |
| --- | --- | --- | --- |
| Seven gRPC services + Laravel gateway -> one Go module, REST `/api/v1`; Laravel removed | Domain and application (auth, employee, attendance, leave, notification, audit, document) | L | `HRIS-Stery/services`, `HRIS-Stery/apps/api-gateway/routes/api.php` |
| Completing missing RPCs (`UpdateEmployee`, `GetOrgChart`, document presign and rollback) | Existing entities and repositories | M | `HRIS-Stery/services/employee-service/internal/interfaces/grpc/employee_service.go`, `HRIS-Stery/services/document-service/internal/interfaces/grpc/document_service.go` |
| Migrations fixed (invalid constraint, role, `FORCE`, `WITH CHECK`) and moved to goose | Table schema | M | `HRIS-Stery/services/attendance-service/migrations/001_create_attendance_schema.up.sql` |
| sqlc -> raw pgx SQL | SQL queries as a reference | M | `HRIS-Stery/services/auth-service/sqlc.yaml` |
| NIK/NPWP/birth_date encrypted with `kit/piicrypt` (blind index for search) | Existing columns (data migration required) | M | `HRIS-Stery/services/employee-service/migrations/001_create_employee_schema.up.sql` |
| JWT -> opaque session; bcrypt kept; MinIO -> RustFS | User and role entities | M | `HRIS-Stery/services/auth-service/internal/domain/user.go` |
| SvelteKit SSR -> static SPA; real login; employee and attendance pages built | Dashboard and leave pages | M | `HRIS-Stery/apps/web/src/routes`, `HRIS-Stery/apps/web/src/lib/stores/auth.ts` |
| Payroll, tax, recruitment, performance | None (deferred) | Deferred per ADR-0004 | `HRIS-Stery/docs/adr/0004-defer-payroll-to-phase2.md` |

## 7. Stabilisation gates and roadmap S0-S5

Sequence (D-SUI-12): S0 documents + SELA closed-beta closure -> S1 `kit` extraction (SELA adopts `kit`, behaviour preserved) + platform IAM/ENT -> S2 POS alignment -> S3 HRIS alignment -> S4 suite-mode adapters in all three products + billing + console -> S5 cross-product integrations + new-product onboarding. One alignment runs at a time; each alignment ends at its product's stabilisation gate.

| Stage | Content | Exit criteria |
| --- | --- | --- |
| S0 | This document and the BRD/PRD/FSD set; SELA closed-beta closure | SELA gate: (1) Midtrans webhook proven on a public URL; (2) default retention decision recorded; (3) 20 Pending Verification closed or consciously deferred; (4) media origin separation verified; (5) enforcement of `guest_cap`/`video`/`zip_full_resolution` verified |
| S1 | `kit` extraction; platform IAM and ENT | `kit` used by SELA with behaviour preserved; proto contract `stery.platform.v1` available |
| S2 | POS alignment | POS gate: (1) loyalty called in-process after sale commit; (2) REST surface parity with module operations; (3) CI green with the SELA `check.sh` pattern; (4) RLS `WITH CHECK` on every policy; (5) committed secrets rotated and purged; (6) Postgres integration tests run; (7) fake dashboard data removed; (8) PPN/receipt decision recorded |
| S3 | HRIS alignment | HRIS gate: (1) all migrations up->down->up on a fresh DB in CI; (2) real login through the API; (3) employee update and org chart implemented; (4) document presign/rollback implemented with tests; (5) NIK/NPWP/birth_date encrypted with `kit/piicrypt`; (6) rate limits enforced; (7) secrets and binaries removed |
| S4 | Suite-mode adapters in three products + billing + console | An org can be created, choose a package, log in via SSO, and entitlements are enforced in each product |
| S5 | Cross-product integrations and new-product onboarding | INT-1..INT-3 (hypothesis, validate demand) and the Product Contract tested with one trial product |

## 8. Open decisions for the owner

Default values follow the related decisions; derived documents use `tbd` until the owner decides.

| # | Open decision | Default used by the documents | Impact if changed |
| --- | --- | --- | --- |
| OQ-1 | Prices for HRS, POS, bundles (`HRS+POS`, `HRS+SEL`, `POS+SEL`, `SUITE`), billing cycle, trial period, bundle discount rules | `tbd` | BRD 7, FSD 4.03, SKU table |
| OQ-2 | Observability: OpenTelemetry/Prometheus in the baseline or an optional `kit` module (D-SUI-11) | Baseline = `slog` + `/healthz`; OTel/Prometheus optional, `tbd` | Observability NFRs, risk RISK-SUI-15 |
| OQ-3 | Parent domain of the `stery_session` cookie (D-SUI-03) | `tbd` | SSO flow and Caddy configuration |
| OQ-4 | Grace period of the entitlement snapshot when the platform is down (D-SUI-04) | 24 hours, configurable, `tbd` | Availability NFRs, degrade behaviour |
| OQ-5 | Production hosting (beyond development machine + ngrok) | `tbd` | RISK-SUI-13, deployment profile |
| OQ-6 | Bundle rules: whether a bundle locks SKUs, whether mid-cycle add-ons are prorated | `tbd` | Billing model |
| OQ-7 | Go module owner handle for new repos (default `Briyantama`, unverified) | `Briyantama` | Module path in all `go.mod` files |
| OQ-8 | Default SELA retention decision (K-2) and POS PPN/receipt | `tbd` | Gates S0 and S2 |
| OQ-9 | Whether INT-1..INT-3 are actually requested by customers | Hypothesis, validate demand | Scope of S5 |
| OQ-10 | Target customer segment for HRS, POS, and the suite package (no segment statement in the repos) | `tbd` | BRD 4.1, PRD 2 and 8 |

## Appendix A. Verified evidence

Paths re-read on 6 November 2026 for this document (all present on disk):

- SELA: `SELA/apps/api/go.mod`, `SELA/apps/api/services/payment/postgres.go`, `SELA/apps/api/services/payment/provider.go`, `SELA/apps/api/services/payment/midtrans.go`, `SELA/apps/api/services/auth/http.go`, `SELA/apps/api/services/media/postgres.go`, `SELA/apps/api/services/media/upload.go`, `SELA/apps/api/services/media/export.go`, `SELA/apps/api/internal/db/migrations/0011_plans_transactions.sql`, `SELA/.env.example`, `SELA/deploy/docker-compose.yml`, `SELA/deploy/README.md`, `SELA/scripts/check.sh`, `SELA/.github/workflows/ci.yml`, `SELA/docs/tracking/tracker.json`, `SELA/docs/verification/owner-decisions.md`, `SELA/docs/aidlc/intents/261014-closed-beta-readiness/10-lembar-jawaban-pemilik.md`, `SELA/docs/FSD_Sela.md`, `SELA/docs/BRD_Sela.md`, `SELA/docs/PRD_Sela.md`, `SELA/CLAUDE.md`.
- POS: `POS-Stery/PRD.md`, `POS-Stery/services/api-gateway/cmd/server/main.go`, `POS-Stery/services/sales-service/internal/application/commands/create_sale.go`, `POS-Stery/services/customer-service/internal/application/commands/add_loyalty_points.go`, `POS-Stery/apps/admin/src/routes/(app)/dashboard/+page.svelte`, `POS-Stery/.github/workflows/ci.yml`, `POS-Stery/ecosystem.config.cjs`, `POS-Stery/deploy/docker/init-postgres.sql`, `POS-Stery/services/_shared/nats/streams.go`, `POS-Stery/docs/security/grpc-transport-security.md`, migrations `000001_*` in each service.
- HRIS: `HRIS-Stery/services/attendance-service/migrations/001_create_attendance_schema.up.sql`, `HRIS-Stery/apps/web/src/routes/(auth)/login/+page.server.ts`, `HRIS-Stery/services/employee-service/internal/interfaces/grpc/employee_service.go`, `HRIS-Stery/services/document-service/internal/interfaces/grpc/document_service.go`, `HRIS-Stery/apps/api-gateway/routes/api.php`, `HRIS-Stery/services/employee-service/migrations/001_create_employee_schema.up.sql`, `HRIS-Stery/services/leave-service/internal/domain/leave_request.go`, `HRIS-Stery/.github/workflows/cd-staging.yml`, `HRIS-Stery/docs/adr/0004-defer-payroll-to-phase2.md`, `HRIS-Stery/docs/PHASE5_SUMMARY.md`, `HRIS-Stery/PROJECT_PROGRESS.md`, `HRIS-Stery/proto/hris`.

## Appendix B. What was not run

- No build, `go test`, linter, formatter, migration, `docker compose`, or service was run in any repo.
- All counts (commits, tracker tasks, RPCs, `Test*` functions, RLS policies) come from static reading of files and read-only `git` commands; the RLS count uses a regex over the migration files.
- No automated secret scan; the presence of secret values was only recorded from reading specific paths, without quoting the values.
- Claims that some code is "not called" or "not found" are the result of text search, not call-graph analysis.
- The vault note `Projects/SELA.md` is outside the repo and was not re-read.
- Readiness estimates, probability, impact, and effort S/M/L are `[INFERENCE]`.
