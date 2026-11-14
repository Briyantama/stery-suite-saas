# Local code review: SELA, HRIS-Stery, POS-Stery, stery-kit (2026-11-08)

Scope: every uncommitted change in the four repos (about 780 files). The changes were split into 24 slices, each reviewed by its own agent. A scout then checked every CRITICAL and HIGH claim against the code.

**Decision: BLOCK.** The CRITICAL is fixed. The confirmed pre-existing HIGH findings below are still open.

## Counts

| Stage | Critical | High | Medium | Low |
|---|---|---|---|---|
| Raw reviewer output (before verification) | 12 | 51 | 94 | 54 |
| After verification: fixed in this pass | 1 | 2 | 5 | 0 |
| After verification: open (pre-existing domain logic) | 0 | 18 | ~40 | ~30 |

Most raw CRITICALs were downgraded or merged during verification. Raw outputs: `agent://review4-1..24`; verification: `agent://verify-1..6`.

## Fixed in this pass (regressions from the stack-alignment / design-system work)

| Sev | Location | Issue | Fix |
|---|---|---|---|
| CRITICAL | `stery-kit/go/authn/rsa.go` Verify; `HRIS-Stery/apps/api/services/auth/infrastructure/jwt_signer.go` RefreshClaims | HRIS refresh JWTs use the same key as access tokens and carry `user_id`/`tenant_id`, so the kit's legacy claim fallback let a refresh token authenticate any API route. | Refresh tokens now carry `typ:"refresh"`. `Verify` rejects them, and `ValidateRefreshToken` requires the claim. Tests added in both repos. |
| HIGH | `POS-Stery/apps/{admin,cashier}/src/app.d.ts:1` | Imported `Session` from the deleted `$lib/server/session`, so `locals.session` silently became `any`. | Now imports from `@stery/kit/sveltekit/session`. |
| HIGH | `POS-Stery/.github/workflows/ci.yml` web job | `npm ci` could not resolve `file:../../../stery-kit/web`. | Added a stery-kit checkout (`STERY_KIT_TOKEN`, `persist-credentials: false`). |
| MEDIUM | `*/apps/api/Dockerfile.dockerignore` (new, ×3) | The build context is now the suite root, so per-repo `.dockerignore` files no longer applied and `.env` files and keys entered the context. | Added allowlist ignore files next to each Dockerfile and removed the obsolete per-repo files. |
| MEDIUM | `POS-Stery/.../postgres/store_repository.go:73` | `ListByTenant` returned soft-deleted stores. | Added `AND deleted_at IS NULL`. |
| MEDIUM | `HRIS-Stery/apps/web/src/routes/(auth)/login/+page.svelte` | The form stayed disabled after a failed login, and `form: any` failed lint. | `use:enhance` now resets `loading` after `update()`. Typed with `ActionData`. |
| MEDIUM | `HRIS-Stery/apps/web/src/routes/403.svelte` | Not a route, so the hook's 403 redirect returned a 404. | Moved to `src/routes/(app)/403/+page.svelte`. |
| MEDIUM | POS admin/cashier `package-lock.json` | Stale after the kit gained dependencies. | Reinstalled. SELA was already up to date. |

## Open HIGH (pre-existing; product/design decisions, not fixed)

HRIS-Stery:
- `services/auth/.../token_service.go`: refresh rotation is a non-atomic `Exists` followed by `Del`, so a token can be replayed. Refresh does not reload roles or tenant status. `IsRefreshTokenRevoked` swallows errors.
- `services/document`: any employee can list and download any document (no ownership or classification check).
- `services/notification/.../email_adapter.go`: no `StartTLS` on port 587, so credentials go out in plaintext. `PUT /notification-channels/{channel}` wipes the other channels and `email_config`.
- `services/leave`: balance writes are absolute (lost update). The status UPDATE has no status guard. Overlapping leave is never checked. A manager can approve their own leave.
- `services/audit`: `audit.entries` has no RLS. Partitions end 2027-12 with no DEFAULT partition.
- `deploy/docker/init-postgres.sql` hardcodes the app role password. `docker-compose.production.yml` connects as the superuser.

POS-Stery:
- `services/sales`: the server trusts the client's `unit_price` and discounts. The `GetReport` store branch is missing GROUP BY (Postgres error 42803).
- `services/customer`: a cashier can mint loyalty points, and there is no `UNIQUE (tenant_id, sale_id)`.
- `services/inventory`: stock can go negative (check-then-update, no CHECK constraint).
- `services/supplier`: `receive_stock` is not atomic and double counts.
- `services/product`: `category_id` can point to another tenant, because the FK bypasses RLS.
- `services/auth`: refresh `Rotate` ignores rows affected. A cashier whose role has no store gets an unvalidated `sid` from the request.

## Open MEDIUM/LOW highlights
- Kit:
  - `ratelimit`: INCR/EXPIRE are not atomic.
  - JWT: no `iss`/`aud` check.
  - `events`: no XAutoClaim.
  - `session.ts`: no XFF forwarding and no fetch timeout.
  - UI: toast store is an SSR singleton; `Button` anchor fires `onclick` when disabled; `AppShell` drawer is not `inert`.
- HRIS web: `$:`-wrapped `createQuery` (runtime unverified), division by zero when `entitled_days` = 0, UTC date off-by-one, no `exp` check in `claimsFromToken`, 18 remaining ESLint errors (mostly unused vars in `tests/e2e`).
- POS: `.env.example` contains an unexpanded `${DB_USER}`; tests run as a superuser, so RLS is untested; missing FK indexes; admin/cashier have no ESLint config (pre-existing).
- SELA: the CI kit checkout is not pinned to a `ref`; `db.Fingerprint()` is dead code.

## Validation (after fixes)

| Check | Result |
|---|---|
| `go build` + `go vet` (kit, HRIS, POS, SELA) | pass |
| `go test` kit `./authn/...`, HRIS `./services/auth/...` | pass |
| HRIS web: svelte-check / vitest / build | 0 errors / 15 tests passed / build OK |
| POS admin, POS cashier: svelte-check + build | 0 errors, both build |
| SELA web: svelte-check | 0 errors |
| POS `ci.yml` YAML parse; kit checkout in all 3 jobs | pass |
| Docker build from suite root: HRIS, POS | pass |
| Docker build from suite root: SELA | COPY steps for the build context pass; `go mod download` failed on a proxy.golang.org `unexpected EOF` (network), so the image itself did not build |

CI stays red until `stery-kit` gets its first push to `Briyantama/stery-kit`.
