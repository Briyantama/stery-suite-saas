#!/usr/bin/env python3
"""Builds the Stery Suite progress tracker workbook from docs/tracking/tracker.json.

Outputs (in docs/tracking/): Stery_Suite_Progress_Tracker.xlsx plus tracker.csv, changelog.csv and
traceability.csv for plain-text diffs and Excel import.

Requirements are parsed from the three FSDs (FR-SUI-*, FR-HRS-*, FR-POS-*) so they never drift from the
spec; SELA requirements come from SELA/docs/tracking/{tracker.json,traceability.csv}. tracker.json only
holds tasks, change log and `requirement_overrides` for verified requirements. Commit hashes are checked
against the git repo of the task's product.

Usage:
    python scripts/build_tracker.py           validate, then write the workbook and CSVs
    python scripts/build_tracker.py --check   validate only (no files written)
"""
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent
TRACK_DIR = ROOT / "docs" / "tracking"
DATA_FILE = TRACK_DIR / "tracker.json"
XLSX_FILE = TRACK_DIR / "Stery_Suite_Progress_Tracker.xlsx"
FSD_FILES = [ROOT / "docs" / "FSD_Stery_Suite.en.md", ROOT / "HRIS-Stery" / "docs" / "FSD_HRIS.en.md",
             ROOT / "POS-Stery" / "docs" / "FSD_POS.en.md"]
GATES_FILE = ROOT / "docs" / "00_Analisis_Dampak_Risiko.en.md"
SELA_DIR = ROOT / "SELA"
SELA_DATA = SELA_DIR / "docs" / "tracking" / "tracker.json"
SELA_TRACE = SELA_DIR / "docs" / "tracking" / "traceability.csv"

TASK_STATUSES = ["Not Started", "In Progress", "Pending Verification", "Completed"]
REQ_STATUSES = ["Not Started", "Partial", "Completed"]
PRODUCTS = ["SEL", "POS", "HRS", "KIT", "SUI"]
REPO_DIRS = {"SEL": SELA_DIR, "POS": ROOT / "POS-Stery", "HRS": ROOT / "HRIS-Stery", "KIT": ROOT / "stery-kit",
             "SUI": ROOT}
FR_PRODUCT = {"SUI": "SUI", "HRS": "HRS", "POS": "POS"}

STATUS_FILL = {
    "Not Started": "E7E6E6",
    "In Progress": "FFF2CC",
    "Pending Verification": "FCE4D6",
    "Completed": "C6E0B4",
    "Partial": "FFF2CC",
}

HASH_RE = re.compile(r"\b[0-9a-f]{7,40}\b")
TASK_REF_RE = re.compile(r"\bS[0-5]\.\d+\b")
FR_ID_RE = re.compile(r"\b(?:SEL FR-(?:SEC\.\d+|\d{2}\.\d+)|FR-(?:SUI|HRS|POS)-(?:SEC\.\d+|\d+\.\d+))\b")
# Spec rows: | ID | text | priority | status | evidence |. Split from the right so `|` inside the text survives;
# the shorter 4-column summary tables in the HRIS FSD fail the priority check and are skipped.
FSD_ROW_RE = re.compile(r"^\|\s*(FR-(?:SUI|HRS|POS)-(?:SEC\.\d+|\d+\.\d+))\s*\|(.*)\|\s*$", re.MULTILINE)
PRIORITIES = {"M", "S", "C", "W"}


def fsd_status(text):
    """Maps FSD status text to a requirement status. 'Pending Verification' counts as Partial."""
    head = text.strip().lower()
    if head.startswith("done"):
        return "Completed"
    if head.startswith(("partial", "pending")):
        return "Partial"
    return "Not Started"


def parse_fsd_text(text):
    """Returns {FR-ID: {text, product, status, evidence}}, first spec row of each ID wins."""
    found = {}
    for fr_id, body in FSD_ROW_RE.findall(text):
        parts = [p.strip() for p in body.rsplit(" | ", 3)]
        if len(parts) != 4 or parts[1] not in PRIORITIES:
            continue
        found.setdefault(fr_id, {"text": parts[0], "product": FR_PRODUCT[fr_id.split("-")[1]],
                                 "status": fsd_status(parts[2]), "evidence": parts[3]})
    return found


