# PRD Stery Suite

*Product Requirements Document (PRD): one organisation, one login, and one invoice for HRIS-Stery, POS-Stery, and SELA, without sacrificing separate sales*

|                         |                                                                                                                           |
|-------------------------|---------------------------------------------------------------------------------------------------------------------------|
| **Document Name**       | PRD - Stery Suite (platform and product operating modes)                                                                  |
| **Version**             | 1.0 (Draft)                                                                                                               |
| **Date**                | 6 November 2026                                                                                                           |
| **Prepared by**         | Product & Engineering Team                                                                                                |
| **Status**              | Draft for review                                                                                                          |
| **Related Documents**   | BRD_Stery_Suite, FSD_Stery_Suite, 00_Analisis_Dampak_Risiko, PRD_HRIS, FSD_HRIS, FSD_POS, `POS-Stery/PRD.md`, PRD Sela    |
| **Changes from previous** | Changes from previous: First issue                                                                                      |

## 1. Vision and Summary

Stery Suite turns HRIS-Stery (`HRS`), POS-Stery (`POS`), and SELA (`SEL`) into one portfolio that can be bought per product, as any two products, or all three. The `stery-suite` platform provides a shared organisation, SSO (single sign-on with a product switcher), entitlement, billing, notification hub, audit sink, and console; each product can still run on its own (`STERY_MODE=standalone`, default) or connected (`STERY_MODE=suite`). A new product joins by meeting the Product Contract (section 10.2).

Product principles: (1) a product never depends on the platform for standalone mode; (2) existing SELA packages and prices do not change; (3) a product user only needs to log in once per organisation; (4) usage rights are enforced in the product, not only in the UI; (5) every business value not yet decided is written `tbd`.

This document is derived from BRD_Stery_Suite; architecture decisions are referenced as D-SUI-01 through D-SUI-12 (defined in BRD_Stery_Suite section 9.1).

## 2. Problem and Target Users

### 2.1 Core Problems

- Customers using more than one product manage separate accounts, users, and payments per product.
- The seller cannot offer packages or enforce usage rights per package; the only entitlement today is SELA's per-event package.
- Each product has a different stack, so integration and maintenance are expensive.
- New products have no standard way in.

### 2.2 User Personas

| **Persona** | **Description** | **Key Needs** | **Price Sensitivity** |
| --- | --- | --- | --- |
| Organisation owner (org owner) | Owner of the business/organisation who buys the package and is responsible for billing | One organisation, choose a package, pay via QRIS, add products, view invoices and entitlements | `tbd` |
| Organisation admin (org admin) | Manages members and product access within the organisation | Invite members, set access per product, understand subscription status | `tbd` |
| Product user | Employee, cashier, or event host using HRIS, POS, or SELA | Log in once, switch products, product experience unchanged | indirect (paid by the organisation) |
| Platform operator | Internal team operating the platform | Console, audit trail, SKU configuration, event delivery monitoring, product onboarding | not applicable |

## 3. User Stories

