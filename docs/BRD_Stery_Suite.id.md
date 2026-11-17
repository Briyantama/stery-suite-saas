# BRD Stery Suite

*Business Requirements Document (BRD): HRIS-Stery, POS-Stery, dan SELA yang dapat dijual sebagai satu paket maupun terpisah*

|                         |                                                                                                                                      |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| **Nama Dokumen**        | BRD - Stery Suite (platform, paket, dan model komposisi tiga produk)                                                                 |
| **Versi**               | 1.0 (Draft)                                                                                                                          |
| **Tanggal**             | 6 November 2026                                                                                                                      |
| **Disusun oleh**        | Tim Produk & Engineering                                                                                                             |
| **Status**              | Draft untuk ditinjau                                                                                                                 |
| **Dokumen Terkait**     | 00_Analisis_Dampak_Risiko, PRD_Stery_Suite, FSD_Stery_Suite, BRD_HRIS, PRD_HRIS, FSD_HRIS, BRD_POS, FSD_POS, BRD/PRD/FSD Sela        |
| **Perubahan dari vX**   | Dokumen pertama                                                                                                                      |

## 1. Ringkasan Eksekutif

Stery Suite adalah cara menjual tiga produk yang sudah ada, HRIS-Stery (kode produk `HRS`, SDM), POS-Stery (`POS`, kasir dan inventaris), dan SELA (`SEL`, kamera tamu untuk acara), sebagai paket: ketiganya sekaligus (`SUITE`), dua dari tiga (`HRS+POS`, `HRS+SEL`, `POS+SEL`), atau satu produk saja. Setiap produk tetap dapat berjalan mandiri (`STERY_MODE=standalone`, bawaan) atau terhubung (`STERY_MODE=suite`) ke platform baru `stery-suite` yang menyediakan organisasi dan identitas bersama (SSO), entitlement (hak pakai per paket), billing, notification hub, audit sink, dan konsol. Produk baru dapat ditambahkan kemudian dengan mengikuti Product Contract.

Pemilik telah memutuskan: struktur polyrepo ditambah repo platform baru; stack, pola, dan arsitektur seluruh suite mengikuti SELA; dokumen tersedia dalam Indonesia dan Inggris. Dokumen ini mendefinisikan kebutuhan bisnisnya. Analisis dampak dan risiko ada di `00_Analisis_Dampak_Risiko`; keputusan arsitektur dicatat sebagai D-SUI-01 sampai D-SUI-12 di bagian 9.1.

Kondisi saat ini (bagian 13): SELA paling matang tetapi belum menutup gerbang closed-beta; POS memiliki enam layanan gRPC nyata dengan cacat integrasi; HRIS belum memiliki alur login-ke-database yang berjalan; platform `stery-suite` belum berisi kode. Tidak ada kode sumber yang diubah dalam fase dokumen ini.

Semua harga, kuota, SLA, ukuran pasar, data kompetitor, dan target KPI yang tidak ditemukan di repo ditulis `tbd` dan menjadi pertanyaan terbuka; satu-satunya angka harga adalah harga paket SELA yang sudah ada.

## 2. Latar Belakang dan Pernyataan Masalah

Tiga produk dibangun terpisah dan tidak berbagi kode, tabel, event, identitas, ataupun billing (analisis bagian 3 dan RISK-SUI-01). Pelanggan yang membeli dua atau tiga produk hari ini harus mengelola akun, pengguna, dan pembayaran terpisah, dan penjual tidak dapat menawarkan paket maupun menegakkan hak pakai per paket. SELA hanya mengenal host dan paket per-event; ia tidak punya konsep tenant/organisasi dan tidak punya jalur identitas eksternal. HRIS dan POS multi-tenant tetapi dengan namespace tenant yang berbeda.

Selain itu ketiga repo memakai stack berbeda (gRPC mikroservis + NATS + JWT pada HRIS dan POS, satu modul Go + outbox + sesi opaque pada SELA), sehingga setiap integrasi akan menanggung biaya penerjemahan terus-menerus. Pemilik memutuskan stack SELA sebagai standar; HRIS dan POS harus diselaraskan, dan kondisi masing-masing (HRIS belum bisa dipakai nyata; POS punya cacat integrasi) berarti penyelarasan sekaligus menjadi kesempatan stabilisasi.

Masalah bisnis yang diselesaikan: (1) menjual paket dengan satu organisasi, satu login, dan satu tagihan; (2) tetap menjual tiap produk sendiri tanpa platform; (3) menambah produk baru tanpa membangun ulang fondasi; (4) menyatukan standar teknis agar tim kecil dapat memelihara tiga produk.