def parse_sela_requirements():
    """SELA requirements: text from traceability.csv, status/tasks/evidence from SELA's tracker.json."""
    own = json.loads(SELA_DATA.read_text(encoding="utf-8"))["requirements"]
    found = {}
    with SELA_TRACE.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            fr_id, req = row["FR ID"], own.get(row["FR ID"], {})
            found[f"SEL {fr_id}"] = {"text": row["Requirement (from FSD)"], "product": "SEL",
                                     "status": req.get("status", "Not Started"),
                                     "evidence": req.get("evidence", ""), "tasks": req.get("tasks", "")}
    return found


def parse_requirements():
    found = {}
    for path in FSD_FILES:
        found.update(parse_fsd_text(path.read_text(encoding="utf-8")))
    found.update(parse_sela_requirements())
    return found


def parse_gate_criteria():
    """Returns {stage: number of numbered exit criteria} from the S0-S5 table (at least 1 per stage)."""
    counts = {}
    for stage, _, exit_text in re.findall(r"^\|\s*(S[0-5])\s*\|(.*?)\|(.*)\|\s*$",
                                          GATES_FILE.read_text(encoding="utf-8"), re.MULTILINE):
        counts[stage] = max(1, len(re.findall(r"\(\d+\)", exit_text)))
    return counts


def load_data():
    with DATA_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


def git_has_commit(product, commit):
    result = subprocess.run(["git", "-C", str(REPO_DIRS[product]), "cat-file", "-e", f"{commit}^{{commit}}"],
                            capture_output=True, check=False)
    return result.returncode == 0


def is_na(text):
    return text.strip().lower().startswith("n/a")


def validate(data, requirements, commit_exists=git_has_commit):
    errors = []
    milestone_ids = [m["id"] for m in data["milestones"]]
    task_ids = [t["id"] for t in data["tasks"]]
    product_of = {t["id"]: t["product"] for t in data["tasks"]}

    for dup in sorted({i for i in task_ids if task_ids.count(i) > 1}):
        errors.append(f"duplicate task id {dup}")

    def check_commits(label, product, text):
        if is_na(text):
            return
        for commit in HASH_RE.findall(text):
            if not commit_exists(product, commit):
                errors.append(f"{label}: commit {commit} not found in git repo of {product}")

    for task in data["tasks"]:
        tid = task["id"]
        if task["milestone"] not in milestone_ids:
            errors.append(f"{tid}: unknown milestone {task['milestone']}")
        if task["product"] not in PRODUCTS:
            errors.append(f"{tid}: unknown product {task['product']!r}")
            continue
        if task["status"] not in TASK_STATUSES:
            errors.append(f"{tid}: invalid status {task['status']!r}")
        if task["status"] == "Completed":
            green = task["green"].strip()
            if not green or not (is_na(green) or HASH_RE.search(green)):
                errors.append(f"{tid}: a Completed task needs a GREEN commit (or an explicit n/a (reason))")
        for field in ("red", "green"):
            check_commits(f"{tid} {field}", task["product"], task[field])
        for fr_id in FR_ID_RE.findall(task["frs"]):
            if fr_id not in requirements:
                errors.append(f"{tid}: {fr_id} is not a known requirement")

    for entry in data["changelog"]:
        if entry["task"] not in task_ids:
            errors.append(f"changelog entry references unknown task {entry['task']}")
        elif product_of[entry["task"]] in PRODUCTS:
            check_commits(f"changelog {entry['task']}", product_of[entry["task"]], entry["commits"])

    for fr_id, req in data["requirement_overrides"].items():
        if fr_id not in requirements:
            errors.append(f"requirement_overrides: {fr_id} is not a known requirement")
        if req.get("status", "Not Started") not in REQ_STATUSES:
            errors.append(f"requirement_overrides {fr_id}: invalid status {req.get('status')!r}")
        for ref in TASK_REF_RE.findall(req.get("tasks", "")):
            if ref not in task_ids:
                errors.append(f"requirement_overrides {fr_id}: unknown task {ref}")

    completed = {t["id"] for t in data["tasks"] if t["status"] == "Completed"}
    logged = {e["task"] for e in data["changelog"]}
    for missing in sorted(completed - logged):
        errors.append(f"{missing}: Completed but has no change log entry")

    return errors


