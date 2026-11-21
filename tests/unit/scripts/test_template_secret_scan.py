#!/usr/bin/env python3
"""Check the template secret scan against synthetic Git histories."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / 'docs/repo-template/.github/workflows/ci-baseline.yml'


def secret_scan_config():
    source = WORKFLOW.read_text(encoding='utf-8')
    jobs = source.split('\n  secret-scan:\n')
    if len(jobs) != 2:
        raise ValueError('Cannot uniquely locate secret-scan job')
    job = jobs[1]
    matches = re.findall(r'^      - name: scan reachable history\n        run: ([^\n]+)$',
                         job, flags=re.MULTILINE)
    if len(matches) != 1:
        raise AssertionError('Cannot uniquely locate history scan command')
    return job, matches[0]


class TestTemplateSecretScan(unittest.TestCase):
    def test_checkout_and_binary_are_pinned(self):
        job, _ = secret_scan_config()
        self.assertRegex(job, r'fetch-depth:\s*0\b')
        self.assertIn('gitleaks_8.24.3_linux_x64.tar.gz', job)
        self.assertIn('9991e0b2903da4c8f6122b5c3186448b927a5da4deef1fe45271c3793f4ee29c', job)
        self.assertIn('sha256sum -c', job)

    def test_scan_includes_synthetic_secret_in_root_commit(self):
        _, command = secret_scan_config()
        with tempfile.TemporaryDirectory(prefix='template-scan-test-') as temp:
            root = Path(temp)
            repo = root / 'repo'
            repo.mkdir()
            bindir = root / 'bin'
            bindir.mkdir()
            fake = bindir / 'gitleaks'
            fake.write_text('#!/bin/sh\n'
                            '[ "$*" = "git --redact --exit-code=2 --log-opts=HEAD ." ] || exit 99\n'
                            'git log -p HEAD | grep -q MVP_SYNTHETIC_MARKER && exit 2\n'
                            'exit 0\n', encoding='utf-8')
            fake.chmod(0o755)
            env = {'PATH': str(bindir) + os.pathsep + '/usr/bin:/bin',
                   'HOME': str(root), 'GIT_CONFIG_NOSYSTEM': '1',
                   'GIT_CONFIG_GLOBAL': os.devnull,
                   'GIT_AUTHOR_NAME': 'Fixture', 'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
                   'GIT_COMMITTER_NAME': 'Fixture', 'GIT_COMMITTER_EMAIL': 'fixture@example.invalid'}
            def git(*args):
                return subprocess.run(['git', *args], cwd=repo, env=env,
                                      capture_output=True, text=True, check=True)
            def scan():
                return subprocess.run(['/bin/bash', '--noprofile', '--norc', '-e',
                                       '-o', 'pipefail', '-c', command], cwd=repo, env=env,
                                      capture_output=True, text=True).returncode
            git('init', '-q')
            (repo / 'fixture.txt').write_text('MVP_SYNTHETIC_MARKER\n', encoding='utf-8')
            git('add', 'fixture.txt')
            git('commit', '-qm', 'root fixture')
            self.assertEqual(scan(), 2)
            (repo / 'fixture.txt').write_text('clean now\n', encoding='utf-8')
            git('commit', '-qam', 'remove marker')
            self.assertEqual(scan(), 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
