# PRD Stery Suite

*Product Requirements Document (PRD): satu organisasi, satu login, dan satu tagihan untuk HRIS-Stery, POS-Stery, dan SELA, tanpa mengorbankan penjualan terpisah*

|                         |                                                                                                                           |
|-------------------------|---------------------------------------------------------------------------------------------------------------------------|
| **Nama Dokumen**        | PRD - Stery Suite (platform dan mode operasi produk)                                                                      |
| **Versi**               | 1.0 (Draft)                                                                                                               |
| **Tanggal**             | 6 November 2026                                                                                                           |
| **Disusun oleh**        | Tim Produk & Engineering                                                                                                  |
| **Status**              | Draft untuk ditinjau                                                                                                      |
| **Dokumen Terkait**     | BRD_Stery_Suite, FSD_Stery_Suite, 00_Analisis_Dampak_Risiko, PRD_HRIS, FSD_HRIS, FSD_POS, `POS-Stery/PRD.md`, PRD Sela   |
| **Perubahan dari vX**   | Dokumen pertama                                                                                                           |

## 1. Visi dan Ringkasan

Stery Suite menjadikan HRIS-Stery (`HRS`), POS-Stery (`POS`), dan SELA (`SEL`) satu portofolio yang dapat dibeli per produk, per dua produk, atau semuanya. Platform `stery-suite` menyediakan organisasi bersama, SSO (login tunggal dengan pengalih produk), entitlement, billing, notification hub, audit sink, dan konsol; tiap produk tetap dapat berjalan sendiri (`STERY_MODE=standalone`, bawaan) atau terhubung (`STERY_MODE=suite`). Produk baru bergabung dengan memenuhi Product Contract (bagian 10.2).

Prinsip produk: (1) produk tidak pernah bergantung pada platform untuk mode standalone; (2) paket dan harga SELA yang ada tidak berubah; (3) pengguna produk cukup login sekali per organisasi; (4) hak pakai ditegakkan di produk, bukan hanya di UI; (5) semua nilai bisnis yang belum diputuskan ditulis `tbd`.

Dokumen ini adalah turunan BRD_Stery_Suite; keputusan arsitektur dirujuk sebagai D-SUI-01 sampai D-SUI-12 (didefinisikan di BRD_Stery_Suite bagian 9.1).

## 2. Masalah dan Target Pengguna

### 2.1 Masalah Inti

- Pelanggan yang memakai lebih dari satu produk mengelola akun, pengguna, dan pembayaran terpisah per produk.
- Penjual tidak dapat menawarkan paket maupun menegakkan hak pakai per paket; satu-satunya entitlement saat ini adalah paket per-event SELA.
- Tiap produk punya stack berbeda sehingga integrasi dan pemeliharaan mahal.
- Produk baru tidak punya jalur masuk yang baku.

### 2.2 Persona Pengguna

| **Persona** | **Deskripsi** | **Kebutuhan Utama** | **Sensitivitas Harga** |
| --- | --- | --- | --- |
| Pemilik organisasi (org owner) | Pemilik usaha/organisasi yang membeli paket dan bertanggung jawab atas tagihan | Satu organisasi, memilih paket, membayar lewat QRIS, menambah produk, melihat tagihan dan entitlement | `tbd` |
| Admin organisasi (org admin) | Mengelola anggota dan akses produk di dalam organisasi | Mengundang anggota, menetapkan akses per produk, memahami status langganan | `tbd` |
| Pengguna produk (product user) | Karyawan, kasir, atau host acara yang memakai HRIS, POS, atau SELA | Login sekali, berpindah produk, pengalaman produk tidak berubah | tidak langsung (dibayar organisasi) |
| Operator platform | Tim internal yang mengoperasikan platform | Konsol, jejak audit, konfigurasi SKU, pemantauan pengiriman event, onboarding produk | tidak berlaku |

## 3. User Stories

