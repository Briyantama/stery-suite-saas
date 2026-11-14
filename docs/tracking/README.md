# Stery Suite progress tracking

Tracks the suite roadmap (stages S0-S5 in `../00_Analisis_Dampak_Risiko.en.md` section 7) across SELA (`SEL`), POS-Stery (`POS`), HRIS-Stery (`HRS`), `stery-kit` (`KIT`) and the future platform / suite-level work (`SUI`). Same workflow as SELA's tracker (`SELA/docs/tracking/README.md`).

## Files

| File | Role |
| ------ | ------ |
| `tracker.json` | **Source of truth** for tasks, change log and requirement overrides. Edit this file only. |
| `Stery_Suite_Progress_Tracker.xlsx` | Generated workbook: `Guide`, `Summary`, `Tracker`, `Change Log`, `Traceability`. Do not edit by hand. |
| `tracker.csv`, `changelog.csv`, `traceability.csv` | Generated plain-text mirrors (easy to diff). |
| `../../scripts/build_tracker.py` | Validates `tracker.json` and regenerates the workbook and CSVs. |

Regenerate from the suite root: `python scripts/build_tracker.py` (needs `openpyxl`). `--check` validates without writing. Tests: `python scripts/test_build_tracker.py`.

## Where the numbers come from (no second copy to keep in sync)

- **Tasks:** `tracker.json`. Milestones are the stages S0-S5; each stage's exit criteria are tasks.
- **Requirements:** parsed from the FSD tables on every build: `FR-SUI-*` from `FSD_Stery_Suite.en.md`, `FR-HRS-*` from `HRIS-Stery/docs/FSD_HRIS.en.md`, `FR-POS-*` from `POS-Stery/docs/FSD_POS.en.md`. FSD status text maps to `Done` -> Completed, `Partial` -> Partial, `Not started` -> Not Started. Use `requirement_overrides` in `tracker.json` only when the FSD status is stale and you have verified the code; give the evidence path.
- **SELA:** its own tracker (`SELA/docs/tracking/tracker.json`) is read live for the SELA rollup. Never copy SELA tasks here.

## Statuses

**Tasks:** `Not Started`, `In Progress`, `Pending Verification` (implemented, a stated check is open), `Completed`.
**Requirements:** `Not Started`, `Partial`, `Completed`.

A task is `Completed` only when: a GREEN commit hash (validated in that product's own git repo) or `n/a (reason)` is recorded, the stage's check from the roadmap holds, and a change log entry exists. Suite-level (`SUI`) tasks have no repo of their own, so they use `n/a (reason)`.

## When a task changes

1. Edit the task in `tracker.json` (`status`, `red`, `green`, `coverage`, `updated`); add rows for follow-up work you found.
2. Add a `changelog` entry: what was built, breaking/structural changes, deviations and why.
3. If an FSD requirement changed state, update its Status column in the FSD (the tracker reads it); add an override only when the FSD cannot be changed yet.
4. Run `python scripts/build_tracker.py` and fix what it reports.
5. Put FR IDs in the product commit body so `git log --grep "FR-POS-04"` finds them.

The suite root has no commits yet: commit `docs/tracking/` and `scripts/` once the suite repo gets its first commit.
