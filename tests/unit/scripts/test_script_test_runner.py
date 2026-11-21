#!/usr/bin/env python3
"""Exercise the script test runner with isolated synthetic test suites."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
RUNNER = ROOT / "scripts" / "run-script-tests.py"


class TestScriptTestRunner(unittest.TestCase):
    def run_suite(self, source):
        with tempfile.TemporaryDirectory(prefix="test-runner-fixture-") as directory:
            Path(directory, "test_fixture.py").write_text(source, encoding="utf-8")
            return subprocess.run([sys.executable, "-B", "-I", str(RUNNER), directory],
                                  capture_output=True, text=True)

    def test_empty_suite_is_nonzero(self):
        result = self.run_suite("# no tests\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No tests discovered", result.stdout + result.stderr)

    def test_passing_suite_is_zero(self):
        result = self.run_suite("import unittest\nclass Example(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n")
        self.assertEqual(result.returncode, 0)

    def test_failed_suite_is_nonzero(self):
        result = self.run_suite("import unittest\nclass Example(unittest.TestCase):\n def test_fail(self): self.fail('fixture failure')\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fixture failure", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
