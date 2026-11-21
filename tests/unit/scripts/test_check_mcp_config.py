#!/usr/bin/env python3
"""Test common credential checks using synthetic files only."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
CHECKER = ROOT / "scripts" / "check-mcp-config.py"
SENTINEL = "synthetic-secret-never-print"


class TestChecker(unittest.TestCase):
    def invoke(self, content):
        with tempfile.TemporaryDirectory(prefix="mcp-fixture-") as directory:
            path = Path(directory) / "input.json"
            path.write_text(content, encoding="utf-8")
            result = subprocess.run([sys.executable, "-I", str(CHECKER), str(path)], text=True, capture_output=True)
            self.assertNotIn(SENTINEL, result.stdout + result.stderr)
            self.assertNotIn(directory, result.stdout + result.stderr)
            return result.returncode, result.stdout

    def test_literal_sensitive_fields(self):
        for key in ("password", "api_key", "token", "Authorization", "clientSecret", "refresh_token", "X-API-Key", "X-Auth-Token", "private_key"):
            with self.subTest(key=key):
                status, _ = self.invoke(json.dumps({"servers": {"example": {key: SENTINEL}}}))
                self.assertEqual(status, 1)

    def test_placeholder_credentials(self):
        for value in ("${TOKEN}", "Bearer ${TOKEN}"):
            with self.subTest(value=value):
                status, _ = self.invoke(json.dumps({"headers": {"Authorization": value}}))
                self.assertEqual(status, 0)

    def test_literal_bearer_token(self):
        self.assertEqual(self.invoke(json.dumps({"headers": {"Authorization": "Bearer " + SENTINEL}}))[0], 1)

    def test_query_credentials_even_if_placeholder(self):
        for value in (SENTINEL, "${TOKEN}"):
            with self.subTest(value=value):
                status, _ = self.invoke(json.dumps({"url": "https://example.invalid/mcp?api_key=" + value}))
                self.assertEqual(status, 1)

    def test_url_user_info(self):
        self.assertEqual(self.invoke(json.dumps({"url": "https://user:" + SENTINEL + "@example.invalid"}))[0], 1)

    def test_invalid_json_is_unknown(self):
        self.assertEqual(self.invoke('{"authorization": "' + SENTINEL)[0], 2)

    def test_duplicate_keys_are_not_silently_accepted(self):
        duplicate = '"token": "' + SENTINEL + '", "token": "${TOKEN}"'
        for content in ('{' + duplicate + '}', '{"nested": {' + duplicate + '}}'):
            with self.subTest(content_type="nested" if "nested" in content else "root"):
                self.assertEqual(self.invoke(content)[0], 2)

    def test_json_root_not_object(self):
        self.assertEqual(self.invoke("[]")[0], 2)

    def test_empty_sensitive_value_needs_review(self):
        self.assertEqual(self.invoke('{"token": ""}')[0], 1)

    def test_non_sensitive_configuration_and_caveat(self):
        status, output = self.invoke('{"mcpServers": {"sample": {"type": "http", "url": "${MCP_URL}"}}}')
        self.assertEqual(status, 0)
        self.assertIn("not proof of safety", output)

    def test_empty_configuration(self):
        self.assertEqual(self.invoke("{}")[0], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
