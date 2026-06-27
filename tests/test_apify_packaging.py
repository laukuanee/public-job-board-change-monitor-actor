import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("actor_main", ROOT / "main.py")
actor_main = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["actor_main"] = actor_main
SPEC.loader.exec_module(actor_main)


class ApifyPackagingTests(unittest.TestCase):
    def test_input_schema_defines_public_pages_array(self):
        schema = json.loads((ROOT / "INPUT_SCHEMA.json").read_text(encoding="utf-8"))

        self.assertEqual(schema["title"], "Public Job Board Change Monitor")
        self.assertEqual(schema["type"], "object")
        self.assertIn("pages", schema["properties"])
        self.assertEqual(schema["properties"]["pages"]["type"], "array")

    def test_local_actor_entrypoint_writes_job_and_change_records(self):
        payload = {
            "pages": [
                {
                    "url": "https://example.com/jobs",
                    "html": "<html><body><a class=\"job-card\" href=\"/jobs/engineer\">Engineer</a></body></html>",
                }
            ]
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = pathlib.Path(temp_dir) / "input.json"
            records_path = pathlib.Path(temp_dir) / "records.jsonl"
            input_path.write_text(json.dumps(payload), encoding="utf-8")

            exit_code = actor_main.run_local(input_path, records_path)

            records = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(exit_code, 0)
            self.assertEqual([record["record_type"] for record in records], ["job", "change"])
            self.assertEqual(records[0]["url"], "https://example.com/jobs/engineer")
            self.assertEqual(records[1]["change_type"], "new")


if __name__ == "__main__":
    unittest.main()