## 3. Tujuan Bisnis

1. Menjual setiap produk secara mandiri (`HRS`, `POS`, `SEL`) tanpa ketergantungan pada platform.
2. Menjual bundel dua produk dan bundel tiga produk (`SUITE`) dengan satu organisasi, satu login, dan satu tagihan.
3. Mempertahankan paket SELA yang sudah ada (Gratis, Hemat, Standar, Premium) tanpa perubahan harga maupun perilaku.
4. Menyiapkan jalur masuk produk baru lewat Product Contract (manifest, enam port, `STERY_MODE`, `/healthz`, outbox, daftar periksa STACK-SPEC).
5. Menjaga isolasi data antar organisasi dan antar produk serta kepatuhan UU PDP, terutama untuk data pribadi karyawan (NIK, NPWP, tanggal lahir).
6. Menurunkan biaya pemeliharaan lewat satu stack standar dan `kit` bersama.
7. Menutup gerbang stabilisasi tiap produk sebelum dan sesudah penyelarasan, agar produk yang dijual berfungsi nyata.
8. Menetapkan harga, aturan bundel, siklus penagihan, dan uji coba sebelum penjualan paket pertama (`tbd`, OQ-1).

## 4. Ruang Lingkup

### 4.1 Segmen dan paket

Segmen pelanggan: `tbd` (belum ada pernyataan segmen target HRIS/POS/suite di repo; pertanyaan terbuka OQ-10). SELA sudah menyebut segmen B2C dan B2B2C untuk acara (BRD Sela bagian 3).

| Paket (SKU) | Produk yang termasuk | Mode yang didukung | Catatan |
| --- | --- | --- | --- |
| `HRS` | HRIS-Stery | standalone, suite | Dimensi `hrs.employees.max`; tingkat dan harga `tbd` |
| `POS` | POS-Stery | standalone, suite | Dimensi `pos.stores.max`, `pos.devices.max`; tingkat dan harga `tbd` |
| `SEL` | SELA | standalone, suite | Paket Gratis/Hemat/Standar/Premium/Partner yang ada |
| `HRS+POS` | HRIS + POS | suite (lihat 7.1 untuk standalone) | Aturan diskon `tbd` |
| `HRS+SEL` | HRIS + SELA | suite | Aturan diskon `tbd` |
| `POS+SEL` | POS + SELA | suite | Aturan diskon `tbd` |
| `SUITE` | HRIS + POS + SELA | suite | Aturan diskon `tbd` |

### 4.2 Dalam lingkup

- Platform `stery-suite`: IAM (organisasi, anggota, sesi), ENT (entitlement dan snapshot), BIL (langganan, invoice, pembayaran Midtrans QRIS), NTF (notification hub), AUD (audit sink), ADM (konsol), INT (integrasi lintas produk), DEP (profil deploy dan Product Contract). Modul diurai di FSD_Stery_Suite bagian 4.01-4.08.
- Paket `kit` bersama yang diangkat dari `internal/` SELA ditambah `tenantdb`, `session`, `outbox`.
- Dua mode per produk (`STERY_MODE`), enam port (`Identity`, `Tenant`, `Entitlement`, `Notification`, `Audit`, `Events`) dengan dua adapter masing-masing.
- Spesifikasi penyelarasan HRIS dan POS ke stack SELA (dokumen BRD/FSD masing-masing produk) dan jalur migrasi pelanggan standalone ke suite.
- Gerbang stabilisasi S0/S2/S3 dan roadmap S0-S5.
- Dokumen dua bahasa (Indonesia dan Inggris).

### 4.3 Ditunda

| Butir | Alasan penundaan | Syarat membuka |
| --- | --- | --- |
| Integrasi lintas produk INT-1 (tautan staf karyawan HRIS <-> pengguna POS), INT-2 (gathering HRIS membuat event SELA), INT-3 (event toko POS membuat event SELA dan mengundang pelanggan loyalitas yang opt-in) | Hipotesis; validasi permintaan belum dilakukan | Bukti permintaan pelanggan dan penyelesaian S4 (fase S5) |
| Produk keempat dan seterusnya | Product Contract belum teruji dengan satu produk percobaan | S5 |
| Payroll, pajak, rekrutmen, kinerja HRIS (modul HRS 09-12) | Ditunda oleh ADR-0004; perlu tinjauan hukum PPh 21, BPJS, THR | Tinjauan hukum dan keputusan pemilik |
| Observabilitas OpenTelemetry/Prometheus pada baseline | Keputusan terbuka D-SUI-11 | Keputusan pemilik (OQ-2) |
| Harga HRS, POS, bundel | Belum ditetapkan (`tbd`) | Keputusan pemilik (OQ-1) |