| **ID** | **As a...** | **I want to...** | **So that...** | **Priority** |
| --- | --- | --- | --- | --- |
| US-SUI-01 | Organisation owner | create an organisation and choose a package (`HRS`, `POS`, `SEL`, two-product bundle, or `SUITE`) | I can use the products I bought right away | M |
| US-SUI-02 | Organisation owner | pay for a subscription via QRIS | the entitlement is activated automatically once payment is settled | M |
| US-SUI-03 | Organisation owner | add a product to an existing organisation (upsell) | I do not create a new account or organisation | M |
| US-SUI-04 | Organisation admin | invite members and set which products each member may access | access matches job roles | M |
| US-SUI-05 | Product user | log in once and switch between products via the product switcher | I do not need to log in repeatedly | M |
| US-SUI-06 | Organisation owner | view entitlements, usage limits, and invoices | I know what I pay for and its limits | M |
| US-SUI-07 | Organisation owner of a standalone customer | link my standalone product account to the suite organisation | existing data and users continue to be used | M |
| US-SUI-08 | Organisation admin | understand what happens when a subscription ends or is downgraded | I am not surprised by losing access | M |
| US-SUI-09 | Standalone product owner | the product keeps running normally without the platform | buying a single product does not depend on the platform | M |
| US-SUI-10 | Platform operator | view the audit trail and organisation status in the console | I can investigate incidents and support customers | S |
| US-SUI-11 | Platform operator | change SKUs, prices, and limit dimensions as data | new packages do not require a code release | S |
| US-SUI-12 | New product developer | meet the Product Contract with a clear checklist | my product can join the suite | M |
| US-SUI-13 | Platform operator | monitor cross-product event delivery and retry failed deliveries | integrations do not fail silently | S |
| US-SUI-14 | Organisation admin | enable cross-product integrations (opt-in) | I only use the integrations I want (hypothesis, validate demand) | C |
| US-SUI-15 | Organisation owner | buy two products as a bundle | I get one invoice (discount rule `tbd`) | M |
| US-SUI-16 | HRIS organisation owner | employee personal data (NIK, NPWP, date of birth) to be protected | I comply with UU PDP | M |
| US-SUI-17 | SELA customer | the Gratis/Hemat/Standar/Premium packages to remain as they are now in both modes | prices and behaviour do not change | M |

## 4. Product Features (MoSCoW Priority)

### 4.1 Must Have

- Organisation and members (platform IAM): organisation creation, invitations, per-product roles (US-SUI-01, US-SUI-04).
- SSO: opaque session in cookie `stery_session`, `SessionService/Introspect` introspection with 30-second cache, product switcher (US-SUI-05, D-SUI-03).
- Entitlement: `EntitlementService/Check`, signed snapshot, enforcement in every product, degrade behaviour (US-SUI-06, US-SUI-08, D-SUI-04).
- Billing: subscriptions, invoices, Midtrans QRIS payment via `payment.Provider`, signed webhook (US-SUI-02, US-SUI-03, US-SUI-15, D-SUI-05).
- Two modes per product and six ports with two adapters (US-SUI-09, D-SUI-02).
- Migration of standalone customers to the suite (US-SUI-07).
- Existing SELA packages unchanged (US-SUI-17); HRIS personal data protection (US-SUI-16, D-SUI-08).
- Product Contract (US-SUI-12).
- Stabilisation gates S0/S2/S3 (BR-SUI-15).

### 4.2 Should Have

- Admin console: members, entitlements, invoices, audit, SKUs (US-SUI-10, US-SUI-11).
- Notification hub and audit sink for suite-mode products (BR-SUI-12).
- Event delivery monitoring and retry (US-SUI-13).
- Suite deployment profile without port collisions (BR-SUI-18).
- Observability decision (D-SUI-11, `tbd`).

### 4.3 Could Have

- Cross-product integrations INT-1 (HRIS <-> POS staff link), INT-2 (HRIS gathering -> SELA event), INT-3 (POS store event -> SELA event and opt-in loyalty customer invitations); all are hypotheses, validate demand (US-SUI-14).
- Automatic bundle discount (rule `tbd`).

### 4.4 Won't Have (this phase)

- A single application/runtime/database (option C rejected).
- JWT, NATS/Kafka, gateway tier, ORM.
- Changes to SELA packages or prices.
- HRIS payroll, tax, recruitment, performance (Deferred, ADR-0004).
- Refunds, e-wallet, cards in suite billing (SELA only builds QRIS).
- Third-party product marketplace.

## 5. User Flows

All flows are target designs; none is running yet (the platform has no code). Process details are in FSD_Stery_Suite section 7.

### 5.1 Organisation onboarding and package selection

1. The owner opens the platform console and registers (organisation identity is created).
2. The owner chooses a SKU: `HRS`, `POS`, `SEL`, `HRS+POS`, `HRS+SEL`, `POS+SEL`, or `SUITE`.
3. The platform creates an invoice and a Midtrans QRIS charge.
4. After a valid payment webhook and a matching amount, the platform activates the entitlement.
5. The owner is directed to the first product via the product switcher; the suite-mode product verifies the session and entitlement.
6. The owner invites members and sets access per product.

