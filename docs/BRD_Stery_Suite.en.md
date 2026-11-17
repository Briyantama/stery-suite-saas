# BRD Stery Suite

*Business Requirements Document (BRD): HRIS-Stery, POS-Stery, and SELA, sellable as one package or separately*

|                         |                                                                                                                                      |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| **Document Name**       | BRD - Stery Suite (platform, packages, and composition model of the three products)                                                  |
| **Version**             | 1.0 (Draft)                                                                                                                          |
| **Date**                | 6 November 2026                                                                                                                      |
| **Prepared by**         | Product & Engineering Team                                                                                                           |
| **Status**              | Draft for review                                                                                                                     |
| **Related Documents**   | 00_Analisis_Dampak_Risiko, PRD_Stery_Suite, FSD_Stery_Suite, BRD_HRIS, PRD_HRIS, FSD_HRIS, BRD_POS, FSD_POS, BRD/PRD/FSD Sela        |
| **Changes from previous** | Changes from previous: First issue                                                                                                 |

## 1. Executive Summary

Stery Suite is a way to sell three existing products, HRIS-Stery (product code `HRS`, HR), POS-Stery (`POS`, cashier and inventory), and SELA (`SEL`, guest camera for events), as packages: all three together (`SUITE`), two of the three (`HRS+POS`, `HRS+SEL`, `POS+SEL`), or a single product. Each product can still run standalone (`STERY_MODE=standalone`, the default) or connected (`STERY_MODE=suite`) to the new `stery-suite` platform, which provides a shared organisation and identity (SSO), entitlement (usage rights per package), billing, notification hub, audit sink, and console. New products can be added later by following the Product Contract.

The owner has decided: a polyrepo structure plus a new platform repo; the stack, patterns, and architecture of the whole suite follow SELA; documents are provided in Indonesian and English. This document defines the business requirements. The impact and risk analysis is in `00_Analisis_Dampak_Risiko`; architecture decisions are recorded as D-SUI-01 through D-SUI-12 in section 9.1.

Current state (section 13): SELA is the most mature but has not yet closed the closed-beta gate; POS has six real gRPC services with integration defects; HRIS does not yet have a working login-to-database flow; the `stery-suite` platform contains no code yet. No source code was changed in this documentation phase.

All prices, quotas, SLAs, market sizes, competitor data, and KPI targets not found in the repo are written as `tbd` and become open questions; the only price figures are the prices of the existing SELA packages.

## 2. Background and Problem Statement

The three products were built separately and share no code, tables, events, identity, or billing (analysis section 3 and RISK-SUI-01). A customer who buys two or three products today must manage separate accounts, users, and payments, and the seller can neither offer packages nor enforce per-package usage rights. SELA only knows hosts and per-event packages; it has no tenant/organisation concept and no external identity path. HRIS and POS are multi-tenant but with different tenant namespaces.

In addition, the three repos use different stacks (gRPC microservices + NATS + JWT in HRIS and POS, a single Go module + outbox + opaque session in SELA), so every integration would bear a continuous translation cost. The owner decided that the SELA stack is the standard; HRIS and POS must be aligned, and the condition of each (HRIS cannot yet be used for real; POS has integration defects) means the alignment doubles as a stabilisation opportunity.

Business problems solved: (1) selling packages with one organisation, one login, and one invoice; (2) still selling each product on its own without the platform; (3) adding new products without rebuilding the foundation; (4) unifying technical standards so a small team can maintain three products.

## 3. Business Objectives

1. Sell each product independently (`HRS`, `POS`, `SEL`) with no dependency on the platform.
2. Sell two-product bundles and the three-product bundle (`SUITE`) with one organisation, one login, and one invoice.
3. Retain the existing SELA packages (Gratis, Hemat, Standar, Premium) without any change in price or behaviour.
4. Prepare an entry path for new products through the Product Contract (manifest, six ports, `STERY_MODE`, `/healthz`, outbox, STACK-SPEC checklist).
5. Maintain data isolation between organisations and between products and compliance with UU PDP, especially for employee personal data (NIK, NPWP, date of birth).
6. Reduce maintenance cost through one standard stack and a shared `kit`.
7. Close each product's stabilisation gate before and after alignment, so the products sold actually work.
8. Set prices, bundle rules, billing cycle, and trial before the first package sale (`tbd`, OQ-1).

