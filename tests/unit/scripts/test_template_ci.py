#!/usr/bin/env python3
"""Exercise the template GitHub config step in disposable repositories."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / 'docs' / 'repo-template' / '.github' / 'workflows' / 'ci-baseline.yml'


def config_step():
    source = WORKFLOW.read_text(encoding='utf-8')
    pattern = r'^      - name: agent config self-check\n        run: \|\n((?:          [^\n]*\n|[ \t]*\n)+)'
    matches = re.findall(pattern, source, flags=re.MULTILINE)
    if len(matches) != 1:
        raise ValueError('Cannot uniquely locate the template config step')
    lines = matches[0].splitlines(keepends=True)
    content = next((line for line in lines if line.strip()), None)
    if content is None:
        raise ValueError('Template config step has no commands')
    indent = len(content) - len(content.lstrip(' '))
    if any(line.strip() and not line.startswith(' ' * indent) for line in lines):
        raise ValueError('Inconsistent template config step indentation')
    return ''.join(line[indent:] if line.startswith(' ' * indent) else '\n'
                   for line in lines)


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

    def extract_fixture(self, body):
        with tempfile.TemporaryDirectory() as temp:
            workflow = Path(temp) / 'workflow.yml'
            workflow.write_text('      - name: agent config self-check\n'
                                '        run: |\n' + body +
                                '      - name: following step\n'
                                '        run: echo not-part-of-block\n', encoding='utf-8')
            original = config_step.__globals__['WORKFLOW']
            try:
                config_step.__globals__['WORKFLOW'] = workflow
                return config_step()
            finally:
                config_step.__globals__['WORKFLOW'] = original

    def test_config_step_keeps_commands_after_blank_lines(self):
        for blank in ('\n', '    \n'):
            with self.subTest(blank=repr(blank)):
                script = self.extract_fixture('          printf "before\\n"\n' + blank +
                                              '          printf "after\\n"\n'
                                              '          exit 1\n')
                result = run_step(script, {})
                self.assertEqual(result.stdout, 'before\nafter\n')
                self.assertEqual(result.returncode, 1)
                self.assertNotIn('not-part-of-block', script)

    def test_config_step_uses_first_content_line_indentation(self):
        script = self.extract_fixture("            cat <<'EOF'\n"
                                      '            hello\n'
                                      '            EOF\n'
                                      '            printf "done\\n"\n')
        result = run_step(script, {})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'hello\ndone\n')

    def test_config_step_preserves_extra_spaces_on_blank_lines(self):
        script = self.extract_fixture("          value=$(cat <<'EOF'\n"
                                      '            \n'
                                      '          EOF\n'
                                      '          )\n'
                                      '          [ "$value" = "  " ]\n')
        result = run_step(script, {})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_regression_fixture_detects_legacy_and_list_bug(self):
        legacy = ('test -f AGENTS.md && test -f CLAUDE.md && grep -q "@AGENTS.md" CLAUDE.md\n'
                  'python3 -m json.tool .claude/settings.json > /dev/null\n')
        files = {'CLAUDE.md': '@AGENTS.md\n', '.claude/settings.json': '{}\n'}
        self.assertEqual(run_step(legacy, files).returncode, 0)
        self.assertNotEqual(run_step(config_step(), files).returncode, 0)


class TestAgentReferenceChecks(unittest.TestCase):
    def test_workflow_reference_checks_accept_only_exact_path_token(self):
        workflows = (
            ROOT / '.github/workflows/ci-baseline.yml',
            ROOT / 'docs/repo-template/.github/workflows/ci-baseline.yml',
            ROOT / 'docs/repo-template/.gitlab-ci.yml',
        )
        cases = (
            ('exact', '@AGENTS.md\n', True),
            ('surrounded_by_spaces', '  @AGENTS.md  \n', True),
            ('inline_token', 'include @AGENTS.md here\n', True),
            ('regex_wildcard', '@AGENTSXmd\n', False),
            ('suffix', '@AGENTS.md.suffix\n', False),
            ('prefix', 'prefix@AGENTS.md\n', False),
            ('unrelated', 'unrelated\n', False),
        )
        for workflow in workflows:
            matches = re.findall(r'grep -[^\n]*CLAUDE\.md',
                                 workflow.read_text(encoding='utf-8'))
            self.assertEqual(len(matches), 1, str(workflow))
            for name, content, expected in cases:
                with self.subTest(workflow=str(workflow), name=name):
                    result = run_step(matches[0], {'CLAUDE.md': content})
                    self.assertEqual(result.returncode == 0, expected, result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