### 4.4 Di luar lingkup

- Menggabungkan tiga produk menjadi satu aplikasi, satu runtime, atau satu basis data (opsi C ditolak, bagian 8).
- Memindahkan tiga repo ke monorepo (opsi B tidak dipilih).
- Mengubah kode sumber repo mana pun dalam fase dokumen ini.
- JWT dan token yang disimpan di peramban; NATS/Kafka; gateway tier; ORM (lihat STACK-SPEC di FSD_Stery_Suite).
- Mengubah paket, harga, atau perilaku SELA yang ada.
- Fitur baru HRIS/POS di luar dokumen BRD/PRD/PRD.md masing-masing.
- Pembuatan ulang dokumen SELA, `POS-Stery/PRD.md`, atau dokumen status yang ada.

## 5. Pemangku Kepentingan

| Pemangku kepentingan | Peran | Kepentingan |
| --- | --- | --- |
| Pemilik produk / sponsor bisnis | Penetapan harga, bundel, keputusan terbuka OQ-1..OQ-10 | Pendapatan paket, kendali risiko |
| Engineering lead | Arsitektur, urutan penyelarasan S0-S5 | Beban kerja yang dapat ditangani tim kecil (RISK-SUI-08) |
| Pelanggan organisasi (pemilik/admin organisasi) | Membeli paket, mengelola anggota dan produk | Satu login, satu tagihan, produk bisa dibeli terpisah |
| Pengguna produk (karyawan, kasir, host/tamu) | Memakai HRIS, POS, SELA | Pengalaman tidak berubah di mode standalone |
| Operator platform | Mengoperasikan konsol, billing, deploy | Kemampuan audit dan pemantauan |
| Penasihat hukum/kepatuhan | Tinjauan UU PDP, PPh 21/BPJS/THR, PPN | Kepatuhan sebelum fitur terkait dibuka |
| Penyedia pembayaran (Midtrans) | Pemrosesan QRIS | Webhook yang valid dan terbukti (RISK-SUI-14) |
| Calon pengembang produk baru | Mengikuti Product Contract | Kontrak yang jelas dan dapat dicek |

## 6. Kebutuhan Bisnis

Prioritas: M = Must, S = Should, C = Could. Setiap BR dipetakan ke FR di FSD_Stery_Suite bagian 11.2.

