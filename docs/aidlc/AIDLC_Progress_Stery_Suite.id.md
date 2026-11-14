# AI-DLC Progress: Stery Suite

Tanggal: 2026-11-14

Cara membaca: Summary memberi satu baris per repo; Stage map menunjukkan, per repo, stage AI-DLC mana yang punya bukti di disk; Requirements and tasks memuat angka hitungan; Open blockers mendaftar hal yang menghalangi eksekusi AI-DLC yang bersih. Path relatif terhadap root suite `C:/Users/solui/moon-eye/stery-suite`. Cara menjalankan engine ada di `docs/aidlc/AIDLC_Runbook_Stery_Suite.id.md`.

## Summary

Keempat modul produk memakai `go 1.27.3` dan keempat repo berada di branch `chore/go-1.27-pg-18.6`. "Uncommitted" menghitung baris `git status --short`; angka setelah tanda tambah adalah suntingan dari tugas dokumentasi ini sendiri (bagian Doc drift fixed on 2026-11-14).

| Repo | Branch | Commit terakhir | Berkas uncommitted | Intent dan fase | Hitungan requirement | Hitungan tracker | Blocker utama |
|---|---|---|---|---|---|---|---|
| SELA | `chore/go-1.27-pg-18.6` | 2026-11-09 | 14 (11 + 3) | `261014-closed-beta-readiness`: Inception, human review gate Open; B0 selesai, B1-B2 sudah dibangun tetapi belum diverifikasi, B3-B5 sudah di-merge (PR #8-#10), B6 dipindah ke B7, B7 belum dimulai, Operation belum dimulai | 66 requirement FSD: 45 Completed / 21 Partial | 105 task (as_of 2026-10-25): 76 Completed / 20 Pending Verification / 9 Not Started | Inception review gate Open; bukti perangkat nyata dan webhook Midtrans untuk B7 masih tertunda |
| POS-Stery | `chore/go-1.27-pg-18.6` | 2026-11-09 | 23 (20 + 3) | `261108-stack-align-sela`: Construction; B1-B5 selesai, build/test B6 selesai secara lokal, CI U8 sudah ditulis | 68 baris FSD: 11 Done / 32 Partial / 1 Pending Verification / 24 Not started | 22 task suite-tracker: 7 Completed / 3 In Progress / 5 Pending Verification / 7 Not Started | 18 temuan review High terbuka di seluruh repo (verdict BLOCK); temuan `unit_price` tampak sudah teratasi di kode saat ini (blocker a), verifikasi ulang sisanya |
| HRIS-Stery | `chore/go-1.27-pg-18.6` | 2026-11-09 | 15 (9 + 6) | `261108-stack-align-sela`: Construction; B1-B5 selesai, build/test B6 selesai secara lokal, CI U8 sudah ditulis | 75 baris FSD: 1 Done / 40 Partial / 1 Pending Verification / 33 Not started | 20 task suite-tracker: 10 Completed / 2 In Progress / 3 Pending Verification / 5 Not Started | 18 temuan High yang sama (HRIS: rotasi refresh tidak atomik, akses dokumen, cuti); cacat FSD belum diverifikasi ulang |
| stery-kit | `chore/go-1.27-pg-18.6` | 2026-11-09 | 25 (pekerjaan design-system) | tidak ada (tanpa `docs/aidlc`, tanpa intent) | n/a (tanpa FSD) | 1 task suite-tracker (S1.1 extract kit): Completed | Tidak ada intent atau catatan requirement; perubahan design-system belum di-commit |
| Suite root | `master` | 2026-11-14 | 9 entri (4 gitlink produk, 3 berkas tracker, `.aidlc/`, `docs/aidlc/`) | engine run `aidlc-20261114051752-6a2ffc`: scope `classic` (fallback, `scopeLocked:false`), brownfield, 3 stage disetujui, 15 pending | 102 baris FR-SUI: 0 Done / 5 Partial / 0 Pending Verification / 97 Not started | 64 task: 19 Completed / 7 In Progress / 12 Pending Verification / 26 Not Started | Gitlink tanpa `.gitmodules`; scope tetap `classic` sampai `/aidlc scope feature` |

## Stage map

Urutan stage mengikuti engine (`.aidlc/state.json`, `order`) tanpa tiga stage inisialisasi yang disetujui otomatis (workspace-scaffold, state-init, practices-discovery) dan refined-mockups; `operation` didaftar karena scope `feature` memuatnya. Status: `Done` = artefak dengan bukti ada; `Partial` = bukti ada tetapi bukan sebagai artefak khusus atau belum lengkap; `Missing` = tidak ada apa pun di disk.

### SELA

| Stage | Status | Path bukti |
|---|---|---|
| workspace-detection | Done | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/01-context.md` |
| reverse-engineering | Missing | - |
| requirements-analysis | Done | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/03-requirements.md` |
| user-stories | Missing | - |
| domain-design | Done | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/04-design-impact.md` |
| units-generation | Done | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/05-units-of-work.md` |
| contract-design | Partial | `SELA/docs/FSD_Sela.md` (bagian 6; tanpa berkas kontrak) |
| delivery-planning | Done | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/06-bolt-plan.md` |
| functional-design | Done | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/02-decisions.md` (D1-D9) |
| nfr-requirements | Partial | `SELA/docs/FSD_Sela.md` (tanpa berkas khusus) |
| nfr-design | Missing | - |
| infrastructure-design | Partial | `SELA/deploy`, `SELA/.github/workflows/ci.yml` |
| code-generation | Partial | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/aidlc-state.md` (B0-B5; B7 belum dimulai) |
| build-and-test | Partial | `SELA/scripts/check.sh`, `SELA/.github/workflows/ci.yml` (B1-B2 belum diverifikasi) |
| operation | Missing | - |

### POS-Stery

| Stage | Status | Path bukti |
|---|---|---|
| workspace-detection | Done | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/01-context.md` |
| reverse-engineering | Done | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/aidlc-state.md` (peta scout intent; tanpa Code KB) |
| requirements-analysis | Done | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/01-context.md`, `POS-Stery/PRD.md`, `POS-Stery/docs/BRD_POS.en.md`, `POS-Stery/docs/FSD_POS.en.md` |
| user-stories | Missing | - |
| domain-design | Missing | - |
| units-generation | Done | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/05-units-of-work.md` (U1-U10) |
| contract-design | Partial | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/05-units-of-work.md` (tabel rute; tanpa OpenAPI) |
| delivery-planning | Done | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/06-bolt-plan.md` (B0-B6) |
| functional-design | Done | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/02-decisions.md`, `POS-Stery/docs/adr` |
| nfr-requirements | Partial | `POS-Stery/docs/FSD_POS.en.md` (bagian NFR) |
| nfr-design | Missing | - |
| infrastructure-design | Partial | `POS-Stery/deploy`, `POS-Stery/apps/api/Dockerfile`, `POS-Stery/.github/workflows/ci.yml` |
| code-generation | Done | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/aidlc-state.md` (B1-B5; 18 temuan review High terbuka di seluruh repo, lihat `code-review-2026-11-08.md`) |
| build-and-test | Partial | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/aidlc-state.md` (B6 selesai secara lokal; bukti hanya di berkas state) |
| operation | Missing | - |

### HRIS-Stery

| Stage | Status | Path bukti |
|---|---|---|
| workspace-detection | Done | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/01-context.md` |
| reverse-engineering | Done | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/aidlc-state.md` (peta scout intent; tanpa Code KB) |
| requirements-analysis | Done | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/01-context.md`, `HRIS-Stery/docs/BRD_HRIS.en.md`, `HRIS-Stery/docs/PRD_HRIS.en.md`, `HRIS-Stery/docs/FSD_HRIS.en.md` |
| user-stories | Missing | - |
| domain-design | Partial | `HRIS-Stery/docs/adr/0005-single-module-go-api-on-sela-stack.md`, `HRIS-Stery/docs/adr/0006-dragonfly-streams-replace-nats-jetstream.md` |
| units-generation | Done | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/05-units-of-work.md` (U1-U10) |
| contract-design | Partial | `HRIS-Stery/docs/FSD_HRIS.en.md` (tabel RPC; proto dihapus) |
| delivery-planning | Done | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/06-bolt-plan.md` (B0-B6) |
| functional-design | Done | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/02-decisions.md`, `HRIS-Stery/docs/adr` |
| nfr-requirements | Partial | `HRIS-Stery/docs/FSD_HRIS.en.md` (bagian NFR) |
| nfr-design | Missing | - |
| infrastructure-design | Partial | `HRIS-Stery/deploy`, `HRIS-Stery/apps/api/Dockerfile`, `HRIS-Stery/.github/workflows/ci.yml` |
| code-generation | Done | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/aidlc-state.md` (B1-B5; 18 temuan review High terbuka di seluruh repo) |
| build-and-test | Partial | `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/aidlc-state.md` (B6 selesai secara lokal; bukti hanya di berkas state) |
| operation | Partial | `HRIS-Stery/docs/deployment/production.md`, `HRIS-Stery/.github/workflows/cd-staging.yml` |

### stery-kit

Tanpa intent dan tanpa `docs/aidlc`. Bukti requirement dan desain terbatas pada task tracker S1.1 (`docs/tracking/tracker.json`), `stery-kit/DESIGN.md` dan `stery-kit/PRODUCT.md`.

| Stage | Status | Path bukti |
|---|---|---|
| workspace-detection | Missing | - |
| reverse-engineering | Missing | - |
| requirements-analysis | Partial | `docs/tracking/tracker.json` (task KIT S1.1), `stery-kit/PRODUCT.md` |
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

| Stage | Status | Path bukti |
|---|---|---|
| workspace-detection | Done | `.aidlc/state.json` |
| reverse-engineering | Missing | - |
| requirements-analysis | Done | `docs/BRD_Stery_Suite.en.md`, `docs/PRD_Stery_Suite.en.md`, `docs/FSD_Stery_Suite.en.md` |
| user-stories | Missing | - |
| domain-design | Partial | `docs/00_Analisis_Dampak_Risiko.en.md` |
| units-generation | Partial | `docs/tracking/tracker.json` (milestone S0-S5) |
| contract-design | Missing | - |
| delivery-planning | Partial | `docs/00_Analisis_Dampak_Risiko.en.md` (bagian 7) |
| functional-design | Missing | - |
| nfr-requirements | Missing | - |
| nfr-design | Missing | - |
| infrastructure-design | Missing | - |
| code-generation | Missing | - |
| build-and-test | Missing | - |
| operation | Missing | - |

## Requirements and tasks

Dihitung ulang pada 2026-11-14. Rekap FSD menghitung sel Status pertama dari setiap baris `FR-` unik di FSD berbahasa Inggris; `python scripts/build_tracker.py --check` lulus (64 task, 315 requirement).

### FSD requirement rows

| FSD | Baris | Done | Partial | Pending Verification | Not started | Deferred |
|---|---|---|---|---|---|---|
| Suite (`docs/FSD_Stery_Suite.en.md`, FR-SUI) | 102 | 0 | 5 | 0 | 97 | 0 |
| POS (`POS-Stery/docs/FSD_POS.en.md`) | 68 | 11 | 32 | 1 | 24 | 0 |
| HRIS (`HRIS-Stery/docs/FSD_HRIS.en.md`) | 75 | 1 | 40 | 1 | 33 | 0 |

POS bergeser dari 30 Partial / 26 Not started menjadi 32 / 24 pada 2026-11-14: FR-POS-04.4 dan FR-POS-SEC.6 kini Partial, sesuai `requirement_overrides` di `docs/tracking/tracker.json`. Requirement SELA ada di `SELA/docs/tracking/tracker.json` (66 baris: 45 Completed / 21 Partial).

### Suite tracker tasks per milestone (`docs/tracking/tracker.json`, 64 tasks)

| Milestone | Task | Completed | In Progress | Pending Verification | Not Started |
|---|---|---|---|---|---|
| S0 | 6 | 1 | 2 | 3 | 0 |
| S1 | 5 | 1 | 0 | 1 | 3 |
| S2 | 21 | 7 | 3 | 5 | 6 |
| S3 | 19 | 10 | 2 | 3 | 4 |
| S4 | 9 | 0 | 0 | 0 | 9 |
| S5 | 4 | 0 | 0 | 0 | 4 |
| Total | 64 | 19 | 7 | 12 | 26 |

### SELA tracker tasks (`SELA/docs/tracking/tracker.json`, as_of 2026-10-25)

| Cakupan | Task | Completed | Pending Verification | Not Started |
|---|---|---|---|---|
| Semua milestone M1-M8 dan BL | 105 | 76 | 20 | 9 |

## Open blockers

| # | Blocker | Bukti |
|---|---|---|
| a | Verdict code review lokal adalah BLOCK dengan 18 temuan High terbuka. Contoh: rotasi refresh HRIS berupa `Exists` lalu `Del` yang tidak atomik; penjualan POS memercayai `unit_price` dan diskon dari klien; stok POS bisa menjadi negatif; `receive_stock` supplier POS terhitung ganda; poin loyalitas pelanggan POS bisa dicetak oleh kasir; `category_id` POS bisa menunjuk tenant lain. Catatan: FSD POS (yang diperbarui 2026-11-14) mencatat harga satuan sisi server sudah ada di `POS-Stery/apps/api/services/sales/infrastructure/price_port.go`, jadi verifikasi ulang temuan itu lebih dulu | `code-review-2026-11-08.md` |
| b | Inception human review gate SELA masih Open; uji perangkat nyata dan webhook Midtrans tertunda (B7); T7.2 butuh minimal 3 baris di `SELA/docs/tracking/usability_sessions.csv` | `SELA/docs/aidlc/intents/261014-closed-beta-readiness/aidlc-state.md`, `SELA/docs/tracking/usability_sessions.csv` |
| c | Secret POS (FR-POS-SEC.6, Partial): `POS-Stery/ecosystem.config.cjs` kini membaca secret dari `.env`; `deploy/docker/init-postgres.sql` lama dan `scripts/migrate-helper.sh` sudah tidak ada. Masih terbuka: riwayat git belum ditulis ulang dan rotasi nilai lama belum terbukti (task tracker S2.5, In Progress) | `POS-Stery/ecosystem.config.cjs`, `docs/tracking/tracker.json` |
| d | Cacat yang dikutip bagian 3-4 FSD HRIS (teks pra-konsolidasi; sekitar 250 path bukti layout lama belum diverifikasi ulang pada 2026-11-14): sintaks `UNIQUE ... WHERE` pada migrasi attendance, RLS tanpa FORCE pada attendance, leave dan notification, `hris_app` tidak punya INSERT pada `auth.tenants`, job integrasi CI terhubung sebagai `hris_admin` | `HRIS-Stery/docs/FSD_HRIS.en.md` |
| e | A1-A8 pada keputusan intent POS dan HRIS berstatus "Assumed" (status Open), belum dikonfirmasi pemilik | `POS-Stery/docs/aidlc/intents/261108-stack-align-sela/02-decisions.md`, `HRIS-Stery/docs/aidlc/intents/261108-stack-align-sela/02-decisions.md` |
| f | Empat repo membawa perubahan design-system yang belum di-commit (SELA 11, POS-Stery 20, HRIS-Stery 9, stery-kit 25 berkas sebelum suntingan tugas ini) | `git -C <repo> status --short` |
| g | Celah gitlink: pada commit suite yang sudah di-push (`Briyantama/stery-suite-saas`) `HRIS-Stery`, `POS-Stery`, `SELA`, `stery-kit` berupa gitlink (mode 160000) tanpa `.gitmodules`, sehingga clone baru mendapat empat folder kosong. Folder liar `stery-suite/` yang kosong dan untracked (berisi `HRIS-Stery/`) ada di root suite. Keputusan C9 ada di Runbook; tidak ada yang diubah | `docs/aidlc/AIDLC_Runbook_Stery_Suite.id.md` |

## Doc drift fixed on 2026-11-14

| Berkas | Perubahan |
|---|---|
| `POS-Stery/CLAUDE.md` | `Go 1.25.1` menjadi `Go 1.27.3` |
| `POS-Stery/docs/FSD_POS.en.md`, `POS-Stery/docs/FSD_POS.id.md` | Catatan status di bawah judul; sekitar 180 path bukti as-is dan prosa as-is untuk gRPC, NATS, gateway, harga yang dipercaya dari klien dan penerimaan PO ditulis ulang sesuai kode single-module saat ini (`apps/api/services/<x>/`, `cmd/api/{main,routes}.go`, `stery-kit/go/*`); komponen yang dihapus merujuk ke ADR-0001/0002; teks target-state tidak disentuh; FR-POS-04.4 dan FR-POS-SEC.6 ditetapkan Partial (harga satuan sisi server dan penolakan total negatif ada; tidak ada diskon terbatas per peran, D-POS-07 masih `tbd`); paritas EN dan ID (12 heading `##`, masing-masing 486 baris tabel) |
| `HRIS-Stery/CLAUDE.md` | `Go 1.25.1` menjadi `Go 1.27.3` |
| `HRIS-Stery/docs/PHASE5_SUMMARY.md`, `PHASE5_DEEP_CODE_REVIEW.md`, `PHASE5_ARCHITECTURE_REVIEW.md` | Banner `Superseded (2026-11-14)` ditambahkan di awal; isi tidak diubah |
| `HRIS-Stery/docs/FSD_HRIS.en.md`, `HRIS-Stery/docs/FSD_HRIS.id.md` | Catatan status dan satu kalimat pemetaan path di bawah konvensi bukti; bagian 2.2-2.5 dan baris FR-HRS-01.2, FR-HRS-SEC.6, NFR-HRS-08, `/login` disesuaikan dengan ADR-0005/0006; cacat "web login is a mock", "No HTTP mux is mounted" dan "gateway client does not pass the token" ditandai selesai (login kini mengirim ke `/api/v1/auth/login` dan menulis cookie `hris_session`); FR-HRS-01.2 tetap Partial (JWT, bukan sesi opaque); legenda berbahasa Inggris dinormalisasi menjadi `Done / Partial / Not started / Pending Verification / Deferred`; FSD berbahasa Indonesia mendapat blok "Implementation status 2026-11-08" yang sebelumnya tidak ada |
| `SELA/CLAUDE.md` | Versi FSD `v2.21` menjadi `v2.55` (BRD dan PRD tetap v2.5); `min Go 1.25.1` menjadi `Go 1.27.3` |
| `SELA/AGENTS.md` | `Go >= 1.25.1` menjadi `Go 1.27.3` |
| `SELA/docs/aidlc/intents/261014-closed-beta-readiness/aidlc-state.md` | Baris Basis: `FSD v2.39` menjadi `FSD v2.55`, tracker `as_of 2026-10-25` |
| `docs/tracking/README.md` | Baris "no commits yet" diganti dengan pernyataan repo saat ini; kalimat judul merujuk ke `SELA/docs/tracking/README.md` dan menyatakan rollup SELA membaca `SELA/docs/tracking/tracker.json` secara langsung |
| `docs/tracking/Stery_Suite_Progress_Tracker.xlsx`, `docs/tracking/traceability.csv` | Dibangkitkan ulang oleh `python scripts/build_tracker.py`; `tracker.json` tidak berubah (override FR-POS-04.4 sudah sama dengan nilai FSD) |

Drift yang sengaja dibiarkan:

- `docs/tracking/tracker.json` dan `SELA/docs/tracking/tracker.json`: baris tentang dokumen yang di-gitignore adalah teks task historis.
- Bagian 3-4 FSD HRIS dan tabel traceability: sekitar 250 path bukti layout lama (`services/<x>-service/...`, `apps/api-gateway/...`) ditandai sebagai riwayat oleh kalimat pemetaan path, tidak ditulis ulang.
- `HRIS-Stery/docs/FSD_HRIS.id.md`: legenda dan baris mempertahankan kata status berbahasa Indonesia (`Selesai / Sebagian / Belum / Ditunda`, padanan Inggris dalam tanda kurung); `scripts/build_tracker.py` hanya membaca berkas `.en.md`.
- `Go >= 1.25.1` pada baris STACK-SPEC target di FSD HRIS (baris target-state).
- Bagian 2.7 FSD POS (delta as-is ke to-be) dan baris K17 sengaja tetap menyebut `services/api-gateway` dan `X-Service-Token`, sebagai sisi lama dari delta.
