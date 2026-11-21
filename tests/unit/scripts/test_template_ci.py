#!/usr/bin/env python3
"""Exercise the template GitHub config step in disposable repositories."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / 'docs' / 'repo-template' / '.github' / 'workflows' / 'ci-baseline.yml'


def config_step():
    source = WORKFLOW.read_text(encoding='utf-8')
    pattern = r'^      - name: agent config self-check\n        run: \|\n((?:          [^\n]*\n)+)'
    matches = re.findall(pattern, source, flags=re.MULTILINE)
    if len(matches) != 1:
        raise ValueError('Cannot uniquely locate the template config step')
    return textwrap.dedent(matches[0])


def run_step(script, files):
    with tempfile.TemporaryDirectory(prefix='template-ci-test-') as temp:
        root = Path(temp)
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
        env = os.environ.copy()
        env.pop('BASH_ENV', None)
        return subprocess.run(
            ['/bin/bash', '--noprofile', '--norc', '-e', '-o', 'pipefail', '-c', script],
            cwd=root, env=env, capture_output=True, text=True,
        )


class TestTemplateConfigStep(unittest.TestCase):
    def test_config_inputs_enforce_expected_exit_status(self):
        valid = {'AGENTS.md': 'rules\n', 'CLAUDE.md': '@AGENTS.md\n',
                 '.claude/settings.json': '{}\n'}
        cases = [
            ('valid', valid, True),
            ('missing_both', {'.claude/settings.json': '{}\n'}, False),
            ('missing_agents', {k: v for k, v in valid.items() if k != 'AGENTS.md'}, False),
            ('missing_claude', {k: v for k, v in valid.items() if k != 'CLAUDE.md'}, False),
            ('bad_reference', {**valid, 'CLAUDE.md': 'unrelated\n'}, False),
            ('invalid_json', {**valid, '.claude/settings.json': '{'}, False),
            ('missing_json', {k: v for k, v in valid.items() if k != '.claude/settings.json'}, False),
        ]
        script = config_step()
        for name, files, expected_success in cases:
            with self.subTest(name=name):
                result = run_step(script, files)
                self.assertEqual(result.returncode == 0, expected_success, result.stderr)

    def test_regression_fixture_detects_legacy_and_list_bug(self):
        legacy = ('test -f AGENTS.md && test -f CLAUDE.md && grep -q "@AGENTS.md" CLAUDE.md\n'
                  'python3 -m json.tool .claude/settings.json > /dev/null\n')
        files = {'CLAUDE.md': '@AGENTS.md\n', '.claude/settings.json': '{}\n'}
        self.assertEqual(run_step(legacy, files).returncode, 0)
        self.assertNotEqual(run_step(config_step(), files).returncode, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