| **ID** | **Kebutuhan Bisnis** | **Prioritas** |
| --- | --- | --- |
| BR-SUI-01 | Setiap produk (`HRS`, `POS`, `SEL`) dapat dijual dan dipakai secara independen, tanpa platform dan tanpa produk lain. | M |
| BR-SUI-02 | Dua produk mana pun dapat dijual sebagai bundel (`HRS+POS`, `HRS+SEL`, `POS+SEL`) dengan satu organisasi dan satu tagihan. | M |
| BR-SUI-03 | Ketiga produk dapat dijual sebagai bundel `SUITE` dengan satu organisasi, satu login, dan satu tagihan. | M |
| BR-SUI-04 | Setiap pelanggan memilih per produk antara mode `standalone` (bawaan, perilaku saat ini tidak berubah) dan mode `suite`; kedua mode dapat hidup berdampingan pada pelanggan berbeda. | M |
| BR-SUI-05 | Paket SELA yang ada (Gratis, Hemat, Standar, Premium, Partner) dan harganya tetap berlaku dan tidak berubah pada kedua mode; checkout per-event SELA tetap di dalam SELA. | M |
| BR-SUI-06 | Produk baru dapat bergabung ke suite dengan memenuhi Product Contract: manifest (`product_code`, kunci fitur, dimensi batas), enam port dengan dua adapter, `STERY_MODE`, `/healthz`, publikasi outbox, daftar periksa STACK-SPEC, dan tripel BRD/PRD/FSD. | M |
| BR-SUI-07 | Pelanggan standalone dapat dipindahkan ke suite (menautkan organisasi dan pengguna yang sudah ada) tanpa kehilangan data dan tanpa membuat ulang akun. | M |
| BR-SUI-08 | Satu identitas organisasi memberi satu login (SSO) ke semua produk yang dibeli, dengan pengalih produk; sesi berbentuk cookie opaque, tanpa JWT. | M |
| BR-SUI-09 | Hak pakai per organisasi, produk, fitur, dan dimensi batas ditegakkan di setiap produk mode suite; saat langganan berakhir atau platform tidak tersedia, produk menurunkan fitur berbayar secara terdefinisi (masa tenggang lalu gagal tertutup untuk fitur berbayar) dan tidak pernah memutus mode standalone. | M |
| BR-SUI-10 | Langganan suite (HRS, POS, bundel) ditagih oleh platform lewat Midtrans QRIS dengan webhook bertanda tangan; harga disimpan sebagai data konfigurasi, tidak ditanam di kode. | M |
| BR-SUI-11 | Data dipisah per produk (satu basis data dan satu peran aplikasi per produk) dan per organisasi (RLS wajib untuk HRS, POS, dan platform); tidak ada FK lintas basis data; data pribadi (NIK, NPWP, tanggal lahir) dienkripsi dan dikelola sesuai UU PDP. | M |
| BR-SUI-12 | Notifikasi dan jejak audit dari produk mode suite dapat dikirim ke notification hub dan audit sink platform tanpa mengubah perilaku mode standalone. | S |
| BR-SUI-13 | Pemilik/admin organisasi dan operator platform memiliki konsol untuk mengelola anggota, melihat entitlement dan tagihan, dan operasi platform. | S |
| BR-SUI-14 | Integrasi lintas produk INT-1, INT-2, INT-3 tersedia sebagai opt-in per organisasi melalui fitur entitlement `integration.<a>_<b>`; hipotesis, validasi permintaan sebelum dibangun. | C |
| BR-SUI-15 | Setiap produk harus menutup gerbang stabilisasinya (S0 untuk SELA, S2 untuk POS, S3 untuk HRIS) sebelum paket yang memuatnya dijual. | M |
| BR-SUI-16 | Harga produk HRS/POS dan bundel, aturan diskon bundel, siklus penagihan, dan uji coba ditetapkan pemilik sebelum penjualan paket pertama (saat ini `tbd`). | M |
| BR-SUI-17 | Seluruh antarmuka suite berbahasa Indonesia (bawaan) dan Inggris, mata uang IDR, zona waktu WIB. | S |
| BR-SUI-18 | Profil deploy suite menjalankan platform dan tiga produk bersama tanpa tabrakan port dengan satu server Postgres (empat basis data), instance Dragonfly per produk, dan satu RustFS; profil standalone tiap produk tidak berubah. | S |

## 7. Model Bisnis dan Monetisasi

Model: langganan organisasi untuk HRS, POS, dan bundel yang ditagih platform; paket per-event SELA tetap seperti sekarang. Semua harga selain harga SELA di bawah adalah `tbd` (OQ-1); tidak ada angka diturunkan atau ditebak.

### 7.1 Matriks SKU

| SKU | Produk | Mode standalone | Mode suite | Penagihan | Harga |
| --- | --- | --- | --- | --- | --- |
| `HRS` | HRS | Tersedia (tanpa platform) | Tersedia | Standalone: di luar platform, `tbd`; suite: langganan platform | `tbd` |
| `POS` | POS | Tersedia | Tersedia | Sama seperti `HRS` | `tbd` |
| `SEL` | SEL | Tersedia (checkout per-event SELA) | Tersedia (checkout per-event SELA tetap di SELA, D-SUI-05) | Per-event di SELA | Lihat 7.3 |
| `HRS+POS` | HRS, POS | Dua produk standalone dijual bersama: penagihan `tbd` (OQ-6) | Tersedia | Suite: langganan bundel platform | `tbd` |
| `HRS+SEL` | HRS, SEL | `tbd` (OQ-6) | Tersedia | Suite: bundel platform untuk HRS; SELA per-event | `tbd` |
| `POS+SEL` | POS, SEL | `tbd` (OQ-6) | Tersedia | Suite: bundel platform untuk POS; SELA per-event | `tbd` |
| `SUITE` | HRS, POS, SEL | `tbd` (OQ-6) | Tersedia | Suite: bundel platform; SELA per-event | `tbd` |

Aturan diskon bundel, siklus penagihan (bulanan/tahunan), dan masa uji coba: `tbd` (OQ-1, OQ-6).

### 7.2 Dimensi batas

Nama dimensi tetap; nilai SELA berasal dari tabel `plans`; nilai lain `tbd`.

