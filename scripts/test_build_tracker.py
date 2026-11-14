"""Tests for build_tracker.py (run: python scripts/test_build_tracker.py). No git or tracker.json needed."""
import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook, load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_tracker  # noqa: E402

FSD = """
| FR-POS-01.1 | Login | M | Done | `a.go` |
| FR-POS-01.2 | Store id | M | Partial: no UI | `b.go` |
| FR-POS-01.3 | Mode `a|b` selects | S | Not started | `c.go` |
| FR-HRS-01.1 | Tenant registers | M | Pending Verification | `d.go` |
| FR-HRS-01.1 | Partial | not atomic | `d.go` |
"""
REQS = build_tracker.parse_fsd_text(FSD)


def task(**kw):
    base = {"milestone": "S2", "id": "S2.1", "task": "t", "description": "d", "product": "SUI",
            "status": "Not Started", "red": "", "green": "", "coverage": "", "frs": "", "deliverables": "",
            "updated": "2026-11-11"}
    return {**base, **kw}


def data(tasks, changelog=(), overrides=None):
    return {"as_of": "2026-11-11", "milestones": [{"id": "S2", "name": "S2: POS"}], "tasks": tasks,
            "changelog": list(changelog), "requirement_overrides": overrides or {}}


LOG = {"milestone": "S2", "module": "SUI", "task": "S2.1", "summary": "s", "breaking": "", "decisions": "",
       "commits": "", "date": "2026-11-11"}


def errors(d):
    return build_tracker.validate(d, REQS, commit_exists=lambda product, commit: commit == "abcdef1")


class FsdParsingTest(unittest.TestCase):
    def test_status_mapping(self):
        self.assertEqual([REQS[i]["status"] for i in ("FR-POS-01.1", "FR-POS-01.2", "FR-POS-01.3", "FR-HRS-01.1")],
                         ["Completed", "Partial", "Not Started", "Partial"])

    def test_pipe_in_text_and_first_row_wins(self):
        self.assertEqual(REQS["FR-POS-01.3"]["text"], "Mode `a|b` selects")
        self.assertEqual(REQS["FR-HRS-01.1"]["text"], "Tenant registers")
        self.assertEqual(REQS["FR-HRS-01.1"]["product"], "HRS")


class ValidationTest(unittest.TestCase):
    def test_completed_with_na_and_changelog_is_valid(self):
        self.assertEqual(errors(data([task(status="Completed", green="n/a (docs only)")], [LOG])), [])

    def test_completed_without_green_or_changelog_fails(self):
        out = errors(data([task(status="Completed")]))
        self.assertTrue(any("GREEN" in e for e in out) and any("change log" in e for e in out))

    def test_completed_with_valid_and_bad_commit(self):
        self.assertEqual(errors(data([task(status="Completed", product="POS", green="abcdef1")], [LOG])), [])
        self.assertTrue(any("1234567" in e for e in errors(data([task(product="POS", red="1234567")]))))

    def test_unknown_fr_id_in_task_and_overrides(self):
        out = errors(data([task(frs="FR-POS-01.1, FR-POS-99.9")], overrides={
            "FR-HRS-77.7": {"status": "Completed", "tasks": "S2.9"}}))
        self.assertEqual(len(out), 3, out)

    def test_structural_errors(self):
        out = errors(data([task(status="Done", milestone="S9", product="XXX"), task()]))
        self.assertTrue(any("unknown milestone" in e for e in out) and any("unknown product" in e for e in out))
        self.assertTrue(any("duplicate task id" in e for e in errors(data([task(), task()]))))
        self.assertTrue(any("invalid status" in e for e in errors(data([task(status="Done")]))))

    def test_trace_rows_merge_override_and_task_links(self):
        d = data([task(frs="FR-POS-01.2")], overrides={"FR-POS-01.2": {"status": "Completed", "tasks": "S2.1",
                                                                       "evidence": "verified"}})
        row = next(r for r in build_tracker.trace_rows(d, REQS) if r[0] == "FR-POS-01.2")
        self.assertEqual(row, ["FR-POS-01.2", "Store id", "POS", "S2", "Completed", "S2.1", "verified"])


class SummaryTest(unittest.TestCase):
    def test_counts(self):
        d = data([])
        d["milestones"] = [{"id": "S0", "name": "S0"}, {"id": "S2", "name": "S2"}]
        tasks = [["S0", "", "", "SEL", "Completed"], ["S2", "", "", "POS", "In Progress"],
                 ["S2", "", "", "POS", "Completed"]]
        reqs = [["FR-POS-01.1", "", "POS", "", "Completed"], ["FR-POS-01.2", "", "POS", "", "Partial"]]
        wb = Workbook()
        build_tracker.build_summary(wb, d, tasks, reqs, ({"Completed": 4}, {"Partial": 2}), {"S0": 5, "S2": 8})
        with tempfile.TemporaryDirectory() as tmp:
            wb.save(Path(tmp) / "s.xlsx")
            sheet = load_workbook(Path(tmp) / "s.xlsx", data_only=True)["Summary"]
        rows = [[c.value for c in r] for r in sheet.iter_rows()]
        self.assertEqual(rows[2][1:7], [0, 1, 0, 1, 2, 0.5])
        pos = next(r for r in rows if r[0] == "POS")
        self.assertEqual(pos[1:9], [0, 1, 0, 1, 2, 0, 1, 1])
        sela = next(r for r in rows if r[0] and r[0].startswith("SELA own tracker"))
        self.assertEqual(sela[4], 4)
        self.assertEqual(next(r for r in rows if r[0] == "S2" and r[1] == 8)[2:5], [2, 1, 0.5])


if __name__ == "__main__":
    unittest.main()