def _task_sort_key(task_id):
    head, _, tail = task_id.partition(".")
    return (head, int(tail) if tail.isdigit() else 0)


def _fr_sort_key(fr_id):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", fr_id)]


def milestone_name(data, milestone_id):
    return next((m["name"] for m in data["milestones"] if m["id"] == milestone_id), milestone_id)


def tracker_rows(data):
    order = {m["id"]: i for i, m in enumerate(data["milestones"])}
    tasks = sorted(data["tasks"], key=lambda t: (order.get(t["milestone"], 99), _task_sort_key(t["id"])))
    return [
        [milestone_name(data, t["milestone"]), t["id"], f"{t['task']}\n{t['description']}".strip(), t["product"],
         t["status"], t["red"], t["green"], t["coverage"], t["frs"], t["deliverables"], t["updated"]]
        for t in tasks
    ]


def changelog_rows(data):
    order = {m["id"]: i for i, m in enumerate(data["milestones"])}
    entries = sorted(data["changelog"], key=lambda e: (order.get(e["milestone"], 99), _task_sort_key(e["task"])))
    return [
        [milestone_name(data, e["milestone"]), e["module"], e["task"], e["summary"], e["breaking"],
         e["decisions"], e["commits"], e["date"]]
        for e in entries
    ]


def trace_rows(data, requirements):
    """One row per requirement: FSD/SELA status unless overridden; tasks = task `frs` refs + override tasks."""
    milestone_of = {t["id"]: t["milestone"] for t in data["tasks"]}
    linked = {}
    for task in data["tasks"]:
        for fr_id in FR_ID_RE.findall(task["frs"]):
            linked.setdefault(fr_id, set()).add(task["id"])
    rows = []
    for fr_id in sorted(requirements, key=_fr_sort_key):
        req = requirements[fr_id]
        over = data["requirement_overrides"].get(fr_id, {})
        refs = linked.get(fr_id, set()) | set(TASK_REF_RE.findall(over.get("tasks", "")))
        refs |= set(TASK_REF_RE.findall(req.get("tasks", "")))
        refs = sorted(refs, key=_task_sort_key)
        milestones = sorted({milestone_of[r] for r in refs if r in milestone_of})
        rows.append([fr_id, req["text"], req["product"], ", ".join(milestones),
                     over.get("status", req["status"]), ", ".join(refs), over.get("evidence", req["evidence"])])
    return rows


TRACKER_HEADERS = ["Phase / Milestone", "Task ID", "Task & Description", "Product", "Status",
                   "TDD: RED commit", "TDD: GREEN commit", "Test coverage", "FR IDs", "Key Deliverables / Artifacts",
                   "Last Updated"]
CHANGELOG_HEADERS = ["Phase / Milestone", "Module / Service", "Task ID", "Summary of implemented functionality",
                     "Breaking changes / structural refactors", "Deviations & technical decisions", "Commits", "Date"]
TRACE_HEADERS = ["Req ID", "Requirement", "Product", "Milestone", "Status", "Tracker task(s)", "Evidence"]

THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEADER_FILL = PatternFill("solid", fgColor="1F3864")
HEADER_FONT = Font(bold=True, color="FFFFFF")


def write_table(ws, headers, rows, widths, freeze="C2"):
    ws.append(headers)
    for row in rows:
        ws.append(row)
    for cell in ws[1]:
        cell.fill, cell.font, cell.border = HEADER_FILL, HEADER_FONT, BORDER
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = BORDER
    for index, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(index)].width = width
    ws.freeze_panes = freeze
    ws.auto_filter.ref = ws.dimensions


def add_status_formatting(ws, column_letter, last_row):
    for status, color in STATUS_FILL.items():
        ws.conditional_formatting.add(
            f"{column_letter}2:{column_letter}{last_row}",
            FormulaRule(formula=[f'${column_letter}2="{status}"'], fill=PatternFill("solid", bgColor=color, fgColor=color)),
        )