| Dimensi | Produk | Gratis | Hemat | Standar | Premium | Partner | Sumber nilai |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `hrs.employees.max` | HRS | `tbd` | `tbd` | `tbd` | `tbd` | `tbd` | Belum ada di repo |
| `pos.stores.max` | POS | `tbd` | `tbd` | `tbd` | `tbd` | `tbd` | Belum ada di repo |
| `pos.devices.max` | POS | `tbd` | `tbd` | `tbd` | `tbd` | `tbd` | Belum ada di repo |
| `sel.guest_cap` | SEL | 30 | 80 | 200 | tanpa batas | tanpa batas | `plans` (migrasi 0011) |
| `sel.retention_days` | SEL | 7 | 30 | 365 | 730 | tidak pernah | `plans` (migrasi 0015) |
| `sel.watermark` | SEL | ya | tidak | tidak | tidak | tidak | `plans` |
| `sel.video` | SEL | tidak | tidak | ya | ya | ya | `plans` |
| `sel.zip_full_resolution` | SEL | tidak | tidak | ya | ya | ya | `plans` (belum ditegakkan di ekspor, analisis 3.1) |

Tingkat paket untuk HRS dan POS (nama dan jumlah) `tbd`. Tingkat HRS dibatasi dimensi `hrs.employees.max`; tingkat POS oleh `pos.stores.max` dan `pos.devices.max`.

### 7.3 Harga paket SELA yang ada (per event)

| Paket | Harga | Sumber |
| --- | --- | --- |
| Gratis | Rp0 | `SELA/docs/BRD_Sela.md` bagian 7 |
| Hemat | Rp39.000 | `PLAN_PRICE_IDR_HEMAT=39000` pada `SELA/.env.example` |
| Standar | Rp129.000 | `PLAN_PRICE_IDR_STANDAR=129000` |
| Premium | Rp350.000 | `PLAN_PRICE_IDR_PREMIUM=350000` |
| Partner | kontrak/komisi khusus (tidak terdaftar publik) | `SELA/docs/BRD_Sela.md` bagian 7 |

### 7.4 Prinsip

- Harga di data konfigurasi, bukan kode; paket baru tidak memerlukan rilis kode.
- Entitlement dipetakan dari langganan aktif ke kunci fitur dan dimensi batas per produk (FSD_Stery_Suite 4.02).
- Pembayaran memakai abstraksi `payment.Provider` SELA (Midtrans QRIS; Xendit sudah dihapus) (D-SUI-05).

## 8. Analisis Alternatif dan Kompetitor

### 8.1 Opsi arsitektur

| Opsi | Deskripsi | Keputusan |
| --- | --- | --- |
| A. Polyrepo + platform | Tiga repo produk tetap; repo baru `stery-suite` berisi platform dan `kit` | **Dipilih** (D-SUI-01) |
| B. Monorepo | Satu repo semua produk dan platform | Tidak dipilih: memindahkan tiga riwayat git dan memaksa satu pipeline CI untuk produk yang dijual terpisah |
| C. Satu basis kode/runtime | Satu aplikasi dan satu basis data | **Ditolak**: melanggar penjualan mandiri per produk, memperbesar blast radius, memperumit UU PDP |

Perbandingan rinci ada di `00_Analisis_Dampak_Risiko` bagian 5.

### 8.2 Kompetitor

Data kompetitor untuk paket HRIS/POS/suite belum ada di repo; seluruh isinya `tbd` dan tidak boleh diisi tanpa riset.

| Kategori pembanding | Pemain | Model harga | Kekuatan/kelemahan |
| --- | --- | --- | --- |
| Suite SDM + kasir + acara terintegrasi | `tbd` | `tbd` | `tbd` |
| HRIS lokal (UU PDP, PPh 21, BPJS) | `tbd` | `tbd` | `tbd` |
| POS lokal (QRIS, PPN, struk) | `tbd` | `tbd` | `tbd` |

Pertanyaan riset: (1) apakah pelanggan UKM membeli HRIS dan POS dari satu vendor? (2) apakah ada kebutuhan SELA untuk gathering korporat dan acara toko (INT-2, INT-3)? (3) berapa kesediaan membayar bundel dibanding produk terpisah? (4) paket SELA berbasis per-event cocok dengan langganan organisasi atau perlu kredit bulanan?

## 9. Asumsi dan Batasan

### 9.1 Log keputusan

Keputusan berikut tertanam dalam dokumen dan boleh diubah pemilik; mengubah satu keputusan berarti menyusun ulang dokumen yang merujuknya.

