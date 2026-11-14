# Analisis Dampak dan Risiko

*Analisis dampak, risiko, dan opsi arsitektur untuk menjual HRIS-Stery, POS-Stery, dan SELA sebagai paket Stery Suite*

|                         |                                                                                                                                                                  |
|-------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Nama Dokumen**        | Analisis Dampak dan Risiko - Stery Suite                                                                                                                         |
| **Versi**               | 1.0 (Draft)                                                                                                                                                      |
| **Tanggal**             | 6 November 2026                                                                                                                                                  |
| **Disusun oleh**        | Tim Produk & Engineering                                                                                                                                         |
| **Status**              | Draft untuk ditinjau                                                                                                                                             |
| **Dokumen Terkait**     | BRD_Stery_Suite, PRD_Stery_Suite, FSD_Stery_Suite, BRD_HRIS, PRD_HRIS, FSD_HRIS, BRD_POS, FSD_POS, `POS-Stery/PRD.md`, BRD/PRD/FSD Sela (v2.5 / v2.5 / v2.55)    |
| **Perubahan dari vX**   | Dokumen pertama                                                                                                                                                  |

## 1. Ringkasan dan rekomendasi

Pemilik ingin menjual tiga produk (HRIS-Stery, POS-Stery, SELA) sebagai paket: ketiganya, dua dari tiga, atau satu saja; setiap produk dapat berjalan mandiri atau terintegrasi; produk baru dapat ditambahkan kemudian. Pemilik sudah memutuskan tiga hal: (1) struktur = polyrepo ditambah repo platform baru `stery-suite`; (2) stack, pola, desain sistem, dan arsitektur seluruh suite = milik SELA; (3) semua dokumen baru tersedia dalam bahasa Indonesia dan Inggris. Lingkup pekerjaan ini adalah **dokumen saja**: tidak ada kode sumber yang diubah di repo mana pun.

**Rekomendasi (verdict): compose, do not consolidate; stack SELA sebagai standar.** Tiga produk tetap menjadi tiga unit deploy dengan basis data terpisah (D-SUI-01). Unit deploy keempat, platform `stery-suite`, memegang organisasi/identitas, entitlement, billing, notification hub, audit sink, dan konsol. Kode Go bersama hidup di `stery-suite/kit`, diangkat dari paket `internal/` SELA. Setiap produk punya dua mode, `STERY_MODE=standalone|suite` (D-SUI-02), sehingga penjualan produk tunggal tidak berubah perilakunya. HRIS dan POS dispesifikasikan ulang ke stack SELA melalui alur kerja bertahap S0-S5 (D-SUI-12); semua keputusan D-SUI-01 sampai D-SUI-12 didefinisikan di BRD_Stery_Suite bagian 9.1.

Temuan pendorong rekomendasi (rincian dan bukti di bagian 3-6):

- **Tidak ada fondasi bersama.** Tidak ada satu pun repo yang memiliki SSO, entitlement, lisensi, langganan/billing suite, atau tabel/kode/event bersama (RISK-SUI-01). SELA tidak mengenal tenant/organisasi, tidak memakai RLS, dan tidak punya jalur identitas eksternal; entitlement SELA berupa kolom `events.package` -> tabel `plans`, tidak ada entitlement untuk bundel.
- **Kondisi tiga repo tidak setara.** SELA paling matang (427 commit, 76 dari 105 task Completed menurut tracker per 2026-10-25) tetapi belum lulus gerbang closed-beta; POS memiliki enam layanan gRPC nyata tetapi sejumlah cacat integrasi; HRIS memiliki cacat yang membuat sistem belum bisa dipakai nyata (migrasi absensi tidak valid, gateway HTTP tidak pernah di-mount, login web masih mock).
- **Penyelarasan stack = penulisan ulang lapisan infrastruktur/antarmuka** HRIS dan POS (gRPC mikroservis + NATS + JWT + sqlc/zap/golang-migrate menjadi satu modul Go + outbox + sesi opaque + pgx/slog/goose). Lapisan domain dan application dipertahankan (bagian 6).
- **Kapasitas tim terbatas**: satu penyelarasan dalam satu waktu (RISK-SUI-08), dan setiap penyelarasan ditutup oleh gerbang stabilisasi produknya (bagian 7).

## 2. Metode dan bukti

**Sumber.** Pembacaan statis tiga repo dan dokumen yang ada: `SELA` (cabang `feat/strip-templates`, 427 commit, commit terakhir 2026-10-26), `POS-Stery` (cabang `development`, 21 commit, terakhir 2026-06-30), `HRIS-Stery` (cabang `development`, 33 commit, terakhir 2026-06-10). Hitungan commit dan tanggal dibaca dari `git` pada 6 November 2026. Prinsip: **kode adalah kebenaran**; dokumen status yang bertentangan dengan kode dicatat sebagai "Kontradiksi" (bagian 3), tidak diulang sebagai fakta.

**Provenance klaim.** Klaim dasar dari perencana ditandai [V] (diverifikasi perencana) atau [S] (dilaporkan scout). Penulis dokumen ini membaca ulang setiap path yang dikutip sebelum menegaskannya. Klaim [S] yang ternyata keliru dikoreksi di bagian 3.4.

**Aturan bukti.** Setiap pernyataan tentang kondisi saat ini membawa status dari himpunan {Selesai, Sebagian, Belum, Pending Verification, Ditunda} dan path repo relatif di kolom `Bukti`. Nilai bisnis yang tidak ditemukan di repo (harga, SLA, kuota, ukuran pasar, data kompetitor, target KPI) ditulis literal `tbd` dan menjadi pertanyaan terbuka (bagian 8). Hanya harga paket SELA yang boleh berupa angka. Estimasi ditandai `[INFERENCE]`. Rahasia yang ter-commit hanya disebut path-nya, tidak pernah nilainya.

**Yang tidak dijalankan.** Lihat Lampiran B: tidak ada build, test, linter, migrasi, atau layanan yang dijalankan; semua angka adalah hasil pembacaan statis.

## 3. Progres per repo

Estimasi kesiapan di bawah ini bukan hasil pengukuran; seluruhnya `[INFERENCE]` dan hanya dipakai untuk urutan kerja.

### 3.1 SELA

Estimasi kesiapan menuju closed-beta: sekitar 75% `[INFERENCE]` (dasar: 76 dari 105 task Completed, tetapi 20 task Pending Verification termasuk jalur pembayaran, dan penayangan publik belum terbukti).