| **ID** | **Sebagai...** | **Saya ingin...** | **Agar...** | **Prioritas** |
| --- | --- | --- | --- | --- |
| US-SUI-01 | Pemilik organisasi | membuat organisasi dan memilih paket (`HRS`, `POS`, `SEL`, bundel dua produk, atau `SUITE`) | langsung dapat memakai produk yang saya beli | M |
| US-SUI-02 | Pemilik organisasi | membayar langganan lewat QRIS | entitlement aktif otomatis setelah pembayaran lunas | M |
| US-SUI-03 | Pemilik organisasi | menambah produk ke organisasi yang sudah ada (upsell) | tidak membuat akun atau organisasi baru | M |
| US-SUI-04 | Admin organisasi | mengundang anggota dan menetapkan produk yang boleh diakses tiap anggota | akses sesuai peran kerja | M |
| US-SUI-05 | Pengguna produk | login satu kali dan berpindah antar produk lewat pengalih produk | tidak perlu login berulang | M |
| US-SUI-06 | Pemilik organisasi | melihat entitlement, batas pemakaian, dan invoice | tahu apa yang saya bayar dan batasnya | M |
| US-SUI-07 | Pemilik organisasi pelanggan standalone | menautkan akun produk standalone saya ke organisasi suite | data dan pengguna yang ada tetap dipakai | M |
| US-SUI-08 | Admin organisasi | memahami apa yang terjadi saat langganan berakhir atau diturunkan | tidak terkejut kehilangan akses | M |
| US-SUI-09 | Pemilik produk standalone | produk tetap berjalan normal tanpa platform | pembelian produk tunggal tidak bergantung platform | M |
| US-SUI-10 | Operator platform | melihat jejak audit dan status organisasi di konsol | dapat menyelidiki insiden dan mendukung pelanggan | S |
| US-SUI-11 | Operator platform | mengubah SKU, harga, dan dimensi batas sebagai data | paket baru tidak memerlukan rilis kode | S |
| US-SUI-12 | Pengembang produk baru | memenuhi Product Contract dengan daftar periksa yang jelas | produk saya dapat bergabung ke suite | M |
| US-SUI-13 | Operator platform | memantau pengiriman event lintas produk dan mengulang pengiriman yang gagal | integrasi tidak diam-diam gagal | S |
| US-SUI-14 | Admin organisasi | mengaktifkan integrasi lintas produk (opt-in) | hanya memakai integrasi yang saya mau (hipotesis, validasi permintaan) | C |
| US-SUI-15 | Pemilik organisasi | membeli dua produk sebagai bundel | mendapat satu tagihan (aturan diskon `tbd`) | M |
| US-SUI-16 | Pemilik organisasi HRIS | data pribadi karyawan (NIK, NPWP, tanggal lahir) terlindungi | memenuhi UU PDP | M |
| US-SUI-17 | Pelanggan SELA | paket Gratis/Hemat/Standar/Premium tetap seperti sekarang pada kedua mode | harga dan perilaku tidak berubah | M |

## 4. Fitur Produk (Prioritas MoSCoW)

### 4.1 Must Have

- Organisasi dan anggota (platform IAM): pembuatan organisasi, undangan, peran per produk (US-SUI-01, US-SUI-04).
- SSO: sesi opaque di cookie `stery_session`, introspeksi `SessionService/Introspect` dengan cache 30 detik, pengalih produk (US-SUI-05, D-SUI-03).
- Entitlement: `EntitlementService/Check`, snapshot bertanda tangan, penegakan di tiap produk, perilaku degrade (US-SUI-06, US-SUI-08, D-SUI-04).
- Billing: langganan, invoice, pembayaran Midtrans QRIS lewat `payment.Provider`, webhook bertanda tangan (US-SUI-02, US-SUI-03, US-SUI-15, D-SUI-05).
- Dua mode per produk dan enam port dengan dua adapter (US-SUI-09, D-SUI-02).
- Migrasi pelanggan standalone ke suite (US-SUI-07).
- Paket SELA yang ada tetap (US-SUI-17); perlindungan data pribadi HRIS (US-SUI-16, D-SUI-08).
- Product Contract (US-SUI-12).
- Gerbang stabilisasi S0/S2/S3 (BR-SUI-15).

### 4.2 Should Have