| ID | Keputusan | Ringkasan |
| --- | --- | --- |
| D-SUI-01 | Komposisi, bukan konsolidasi | Tiga produk tetap unit deploy terpisah dengan basis data terpisah. Unit deploy keempat, platform `stery-suite`, memegang organisasi/identitas, entitlement, billing, notification hub, audit sink, dan konsol. Kode Go bersama di `stery-suite/kit` (diangkat dari `internal/{httpx,config,db,testdb,audit,piicrypt,objstore,health}` SELA, ditambah `tenantdb`, `session`, `outbox`). |
| D-SUI-02 | Dua mode per produk | Env `STERY_MODE=standalone\|suite`, bawaan `standalone`. `standalone` = perilaku saat ini (pengguna, sesi, paket sendiri). `suite` = produk mendelegasikan identitas, entitlement, billing, notifikasi, audit ke platform lewat port Go `Identity`, `Tenant`, `Entitlement`, `Notification`, `Audit`, `Events` dengan dua adapter masing-masing. |
| D-SUI-03 | Identitas pada mode suite | Platform menerbitkan sesi opaque di cookie HttpOnly `stery_session` (domain induk, nilai `tbd`); hanya hash-nya disimpan di Dragonfly platform. Produk memvalidasi lewat gRPC `stery.platform.v1.SessionService/Introspect` dengan cache lokal 30 detik, interceptor deny-by-default, dan token HMAC layanan. Tanpa JWT. |
| D-SUI-04 | Entitlement | `stery.platform.v1.EntitlementService/Check(org_id, product, feature)` ditambah snapshot entitlement bertanda tangan yang di-cache di produk; saat platform mati produk memakai snapshot terakhir hingga 24 jam (dapat dikonfigurasi, `tbd`), lalu gagal tertutup untuk fitur berbayar, tidak pernah untuk mode standalone. |
| D-SUI-05 | Billing | Langganan suite (HRS, POS, bundel) ditagih platform memakai abstraksi `payment.Provider` SELA (Midtrans QRIS). Checkout per-event SELA tetap di dalam SELA pada kedua mode (paket Gratis/Hemat/Standar/Premium tidak berubah). Harga HRS/POS/bundel `tbd`. |
| D-SUI-06 | Event | Tanpa NATS. Per produk: event domain dalam proses + outbox transaksional Postgres (`FOR UPDATE SKIP LOCKED`) + konsumen idempoten (`processed_events`). Lintas produk: outbox produk -> `IntegrationService/Publish` (gRPC) -> platform mengirim ke endpoint `Deliver` produk pelanggan; envelope `{event_id UUIDv7, event_type, org_id, store_id?, actor_id, occurred_at, schema_version, payload}`; at-least-once; opt-in per organisasi lewat fitur entitlement `integration.<a>_<b>`. |
| D-SUI-07 | Data | Satu server Postgres per profil dengan satu basis data dan satu peran aplikasi per produk (`stery_platform`, `hris`, `pos`, `sela`), tanpa FK lintas basis data; referensi lintas produk berupa UUID + kolom `external_ref`. Satu Dragonfly per produk pada profil suite. Satu RustFS dengan satu bucket dan satu access key per produk. ClamAV bersama. |
| D-SUI-08 | Invarian multi-tenancy | RLS wajib untuk HRS, POS, platform: `ENABLE`+`FORCE`, kebijakan `tenant_isolation` dengan `USING` dan `WITH CHECK`, `current_setting('app.tenant_id', true)::uuid` diatur per transaksi oleh `kit/tenantdb.WithTenant`; POS menambah `app.store_id`; peran aplikasi NOBYPASSRLS; peran migrasi terpisah; tes lintas tenant wajib per modul. SELA hanya menambah `hosts.org_id` dan `hosts.external_subject` nullable pada mode suite, tanpa perubahan RLS. |
| D-SUI-09 | Web produk | Tiap produk satu `apps/web` (SvelteKit SPA); POS menggabungkan admin dan kasir menjadi grup rute `(admin)` dan `(cashier)`; scope service worker PWA per area yang butuh offline (kasir POS `/cashier/`, tamu SELA `/e/`). Konsol suite = `stery-suite/apps/web`. |
| D-SUI-10 | Kredensial | SELA tetap OTP email; HRIS dan POS tetap login kata sandi (skema hash bcrypt yang ada dipertahankan) tetapi sesi menjadi cookie opaque (JWT dihapus). Token POS-dengan-toko menjadi atribut sesi `store_id`. |
| D-SUI-11 | Observabilitas | Baseline SELA = `slog` JSON + `/healthz`. OpenTelemetry/Prometheus (ada di HRIS dan POS) tidak masuk baseline; dicatat sebagai keputusan terbuka pemilik `tbd` (modul `kit` opsional). |
| D-SUI-12 | Urutan | S0 dokumen + penutupan closed-beta SELA -> S1 ekstraksi `kit` (SELA mengadopsi `kit`, perilaku dipertahankan) + platform IAM/ENT -> S2 penyelarasan POS -> S3 penyelarasan HRIS -> S4 adapter mode suite di ketiga produk + billing + konsol -> S5 integrasi lintas produk + onboarding produk baru. Satu penyelarasan berjalan pada satu waktu; masing-masing berakhir di gerbang stabilisasi produk itu. |