### 5.2 Adding a product (upsell)

1. The owner/admin opens the subscription page in the console.
2. Chooses an additional product or a higher bundle; the platform calculates the invoice (proration rule `tbd`, OQ-6).
3. Once payment is settled the new entitlement is active; the product switcher shows the new product without re-login.
4. If the product has no data yet, the product creates initial configuration for the organisation.

### 5.3 SSO and product switcher

1. The user logs in once on the platform; the platform issues the HttpOnly cookie `stery_session`.
2. The user opens a product from the switcher; the product calls `SessionService/Introspect` (30-second local cache) and receives a `Principal`.
3. The product checks entitlement for the requested feature; if not entitled, the product shows an upsell page instead of an error.
4. Logout on the platform revokes the session; the product stops accepting that session no later than the end of the cache period.

### 5.4 Migrating a standalone customer to the suite

1. A standalone customer (e.g. a SELA host using OTP, or an HRIS/POS tenant) creates an organisation on the platform.
2. The platform starts the link: the organisation is bound to the product tenant through `integration_links` and `external_ref` (HRS/POS) or `hosts.org_id`/`hosts.external_subject` (SELA).
3. Existing users are mapped to organisation members (identity matching by the admin; matching rules are defined in FSD_Stery_Suite 7.5).
4. The product switches to `STERY_MODE=suite` for that organisation; data stays in the product database (no move between databases).
5. A path back to standalone is available as long as the link is cancelled (detailed behaviour `tbd`, OQ-6).

### 5.5 Entitlement expiry and downgrade

1. A subscription ends or is downgraded: the platform updates the entitlement and snapshot.
2. The product uses the latest snapshot; paid features are disabled according to the new entitlement, data is not deleted by the platform.
3. If the platform is unavailable, the product uses the latest snapshot until the grace period (24 hours, `tbd`) and then fails closed for paid features; basic features and standalone mode are unaffected.
4. When the subscription is restored, features return without user action.

## 6. Non-Functional Requirements

| **ID** | **Category** | **Requirement** |
| --- | --- | --- |
| NFR-SUI-01 | Session performance | Session introspection uses a 30-second local cache in the product; p95 latency target `tbd` |
| NFR-SUI-02 | Resilience | The signed entitlement snapshot is used for up to 24 hours (configurable, `tbd`) when the platform is down; fails closed for paid features afterwards |
| NFR-SUI-03 | Platform availability | Availability target `tbd` (no SLA in the repo) |
| NFR-SUI-04 | Data isolation | RLS mandatory (`ENABLE`+`FORCE`, `USING`+`WITH CHECK`) for HRS, POS, platform; mandatory cross-tenant tests per module (D-SUI-08) |
| NFR-SUI-05 | Session security | Cookie `stery_session` is HttpOnly and Secure, only the hash is stored in Dragonfly; no JWT and no tokens in the browser |
| NFR-SUI-06 | Inter-service security | Platform gRPC with deny-by-default interceptor and service HMAC token |
| NFR-SUI-07 | Event delivery | At-least-once; idempotent consumers (`processed_events`); `event_id` UUIDv7 |
| NFR-SUI-08 | Confidentiality | Secrets never in the repo or logs; env configuration fails fast; `.env.example` |
| NFR-SUI-09 | Personal data | NIK, NPWP, date of birth encrypted with `kit/piicrypt` (AES-256-GCM, per-purpose AAD, blind index, key rotation) |
| NFR-SUI-10 | Audit | Append-only `audit_logs` with database triggers |
| NFR-SUI-11 | Payments | Webhook signature verified; paid notification amount-matched |
| NFR-SUI-12 | Compatibility | Standalone mode does not change behaviour and does not need the platform |
| NFR-SUI-13 | Localisation | Indonesian (default) and English with catalogue parity tests; IDR; WIB |
| NFR-SUI-14 | Quality gate | `scripts/check.sh` (proto drift, gofmt, vet, golangci-lint, `go test -cover`, svelte-check, vitest, e2e), 80% coverage floor, `-race` in CI |
| NFR-SUI-15 | Ports | The suite profile has no port collisions; each product's standalone ports do not change |
| NFR-SUI-16 | Observability | Baseline `slog` JSON + `/healthz`; OpenTelemetry/Prometheus `tbd` (D-SUI-11) |