- Konsol admin: anggota, entitlement, invoice, audit, SKU (US-SUI-10, US-SUI-11).
- Notification hub dan audit sink untuk produk mode suite (BR-SUI-12).
- Pemantauan dan pengulangan pengiriman event (US-SUI-13).
- Profil deploy suite tanpa tabrakan port (BR-SUI-18).
- Keputusan observabilitas (D-SUI-11, `tbd`).

### 4.3 Could Have

- Integrasi lintas produk INT-1 (tautan staf HRIS <-> POS), INT-2 (gathering HRIS -> event SELA), INT-3 (event toko POS -> event SELA dan undangan pelanggan loyalitas opt-in); semuanya hipotesis, validasi permintaan (US-SUI-14).
- Diskon bundel otomatis (aturan `tbd`).

### 4.4 Won't Have (fase ini)

- Satu aplikasi/runtime/basis data tunggal (opsi C ditolak).
- JWT, NATS/Kafka, gateway tier, ORM.
- Perubahan paket atau harga SELA.
- Payroll, pajak, rekrutmen, kinerja HRIS (Ditunda, ADR-0004).
- Refund, e-wallet, kartu pada billing suite (SELA hanya membangun QRIS).
- Marketplace produk pihak ketiga.

## 5. Alur Pengguna

Seluruh alur adalah rancangan target; tidak ada yang sudah berjalan (platform belum ada kode). Rincian proses ada di FSD_Stery_Suite bagian 7.

### 5.1 Onboarding organisasi dan memilih paket

1. Pemilik membuka konsol platform dan mendaftar (identitas organisasi dibuat).
2. Pemilik memilih SKU: `HRS`, `POS`, `SEL`, `HRS+POS`, `HRS+SEL`, `POS+SEL`, atau `SUITE`.
3. Platform membuat invoice dan tagihan QRIS Midtrans.
4. Setelah webhook pembayaran valid dan jumlah cocok, platform mengaktifkan entitlement.
5. Pemilik diarahkan ke produk pertama lewat pengalih produk; produk mode suite memverifikasi sesi dan entitlement.
6. Pemilik mengundang anggota dan menetapkan akses per produk.

### 5.2 Menambah produk (upsell)

1. Pemilik/admin membuka halaman langganan di konsol.
2. Memilih produk tambahan atau bundel yang lebih tinggi; platform menghitung invoice (aturan prorata `tbd`, OQ-6).
3. Setelah pembayaran lunas entitlement baru aktif; pengalih produk menampilkan produk baru tanpa login ulang.
4. Bila produk belum punya data, produk membuat konfigurasi awal untuk organisasi.

### 5.3 SSO dan pengalih produk

1. Pengguna login sekali di platform; platform menerbitkan cookie HttpOnly `stery_session`.
2. Pengguna membuka produk dari pengalih; produk memanggil `SessionService/Introspect` (cache lokal 30 detik) dan mendapat `Principal`.
3. Produk mengecek entitlement fitur yang diminta; bila tidak berhak, produk menampilkan halaman upsell bukan galat.
4. Logout di platform mencabut sesi; produk berhenti menerima sesi tersebut paling lambat setelah masa cache.

### 5.4 Migrasi pelanggan standalone ke suite

1. Pelanggan standalone (mis. pengguna SELA berbasis host OTP, atau tenant HRIS/POS) membuat organisasi di platform.
2. Platform memulai tautan: organisasi diikat ke tenant produk melalui `integration_links` dan `external_ref` (HRS/POS) atau `hosts.org_id`/`hosts.external_subject` (SELA).
3. Pengguna lama dipetakan ke anggota organisasi (pencocokan identitas oleh admin; aturan pencocokan didefinisikan di FSD_Stery_Suite 7.5).
4. Produk berpindah ke `STERY_MODE=suite` untuk organisasi itu; data tetap di basis data produk (tidak ada pemindahan antar basis data).
5. Jalur kembali ke standalone tersedia selama tautan dibatalkan (perilaku rinci `tbd`, OQ-6).

### 5.5 Entitlement kedaluwarsa dan penurunan paket

1. Langganan berakhir atau diturunkan: platform memperbarui entitlement dan snapshot.
2. Produk memakai snapshot terakhir; fitur berbayar dinonaktifkan sesuai entitlement baru, data tidak dihapus oleh platform.
3. Bila platform tidak tersedia, produk memakai snapshot terakhir hingga masa tenggang (24 jam, `tbd`) lalu gagal tertutup untuk fitur berbayar; fitur dasar dan mode standalone tidak terpengaruh.
4. Saat langganan dipulihkan, fitur kembali tanpa tindakan pengguna.