### 9.2 Asumsi

- Pemilik dapat menetapkan harga dan aturan bundel sebelum S4 selesai; bila tidak, penjualan paket tertunda (RISK-SUI-10).
- Calon pelanggan paket membutuhkan satu login dan satu tagihan; belum divalidasi (pertanyaan riset 8.2).
- Satu server Postgres dan Dragonfly per produk cukup untuk profil suite pada fase awal; kapasitas dan SLA `tbd`.
- Midtrans QRIS cukup sebagai satu-satunya metode pembayaran suite pada fase awal (SELA hanya membangun QRIS; refund, e-wallet, kartu belum dibangun).

### 9.3 Batasan

- Fase ini hanya dokumen; tidak ada kode yang diubah.
- Satu penyelarasan dalam satu waktu karena tim kecil (RISK-SUI-08).
- Platform harus tidak menjadi syarat bagi mode standalone.
- Nilai bisnis yang tidak ada di repo tidak boleh diisi (aturan `tbd`).
- Handle pemilik modul Go untuk repo baru (`Briyantama`) belum terverifikasi (OQ-7).
- HRIS dan POS belum lulus gerbang stabilisasi sehingga belum layak dijual sebagai bagian paket (BR-SUI-15).

## 10. Risiko dan Mitigasi

Definisi lengkap risiko ada di `00_Analisis_Dampak_Risiko` bagian 4; tabel berikut merangkum dampak bisnisnya.

| **Risiko** | **Dampak bisnis** | **Mitigasi** |
| --- | --- | --- |
| RISK-SUI-01 Tidak ada fondasi tenancy/identitas/entitlement/billing bersama | Paket tidak dapat dijual | Bangun platform (S1, S4); BR-SUI-08 sampai BR-SUI-10 |
| RISK-SUI-03 Penyelarasan HRIS/POS adalah penulisan ulang infrastruktur | Jadwal molor | Pertahankan domain/application; satu penyelarasan satu waktu |
| RISK-SUI-07 Blast radius dan UU PDP (unggahan publik SELA vs NIK/NPWP HRIS) | Risiko hukum dan reputasi | Basis data, bucket, dan peran terpisah per produk; enkripsi PII |
| RISK-SUI-08 Tim kecil | Pekerjaan paralel menumpuk | D-SUI-12 |
| RISK-SUI-10 Harga belum ditetapkan | Tidak ada model bisnis teruji | BR-SUI-16; OQ-1 |
| RISK-SUI-11 Platform titik kegagalan tunggal | Semua produk mode suite terdampak | Snapshot entitlement + masa tenggang; standalone tidak bergantung |
| RISK-SUI-14 Midtrans baru terbukti di sandbox | Pembayaran nyata gagal | Gerbang S0 webhook terbukti |

## 11. KPI

Definisi saja; seluruh target `tbd` karena belum ada baseline di repo.

| KPI | Definisi | Target |
| --- | --- | --- |
| Organisasi aktif | Jumlah organisasi dengan setidaknya satu entitlement aktif | `tbd` |
| Penetrasi bundel | Persentase organisasi dengan dua atau lebih produk | `tbd` |
| Konversi migrasi | Persentase pelanggan standalone yang dipindahkan ke suite tanpa kehilangan data | `tbd` |
| Aktivasi entitlement | Waktu dari pembayaran Midtrans lunas hingga entitlement aktif | `tbd` |
| Ketersediaan platform | Persentase waktu SessionService dan EntitlementService menjawab | `tbd` |
| Kegagalan degrade | Jumlah kejadian fitur berbayar terblokir akibat platform mati melebihi masa tenggang | `tbd` |
| Waktu onboarding produk baru | Durasi dari awal hingga produk lolos daftar periksa Product Contract | `tbd` |
| Kepatuhan gerbang | Jumlah gerbang S0/S2/S3 yang tertutup dari total | `tbd` |

## 12. Linimasa dan Fase

Durasi dan tanggal `tbd` (tidak ada estimasi waktu di repo; pemilik menetapkan setelah meninjau bagian 6 analisis).