def add_status_dropdown(ws, column_letter, last_row, statuses):
    dv = DataValidation(type="list", formula1='"' + ",".join(statuses) + '"', allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(f"{column_letter}2:{column_letter}{last_row}")


def _share(part, whole):
    return part / whole if whole else 0


def _count(rows, column, status_column, key, statuses):
    return [sum(1 for r in rows if r[column] == key and r[status_column] == s) for s in statuses]


def _style_header(summary, row):
    for cell in summary[row]:
        if cell.value:
            cell.fill, cell.font, cell.border = HEADER_FILL, HEADER_FONT, BORDER


def build_summary(wb, data, task_rows, trace_rows_, sela=None, gate_criteria=None):
    """Writes computed numbers, not formulas: openpyxl cannot store a formula together with its cached
    result, so formula cells read as None for pandas/openpyxl (data_only=True). The workbook is
    regenerated from tracker.json on every run, so there is nothing for a formula to keep live.
    `sela` = (task status counts, requirement status counts) read live from SELA's own tracker."""
    summary = wb.create_sheet("Summary", 1)
    headers = TASK_STATUSES + ["Total", "% Completed"]
    summary.append(["Phase / Milestone"] + headers)
    header_rows = [1]
    for milestone in data["milestones"]:
        counts = _count(task_rows, 0, 4, milestone["name"], TASK_STATUSES)
        summary.append([milestone["name"]] + counts + [sum(counts), _share(counts[-1], sum(counts))])
    totals = [sum(1 for r in task_rows if r[4] == s) for s in TASK_STATUSES]
    summary.append(["All tasks"] + totals + [sum(totals), _share(totals[-1], sum(totals))])

    summary.append([])
    summary.append(["Product rollup"] + [f"Tasks: {s}" for s in TASK_STATUSES] + ["Tasks: total"]
                   + [f"Reqs: {s}" for s in REQ_STATUSES] + ["Reqs: total"])
    header_rows.append(summary.max_row)
    for product in PRODUCTS:
        t = _count(task_rows, 3, 4, product, TASK_STATUSES)
        r = _count(trace_rows_, 2, 4, product, REQ_STATUSES)
        summary.append([product] + t + [sum(t)] + r + [sum(r)])
    if sela:
        t = [sela[0].get(s, 0) for s in TASK_STATUSES]
        r = [sela[1].get(s, 0) for s in REQ_STATUSES]
        summary.append(["SELA own tracker (SELA/docs/tracking/tracker.json)"] + t + [sum(t)] + r + [sum(r)])

    if gate_criteria:
        summary.append([])
        summary.append(["Stabilisation gate (stage)", "Gate criteria", "Stage tasks", "Completed tasks", "% Completed"])
        header_rows.append(summary.max_row)
        for milestone in data["milestones"]:
            counts = _count(task_rows, 0, 4, milestone["name"], TASK_STATUSES)
            summary.append([milestone["name"], gate_criteria.get(milestone["id"], 0), sum(counts), counts[-1],
                            _share(counts[-1], sum(counts))])
            summary.cell(row=summary.max_row, column=5).number_format = "0%"
    for row in range(2, 2 + len(data["milestones"]) + 1):
        summary.cell(row=row, column=7).number_format = "0%"
    for row in header_rows:
        _style_header(summary, row)
    summary.column_dimensions["A"].width = 52
    for col in "BCDEFGHIJK":
        summary.column_dimensions[col].width = 20
    summary.freeze_panes = "B2"


def build_guide(wb, data):
    guide = wb.active
    guide.title = "Guide"
    lines = [
        ("Stery Suite progress tracker", True),
        (f"Data as of {data['as_of']}. Generated from docs/tracking/tracker.json, the three FSDs and SELA's own tracker; do not edit this workbook by hand.", False),
        ("To update: edit tracker.json, then run `python scripts/build_tracker.py` (see docs/tracking/README.md).", False),
        ("", False),
        ("Stages: S0-S5 from docs/00_Analisis_Dampak_Risiko.en.md section 7. Products: SEL (SELA), POS, HRS, KIT (stery-kit), SUI (platform / suite level).", False),
        ("", False),
        ("Task statuses", True),
        ("Not Started: nothing committed for the task.", False),
        ("In Progress: RED test committed or work under way.", False),
        ("Pending Verification: implemented, but a stated verification step is still open.", False),
        ("Completed: GREEN commit recorded (or an explicit n/a (reason), required for SUI tasks), change log entry present.", False),
        ("", False),
        ("Requirement statuses (Traceability sheet): Not Started, Partial, Completed. FSD 'Done' = Completed, 'Partial' / 'Pending Verification' = Partial, 'Not started' = Not Started; requirement_overrides replace them once verified.", False),
        ("Sheets: Summary (counts computed at build time), Tracker (one row per task), Change Log, Traceability (SUI/HRS/POS requirements from the FSDs; SELA requirements as 'SEL FR-xx.y').", False),
    ]
    for index, (text, bold) in enumerate(lines, start=1):
        guide.cell(row=index, column=1, value=text).font = Font(bold=bold, size=14 if index == 1 else 11)
    guide.column_dimensions["A"].width = 130


def sela_rollup():
    own = json.loads(SELA_DATA.read_text(encoding="utf-8"))
    tasks, reqs = {}, {}
    for t in own["tasks"]:
        tasks[t["status"]] = tasks.get(t["status"], 0) + 1
    for r in own["requirements"].values():
        reqs[r["status"]] = reqs.get(r["status"], 0) + 1
    return tasks, reqs


def build_workbook(data, requirements, sela=None, gate_criteria=None):
    wb = Workbook()
    build_guide(wb, data)

    t_rows = tracker_rows(data)
    tracker = wb.create_sheet("Tracker")
    write_table(tracker, TRACKER_HEADERS, t_rows, [30, 9, 55, 10, 20, 18, 20, 22, 26, 70, 14])
    add_status_dropdown(tracker, "E", tracker.max_row, TASK_STATUSES)
    add_status_formatting(tracker, "E", tracker.max_row)

    c_rows = changelog_rows(data)
    changelog = wb.create_sheet("Change Log")
    write_table(changelog, CHANGELOG_HEADERS, c_rows, [30, 30, 9, 60, 55, 70, 30, 12])

    r_rows = trace_rows(data, requirements)
    trace = wb.create_sheet("Traceability")
    write_table(trace, TRACE_HEADERS, r_rows, [16, 80, 9, 14, 14, 26, 60], freeze="B2")
    add_status_formatting(trace, "E", trace.max_row)
    add_status_dropdown(trace, "E", trace.max_row, REQ_STATUSES)

    build_summary(wb, data, t_rows, r_rows, sela, gate_criteria)
    return wb, t_rows, c_rows, r_rows


def write_csv(path, headers, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)
        writer.writerows(rows)


def main(argv):
    check_only = "--check" in argv
    data = load_data()
    requirements = parse_requirements()
    if not any(r["product"] != "SEL" for r in requirements.values()):
        print("no FR rows found in the suite FSDs", file=sys.stderr)
        return 1

    errors = validate(data, requirements)
    if errors:
        print("tracker validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    wb, t_rows, c_rows, r_rows = build_workbook(data, requirements, sela_rollup(), parse_gate_criteria())
    counts = {status: sum(1 for row in t_rows if row[4] == status) for status in TASK_STATUSES}
    print(f"tracker ok: {len(t_rows)} tasks {counts}; {len(c_rows)} change log entries; {len(r_rows)} requirements")
    if check_only:
        return 0

    wb.save(XLSX_FILE)
    write_csv(TRACK_DIR / "tracker.csv", TRACKER_HEADERS, t_rows)
    write_csv(TRACK_DIR / "changelog.csv", CHANGELOG_HEADERS, c_rows)
    write_csv(TRACK_DIR / "traceability.csv", TRACE_HEADERS, r_rows)
    print(f"wrote {XLSX_FILE.relative_to(ROOT)} and 3 CSV files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