## 6. Kebutuhan Non-Fungsional

| **ID** | **Kategori** | **Kebutuhan** |
| --- | --- | --- |
| NFR-SUI-01 | Performa sesi | Introspeksi sesi memakai cache lokal 30 detik di produk; target latensi p95 `tbd` |
| NFR-SUI-02 | Ketahanan | Snapshot entitlement bertanda tangan dipakai hingga 24 jam (dapat dikonfigurasi, `tbd`) saat platform mati; gagal tertutup untuk fitur berbayar setelahnya |
| NFR-SUI-03 | Ketersediaan platform | Target ketersediaan `tbd` (tidak ada SLA di repo) |
| NFR-SUI-04 | Isolasi data | RLS wajib (`ENABLE`+`FORCE`, `USING`+`WITH CHECK`) untuk HRS, POS, platform; tes lintas tenant wajib per modul (D-SUI-08) |
| NFR-SUI-05 | Keamanan sesi | Cookie `stery_session` HttpOnly dan Secure, hanya hash disimpan di Dragonfly; tanpa JWT dan tanpa token di peramban |
| NFR-SUI-06 | Keamanan antar-layanan | gRPC platform dengan interceptor deny-by-default dan token HMAC layanan |
| NFR-SUI-07 | Pengiriman event | At-least-once; konsumen idempoten (`processed_events`); `event_id` UUIDv7 |
| NFR-SUI-08 | Kerahasiaan | Rahasia tidak pernah ada di repo atau log; konfigurasi env gagal cepat; `.env.example` |
| NFR-SUI-09 | Data pribadi | NIK, NPWP, tanggal lahir dienkripsi dengan `kit/piicrypt` (AES-256-GCM, AAD per tujuan, blind index, rotasi kunci) |
| NFR-SUI-10 | Audit | `audit_logs` append-only dengan trigger basis data |
| NFR-SUI-11 | Pembayaran | Webhook diverifikasi tanda tangan; notifikasi lunas dicocokkan jumlah |
| NFR-SUI-12 | Kompatibilitas | Mode standalone tidak berubah perilaku dan tidak membutuhkan platform |
| NFR-SUI-13 | Lokalisasi | Indonesia (bawaan) dan Inggris dengan tes paritas katalog; IDR; WIB |
| NFR-SUI-14 | Gerbang kualitas | `scripts/check.sh` (drift proto, gofmt, vet, golangci-lint, `go test -cover`, svelte-check, vitest, e2e), ambang cakupan 80%, `-race` di CI |
| NFR-SUI-15 | Port | Profil suite tidak bertabrakan port; port standalone tiap produk tidak berubah |
| NFR-SUI-16 | Observabilitas | Baseline `slog` JSON + `/healthz`; OpenTelemetry/Prometheus `tbd` (D-SUI-11) |

## 7. Model Monetisasi (ringkas, rujuk BRD)

Rincian di BRD_Stery_Suite bagian 7. Ringkasan: langganan organisasi untuk HRS, POS, dan bundel ditagih platform; paket per-event SELA tetap (Gratis Rp0, Hemat Rp39.000, Standar Rp129.000, Premium Rp350.000). Harga HRS, POS, bundel, aturan diskon, siklus penagihan, dan uji coba: `tbd`. Dimensi batas: `hrs.employees.max`, `pos.stores.max`, `pos.devices.max`, `sel.guest_cap`, `sel.retention_days`, `sel.watermark`, `sel.video`, `sel.zip_full_resolution`.

## 8. Positioning

Pernyataan positioning, pesan kunci, dan pembeda terhadap kompetitor: `tbd` (tidak ada riset di repo; pertanyaan riset di BRD_Stery_Suite bagian 8.2). Kandidat pembeda yang perlu divalidasi, bukan fakta: satu login dan satu tagihan lintas produk; pembelian modular; bahasa dan pembayaran lokal (QRIS).

