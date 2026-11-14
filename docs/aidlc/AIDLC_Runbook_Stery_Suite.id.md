# Runbook AI-DLC: Stery Suite

Tanggal: 2026-11-14

Cara membaca: ikuti bagian dari atas ke bawah pada pemakaian pertama; setelah itu pakai "Perintah, berurutan" dan "Konfirmasi yang sudah dijawab di muka" sebagai daftar periksa. Kondisi terkini tiap repo ada di `docs/aidlc/AIDLC_Progress_Stery_Suite.id.md`.

## Prasyarat

| # | Pemeriksaan | Perintah (dari root suite `C:/Users/solui/moon-eye/stery-suite`) | Hasil yang diharapkan |
|---|---|---|---|
| 1 | Ekstensi engine ada | `ls ~/.omp/agent/extensions/aidlc-workflow.ts` | berkas ada |
| 2 | Working tree bersih per repo | `git -C SELA status --short`, sama untuk `POS-Stery`, `HRIS-Stery`, `stery-kit` | kosong; commit atau stash dulu perubahan design-system yang belum di-commit (jumlahnya ada di dokumen Progress, bagian Summary) |
| 3 | Gerbang kualitas hijau per repo produk | `bash scripts/check.sh` di dalam `SELA/`, `POS-Stery/`, `HRIS-Stery/` | exit 0; butuh `TEST_DATABASE_URL` dan `TEST_REDIS_ADDR` |
| 4 | stery-kit sudah di-push | `git -C stery-kit ls-remote origin` | tidak kosong (CI produk melakukan checkout kit) |
| 5 | Tracker dapat dibangun | `python scripts/build_tracker.py --check` | exit 0 |

Fakta engine (sumber: `~/.omp/agent/extensions/aidlc-engine/README.md`):

- Perintah: `/aidlc start <task> [--scope X] [--run]`, `status`, `next`, `approve [note] [--hold]`, `reject <feedback>`, `resume`, `report`, `scope <name>`, `skip`, `help`.
- State berada di `<project>/.aidlc/`: `state.json`, `audit.jsonl` (hash chain), `attest/*.json`, `records/<phase>/<stage>/*.md`, `report.md`.
- Sebuah stage selesai hanya jika artefaknya ada, minimal 60 byte, memuat heading `##`, dan tanpa placeholder.
- Guard hanya aktif bila `<cwd>/.aidlc` ada.

## Topologi eksekusi

Dua tingkat. Jangan dicampur dalam satu sesi.

| Tingkat | Jalankan `omp` di | Dipakai untuk | Folder state |
|---|---|---|---|
| Suite | root suite | intent lintas repo: pekerjaan platform, milestone S4-S5, requirement FR-SUI | `.aidlc/` (sudah ada; id `aidlc-20261114051752-6a2ffc`, scope `classic`, 3 stage disetujui, 15 pending) |
| Produk | `SELA/`, `POS-Stery/` atau `HRIS-Stery/` | FR dan Bolt per produk | `<repo>/.aidlc/`, dibuat oleh `/aidlc start` pertama di folder itu |

Aturan:

- Intent buatan tangan di `<repo>/docs/aidlc/intents/` tetap menjadi catatan yang dapat dibaca manusia. Rekaman engine masuk ke `.aidlc/records/`. Jangan menyalin isi di antara keduanya: rekaman requirements-analysis milik engine menautkan ke folder intent.
- stery-kit tidak punya intent. Pekerjaan kit lintas repo berjalan di tingkat suite; pekerjaan khusus kit boleh menjalankan `omp` di `stery-kit/` (`.aidlc/` dibuat di sana).
- Tambahkan `.aidlc/` ke `.gitignore` terkait sebelum commit pertama bila rekaman ingin dijaga tetap lokal. Saat pemindaian, `.aidlc/` di root suite belum dilacak.

## Perintah, berurutan

1. `omp` di folder yang dipilih. `/aidlc status`: di tingkat suite menampilkan scope `classic`, 3 stage disetujui dan 15 pending.
2. `/aidlc scope feature` (scope belum dikunci di tingkat suite, `scopeLocked:false`). Scope `feature` menandai seluruh 33 stage EXECUTE (`~/.omp/agent/skills/aidlc-upstream/scopes/aidlc-feature.md`), sehingga daftar pending bertambah; jalankan `/aidlc status` lagi dan baca daftar baru sebelum lanjut. Run tingkat produk: `/aidlc start "<task>" --scope feature`.
3. `/aidlc next`: menjalankan stage pending berikutnya. Jawab tiap gerbang (lihat tabel di bawah).
4. Baca artefak stage di `.aidlc/records/<phase>/<stage>/`. Jalur bukti wajib tercantum.
5. `/aidlc approve [note]` bila sudah puas; `/aidlc reject <feedback>` untuk mengembalikan stage agar direvisi.
6. `/aidlc resume` setelah giliran terputus (stage berstatus `interrupted`).
7. `/aidlc report` menulis `.aidlc/report.md` bila Anda ingin ringkasan.

Hanya manusia yang dapat menjalankan `/aidlc approve`; model tidak bisa. Persetujuan ditolak dengan `STALE_ARTIFACTS` bila artefak yang digerbang berubah setelah attestation. Jalankan ulang stage untuk attest ulang, lalu setujui.

## Titik masuk per stage

Diambil dari peta stage di dokumen Progress.

