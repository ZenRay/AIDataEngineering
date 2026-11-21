#!/usr/bin/env python3
"""Exercise the path hook with synthetic paths and isolated subprocesses."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
HOOK = ROOT / '.claude' / 'hooks' / 'protect-paths.sh'


class TestProtectPaths(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='protect-paths-test-')
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'workspace'

    def invoke(self, payload, path=None):
        env = os.environ.copy()
        env['CLAUDE_PROJECT_DIR'] = str(self.project)
        if path is not None:
            env['PATH'] = str(path)
        return subprocess.run(['/bin/bash', str(HOOK)], input=payload,
                              text=True, capture_output=True, env=env)

    def with_path(self, relative):
        return json.dumps({'tool_input': {'file_path': str(self.project / relative)}})

    def test_normal_and_ask_paths_continue(self):
        for relative in ('docs/example.md', 'BackDocs/note.md', 'submodules-sibling/a'):
            with self.subTest(path=relative):
                self.assertEqual(self.invoke(self.with_path(relative)).returncode, 0)

    def test_protected_paths_are_blocked(self):
        for relative in ('submodules/example/a', 'BackDocs/archive/a'):
            with self.subTest(path=relative):
                self.assertEqual(self.invoke(self.with_path(relative)).returncode, 2)

    def test_realistic_edit_and_write_envelopes_continue(self):
        for tool, details in (
            ('Edit', {'old_string': 'old', 'new_string': 'new'}),
            ('Write', {'content': 'new content'}),
        ):
            with self.subTest(tool=tool):
                payload = json.dumps({'tool_name': tool, 'session_id': 'synthetic',
                                      'tool_input': {'file_path': str(self.project / 'docs/a'),
                                                     **details}})
                self.assertEqual(self.invoke(payload).returncode, 0)

    def test_windows_separator_normalization(self):
        payload = json.dumps({'tool_input': {'file_path':
                             str(self.project / 'submodules/a').replace('/', '\\')}})
        self.assertEqual(self.invoke(payload).returncode, 2)

    def test_invalid_inputs_are_blocked(self):
        for payload in ('{', '{}', '{"tool_input":{}}',
                        '{"tool_input":{"file_path":""}}',
                        '{"tool_input":{"file_path":null}}',
                        '{"tool_input":{"file_path":123}}',
                        '{"tool_input":{"file_path":[]}}',
                        self.with_path('docs/a') + '\n' + self.with_path('docs/b')):
            with self.subTest(payload=payload):
                result = self.invoke(payload)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertTrue(result.stderr)

    def test_missing_jq_is_blocked(self):
        bin_dir = Path(self.temp.name) / 'bin'
        bin_dir.mkdir()
        (bin_dir / 'cat').symlink_to('/bin/cat')
        result = self.invoke(self.with_path('docs/a'), path=bin_dir)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertTrue(result.stderr)

    def test_jq_failure_is_blocked(self):
        bin_dir = Path(self.temp.name) / 'failing-bin'
        bin_dir.mkdir()
        jq = bin_dir / 'jq'
        jq.write_text('#!/bin/bash\nexit 1\n', encoding='utf-8')
        jq.chmod(0o755)
        result = self.invoke(self.with_path('docs/a'), path=bin_dir)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertTrue(result.stderr)

    def test_project_directory_falls_back_to_cwd(self):
        self.project.mkdir()
        env = os.environ.copy()
        env.pop('CLAUDE_PROJECT_DIR', None)
        result = subprocess.run(['/bin/bash', str(HOOK)],
                                input=self.with_path('submodules/a'), text=True,
                                capture_output=True, env=env, cwd=self.project)
        self.assertEqual(result.returncode, 2, result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