## 9. Metrik Keberhasilan

Definisi metrik ada di BRD_Stery_Suite bagian 11; seluruh target `tbd`. Metrik produk: organisasi aktif, penetrasi bundel, konversi migrasi standalone -> suite, waktu aktivasi entitlement, ketersediaan SessionService/EntitlementService, jumlah kegagalan degrade, waktu onboarding produk baru.

## 10. Mode Operasi

### 10.1 Standalone vs suite

| Aspek | `STERY_MODE=standalone` (bawaan) | `STERY_MODE=suite` |
| --- | --- | --- |
| Identitas | Pengguna dan sesi milik produk (SELA: OTP + cookie `sela_session`; HRS/POS: kata sandi + sesi opaque) | Platform menerbitkan `stery_session`; produk memanggil `SessionService/Introspect` |
| Entitlement | Paket milik produk (SELA: `plans`) | `EntitlementService/Check` + snapshot |
| Billing | Di luar platform (`tbd`); SELA per-event di SELA | Platform (Midtrans QRIS); SELA per-event tetap di SELA |
| Notifikasi | Adapter lokal produk | Notification hub platform |
| Audit | `audit_logs` lokal | Lokal ditambah audit sink platform |
| Event | Outbox lokal | Outbox produk -> `IntegrationService/Publish` -> platform -> `Deliver` produk |
| Dependensi platform | Tidak ada | Ada, dengan masa tenggang untuk entitlement |

### 10.2 Product Contract

Syarat sebuah produk bergabung ke suite:

1. **Manifest**: `product_code`, daftar kunci fitur, dan dimensi batas (format di FSD_Stery_Suite 4.08).
2. **Enam port dengan dua adapter masing-masing**:

| Port | Tanda tangan | Adapter standalone | Adapter suite |
| --- | --- | --- | --- |
| `Identity` | `Verify(ctx, token) (Principal, error)` | Sesi/OTP/kata sandi lokal | `SessionService/Introspect` |
| `Tenant` | `WithTenant(ctx, tenantID, scope, fn)` | Tenant lokal | Organisasi platform -> `kit/tenantdb.WithTenant` |
| `Entitlement` | `Allows(ctx, org, feature) (bool, error)` | Paket lokal | `EntitlementService/Check` + snapshot |
| `Notification` | `Enqueue(ctx, tx, msg)` | Outbox lokal | Notification hub |
| `Audit` | `Record(ctx, event)` | `audit_logs` lokal | Audit sink platform |
| `Events` | `Publish(ctx, tx, envelope)` | Outbox lokal | `IntegrationService/Publish` |

1. **`STERY_MODE`** dengan nilai `standalone|suite`, bawaan `standalone`.
2. **`/healthz`** pada API produk.
3. **Publikasi outbox** transaksional dengan konsumen idempoten.
4. **Daftar periksa kesesuaian STACK-SPEC** (19 butir): tata letak repo, bahasa Go >= 1.25.1, dekomposisi modul, transport (REST `/api/v1` + gRPC), basis data (PostgreSQL 18, pgx/v5, goose), isolasi tenant, state store (Dragonfly), penyimpanan objek (RustFS, ClamAV), autentikasi (sesi opaque, RBAC), asinkron (ticker + outbox), observabilitas (`slog`, `/healthz`), konfigurasi (env gagal cepat), PII dan audit (`kit/piicrypt`, `kit/audit`), pembayaran (`payment.Provider`), web (SvelteKit SPA), deploy (Caddy, compose), gerbang kualitas (`scripts/check.sh`), proses (TDD, tracker, FSD diperbarui), lokalisasi. Rincian tiap butir di FSD_Stery_Suite 2.1.
5. **Tripel BRD/PRD/FSD** dalam gaya rumah SELA, termasuk jejak ketertelusuran dan kolom `Bukti`.

## 11. Roadmap Rilis

Estimasi waktu `tbd`.