## 4. Scope

### 4.1 Segments and packages

Customer segment: `tbd` (there is no target segment statement for HRIS/POS/suite in the repo; open question OQ-10). SELA already names B2C and B2B2C segments for events (BRD Sela section 3).

| Package (SKU) | Products included | Supported modes | Notes |
| --- | --- | --- | --- |
| `HRS` | HRIS-Stery | standalone, suite | Dimension `hrs.employees.max`; tiers and price `tbd` |
| `POS` | POS-Stery | standalone, suite | Dimensions `pos.stores.max`, `pos.devices.max`; tiers and price `tbd` |
| `SEL` | SELA | standalone, suite | Existing Gratis/Hemat/Standar/Premium/Partner packages |
| `HRS+POS` | HRIS + POS | suite (see 7.1 for standalone) | Discount rule `tbd` |
| `HRS+SEL` | HRIS + SELA | suite | Discount rule `tbd` |
| `POS+SEL` | POS + SELA | suite | Discount rule `tbd` |
| `SUITE` | HRIS + POS + SELA | suite | Discount rule `tbd` |

### 4.2 In scope

- The `stery-suite` platform: IAM (organisations, members, sessions), ENT (entitlements and snapshots), BIL (subscriptions, invoices, Midtrans QRIS payments), NTF (notification hub), AUD (audit sink), ADM (console), INT (cross-product integration), DEP (deployment profile and Product Contract). Modules are detailed in FSD_Stery_Suite sections 4.01-4.08.
- The shared `kit` package lifted from SELA `internal/` plus `tenantdb`, `session`, `outbox`.
- Two modes per product (`STERY_MODE`), six ports (`Identity`, `Tenant`, `Entitlement`, `Notification`, `Audit`, `Events`) with two adapters each.
- Specification of the HRIS and POS alignment to the SELA stack (each product's BRD/FSD documents) and the migration path of standalone customers to the suite.
- Stabilisation gates S0/S2/S3 and the S0-S5 roadmap.
- Bilingual documents (Indonesian and English).

### 4.3 Deferred

| Item | Reason for deferral | Condition to open |
| --- | --- | --- |
| Cross-product integrations INT-1 (HRIS employee staff link <-> POS user), INT-2 (HRIS gathering creates a SELA event), INT-3 (POS store event creates a SELA event and invites opted-in loyalty customers) | Hypothesis; demand validation not yet done | Evidence of customer demand and completion of S4 (phase S5) |
| Fourth and later products | Product Contract not yet tested with a trial product | S5 |
| HRIS payroll, tax, recruitment, performance (HRS modules 09-12) | Deferred by ADR-0004; legal review of PPh 21, BPJS, THR needed | Legal review and owner decision |
| OpenTelemetry/Prometheus observability in the baseline | Open decision D-SUI-11 | Owner decision (OQ-2) |
| HRS, POS, bundle prices | Not yet set (`tbd`) | Owner decision (OQ-1) |

### 4.4 Out of scope

- Merging the three products into one application, one runtime, or one database (option C rejected, section 8).
- Moving the three repos into a monorepo (option B not chosen).
- Changing the source code of any repo in this documentation phase.
- JWT and tokens stored in the browser; NATS/Kafka; gateway tier; ORM (see STACK-SPEC in FSD_Stery_Suite).
- Changing existing SELA packages, prices, or behaviour.
- New HRIS/POS features beyond their respective BRD/PRD/PRD.md documents.
- Re-creating SELA documents, `POS-Stery/PRD.md`, or existing status documents.

## 5. Stakeholders

| Stakeholder | Role | Interest |
| --- | --- | --- |
| Product owner / business sponsor | Setting prices, bundles, open decisions OQ-1..OQ-10 | Package revenue, risk control |
| Engineering lead | Architecture, alignment order S0-S5 | A workload a small team can handle (RISK-SUI-08) |
| Organisation customer (organisation owner/admin) | Buys packages, manages members and products | One login, one invoice, products can be bought separately |
| Product users (employees, cashiers, hosts/guests) | Use HRIS, POS, SELA | Unchanged experience in standalone mode |
| Platform operator | Operates the console, billing, deployment | Audit and monitoring capability |
| Legal/compliance advisor | Review of UU PDP, PPh 21/BPJS/THR, PPN | Compliance before related features are opened |
| Payment provider (Midtrans) | QRIS processing | A valid and proven webhook (RISK-SUI-14) |
| Prospective new-product developers | Follow the Product Contract | A clear, checkable contract |

## 6. Business Requirements

Priority: M = Must, S = Should, C = Could. Each BR is mapped to FRs in FSD_Stery_Suite section 11.2.

| **ID** | **Business Requirement** | **Priority** |
| --- | --- | --- |
| BR-SUI-01 | Each product (`HRS`, `POS`, `SEL`) can be sold and used independently, without the platform and without any other product. | M |
| BR-SUI-02 | Any two products can be sold as a bundle (`HRS+POS`, `HRS+SEL`, `POS+SEL`) with one organisation and one invoice. | M |
| BR-SUI-03 | All three products can be sold as the `SUITE` bundle with one organisation, one login, and one invoice. | M |
| BR-SUI-04 | Each customer chooses per product between `standalone` mode (the default, current behaviour unchanged) and `suite` mode; both modes can coexist across different customers. | M |
| BR-SUI-05 | The existing SELA packages (Gratis, Hemat, Standar, Premium, Partner) and their prices remain valid and unchanged in both modes; SELA per-event checkout stays inside SELA. | M |
| BR-SUI-06 | A new product can join the suite by meeting the Product Contract: manifest (`product_code`, feature keys, limit dimensions), six ports with two adapters, `STERY_MODE`, `/healthz`, outbox publishing, STACK-SPEC checklist, and the BRD/PRD/FSD triple. | M |
| BR-SUI-07 | A standalone customer can be moved to the suite (linking the existing organisation and users) without data loss and without re-creating accounts. | M |
| BR-SUI-08 | One organisation identity gives one login (SSO) to all purchased products, with a product switcher; the session is an opaque cookie, without JWT. | M |
| BR-SUI-09 | Usage rights per organisation, product, feature, and limit dimension are enforced in every suite-mode product; when a subscription ends or the platform is unavailable, the product degrades paid features in a defined way (grace period, then fail closed for paid features) and never cuts off standalone mode. | M |
| BR-SUI-10 | Suite subscriptions (HRS, POS, bundles) are billed by the platform through Midtrans QRIS with a signed webhook; prices are stored as configuration data, not hard-coded. | M |
| BR-SUI-11 | Data is separated per product (one database and one application role per product) and per organisation (RLS mandatory for HRS, POS, and the platform); no cross-database FK; personal data (NIK, NPWP, date of birth) is encrypted and handled in line with UU PDP. | M |
| BR-SUI-12 | Notifications and audit trails from suite-mode products can be sent to the platform's notification hub and audit sink without changing standalone-mode behaviour. | S |
| BR-SUI-13 | Organisation owners/admins and platform operators have a console to manage members, view entitlements and invoices, and perform platform operations. | S |
| BR-SUI-14 | Cross-product integrations INT-1, INT-2, INT-3 are available as opt-in per organisation through the entitlement feature `integration.<a>_<b>`; hypothesis, validate demand before building. | C |
| BR-SUI-15 | Each product must close its stabilisation gate (S0 for SELA, S2 for POS, S3 for HRIS) before a package containing it is sold. | M |
| BR-SUI-16 | HRS/POS product prices and bundles, bundle discount rules, billing cycle, and trial are set by the owner before the first package sale (currently `tbd`). | M |
| BR-SUI-17 | All suite interfaces are in Indonesian (default) and English, currency IDR, time zone WIB. | S |
| BR-SUI-18 | The suite deployment profile runs the platform and three products together without port collisions, with one Postgres server (four databases), one Dragonfly instance per product, and one RustFS; each product's standalone profile is unchanged. | S |

## 7. Business Model and Monetisation

Model: organisation subscriptions for HRS, POS, and bundles billed by the platform; SELA per-event packages stay as they are now. All prices other than the SELA prices below are `tbd` (OQ-1); no figure is derived or guessed.

### 7.1 SKU matrix

| SKU | Products | Standalone mode | Suite mode | Billing | Price |
| --- | --- | --- | --- | --- | --- |
| `HRS` | HRS | Available (without platform) | Available | Standalone: outside the platform, `tbd`; suite: platform subscription | `tbd` |
| `POS` | POS | Available | Available | Same as `HRS` | `tbd` |
| `SEL` | SEL | Available (SELA per-event checkout) | Available (SELA per-event checkout stays in SELA, D-SUI-05) | Per-event in SELA | See 7.3 |
| `HRS+POS` | HRS, POS | Two standalone products sold together: billing `tbd` (OQ-6) | Available | Suite: platform bundle subscription | `tbd` |
| `HRS+SEL` | HRS, SEL | `tbd` (OQ-6) | Available | Suite: platform bundle for HRS; SELA per-event | `tbd` |
| `POS+SEL` | POS, SEL | `tbd` (OQ-6) | Available | Suite: platform bundle for POS; SELA per-event | `tbd` |
| `SUITE` | HRS, POS, SEL | `tbd` (OQ-6) | Available | Suite: platform bundle; SELA per-event | `tbd` |

Bundle discount rules, billing cycle (monthly/annual), and trial period: `tbd` (OQ-1, OQ-6).

### 7.2 Limit dimensions

Dimension names are fixed; SELA values come from the `plans` table; other values are `tbd`.

| Dimension | Product | Gratis | Hemat | Standar | Premium | Partner | Value source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `hrs.employees.max` | HRS | `tbd` | `tbd` | `tbd` | `tbd` | `tbd` | Not yet in repo |
| `pos.stores.max` | POS | `tbd` | `tbd` | `tbd` | `tbd` | `tbd` | Not yet in repo |
| `pos.devices.max` | POS | `tbd` | `tbd` | `tbd` | `tbd` | `tbd` | Not yet in repo |
| `sel.guest_cap` | SEL | 30 | 80 | 200 | unlimited | unlimited | `plans` (migration 0011) |
| `sel.retention_days` | SEL | 7 | 30 | 365 | 730 | never | `plans` (migration 0015) |
| `sel.watermark` | SEL | yes | no | no | no | no | `plans` |
| `sel.video` | SEL | no | no | yes | yes | yes | `plans` |
| `sel.zip_full_resolution` | SEL | no | no | yes | yes | yes | `plans` (not yet enforced in export, analysis 3.1) |

Package tiers for HRS and POS (names and number) `tbd`. HRS tiers are bounded by dimension `hrs.employees.max`; POS tiers by `pos.stores.max` and `pos.devices.max`.

### 7.3 Existing SELA package prices (per event)

| Package | Price | Source |
| --- | --- | --- |
| Gratis | Rp0 | `SELA/docs/BRD_Sela.md` section 7 |
| Hemat | Rp39.000 | `PLAN_PRICE_IDR_HEMAT=39000` in `SELA/.env.example` |
| Standar | Rp129.000 | `PLAN_PRICE_IDR_STANDAR=129000` |
| Premium | Rp350.000 | `PLAN_PRICE_IDR_PREMIUM=350000` |
| Partner | special contract/commission (not publicly listed) | `SELA/docs/BRD_Sela.md` section 7 |

### 7.4 Principles

- Prices in configuration data, not code; a new package requires no code release.
- Entitlements are mapped from the active subscription to feature keys and limit dimensions per product (FSD_Stery_Suite 4.02).
- Payment uses SELA's `payment.Provider` abstraction (Midtrans QRIS; Xendit has been removed) (D-SUI-05).

## 8. Alternatives and Competitor Analysis

### 8.1 Architecture options

| Option | Description | Decision |
| --- | --- | --- |
| A. Polyrepo + platform | The three product repos remain; a new repo `stery-suite` holds the platform and `kit` | **Chosen** (D-SUI-01) |
| B. Monorepo | One repo for all products and the platform | Not chosen: moves three git histories and forces one CI pipeline for products sold separately |
| C. Single codebase/runtime | One application and one database | **Rejected**: violates per-product standalone sales, enlarges blast radius, complicates UU PDP |

Detailed comparison is in `00_Analisis_Dampak_Risiko` section 5.

### 8.2 Competitors

Competitor data for the HRIS/POS/suite packages is not yet in the repo; all content is `tbd` and must not be filled in without research.

| Comparison category | Players | Pricing model | Strengths/weaknesses |
| --- | --- | --- | --- |
| Integrated HR + cashier + events suite | `tbd` | `tbd` | `tbd` |
| Local HRIS (UU PDP, PPh 21, BPJS) | `tbd` | `tbd` | `tbd` |
| Local POS (QRIS, PPN, receipt) | `tbd` | `tbd` | `tbd` |

Research questions: (1) do SME customers buy HRIS and POS from a single vendor? (2) is there a need for SELA for corporate gatherings and store events (INT-2, INT-3)? (3) what is the willingness to pay for a bundle compared with separate products? (4) does SELA's per-event package fit an organisation subscription or are monthly credits needed?

## 9. Assumptions and Constraints

### 9.1 Decision log

The following decisions are embedded in the documents and may be changed by the owner; changing one decision means re-drafting the documents that reference it.

| ID | Decision | Summary |
| --- | --- | --- |
| D-SUI-01 | Composition, not consolidation | The three products remain separate deployables with separate databases. A fourth deployable, the `stery-suite` platform, holds organisation/identity, entitlement, billing, notification hub, audit sink, and console. Shared Go code in `stery-suite/kit` (lifted from SELA `internal/{httpx,config,db,testdb,audit,piicrypt,objstore,health}`, plus `tenantdb`, `session`, `outbox`). |
| D-SUI-02 | Two modes per product | Env `STERY_MODE=standalone\|suite`, default `standalone`. `standalone` = current behaviour (own users, sessions, packages). `suite` = the product delegates identity, entitlement, billing, notification, audit to the platform through the Go ports `Identity`, `Tenant`, `Entitlement`, `Notification`, `Audit`, `Events` with two adapters each. |
| D-SUI-03 | Identity in suite mode | The platform issues an opaque session in the HttpOnly cookie `stery_session` (parent domain, value `tbd`); only its hash is stored in the platform Dragonfly. Products validate through gRPC `stery.platform.v1.SessionService/Introspect` with a 30-second local cache, a deny-by-default interceptor, and a service HMAC token. No JWT. |
| D-SUI-04 | Entitlement | `stery.platform.v1.EntitlementService/Check(org_id, product, feature)` plus a signed entitlement snapshot cached in the product; when the platform is down the product uses the last snapshot for up to 24 hours (configurable, `tbd`), then fails closed for paid features, never for standalone mode. |
| D-SUI-05 | Billing | Suite subscriptions (HRS, POS, bundles) are billed by the platform using SELA's `payment.Provider` abstraction (Midtrans QRIS). SELA per-event checkout stays inside SELA in both modes (Gratis/Hemat/Standar/Premium packages unchanged). HRS/POS/bundle prices `tbd`. |
| D-SUI-06 | Events | No NATS. Per product: in-process domain events + Postgres transactional outbox (`FOR UPDATE SKIP LOCKED`) + idempotent consumers (`processed_events`). Cross-product: product outbox -> `IntegrationService/Publish` (gRPC) -> the platform delivers to the subscribed product's `Deliver` endpoint; envelope `{event_id UUIDv7, event_type, org_id, store_id?, actor_id, occurred_at, schema_version, payload}`; at-least-once; opt-in per organisation through the entitlement feature `integration.<a>_<b>`. |
| D-SUI-07 | Data | One Postgres server per profile with one database and one application role per product (`stery_platform`, `hris`, `pos`, `sela`), no cross-database FK; cross-product references are UUID + `external_ref` columns. One Dragonfly per product in the suite profile. One RustFS with one bucket and one access key per product. ClamAV shared. |
| D-SUI-08 | Multi-tenancy invariant | RLS mandatory for HRS, POS, platform: `ENABLE`+`FORCE`, `tenant_isolation` policy with `USING` and `WITH CHECK`, `current_setting('app.tenant_id', true)::uuid` set per transaction by `kit/tenantdb.WithTenant`; POS adds `app.store_id`; application role NOBYPASSRLS; separate migration role; cross-tenant tests mandatory per module. SELA only adds nullable `hosts.org_id` and `hosts.external_subject` in suite mode, with no RLS change. |
| D-SUI-09 | Product web | Each product has one `apps/web` (SvelteKit SPA); POS merges admin and cashier into the route groups `(admin)` and `(cashier)`; PWA service worker scope per area that needs offline (POS cashier `/cashier/`, SELA guest `/e/`). Suite console = `stery-suite/apps/web`. |
| D-SUI-10 | Credentials | SELA keeps email OTP; HRIS and POS keep password login (the existing bcrypt hash scheme is retained) but sessions become opaque cookies (JWT removed). The POS token-with-store becomes the session attribute `store_id`. |
| D-SUI-11 | Observability | SELA baseline = `slog` JSON + `/healthz`. OpenTelemetry/Prometheus (present in HRIS and POS) are not in the baseline; recorded as an open owner decision `tbd` (optional `kit` module). |
| D-SUI-12 | Sequence | S0 documents + SELA closed-beta closure -> S1 `kit` extraction (SELA adopts `kit`, behaviour preserved) + platform IAM/ENT -> S2 POS alignment -> S3 HRIS alignment -> S4 suite-mode adapters in all three products + billing + console -> S5 cross-product integrations + new-product onboarding. One alignment runs at a time; each ends at that product's stabilisation gate. |

### 9.2 Assumptions

- The owner can set prices and bundle rules before S4 completes; otherwise package sales are delayed (RISK-SUI-10).
- Prospective package customers need one login and one invoice; not yet validated (research question 8.2).
- One Postgres server and one Dragonfly per product are sufficient for the suite profile in the initial phase; capacity and SLA `tbd`.
- Midtrans QRIS is sufficient as the only suite payment method in the initial phase (SELA only built QRIS; refunds, e-wallets, cards are not yet built).

### 9.3 Constraints

- This phase is documents only; no code is changed.
- One alignment at a time because the team is small (RISK-SUI-08).
- The platform must not be a prerequisite for standalone mode.
- Business values not in the repo must not be filled in (the `tbd` rule).
- The Go module owner handle for new repos (`Briyantama`) is unverified (OQ-7).
- HRIS and POS have not passed their stabilisation gates, so they are not yet fit to be sold as part of a package (BR-SUI-15).

## 10. Risks and Mitigation

Full risk definitions are in `00_Analisis_Dampak_Risiko` section 4; the following table summarises their business impact.

| **Risk** | **Business impact** | **Mitigation** |
| --- | --- | --- |
| RISK-SUI-01 No shared tenancy/identity/entitlement/billing foundation | Packages cannot be sold | Build the platform (S1, S4); BR-SUI-08 through BR-SUI-10 |
| RISK-SUI-03 HRIS/POS alignment is an infrastructure rewrite | Schedule slips | Keep domain/application; one alignment at a time |
| RISK-SUI-07 Blast radius and UU PDP (SELA public uploads vs HRIS NIK/NPWP) | Legal and reputational risk | Separate database, bucket, and role per product; PII encryption |
| RISK-SUI-08 Small team | Parallel work piles up | D-SUI-12 |
| RISK-SUI-10 Prices not yet set | No tested business model | BR-SUI-16; OQ-1 |
| RISK-SUI-11 Platform single point of failure | All suite-mode products affected | Entitlement snapshot + grace period; standalone does not depend on it |
| RISK-SUI-14 Midtrans only proven in sandbox | Real payments fail | S0 gate: webhook proven |

## 11. KPIs

Definitions only; all targets are `tbd` because there is no baseline in the repo.

| KPI | Definition | Target |
| --- | --- | --- |
| Active organisations | Number of organisations with at least one active entitlement | `tbd` |
| Bundle penetration | Percentage of organisations with two or more products | `tbd` |
| Migration conversion | Percentage of standalone customers moved to the suite without data loss | `tbd` |
| Entitlement activation | Time from Midtrans payment settled to entitlement active | `tbd` |
| Platform availability | Percentage of time SessionService and EntitlementService respond | `tbd` |
| Degrade failures | Number of incidents of paid features blocked because the platform was down beyond the grace period | `tbd` |
| New-product onboarding time | Duration from start until the product passes the Product Contract checklist | `tbd` |
| Gate compliance | Number of S0/S2/S3 gates closed out of the total | `tbd` |

## 12. Timeline and Phases

Durations and dates `tbd` (there are no time estimates in the repo; the owner sets them after reviewing section 6 of the analysis).

| Phase | Scope | Exit gate | Estimate |
| --- | --- | --- | --- |
| S0 | Documents + SELA closed-beta closure | SELA stabilisation gate (analysis section 7) | `tbd` |
| S1 | `kit` extraction; platform IAM and ENT | `kit` used by SELA with no behaviour change | `tbd` |
| S2 | POS alignment | POS stabilisation gate | `tbd` |
| S3 | HRIS alignment | HRIS stabilisation gate | `tbd` |
| S4 | Suite-mode adapters + billing + console | Org can be created, choose a package, SSO, entitlement enforced | `tbd` |
| S5 | Cross-product integrations + new-product onboarding | Product Contract tested on one trial product | `tbd` |

## 13. Current Implementation Status

### 13.1 Portfolio of three products and platform

Status as of 6 November 2026. Readiness estimates are in analysis section 3 and marked `[INFERENCE]`.

| Product | Status | Summary | Evidence |
| --- | --- | --- | --- |
| SELA (`SEL`) | Partial | 427 commits (last 2026-10-26); 76 of 105 tasks Completed, 20 Pending Verification, 9 Not Started (tracker 2026-10-25); Midtrans webhook not yet proven on a public URL; retention conflict not yet decided | `SELA/docs/tracking/tracker.json`, `SELA/apps/api/go.mod`, `SELA/docs/BRD_Sela.md` |
| POS-Stery (`POS`) | Partial | 21 commits (last 2026-06-30); six real gRPC services; `AddLoyaltyPoints` has no caller; dashboard uses a fabricated 55/30/15 payment mix; stale CI (Laravel job) | `POS-Stery/PRD.md`, `POS-Stery/services/customer-service/internal/application/commands/add_loyalty_points.go`, `POS-Stery/.github/workflows/ci.yml` |
| HRIS-Stery (`HRS`) | Partial | 33 commits (last 2026-06-10); 39 of 47 RPCs have real handlers; attendance migration invalid; no HTTP mux mounted; web login still mocked | `HRIS-Stery/services/attendance-service/migrations/001_create_attendance_schema.up.sql`, `HRIS-Stery/apps/web/src/routes/(auth)/login/+page.server.ts`, `HRIS-Stery/docs/adr/0004-defer-payroll-to-phase2.md` |
| `stery-suite` platform | Not started | Folder and git repo created; contains only `docs/`; no code | `stery-suite/docs` |

### 13.2 Status per platform module

| Module | Status | Notes | Evidence |
| --- | --- | --- | --- |
| SUI 01 IAM | Not started | No code; SELA only has local OTP | `SELA/apps/api/services/auth/http.go` |
| SUI 02 ENT | Not started | SELA only has per-event `events.package` -> `plans` | `SELA/apps/api/services/payment/postgres.go` |
| SUI 03 BIL | Not started | SELA's payment provider can be reused (Midtrans + sandbox) | `SELA/apps/api/services/payment/provider.go` |
| SUI 04 NTF | Not started | SELA notification outbox as reference | `SELA/apps/api/internal/db/migrations/0008_notifications.sql` |
| SUI 05 AUD | Not started | SELA `internal/audit` as the source of `kit/audit` | `SELA/apps/api/internal/audit/audit.go` |
| SUI 06 ADM | Not started | None | `stery-suite/docs` |
| SUI 07 INT | Not started | HRIS and POS have a shared NATS package; no cross-product | `POS-Stery/services/_shared/nats/event_envelope.go` |
| SUI 08 DEP | Not started | SELA compose as reference | `SELA/deploy/docker-compose.yml` |

Contradictions between status documents and code are recorded in `00_Analisis_Dampak_Risiko` section 3 and in each product's FSD section 11.3.

## 14. Approval

This document is the first BRD for Stery Suite and needs to be reviewed and approved by business stakeholders before it is used as the basis for the final PRD and FSD and for S1 work.

| **Name** | **Title** | **Signature** | **Date** |
|----------|------------------|------------------|-------------|
|          | Product Owner    |                  |             |
|          | Business Sponsor |                  |             |
|          | Engineering Lead |                  |             |