| Target | Mulai run dari | Lalu |
|---|---|---|
| SELA | Tutup gerbang tinjauan manusia inception (intent `261014-closed-beta-readiness`, gerbang Open); catat keputusan di rekaman requirements-analysis milik engine | Verifikasi B1-B2 (sudah dibangun, belum diverifikasi), lalu B7: uji perangkat nyata, bukti webhook Midtrans, T7.2 butuh minimal 3 baris di `SELA/docs/tracking/usability_sessions.csv` |
| POS-Stery | build-and-test: verifikasi ulang B6 secara lokal dan jalankan ulang `bash scripts/check.sh` | Kerjakan 18 temuan High yang masih terbuka di `code-review-2026-11-08.md`; lalu isi celah user-stories dan domain-design; lalu contract-design (OpenAPI) |
| HRIS-Stery | build-and-test: verifikasi ulang B6 secara lokal dan jalankan ulang `bash scripts/check.sh` | Kerjakan temuan High yang terbuka dan cacat yang dikutip FSD; lalu celah user-stories; lalu contract-design (tabel RPC ada di FSD, proto dihapus) |
| stery-kit | requirements-analysis dan contract-design untuk tugas KIT (tracker S1.1 satu-satunya tugas KIT) | Pakai hasil reverse-engineering full rescan sebagai dasar; lalu build-and-test dengan perintah kit (C3) |
| Suite | units-generation dan delivery-planning untuk milestone S4-S5 | Tautkan ke `docs/00_Analisis_Dampak_Risiko.id.md` bagian 7 dan milestone tracker, jangan ditulis ulang |

## Konfirmasi yang sudah dijawab di muka

Default yang diusulkan lebih dulu. Ganti dengan menjawab berbeda pada gerbang.

| Gerbang | Muncul di | Jawaban default | Alasan |
|---|---|---|---|
| C1 Persetujuan stage | Setiap akhir stage, `/aidlc approve` | Setujui hanya bila artefak mencantumkan jalur bukti; selain itu `/aidlc reject` | Kualitas artefak hanya diperiksa secara struktural, bukan semantik |
| C2 Pakai ulang atau pindai ulang Code KB | reverse-engineering, per repo | `Focused scan` untuk POS-Stery, HRIS-Stery, SELA; `Full rescan` untuk stery-kit | Peta scout intent ada untuk tiga produk tetapi belum ada Code KB; kit tidak punya peta |
| C3 Perintah verifikasi per Unit | build-and-test dan tiap Bolt | SELA, POS-Stery, HRIS-Stery: `bash scripts/check.sh` (butuh `TEST_DATABASE_URL`, `TEST_REDIS_ADDR`; persempit dengan `CHECK_STAGES=go` atau `CHECK_STAGES=web`). stery-kit: `cd go && go build ./... && go vet ./... && go test ./... && cd ../web && npm run check && npm run test:unit`. Root suite: `python scripts/build_tracker.py --check` | Gerbang yang sama dengan yang sudah dipakai CI repo |
| C4 Otonomi saat konstruksi | awal konstruksi | Berhenti setelah tiap Bolt untuk ditinjau. Tanpa merge, tanpa push, tanpa kredensial asli. Selalu tanya sebelum migrasi destruktif, perubahan harga, kunci produksi | Aturan repo: AI mengusulkan, manusia memutuskan |
| C5 Bolt gagal | konstruksi | Berhenti dan tanya; kerjakan di branch sekali pakai, bukan `main` | Menjaga riwayat keempat repo tetap bersih |
| C6 Build gagal | build-and-test | Terima loop-back yang diusulkan, maksimum 3 per stage | Percobaan ulang dibatasi |
| C7 Persetujuan rencana sebelum code-generation menulis (`plan_approval`) | langkah rencana code-generation | Biarkan aktif | Engine memblokir penulisan di luar `.aidlc/` sampai rencana disetujui |
| C8 Scope | `/aidlc scope` | `feature` di tingkat suite; run tingkat produk juga memakai `feature` | Siklus penuh pada kedalaman praktis |
| C9 Tata letak repo | repo suite | Disarankan: tambahkan `.gitmodules` untuk `HRIS-Stery`, `POS-Stery`, `SELA`, `stery-kit` (URL `git@github.com:Briyantama/<repo>.git`; origin SELA saat ini `https://github.com/Briyantama/SELA.git`) dan hapus folder liar kosong `stery-suite/` di root suite | Commit suite yang sudah di-push menyimpan keempat repo sebagai gitlink (mode 160000) tanpa `.gitmodules`: clone baru mendapat empat folder kosong. Ini mengubah repo, jadi butuh persetujuan eksplisit Anda dan TIDAK dikerjakan oleh tugas dokumentasi ini |

## Pemecahan masalah

| Gejala | Tindakan |
|---|---|
| Stage macet `interrupted` | `/aidlc resume` (atau `/aidlc next`) menjalankannya ulang |
| Artefak ditolak karena ukuran, tanpa heading `##`, atau ada placeholder | Perbaiki berkas rekaman di `.aidlc/records/`, lalu jalankan ulang stage |
| `STALE_ARTIFACTS` saat approve | Artefak yang digerbang berubah setelah attestation; jalankan ulang stage untuk attest ulang, lalu setujui |
| Workflow beku, audit-chain atau state-digest tidak cocok | Jangan edit `.aidlc/state.json` dengan tangan. Pulihkan `.aidlc/` dari cadangan, atau hapus `<project>/.aidlc/` dan mulai ulang (README engine, rollback) |
| Engine bermasalah di mana-mana | Nonaktifkan dengan `omp --no-extensions`, atau ganti nama `aidlc-workflow.ts` |
| Port 8080 sudah terpakai di mesin dev | Apache tak terkait memakainya. e2e memakai 8081, 9091, 5174, 5175, 2525, 2526 |
| `go test -race` gagal atau dilewati | `-race` butuh cgo/gcc, tidak ada di mesin dev Windows; `scripts/check.sh` melewatinya, CI menjalankannya |
| `omp -p` berhenti setelah satu giliran | Mode print berakhir saat perintah kembali; stage berantai butuh mode TUI atau RPC |