| Area | Status | Temuan | Bukti |
| --- | --- | --- | --- |
| Struktur modul | Selesai | Satu modul Go `apps/api` (go 1.25.1); `services/{auth,event,media,payment,instant,rbac}`; `internal/{audit,piicrypt,objstore,httpx,config,db,testdb,health}`; 29 migrasi goose (`0001`..`0029`) | `SELA/apps/api/go.mod`, `SELA/apps/api/services`, `SELA/apps/api/internal`, `SELA/apps/api/internal/db/migrations` |
| Transport | Selesai | REST `/api/v1` dan gRPC untuk auth dan event (`auth.proto`, `event.proto`) | `SELA/apps/api/api/proto/v1/auth.proto`, `SELA/apps/api/api/proto/v1/event.proto` |
| Async | Selesai | Worker ticker dalam proses; outbox DB `notifications` dan `instant_outbox` | `SELA/apps/api/internal/db/migrations/0008_notifications.sql`, `SELA/apps/api/internal/db/migrations/0029_instant_mode.sql`, `SELA/apps/api/services/instant/jobs.go` |
| Tracker | Sebagian | 105 task: 76 Completed, 20 Pending Verification, 9 Not Started (6 penanda milestone M2.1-M7.1 dan BL.1 notifikasi, BL.2 Hall of Fame, BL.3 instan); data per 2026-10-25 | `SELA/docs/tracking/tracker.json` |
| Identitas | Selesai | Hanya OTP email dan cookie `sela_session`; tidak ada jalur identitas eksternal/SSO | `SELA/apps/api/services/auth/http.go`, `SELA/apps/api/services/auth/service.go` |
| Tenant / organisasi | Belum | Tidak ada konsep tenant, organisasi, atau RLS: pencarian `tenant` dan `ROW LEVEL SECURITY` di migrasi tidak menghasilkan temuan | `SELA/apps/api/internal/db/migrations` |
| Entitlement | Sebagian | Entitlement = `events.package` -> `plans`, ditulis oleh webhook pembayaran (`UPDATE events ... FROM plans`); hanya per-event, tidak ada entitlement organisasi atau bundel | `SELA/apps/api/services/payment/postgres.go`, `SELA/apps/api/internal/db/migrations/0011_plans_transactions.sql` |
| Paket dan harga | Selesai | `plans`: Gratis guest_cap 30 / retensi 7; Hemat 80 / 30; Standar 200 / 365 (video, zip_full_resolution); Premium tanpa batas tamu / 730; partner tanpa batas / tidak pernah kedaluwarsa. Harga hanya di env `PLAN_PRICE_IDR_{HEMAT,STANDAR,PREMIUM}` = 39000 / 129000 / 350000 (Rp39.000 / Rp129.000 / Rp350.000; Gratis Rp0) | `SELA/.env.example`, `SELA/apps/api/internal/config/config.go`, `SELA/apps/api/internal/db/migrations/0011_plans_transactions.sql`, `SELA/apps/api/internal/db/migrations/0015_plan_retention_policy.sql` |
| Penegakan `guest_cap` | Selesai | Dikoreksi dari baseline: `CreateSession` menerima `guestCap` dan menolak di batas (`n >= *guestCap`) | `SELA/apps/api/services/media/postgres.go` |
| Penegakan `video` | Selesai | Dikoreksi dari baseline: `upload.go` menolak video dengan `ErrVideoNotInPlan` bila paket tidak memuat video | `SELA/apps/api/services/media/upload.go`, `SELA/apps/api/services/media/service.go` |
| Penegakan `zip_full_resolution` | Belum | Bendera hanya dibaca di layanan pembayaran (daftar paket); ekspor ZIP selalu mengalirkan objek asli, tidak membaca bendera | `SELA/apps/api/services/media/export.go`, `SELA/apps/api/services/payment/http.go` |
| Pembayaran | Pending Verification | Provider `sandbox` dan `midtrans` (QRIS Core API); Xendit sudah dihapus pada 14 Oktober 2026; webhook Midtrans belum pernah diuji dengan akun sungguhan melalui URL publik (lembar pemilik C3, T29.1) | `SELA/apps/api/services/payment/midtrans.go`, `SELA/apps/api/services/payment/provider.go`, `SELA/docs/verification/owner-decisions.md`, `SELA/docs/aidlc/intents/261014-closed-beta-readiness/10-lembar-jawaban-pemilik.md` |
| Retensi | Sebagian | Konflik: owner-decisions A8 menyatakan retensi berbasis `plans` aktif di semua lingkungan, sedangkan tracker T18.3 menyatakan "Retention is opt-in" (tidak ada penghapusan kecuali `RETENTION_DAYS_*` diset); kode memakai `plans.retention_days` | `SELA/docs/verification/owner-decisions.md`, `SELA/docs/tracking/tracker.json`, `SELA/CLAUDE.md` |
| Origin media terpisah | Pending Verification | Penjaga konfigurasi `MEDIA_ORIGIN_REQUIRED` ada (FSD FR-SEC.1, v2.49) tetapi pemisahan origin pada deployment sungguhan belum terbukti | `SELA/docs/FSD_Sela.md`, `SELA/apps/api/internal/config/config.go` |
| Mode instan | Pending Verification | T38.1 dibangun (migrasi 0029, `services/instant`) tetapi berstatus Pending Verification; retensi berbayar T38.1 dan upgrade FR-10.7 belum dibangun | `SELA/docs/tracking/tracker.json`, `SELA/apps/api/services/instant/service.go` |
| Hosting | Pending Verification | API berjalan di mesin pengembangan lewat tunnel ngrok; belum dijalankan end-to-end dengan tamu sungguhan | `SELA/deploy/README.md` |
| Infrastruktur | Sebagian | `deploy/docker-compose.yml` memakai image `:latest` untuk Dragonfly, RustFS, aws-cli (ClamAV `stable`); PostgreSQL tidak ada di compose | `SELA/deploy/docker-compose.yml` |
| Gerbang kualitas | Selesai | `scripts/check.sh` (stage `go web e2e`, `CHECK_STAGES`), workflow `ci.yml`; 774 fungsi `Test*` Go (hitungan statis); namun T18.1 mencatat tidak ada satu pun run `check.sh` penuh yang keluar 0 | `SELA/scripts/check.sh`, `SELA/.github/workflows/ci.yml`, `SELA/docs/tracking/tracker.json` |

**Task Pending Verification (20, per tracker 2026-10-25):** T11.3, T15.1, T16.1, T17.1, T18.1, T18.2, T18.3, T19.1, T19.2, T19.3, T19.4, T20.1, T23.1, T25.1, T26.1, T27.1, T28.1, T29.1, T37.1, T38.1 (bukti: `SELA/docs/tracking/tracker.json`).

**Kontradiksi dokumen status vs kode/dokumen lain (SELA):**