## 7. Monetisation Model (summary, see BRD)

Details are in BRD_Stery_Suite section 7. Summary: organisation subscriptions for HRS, POS, and bundles are billed by the platform; SELA's per-event packages remain (Gratis Rp0, Hemat Rp39.000, Standar Rp129.000, Premium Rp350.000). Prices for HRS, POS, bundles, discount rules, billing cycle, and trial: `tbd`. Limit dimensions: `hrs.employees.max`, `pos.stores.max`, `pos.devices.max`, `sel.guest_cap`, `sel.retention_days`, `sel.watermark`, `sel.video`, `sel.zip_full_resolution`.

## 8. Positioning

Positioning statement, key messages, and differentiators against competitors: `tbd` (no research in the repo; research questions are in BRD_Stery_Suite section 8.2). Candidate differentiators to validate, not facts: one login and one invoice across products; modular purchase; local language and payment (QRIS).

## 9. Success Metrics

Metric definitions are in BRD_Stery_Suite section 11; all targets `tbd`. Product metrics: active organisations, bundle penetration, standalone -> suite migration conversion, entitlement activation time, SessionService/EntitlementService availability, number of degrade failures, new product onboarding time.

## 10. Operating Modes

### 10.1 Standalone vs suite

| Aspect | `STERY_MODE=standalone` (default) | `STERY_MODE=suite` |
| --- | --- | --- |
| Identity | Users and sessions owned by the product (SELA: OTP + cookie `sela_session`; HRS/POS: password + opaque session) | The platform issues `stery_session`; the product calls `SessionService/Introspect` |
| Entitlement | Package owned by the product (SELA: `plans`) | `EntitlementService/Check` + snapshot |
| Billing | Outside the platform (`tbd`); SELA per-event in SELA | Platform (Midtrans QRIS); SELA per-event stays in SELA |
| Notifications | Product-local adapter | Platform notification hub |
| Audit | Local `audit_logs` | Local plus platform audit sink |
| Events | Local outbox | Product outbox -> `IntegrationService/Publish` -> platform -> product `Deliver` |
| Platform dependency | None | Yes, with a grace period for entitlement |

### 10.2 Product Contract

Requirements for a product to join the suite:

1. **Manifest**: `product_code`, list of feature keys, and limit dimensions (format in FSD_Stery_Suite 4.08).
2. **Six ports with two adapters each**:

| Port | Signature | Standalone adapter | Suite adapter |
| --- | --- | --- | --- |
| `Identity` | `Verify(ctx, token) (Principal, error)` | Local session/OTP/password | `SessionService/Introspect` |
| `Tenant` | `WithTenant(ctx, tenantID, scope, fn)` | Local tenant | Platform organisation -> `kit/tenantdb.WithTenant` |
| `Entitlement` | `Allows(ctx, org, feature) (bool, error)` | Local package | `EntitlementService/Check` + snapshot |
| `Notification` | `Enqueue(ctx, tx, msg)` | Local outbox | Notification hub |
| `Audit` | `Record(ctx, event)` | Local `audit_logs` | Platform audit sink |
| `Events` | `Publish(ctx, tx, envelope)` | Local outbox | `IntegrationService/Publish` |

1. **`STERY_MODE`** with values `standalone|suite`, default `standalone`.
2. **`/healthz`** on the product API.
3. **Transactional outbox publishing** with idempotent consumers.
4. **STACK-SPEC conformance checklist** (19 items): repo layout, Go language >= 1.25.1, module decomposition, transport (REST `/api/v1` + gRPC), database (PostgreSQL 18, pgx/v5, goose), tenant isolation, state store (Dragonfly), object storage (RustFS, ClamAV), authentication (opaque session, RBAC), async (ticker + outbox), observability (`slog`, `/healthz`), configuration (env fail-fast), PII and audit (`kit/piicrypt`, `kit/audit`), payments (`payment.Provider`), web (SvelteKit SPA), deploy (Caddy, compose), quality gate (`scripts/check.sh`), process (TDD, tracker, FSD updated), localisation. Details of each item in FSD_Stery_Suite 2.1.
5. **BRD/PRD/FSD triple** in the SELA house style, including the traceability trail and the `Evidence` column.

