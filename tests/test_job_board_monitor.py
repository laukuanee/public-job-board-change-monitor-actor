import importlib.util
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("job_board_monitor", ROOT / "job_board_monitor.py")
monitor = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["job_board_monitor"] = monitor
SPEC.loader.exec_module(monitor)


SAMPLE_HTML = """<!doctype html>
<html>
  <body>
    <a class="job-card" href="/careers/senior-data-engineer">
      Senior Data Engineer
    </a>
    <a data-job-id="pm-42" href="https://jobs.example.com/product-manager">
      Product Manager, Growth
    </a>
    <a href="/about">About us</a>
    <a class="job-card" href="/careers/senior-data-engineer">
      Senior Data Engineer duplicate
    </a>
  </body>
</html>"""


class JobBoardMonitorTests(unittest.TestCase):
    def test_extracts_likely_public_job_links_and_dedupes_urls(self):
        result = monitor.extract_jobs_from_html("https://example.com/jobs", SAMPLE_HTML)

        self.assertEqual([job["title"] for job in result["jobs"]], ["Senior Data Engineer", "Product Manager, Growth"])
        self.assertEqual(
            [job["url"] for job in result["jobs"]],
            ["https://example.com/careers/senior-data-engineer", "https://jobs.example.com/product-manager"],
        )
        self.assertTrue(result["jobs"][0]["signature"].startswith("senior-data-engineer|"))
        self.assertEqual(result["stats"]["duplicate_jobs_removed"], 1)
        self.assertEqual(result["stats"]["links_seen"], 4)

    def test_compares_current_jobs_against_previous_signatures(self):
        current_jobs = [
            {"title": "Senior Data Engineer", "url": "https://example.com/jobs/1", "signature": "senior-data-engineer|https://example.com/jobs/1"},
            {"title": "Product Manager", "url": "https://example.com/jobs/2", "signature": "product-manager|https://example.com/jobs/2"},
        ]
        previous = [
            {"title": "Senior Data Engineer", "url": "https://example.com/jobs/1", "signature": "senior-data-engineer|https://example.com/jobs/1"},
            {"title": "Support Specialist", "url": "https://example.com/jobs/3", "signature": "support-specialist|https://example.com/jobs/3"},
        ]

        changes = monitor.compare_jobs(current_jobs, previous)

        self.assertEqual([change["change_type"] for change in changes], ["new", "unchanged", "removed"])
        self.assertEqual(changes[0]["title"], "Product Manager")
        self.assertEqual(changes[2]["title"], "Support Specialist")

    def test_run_actor_accepts_inline_html_and_previous_signatures(self):
        payload = {
            "pages": [
                {
                    "url": "https://example.com/jobs",
                    "html": SAMPLE_HTML,
                    "previous_jobs": [
                        {
                            "title": "Senior Data Engineer",
                            "url": "https://example.com/careers/senior-data-engineer",
                            "signature": "senior-data-engineer|https://example.com/careers/senior-data-engineer",
                        }
                    ],
                }
            ]
        }

        result = monitor.run_actor(payload)

        self.assertEqual(result["page_count"], 1)
        self.assertEqual(result["total_jobs"], 2)
        self.assertEqual(result["total_changes"], 2)
        self.assertEqual([change["change_type"] for change in result["pages"][0]["changes"]], ["new", "unchanged"])

    def test_run_actor_rejects_missing_pages(self):
        with self.assertRaises(ValueError) as context:
            monitor.run_actor({})

        self.assertIn("pages", str(context.exception))


if __name__ == "__main__":
    unittest.main()