| # | Kontradiksi | Yang ditunjukkan kode / dokumen | Bukti |
| --- | --- | --- | --- |
| K-1 | Lembar pemilik D2 menyebut "56 task Pending Verification" | Tracker memuat 20 task Pending Verification (76 Completed, 9 Not Started) | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/10-lembar-jawaban-pemilik.md`, `SELA/docs/tracking/tracker.json` |
| K-2 | Owner-decisions A8 (retensi aktif) vs tracker T18.3 (retensi opt-in) | Kode memakai `plans.retention_days`; keputusan pemilik belum dicatat sebagai satu pernyataan tunggal | `SELA/docs/verification/owner-decisions.md`, `SELA/docs/tracking/tracker.json` |
| K-3 | Rujukan versi usang di FSD: baris 67, 1351, 1444 menyebut "v2.1" | FSD kini v2.55, BRD v2.5 | `SELA/docs/FSD_Sela.md` |
| K-4 | PRD baris 208 menyebut "BRD v2.1"; header PRD merujuk FSD v2.54 | FSD kini v2.55 | `SELA/docs/PRD_Sela.md` |
| K-5 | Catatan vault `Projects/SELA.md` masih menyebut Xendit | Xendit dihapus 14 Oktober 2026; catatan tersebut berada di luar repo dan tidak dibaca ulang (dilaporkan perencana) | `SELA/docs/verification/owner-decisions.md` |

### 3.2 POS

Estimasi kesiapan: sekitar 55% `[INFERENCE]` (enam layanan gRPC nyata dan 79 fungsi `Test*`, tetapi integrasi antarlayanan dan CI belum sehat).

| Area | Status | Temuan | Bukti |
| --- | --- | --- | --- |
| Layanan gRPC | Selesai | Enam layanan nyata: auth, product, inventory, sales, supplier, customer; 79 fungsi `Test*` di 12 berkas (hitungan statis) | `POS-Stery/services/auth-service`, `POS-Stery/services/product-service`, `POS-Stery/services/inventory-service`, `POS-Stery/services/sales-service`, `POS-Stery/services/supplier-service`, `POS-Stery/services/customer-service` |
| Gateway HTTP | Sebagian | Gateway adalah Go `chi` (bukan Laravel); permukaan REST adalah subset operasi proto: tidak ada `GetSale`, `ReceiveStock`, daftar PO, loyalty, threshold, auth refresh | `POS-Stery/services/api-gateway/cmd/server/main.go` |
| Loyalitas | Belum | `AddLoyaltyPoints` terdefinisi di customer-service tetapi **tidak ada pemanggil** di layanan mana pun | `POS-Stery/services/customer-service/internal/application/commands/add_loyalty_points.go`, `POS-Stery/services/sales-service` |
| Event NATS | Belum | Paket NATS bersama ada (envelope, stream, JetStream) tetapi tidak ada subscriber di layanan mana pun; `AI.OrderForecasted` tidak punya publisher | `POS-Stery/services/_shared/nats/streams.go`, `POS-Stery/services/_shared/nats/jetstream.go` |
| Alur penjualan | Sebagian | Saga sinkron: validasi -> kurangi stok (dengan kompensasi) -> simpan -> publish; tidak ada kunci idempotensi; tidak ada penyimpanan PPN di domain penjualan | `POS-Stery/services/sales-service/internal/application/commands/create_sale.go` |
| Dashboard admin | Sebagian | Bauran pembayaran dipalsukan 55/30/15 (cash/qris/debit) sebagai fallback bila API tidak mengembalikan `payment_mix` | `POS-Stery/apps/admin/src/routes/(app)/dashboard/+page.svelte` |
| CI | Sebagian | `ci.yml` usang: job Laravel gateway, Go 1.24 padahal modul layanan memakai go 1.25.0, memanggil `scripts/migrate-validate.sh` (berkas ada), `npm --filter` gaya pnpm | `POS-Stery/.github/workflows/ci.yml`, `POS-Stery/scripts/migrate-validate.sh`, `POS-Stery/services/Dockerfile.base` |
| Rahasia ter-commit | Sebagian | Berkas ter-commit memuat nilai rahasia/kredensial lemah (nilai tidak dikutip): konfigurasi PM2 dan skrip init Postgres | `POS-Stery/ecosystem.config.cjs`, `POS-Stery/deploy/docker/init-postgres.sql` |
| RLS | Sebagian | 15 kebijakan RLS; `FORCE ROW LEVEL SECURITY` ada di tiap migrasi layanan; 7 kebijakan tanpa `WITH CHECK`: `customer.loyalty_points`, `inventory.stock_thresholds`, `product.categories`, `sales.sale_items`, `sales.receipts`, `supplier.purchase_orders`, `supplier.purchase_order_items` (hitungan regex statis) | `POS-Stery/services/customer-service/migrations/000001_create_customer_schema.up.sql`, `POS-Stery/services/inventory-service/migrations/000001_create_inventory_schema.up.sql`, `POS-Stery/services/product-service/migrations/000001_create_product_schema.up.sql`, `POS-Stery/services/sales-service/migrations/000001_create_sales_schema.up.sql`, `POS-Stery/services/supplier-service/migrations/000001_create_supplier_schema.up.sql` |
| Tes integrasi Postgres | Belum | Tidak ada tes yang merujuk `TEST_DATABASE`/testcontainers (pencarian statis) | `POS-Stery/services` |
| Autentikasi | Selesai | Login bcrypt, JWT dengan klaim `tid`, `sid`, `role`; gateway memasang JWT -> Tenant -> Store; peran `admin`, `cashier`, `stock_manager` | `POS-Stery/services/auth-service/internal/application/commands/login.go`, `POS-Stery/services/api-gateway/cmd/server/main.go` |
| Web | Sebagian | Dua aplikasi SvelteKit: `apps/admin` (dashboard, produk, inventaris, pemasok, pelanggan, laporan) dan `apps/cashier` (kasir, struk) dengan `service-worker.ts`; keduanya memakai proxy BFF `+server.ts` di bawah `routes/api` yang menyimpan token di cookie httpOnly sisi server; `X-Store-ID` untuk admin hanya disebut di komentar proxy dan tidak ada kode klien yang mengaturnya (pemilih toko admin belum ada, pencarian statis) | `POS-Stery/apps/admin/src/routes`, `POS-Stery/apps/cashier/src/routes`, `POS-Stery/apps/cashier/src/service-worker.ts` |
| Transport gRPC | Selesai | Plaintext secara sengaja, terdokumentasi | `POS-Stery/docs/security/grpc-transport-security.md` |

**Kontradiksi dokumen status vs kode (POS):**

| # | Kontradiksi | Yang ditunjukkan kode | Bukti |
| --- | --- | --- | --- |
| K-6 | `PRD.md` bagian 10 (baris 195) menyebut "Laravel gateway for auth and HTTP API" | Gateway adalah Go `chi` | `POS-Stery/PRD.md`, `POS-Stery/services/api-gateway/cmd/server/main.go` |
| K-7 | `ci.yml` masih memuat job Laravel dan Go 1.24 | Gateway Go `chi`; modul layanan go 1.25.0 | `POS-Stery/.github/workflows/ci.yml`, `POS-Stery/services/api-gateway/go.mod` |
| K-8 | Dashboard menampilkan bauran pembayaran seolah data | Angka 55/30/15 adalah fallback buatan | `POS-Stery/apps/admin/src/routes/(app)/dashboard/+page.svelte` |

### 3.3 HRIS

Estimasi kesiapan: sekitar 40% `[INFERENCE]` (selaras dengan skor 45/100 pada `docs/PHASE5_SUMMARY.md` tertanggal 2026-06-08, yang tidak diverifikasi ulang di sini). Alasan: domain/application banyak, tetapi tidak ada alur dari browser ke basis data yang berjalan.

| Area | Status | Temuan | Bukti |
| --- | --- | --- | --- |
| Layanan gRPC | Sebagian | 47 RPC pada 8 proto; 39 punya handler nyata. employee 8 dari 10 (`UpdateEmployee`, `GetOrgChart` tidak ada); document 5 dari 7 (`DownloadDocument` mengembalikan URL kosong, `GetPresignedUrl` dan `RollbackDocumentVersion` kosong); ai-service: proto 3 RPC, direktori `cmd/server` kosong | `HRIS-Stery/proto/hris/employee/v1/employee.proto`, `HRIS-Stery/services/employee-service/internal/interfaces/grpc/employee_service.go`, `HRIS-Stery/services/document-service/internal/interfaces/grpc/document_service.go`, `HRIS-Stery/proto/hris/ai/v1/ai.proto`, `HRIS-Stery/services/ai-service/cmd/server` |
| Migrasi absensi | Belum | `001_create_attendance_schema.up.sql` baris 25: `CONSTRAINT attendance_unique_per_day UNIQUE (...) WHERE NOT is_override` **tidak valid di PostgreSQL** (UNIQUE constraint tidak boleh memakai klausa WHERE; harus berupa unique index parsial); baris 45-46 `GRANT ... TO app` memakai peran `app` (bukan `hris_app` seperti migrasi auth); RLS hanya `ENABLE` tanpa `FORCE`, kebijakan tanpa `WITH CHECK` | `HRIS-Stery/services/attendance-service/migrations/001_create_attendance_schema.up.sql`, `HRIS-Stery/services/auth-service/migrations/001_create_auth_schema.up.sql` |
| Jalur HTTP | Belum | Tidak ada `http.ListenAndServe`/`NewServeMux` di `services/**` di luar `*.pb.gw.go`; jalur grpc-gateway yang dipanggil gateway Laravel tidak pernah di-mount | `HRIS-Stery/services`, `HRIS-Stery/docs/adr/0001-grpc-gateway-over-grpc-php.md` |
| Login web | Belum | `+page.server.ts` baris 38-40 memanggil `http://localhost:3000/api/auth/login` dengan komentar "mocked for now" | `HRIS-Stery/apps/web/src/routes/(auth)/login/+page.server.ts` |
| Gateway Laravel | Sebagian | Hanya rute `auth/*` dan cuti (`leaves`, `leave-balance`, `leave-types`); rute karyawan/absensi/dokumen/audit hanya berupa komentar placeholder; tidak ada penggunaan `throttle` di `routes/api.php` | `HRIS-Stery/apps/api-gateway/routes/api.php` |
| Web | Sebagian | Halaman: `/`, `(auth)/login`, `(app)/dashboard`, `(app)/leaves/apply`, `(app)/admin/leaves`; token juga disimpan di sisi klien (`stores/auth.ts` memakai `localStorage`) | `HRIS-Stery/apps/web/src/routes`, `HRIS-Stery/apps/web/src/lib/stores/auth.ts` |
| Domain cuti | Sebagian | `Cancel` hanya menolak REJECTED dan CANCELLED, sehingga PENDING bisa dibatalkan walau `ErrCannotCancelPending` dideklarasikan; `ErrInsufficientLeaveBalance` ditegakkan di `leave_balance.go`; `ErrLeaveOverlapExists` dideklarasikan, penegakan tidak ditemukan di luar `errors.go` | `HRIS-Stery/services/leave-service/internal/domain/leave_request.go`, `HRIS-Stery/services/leave-service/internal/domain/errors.go`, `HRIS-Stery/services/leave-service/internal/domain/leave_balance.go` |
| Data pribadi | Belum | `national_id` (NIK) dan `tax_id` (NPWP) bertipe `TEXT`, `birth_date` bertipe `DATE`; komentar skema menyatakan "stored encrypted" tetapi tidak ada kode enkripsi di employee-service; tidak ada pernyataan UU PDP di repo | `HRIS-Stery/services/employee-service/migrations/001_create_employee_schema.up.sql` |
| Notifikasi | Sebagian | Adaptor email dibuat tetapi tidak dipasang (`_ = emailAdapter // Placeholder`) | `HRIS-Stery/services/notification-service/cmd/server/main.go` |
| Auth | Sebagian | Login bcrypt; `extractIPAddr` selalu mengembalikan `0.0.0.0` | `HRIS-Stery/services/auth-service/internal/domain/user.go`, `HRIS-Stery/services/auth-service/internal/interfaces/grpc/auth_service.go` |
| CI/CD | Sebagian | `cd-staging.yml` membangun api-gateway, web, auth, employee, attendance, leave, notification, audit, ai tetapi **tidak** document-service; `deploy/k8s/base` kosong | `HRIS-Stery/.github/workflows/cd-staging.yml`, `HRIS-Stery/deploy` |
| Tes | Sebagian | 131 fungsi `Test*` (statis); tidak ada tes berbasis Postgres/testcontainers | `HRIS-Stery/services` |
| Pekerjaan yang ditunda | Ditunda | Payroll, aturan pajak, rekrutmen, kinerja ditunda ke Phase 2 (ADR-0004, tanggal 2026-05-30) karena regulasi PPh 21, BPJS, THR | `HRIS-Stery/docs/adr/0004-defer-payroll-to-phase2.md` |
| Peristiwa | Sebagian | Event NATS (`hris.identity.user.registered` -> employee; `hris.workforce.employee.created` -> leave) dirancang; konsumen lain terbatas | `HRIS-Stery/docs/adr/0003-nats-jetstream-event-backbone.md` |
| Biner di working tree | Sebagian | Delapan `server.exe` (akar dan tujuh layanan) ada di disk; **tidak ter-commit** karena `.gitignore` memuat `*.exe` | `HRIS-Stery/.gitignore`, `HRIS-Stery/server.exe` |

**Kontradiksi dokumen status vs kode (HRIS):**

| # | Kontradiksi | Yang ditunjukkan kode | Bukti |
| --- | --- | --- | --- |
| K-9 | `PROJECT_PROGRESS.md` menyatakan Auth/Employee/Attendance/Leave/Notification "100% COMPLETE" dan "Production-ready"; `PHASE1_RELEASE.md` dan `IMPLEMENTATION_COMPLETE.md` serupa | Migrasi absensi tidak valid (baris 25), tidak ada HTTP mux terpasang, login web mock ke `localhost:3000`, `UpdateEmployee`/`GetOrgChart` tidak ada; `PHASE5_SUMMARY.md` (2026-06-08) memberi 45/100 | `HRIS-Stery/PROJECT_PROGRESS.md`, `HRIS-Stery/PHASE1_RELEASE.md`, `HRIS-Stery/IMPLEMENTATION_COMPLETE.md`, `HRIS-Stery/docs/PHASE5_SUMMARY.md` |
| K-10 | Komentar skema: NIK/NPWP "stored encrypted via application-level encryption" | Kolom `TEXT` polos; tidak ada kode enkripsi di employee-service | `HRIS-Stery/services/employee-service/migrations/001_create_employee_schema.up.sql` |

### 3.4 Koreksi terhadap klaim dasar [S]

Klaim berikut dibaca ulang dan ternyata berbeda dari baseline; dokumen turunan memakai versi koreksi.

| # | Klaim dasar [S] | Yang ditunjukkan kode | Bukti |
| --- | --- | --- | --- |
| C-1 | "`guest_cap`/`video`/`zip_full_resolution` tidak ditemukan ditegakkan di jalur media" | `guest_cap` dan `video` ditegakkan; hanya `zip_full_resolution` yang tidak dibaca di jalur ekspor | `SELA/apps/api/services/media/postgres.go`, `SELA/apps/api/services/media/upload.go`, `SELA/apps/api/services/media/export.go` |
| C-2 | "`server.exe` ter-commit" (HRIS) | Tidak ter-commit (diabaikan git); delapan biner ada di working tree | `HRIS-Stery/.gitignore` |
| C-3 | "CD (`cd-staging.yml`) tidak memuat audit/document/notification/ai" | Matriks CD memuat audit, notification, dan ai; hanya document-service yang tidak ada | `HRIS-Stery/.github/workflows/cd-staging.yml` |
| C-4 | "`birth_date` bertipe TEXT" | `birth_date` bertipe `DATE`; hanya NIK dan NPWP bertipe `TEXT` | `HRIS-Stery/services/employee-service/migrations/001_create_employee_schema.up.sql` |
| C-5 | "grpc POS 1.65" | Modul layanan POS memakai grpc v1.80.0; v1.65.0 hanya pada modul `_shared` | `POS-Stery/services/sales-service/go.mod`, `POS-Stery/services/_shared/go.mod` |
| C-6 | "Lembar pemilik menyebut 56 Pending Verification" | Dikonfirmasi (D2), berbeda dari 20 di tracker | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/10-lembar-jawaban-pemilik.md` |

**Kesenjangan lintas repo (dibaca ulang):** versi dependensi grpc 1.80.0 (POS, modul layanan) / 1.81.1 (HRIS) / 1.84.0 (SELA); pgx 5.6.0 / 5.9.2 / 5.11.0; nats.go 1.36.0 / 1.52.0 / tidak dipakai SELA; jwt/v5 5.2.1 (POS) / 5.3.1 (HRIS) / tidak dipakai SELA. Migrasi: golang-migrate (HRIS `Makefile`), skrip `migrate-helper.sh` (POS), goose 3.26.0 (SELA). sqlc hanya di HRIS (`sqlc.yaml`). Logging zap (HRIS, POS) vs slog (SELA). Redis `redis:7-alpine` (HRIS `docker-compose.production.yml`) vs Dragonfly (SELA). HRIS membawa OpenTelemetry dan Prometheus di `go.mod`; baseline SELA tidak (RISK-SUI-15). Bukti: `HRIS-Stery/services/auth-service/go.mod`, `HRIS-Stery/services/employee-service/go.mod`, `POS-Stery/services/auth-service/go.mod`, `SELA/apps/api/go.mod`, `HRIS-Stery/Makefile`, `POS-Stery/scripts/migrate-helper.sh`, `HRIS-Stery/services/auth-service/sqlc.yaml`, `HRIS-Stery/docker-compose.production.yml`.

## 4. Daftar risiko

Probabilitas dan dampak: T (tinggi), S (sedang), R (rendah), seluruhnya `[INFERENCE]`. Kolom Bukti hanya memuat path yang ada saat ini; risiko ke depan tanpa bukti kode ditulis "risiko ke depan".

| ID | Risiko | Bukti | Probabilitas | Dampak | Mitigasi | Pemicu |
| --- | --- | --- | --- | --- | --- | --- |
| RISK-SUI-01 | Tidak ada fondasi bersama untuk tenancy, identitas, entitlement, dan billing; suite tidak dapat dijual sebagai paket tanpa platform baru | `SELA/apps/api/services/auth/http.go`, `SELA/apps/api/services/payment/postgres.go`, `HRIS-Stery/services/auth-service`, `POS-Stery/services/auth-service` | T | T | Bangun platform `stery-suite` (IAM, ENT, BIL) sebagai langkah S1; produk delegasi lewat port | Penjualan paket pertama dijadwalkan sebelum S4 selesai |
| RISK-SUI-02 | SELA tidak punya konsep tenant/organisasi dan jalur identitas eksternal; menambah organisasi dapat memecah model host saat ini | `SELA/apps/api/internal/db/migrations/0001_hosts.sql` | T | S | Hanya tambah `hosts.org_id` dan `hosts.external_subject` nullable pada mode suite; tanpa RLS (D-SUI-08); mode standalone tak berubah | Permintaan fitur multi-pengguna per organisasi di SELA |
| RISK-SUI-03 | Penyelarasan HRIS/POS ke stack SELA adalah penulisan ulang lapisan infrastruktur/antarmuka dan memakan waktu | `HRIS-Stery/services/employee-service/internal/interfaces/grpc/employee_service.go`, `POS-Stery/services/sales-service/internal/application/commands/create_sale.go` | T | T | Pertahankan domain/application; rewrite bertahap S2 (POS) lalu S3 (HRIS) dengan gerbang stabilisasi | Estimasi bagian 6 meleset lebih dari satu tingkat (S/M/L) |
| RISK-SUI-04 | Regresi RLS saat berpindah ke `kit/tenantdb` (isolasi lintas tenant bocor) | `POS-Stery/services/sales-service/migrations/000001_create_sales_schema.up.sql`, `HRIS-Stery/services/attendance-service/migrations/001_create_attendance_schema.up.sql` | S | T | Wajib `ENABLE`+`FORCE`, `USING`+`WITH CHECK`, peran aplikasi NOBYPASSRLS, tes lintas tenant per modul | Satu tes lintas tenant gagal atau tidak ada untuk modul baru |
| RISK-SUI-05 | Konversi web HRIS/POS dari SSR ke SPA statis (SvelteKit `ssr=false`, `adapter-static`) | `HRIS-Stery/apps/web/src/routes/(auth)/login/+page.server.ts`, `POS-Stery/apps/cashier/src/hooks.server.ts` | S | S | Tiap produk satu `apps/web`; POS digabung ke grup rute `(admin)` dan `(cashier)`; PWA scope per area | Fitur bergantung pada `+page.server.ts`/hooks yang tidak punya padanan klien |
| RISK-SUI-06 | Semantik NATS -> outbox Postgres berubah (urutan, pengiriman ulang, konsumen idempoten) | `HRIS-Stery/docs/adr/0003-nats-jetstream-event-backbone.md`, `POS-Stery/services/_shared/nats/streams.go` | S | S | Outbox `FOR UPDATE SKIP LOCKED`, konsumen idempoten (`processed_events`), pengiriman at-least-once (D-SUI-06) | Event ganda atau hilang pada uji integrasi |
| RISK-SUI-07 | Blast radius dan UU PDP: unggahan publik SELA berdampingan dengan data NIK/NPWP HRIS pada infrastruktur bersama | `HRIS-Stery/services/employee-service/migrations/001_create_employee_schema.up.sql` | S | T | Basis data dan peran terpisah per produk, bucket dan kunci akses terpisah, `kit/piicrypt` untuk NIK/NPWP/birth_date, tinjauan hukum UU PDP | Satu cluster/host dipakai bersama tanpa pemisahan kredensial |
| RISK-SUI-08 | Tim kecil (solo): terlalu banyak pekerjaan berjalan bersamaan | `SELA/docs/tracking/tracker.json` | T | T | Satu penyelarasan dalam satu waktu (D-SUI-12); gerbang S0/S2/S3 harus ditutup sebelum lanjut | Dua alur kerja berjalan paralel lebih dari satu sprint |
| RISK-SUI-09 | Drift dokumen status: dokumen menyatakan selesai tetapi kode tidak | `HRIS-Stery/PROJECT_PROGRESS.md`, `HRIS-Stery/docs/PHASE5_SUMMARY.md`, `SELA/docs/aidlc/intents/261014-closed-beta-readiness/10-lembar-jawaban-pemilik.md` | T | S | Kebenaran = kode; kolom `Bukti` wajib; kontradiksi dicatat di FSD 11.3 | Dokumen status baru tanpa jalur bukti |
| RISK-SUI-10 | Harga HRIS/POS/bundel belum ditetapkan; tanpa harga tidak ada model bisnis yang dapat diuji | `SELA/.env.example` | T | S | Tetapkan harga sebagai keputusan pemilik (bagian 8); dokumen memakai `tbd` | Penawaran pertama ke calon pelanggan tanpa harga |
| RISK-SUI-11 | Platform menjadi titik kegagalan tunggal untuk mode suite | risiko ke depan | S | T | Snapshot entitlement bertanda tangan dengan masa tenggang (24 jam, `tbd`), cache introspeksi 30 detik, mode standalone tidak bergantung platform (D-SUI-03, D-SUI-04) | Insiden platform yang menghentikan login produk |
| RISK-SUI-12 | Rahasia dan biner ter-commit atau tersisa di working tree | `POS-Stery/ecosystem.config.cjs`, `POS-Stery/deploy/docker/init-postgres.sql`, `HRIS-Stery/server.exe` | T | T | Rotasi dan pembersihan riwayat git rahasia POS; hapus biner dari working tree HRIS; gerbang S2/S3 | Pemindaian rahasia menemukan nilai yang masih aktif |
| RISK-SUI-13 | Image `:latest` dan hosting di mesin pengembangan menghalangi build yang dapat direproduksi dan ketersediaan | `SELA/deploy/docker-compose.yml`, `SELA/deploy/README.md` | T | S | Pin tag/digest image; pilih hosting produksi (keputusan terbuka, bagian 8) | Rilis closed-beta ke tamu sungguhan |
| RISK-SUI-14 | Midtrans baru terbukti di sandbox; webhook publik belum teruji | `SELA/apps/api/services/payment/midtrans.go`, `SELA/docs/aidlc/intents/261014-closed-beta-readiness/10-lembar-jawaban-pemilik.md` | T | T | Gerbang S0: webhook terbukti pada URL publik; billing suite memakai abstraksi `payment.Provider` yang sama | Pembayaran nyata pertama gagal diaktifkan |
| RISK-SUI-15 | Celah observabilitas: baseline SELA hanya `slog` dan `/healthz`, sementara HRIS/POS memakai OpenTelemetry/Prometheus | `HRIS-Stery/services/auth-service/go.mod`, `SELA/apps/api/internal/health` | S | S | Keputusan pemilik terbuka (D-SUI-11); modul opsional `kit` | Insiden produksi tanpa metrik/trace yang cukup |

## 5. Opsi arsitektur

| Opsi | Deskripsi | Kelebihan | Kekurangan | Keputusan |
| --- | --- | --- | --- | --- |
| A. Polyrepo + platform | Tiga repo produk tetap utuh; repo baru `stery-suite` berisi platform dan `kit` bersama; produk punya `STERY_MODE` | Penjualan mandiri tidak berubah; blast radius terbatas; produk baru ditambahkan lewat Product Contract; tim dapat bergerak bertahap | Biaya sinkronisasi `kit` lintas repo; platform adalah komponen baru yang harus dibangun dan dioperasikan | **Dipilih** (D-SUI-01) |
| B. Monorepo | Satu repo untuk semua produk dan platform | Berbagi kode mudah; versi dependensi seragam | Memindahkan tiga riwayat git; pipeline CI tunggal untuk tim kecil; mengaburkan batas produk yang dijual terpisah | Tidak dipilih; dapat dikaji ulang bila `kit` terlalu mahal disinkronkan |
| C. Satu basis kode/runtime | Satu aplikasi dan satu basis data untuk seluruh suite | Fondasi bersama paling sederhana | Melanggar penjualan mandiri per produk; blast radius dan UU PDP (RISK-SUI-07); satu kegagalan menjatuhkan semua produk | **Ditolak** |

## 6. Dampak penyelarasan stack

Estimasi usaha S/M/L semuanya `[INFERENCE]`; skala ordinal, bukan hari kerja. Kolom `Bukti` menunjuk kondisi saat ini. Jalur tujuan ditulis di FSD masing-masing (bagian 2.7), bukan di sini.

### 6.1 SELA (sudah di stack standar; perubahan = adopsi `kit` dan mode suite)

| Kondisi saat ini -> pemetaan | Dapat dipakai ulang | Usaha | Bukti |
| --- | --- | --- | --- |
| `internal/{httpx,config,db,testdb,audit,piicrypt,objstore,health}` diangkat menjadi `stery-suite/kit` dan diimpor kembali oleh SELA (perilaku dipertahankan) | Seluruh paket sebagai sumber `kit` | M | `SELA/apps/api/internal` |
| Port `Identity`, `Entitlement`, `Notification`, `Audit`, `Events` dengan adapter lokal (standalone) dan adapter platform (suite) | `services/auth`, `services/payment`, `internal/audit` sebagai adapter lokal | M | `SELA/apps/api/services/auth/service.go`, `SELA/apps/api/services/payment/provider.go` |
| `hosts.org_id` dan `hosts.external_subject` nullable pada mode suite | Tabel `hosts` | S | `SELA/apps/api/internal/db/migrations/0001_hosts.sql` |
| Penyelesaian gerbang S0 (webhook, retensi, 20 Pending Verification, origin media, `zip_full_resolution`) | Seluruh basis kode | M | `SELA/docs/tracking/tracker.json` |

### 6.2 POS

| Kondisi saat ini -> pemetaan SELA | Dapat dipakai ulang | Usaha | Bukti |
| --- | --- | --- | --- |
| Enam layanan gRPC + gateway chi -> satu modul Go dengan paket `services/<nama>`, REST `/api/v1` di `net/http` ServeMux | Domain dan application tiap layanan | L | `POS-Stery/services/api-gateway/cmd/server/main.go`, `POS-Stery/services/sales-service` |
| Saga penjualan gRPC -> satu transaksi DB; loyalitas dipanggil dalam proses setelah commit | `create_sale.go` (aturan), `add_loyalty_points.go` | M | `POS-Stery/services/sales-service/internal/application/commands/create_sale.go`, `POS-Stery/services/customer-service/internal/application/commands/add_loyalty_points.go` |
| NATS -> outbox Postgres + konsumen idempoten | Envelope event (`event_envelope.go`) sebagai acuan skema | M | `POS-Stery/services/_shared/nats/event_envelope.go` |
| JWT (`tid`, `sid`, `role`) -> sesi opaque cookie; `store_id` menjadi atribut sesi; hash bcrypt dipertahankan | Perintah login dan peran | M | `POS-Stery/services/auth-service/internal/application/commands/login.go` |
| golang-migrate -> goose embedded; zap -> slog; Redis -> Dragonfly | Skema SQL (RLS sudah `FORCE`) setelah menambah `WITH CHECK` | M | `POS-Stery/services/customer-service/migrations/000001_create_customer_schema.up.sql` |
| Dua SPA (`apps/admin`, `apps/cashier`) -> satu `apps/web` dengan grup rute `(admin)` dan `(cashier)`; PWA kasir | Komponen UI dan service worker kasir | M | `POS-Stery/apps/admin/src/routes`, `POS-Stery/apps/cashier/src/service-worker.ts` |
| CI -> pola `check.sh`; rotasi rahasia; hapus data dashboard palsu | `Makefile` dan skrip migrasi sebagai acuan | S | `POS-Stery/.github/workflows/ci.yml`, `POS-Stery/scripts/migrate-validate.sh` |

### 6.3 HRIS

| Kondisi saat ini -> pemetaan SELA | Dapat dipakai ulang | Usaha | Bukti |
| --- | --- | --- | --- |
| Tujuh layanan gRPC + gateway Laravel -> satu modul Go, REST `/api/v1`; Laravel dihapus | Domain dan application (auth, employee, attendance, leave, notification, audit, document) | L | `HRIS-Stery/services`, `HRIS-Stery/apps/api-gateway/routes/api.php` |
| Melengkapi RPC yang hilang (`UpdateEmployee`, `GetOrgChart`, presign dan rollback dokumen) | Entitas dan repositori yang ada | M | `HRIS-Stery/services/employee-service/internal/interfaces/grpc/employee_service.go`, `HRIS-Stery/services/document-service/internal/interfaces/grpc/document_service.go` |
| Migrasi diperbaiki (constraint tidak valid, peran, `FORCE`, `WITH CHECK`) dan dipindah ke goose | Skema tabel | M | `HRIS-Stery/services/attendance-service/migrations/001_create_attendance_schema.up.sql` |
| sqlc -> pgx SQL mentah | Query SQL sebagai acuan | M | `HRIS-Stery/services/auth-service/sqlc.yaml` |
| NIK/NPWP/birth_date dienkripsi dengan `kit/piicrypt` (blind index untuk pencarian) | Kolom yang ada (migrasi data diperlukan) | M | `HRIS-Stery/services/employee-service/migrations/001_create_employee_schema.up.sql` |
| JWT -> sesi opaque; bcrypt dipertahankan; MinIO -> RustFS | Entitas pengguna dan peran | M | `HRIS-Stery/services/auth-service/internal/domain/user.go` |
| SvelteKit SSR -> SPA statis; login sungguhan; halaman karyawan dan absensi dibangun | Halaman dashboard dan cuti | M | `HRIS-Stery/apps/web/src/routes`, `HRIS-Stery/apps/web/src/lib/stores/auth.ts` |
| Payroll, pajak, rekrutmen, kinerja | Tidak ada (ditunda) | Ditunda per ADR-0004 | `HRIS-Stery/docs/adr/0004-defer-payroll-to-phase2.md` |

## 7. Gerbang stabilisasi dan roadmap S0-S5

Urutan (D-SUI-12): S0 dokumen + penutupan closed-beta SELA -> S1 ekstraksi `kit` (SELA mengadopsi `kit`, perilaku dipertahankan) + platform IAM/ENT -> S2 penyelarasan POS -> S3 penyelarasan HRIS -> S4 adapter mode suite di ketiga produk + billing + konsol -> S5 integrasi lintas produk + onboarding produk baru. Satu penyelarasan berjalan pada satu waktu; tiap penyelarasan berakhir di gerbang stabilisasi produknya.

| Tahap | Isi | Kriteria keluar |
| --- | --- | --- |
| S0 | Dokumen ini dan set BRD/PRD/FSD; penutupan closed-beta SELA | Gerbang SELA: (1) webhook Midtrans terbukti pada URL publik; (2) keputusan retensi default tercatat; (3) 20 Pending Verification ditutup atau ditunda secara sadar; (4) pemisahan origin media terverifikasi; (5) penegakan `guest_cap`/`video`/`zip_full_resolution` terverifikasi |
| S1 | Ekstraksi `kit`; platform IAM dan ENT | `kit` dipakai SELA dengan perilaku dipertahankan; kontrak proto `stery.platform.v1` tersedia |
| S2 | Penyelarasan POS | Gerbang POS: (1) loyalitas dipanggil dalam proses setelah commit penjualan; (2) paritas permukaan REST dengan operasi modul; (3) CI hijau dengan pola `check.sh` SELA; (4) RLS `WITH CHECK` pada setiap kebijakan; (5) rahasia ter-commit dirotasi dan dibersihkan; (6) tes integrasi Postgres berjalan; (7) data dashboard palsu dihapus; (8) keputusan PPN/struk tercatat |
| S3 | Penyelarasan HRIS | Gerbang HRIS: (1) semua migrasi up->down->up pada DB baru di CI; (2) login sungguhan lewat API; (3) update karyawan dan org chart terimplementasi; (4) presign/rollback dokumen terimplementasi dengan tes; (5) NIK/NPWP/birth_date terenkripsi dengan `kit/piicrypt`; (6) rate limit ditegakkan; (7) rahasia dan biner terhapus |
| S4 | Adapter mode suite di tiga produk + billing + konsol | Org dapat dibuat, memilih paket, login SSO, dan entitlement ditegakkan di tiap produk |
| S5 | Integrasi lintas produk dan onboarding produk baru | INT-1..INT-3 (hipotesis, validasi permintaan) dan Product Contract teruji dengan satu produk percobaan |

## 8. Keputusan terbuka untuk pemilik

Nilai default mengikuti keputusan terkait; dokumen turunan memakai `tbd` sampai pemilik memutuskan.

| # | Keputusan terbuka | Default yang dipakai dokumen | Dampak bila berubah |
| --- | --- | --- | --- |
| OQ-1 | Harga HRS, POS, bundel (`HRS+POS`, `HRS+SEL`, `POS+SEL`, `SUITE`), siklus penagihan, masa uji coba, aturan diskon bundel | `tbd` | BRD 7, FSD 4.03, tabel SKU |
| OQ-2 | Observabilitas: OpenTelemetry/Prometheus dalam baseline atau modul `kit` opsional (D-SUI-11) | Baseline = `slog` + `/healthz`; OTel/Prometheus opsional, `tbd` | NFR observabilitas, risiko RISK-SUI-15 |
| OQ-3 | Domain induk cookie `stery_session` (D-SUI-03) | `tbd` | Alur SSO dan konfigurasi Caddy |
| OQ-4 | Masa tenggang snapshot entitlement saat platform down (D-SUI-04) | 24 jam, dapat dikonfigurasi, `tbd` | NFR ketersediaan, perilaku degrade |
| OQ-5 | Hosting produksi (di luar mesin pengembangan + ngrok) | `tbd` | RISK-SUI-13, profil deploy |
| OQ-6 | Aturan bundel: apakah bundel mengunci SKU, apakah add-on mid-cycle diprorata | `tbd` | Model billing |
| OQ-7 | Handle pemilik modul Go untuk repo baru (default `Briyantama`, tidak terverifikasi) | `Briyantama` | Path modul di seluruh `go.mod` |
| OQ-8 | Keputusan retensi default SELA (K-2) dan PPN/struk POS | `tbd` | Gerbang S0 dan S2 |
| OQ-9 | Apakah INT-1..INT-3 benar-benar diminta pelanggan | Hipotesis, validasi permintaan | Lingkup S5 |
| OQ-10 | Segmen pelanggan target HRS, POS, dan paket suite (tidak ada pernyataan segmen di repo) | `tbd` | BRD 4.1, PRD 2 dan 8 |

## Lampiran A. Bukti terverifikasi

Path yang dibaca ulang pada 6 November 2026 untuk dokumen ini (seluruhnya ada di disk):

- SELA: `SELA/apps/api/go.mod`, `SELA/apps/api/services/payment/postgres.go`, `SELA/apps/api/services/payment/provider.go`, `SELA/apps/api/services/payment/midtrans.go`, `SELA/apps/api/services/auth/http.go`, `SELA/apps/api/services/media/postgres.go`, `SELA/apps/api/services/media/upload.go`, `SELA/apps/api/services/media/export.go`, `SELA/apps/api/internal/db/migrations/0011_plans_transactions.sql`, `SELA/.env.example`, `SELA/deploy/docker-compose.yml`, `SELA/deploy/README.md`, `SELA/scripts/check.sh`, `SELA/.github/workflows/ci.yml`, `SELA/docs/tracking/tracker.json`, `SELA/docs/verification/owner-decisions.md`, `SELA/docs/aidlc/intents/261014-closed-beta-readiness/10-lembar-jawaban-pemilik.md`, `SELA/docs/FSD_Sela.md`, `SELA/docs/BRD_Sela.md`, `SELA/docs/PRD_Sela.md`, `SELA/CLAUDE.md`.
- POS: `POS-Stery/PRD.md`, `POS-Stery/services/api-gateway/cmd/server/main.go`, `POS-Stery/services/sales-service/internal/application/commands/create_sale.go`, `POS-Stery/services/customer-service/internal/application/commands/add_loyalty_points.go`, `POS-Stery/apps/admin/src/routes/(app)/dashboard/+page.svelte`, `POS-Stery/.github/workflows/ci.yml`, `POS-Stery/ecosystem.config.cjs`, `POS-Stery/deploy/docker/init-postgres.sql`, `POS-Stery/services/_shared/nats/streams.go`, `POS-Stery/docs/security/grpc-transport-security.md`, migrasi `000001_*` pada tiap layanan.
- HRIS: `HRIS-Stery/services/attendance-service/migrations/001_create_attendance_schema.up.sql`, `HRIS-Stery/apps/web/src/routes/(auth)/login/+page.server.ts`, `HRIS-Stery/services/employee-service/internal/interfaces/grpc/employee_service.go`, `HRIS-Stery/services/document-service/internal/interfaces/grpc/document_service.go`, `HRIS-Stery/apps/api-gateway/routes/api.php`, `HRIS-Stery/services/employee-service/migrations/001_create_employee_schema.up.sql`, `HRIS-Stery/services/leave-service/internal/domain/leave_request.go`, `HRIS-Stery/.github/workflows/cd-staging.yml`, `HRIS-Stery/docs/adr/0004-defer-payroll-to-phase2.md`, `HRIS-Stery/docs/PHASE5_SUMMARY.md`, `HRIS-Stery/PROJECT_PROGRESS.md`, `HRIS-Stery/proto/hris`.

## Lampiran B. Hal yang tidak dijalankan

- Tidak ada build, `go test`, linter, formatter, migrasi, `docker compose`, atau layanan yang dijalankan di repo mana pun.
- Semua hitungan (commit, task tracker, RPC, fungsi `Test*`, kebijakan RLS) berasal dari pembacaan statis berkas dan perintah baca `git`; hitungan RLS memakai regex atas berkas migrasi.
- Tidak ada pemindaian rahasia otomatis; keberadaan nilai rahasia hanya dicatat berdasarkan pembacaan path tertentu, tanpa mengutip nilai.
- Klaim bahwa suatu kode "tidak dipanggil" atau "tidak ditemukan" adalah hasil pencarian teks, bukan analisis grafik panggilan.
- Catatan vault `Projects/SELA.md` berada di luar repo dan tidak dibaca ulang.
- Estimasi kesiapan, probabilitas, dampak, dan usaha S/M/L bersifat `[INFERENCE]`.