## 11. Release Roadmap

Time estimates `tbd`.

| **Release** | **Focus** | **Main Features** | **Exit gate** |
| --- | --- | --- | --- |
| S0 | Documents + SELA closed-beta exit | BRD/PRD/FSD set; Midtrans webhook proven; retention decision; 20 Pending Verification closed or deferred; media origin; enforcement of `guest_cap`/`video`/`zip_full_resolution` | SELA gate |
| S1 | `kit` and core platform | `kit` extraction; platform IAM and ENT | `kit` used by SELA with no behaviour change |
| S2 | POS alignment | In-process loyalty after sale commit; REST parity; CI green; RLS `WITH CHECK`; secret rotation; Postgres tests; real dashboard data; PPN/receipt decision | POS gate |
| S3 | HRIS alignment | up->down->up migrations in CI; real login; employee update and org chart; document presign/rollback; NIK/NPWP/birth_date encryption; rate limits; secrets and binaries removed | HRIS gate |
| S4 | Suite mode | Suite adapters in three products, billing, console | Org, package, SSO, entitlement work |
| S5 | Integrations and new products | INT-1..INT-3 (hypotheses), Product Contract on a pilot product | Pilot product passes the checklist |

## 12. Out of Scope

- A single application, runtime, or database.
- JWT, NATS/Kafka, gateway tier, ORM.
- Changing SELA packages/prices or changing any repo code during this documentation phase.
- HRIS payroll, tax, recruitment, performance (ADR-0004).
- Refunds, e-wallet, and cards in suite billing.
- Integrations other than INT-1..INT-3.

## 13. Dependencies and Risks

| Dependency / risk | Impact | Handling |
| --- | --- | --- |
| RISK-SUI-14 Midtrans webhook not yet proven on a public URL | Suite billing cannot be trusted | S0 gate |
| RISK-SUI-08 Small team | Parallel workstreams pile up | One alignment at a time (D-SUI-12) |
| RISK-SUI-11 Platform single point of failure | Suite mode affected | Snapshot, 30-second cache, standalone does not depend on it |
| RISK-SUI-10 Prices `tbd` | Cannot sell packages | OQ-1 |
| RISK-SUI-07 UU PDP vs public uploads | Legal risk | Data separation, `kit/piicrypt` |
| Dependency on open decisions OQ-2 (observability), OQ-3 (cookie domain), OQ-4 (grace period) | Specification waits on the owner | Defaults in D-SUI-03, D-SUI-04, D-SUI-11 |

## 14. Current Status

| Area | Status | Notes | Evidence |
| --- | --- | --- | --- |
| `stery-suite` platform | Not started | Git repo created; only `docs/`, no code | `stery-suite/docs` |
| SELA (product) | Partial | 76/105 tasks Completed, 20 Pending Verification; identity is local OTP only; no tenant, SSO, or bundle entitlement | `SELA/docs/tracking/tracker.json`, `SELA/apps/api/services/auth/http.go`, `SELA/apps/api/services/payment/postgres.go` |
| POS (product) | Partial | Six real gRPC services; no cross-service loyalty integration yet | `POS-Stery/services/customer-service/internal/application/commands/add_loyalty_points.go` |
| HRIS (product) | Partial | 39 of 47 RPCs real; login-to-DB flow not yet working | `HRIS-Stery/apps/web/src/routes/(auth)/login/+page.server.ts` |
| Payments | Pending Verification | Midtrans provider + sandbox exist in SELA; not yet tested with a real account | `SELA/apps/api/services/payment/provider.go`, `SELA/apps/api/services/payment/midtrans.go` |
| `kit` code | Not started | Source exists in SELA `internal/` but has not been extracted | `SELA/apps/api/internal` |

Per-repo details and status-document contradictions are in `00_Analisis_Dampak_Risiko` section 3.