| Fase | Cakupan | Gerbang keluar | Estimasi |
| --- | --- | --- | --- |
| S0 | Dokumen + penutupan closed-beta SELA | Gerbang stabilisasi SELA (analisis bagian 7) | `tbd` |
| S1 | Ekstraksi `kit`; platform IAM dan ENT | `kit` dipakai SELA tanpa perubahan perilaku | `tbd` |
| S2 | Penyelarasan POS | Gerbang stabilisasi POS | `tbd` |
| S3 | Penyelarasan HRIS | Gerbang stabilisasi HRIS | `tbd` |
| S4 | Adapter mode suite + billing + konsol | Org dapat dibuat, memilih paket, SSO, entitlement ditegakkan | `tbd` |
| S5 | Integrasi lintas produk + onboarding produk baru | Product Contract teruji pada satu produk percobaan | `tbd` |

## 13. Status Implementasi Saat Ini

### 13.1 Portofolio tiga produk dan platform

Status per 6 November 2026. Estimasi kesiapan ada di analisis bagian 3 dan ditandai `[INFERENCE]`.

| Produk | Status | Ringkasan | Bukti |
| --- | --- | --- | --- |
| SELA (`SEL`) | Sebagian | 427 commit (terakhir 2026-10-26); 76 dari 105 task Completed, 20 Pending Verification, 9 Not Started (tracker 2026-10-25); webhook Midtrans belum terbukti di URL publik; konflik retensi belum diputuskan | `SELA/docs/tracking/tracker.json`, `SELA/apps/api/go.mod`, `SELA/docs/BRD_Sela.md` |
| POS-Stery (`POS`) | Sebagian | 21 commit (terakhir 2026-06-30); enam layanan gRPC nyata; `AddLoyaltyPoints` tidak punya pemanggil; dashboard memakai bauran pembayaran 55/30/15 buatan; CI usang (job Laravel) | `POS-Stery/PRD.md`, `POS-Stery/services/customer-service/internal/application/commands/add_loyalty_points.go`, `POS-Stery/.github/workflows/ci.yml` |
| HRIS-Stery (`HRS`) | Sebagian | 33 commit (terakhir 2026-06-10); 39 dari 47 RPC punya handler nyata; migrasi absensi tidak valid; tidak ada HTTP mux terpasang; login web masih mock | `HRIS-Stery/services/attendance-service/migrations/001_create_attendance_schema.up.sql`, `HRIS-Stery/apps/web/src/routes/(auth)/login/+page.server.ts`, `HRIS-Stery/docs/adr/0004-defer-payroll-to-phase2.md` |
| Platform `stery-suite` | Belum | Folder dan repo git dibuat; hanya berisi `docs/`; tidak ada kode | `stery-suite/docs` |

### 13.2 Status per modul platform

| Modul | Status | Keterangan | Bukti |
| --- | --- | --- | --- |
| SUI 01 IAM | Belum | Tidak ada kode; SELA hanya OTP lokal | `SELA/apps/api/services/auth/http.go` |
| SUI 02 ENT | Belum | SELA hanya `events.package` -> `plans` per-event | `SELA/apps/api/services/payment/postgres.go` |
| SUI 03 BIL | Belum | Provider pembayaran SELA dapat dipakai ulang (Midtrans + sandbox) | `SELA/apps/api/services/payment/provider.go` |
| SUI 04 NTF | Belum | Outbox notifikasi SELA sebagai acuan | `SELA/apps/api/internal/db/migrations/0008_notifications.sql` |
| SUI 05 AUD | Belum | `internal/audit` SELA sebagai sumber `kit/audit` | `SELA/apps/api/internal/audit/audit.go` |
| SUI 06 ADM | Belum | Tidak ada | `stery-suite/docs` |
| SUI 07 INT | Belum | HRIS dan POS punya paket NATS bersama; tidak ada lintas produk | `POS-Stery/services/_shared/nats/event_envelope.go` |
| SUI 08 DEP | Belum | Compose SELA sebagai acuan | `SELA/deploy/docker-compose.yml` |

Kontradiksi dokumen status vs kode dicatat di `00_Analisis_Dampak_Risiko` bagian 3 dan FSD masing-masing produk bagian 11.3.

## 14. Persetujuan

Dokumen ini merupakan BRD pertama untuk Stery Suite dan perlu ditinjau serta disetujui pemangku kepentingan bisnis sebelum dijadikan acuan PRD dan FSD final serta pekerjaan S1.

| **Nama** | **Jabatan** | **Tanda Tangan** | **Tanggal** |
|----------|------------------|------------------|-------------|
|          | Product Owner    |                  |             |
|          | Business Sponsor |                  |             |
|          | Engineering Lead |                  |             |