| **Rilis** | **Fokus** | **Fitur Utama** | **Gerbang keluar** |
| --- | --- | --- | --- |
| S0 | Dokumen + penutupan closed-beta SELA | Set BRD/PRD/FSD; webhook Midtrans terbukti; keputusan retensi; 20 Pending Verification ditutup atau ditunda; origin media; penegakan `guest_cap`/`video`/`zip_full_resolution` | Gerbang SELA |
| S1 | `kit` dan platform inti | Ekstraksi `kit`; platform IAM dan ENT | `kit` dipakai SELA tanpa perubahan perilaku |
| S2 | Penyelarasan POS | Loyalitas dalam proses setelah commit penjualan; paritas REST; CI hijau; RLS `WITH CHECK`; rotasi rahasia; tes Postgres; data dashboard asli; keputusan PPN/struk | Gerbang POS |
| S3 | Penyelarasan HRIS | Migrasi up->down->up di CI; login nyata; update karyawan dan org chart; presign/rollback dokumen; enkripsi NIK/NPWP/birth_date; rate limit; rahasia dan biner dihapus | Gerbang HRIS |
| S4 | Mode suite | Adapter suite di tiga produk, billing, konsol | Org, paket, SSO, entitlement berfungsi |
| S5 | Integrasi dan produk baru | INT-1..INT-3 (hipotesis), Product Contract pada produk percobaan | Produk percobaan lolos daftar periksa |

## 12. Di Luar Cakupan

- Satu aplikasi, runtime, atau basis data tunggal.
- JWT, NATS/Kafka, gateway tier, ORM.
- Mengubah paket/harga SELA atau mengubah kode repo apa pun dalam fase dokumen ini.
- Payroll, pajak, rekrutmen, kinerja HRIS (ADR-0004).
- Refund, e-wallet, dan kartu pada billing suite.
- Integrasi selain INT-1..INT-3.

## 13. Ketergantungan dan Risiko

| Ketergantungan / risiko | Dampak | Penanganan |
| --- | --- | --- |
| RISK-SUI-14 Webhook Midtrans belum terbukti di URL publik | Billing suite tidak dapat dipercaya | Gerbang S0 |
| RISK-SUI-08 Tim kecil | Alur kerja paralel menumpuk | Satu penyelarasan satu waktu (D-SUI-12) |
| RISK-SUI-11 Platform titik kegagalan tunggal | Mode suite terdampak | Snapshot, cache 30 detik, standalone tidak bergantung |
| RISK-SUI-10 Harga `tbd` | Tidak dapat menjual paket | OQ-1 |
| RISK-SUI-07 UU PDP vs unggahan publik | Risiko hukum | Pemisahan data, `kit/piicrypt` |
| Ketergantungan keputusan terbuka OQ-2 (observabilitas), OQ-3 (domain cookie), OQ-4 (masa tenggang) | Spesifikasi menunggu pemilik | Default pada D-SUI-03, D-SUI-04, D-SUI-11 |

## 14. Status Saat Ini

| Area | Status | Keterangan | Bukti |
| --- | --- | --- | --- |
| Platform `stery-suite` | Belum | Repo git dibuat; hanya `docs/`, tanpa kode | `stery-suite/docs` |
| SELA (produk) | Sebagian | 76/105 task Completed, 20 Pending Verification; identitas hanya OTP lokal; tidak ada tenant, SSO, atau entitlement bundel | `SELA/docs/tracking/tracker.json`, `SELA/apps/api/services/auth/http.go`, `SELA/apps/api/services/payment/postgres.go` |
| POS (produk) | Sebagian | Enam layanan gRPC nyata; belum ada integrasi lintas layanan loyalitas | `POS-Stery/services/customer-service/internal/application/commands/add_loyalty_points.go` |
| HRIS (produk) | Sebagian | 39 dari 47 RPC nyata; alur login-ke-DB belum berjalan | `HRIS-Stery/apps/web/src/routes/(auth)/login/+page.server.ts` |
| Pembayaran | Pending Verification | Provider Midtrans + sandbox ada di SELA; belum diuji dengan akun sungguhan | `SELA/apps/api/services/payment/provider.go`, `SELA/apps/api/services/payment/midtrans.go` |
| Kode `kit` | Belum | Sumber ada di `internal/` SELA tetapi belum diekstraksi | `SELA/apps/api/internal` |

Rincian per repo dan kontradiksi dokumen status ada di `00_Analisis_Dampak_Risiko` bagian 3.
