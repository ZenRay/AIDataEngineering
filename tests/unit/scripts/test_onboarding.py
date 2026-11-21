#!/usr/bin/env python3
"""Exercise onboarding flow with fake tools and synthetic configuration."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
ONBOARDING = ROOT / "scripts" / "onboarding.sh"
CHECKER = ROOT / "scripts" / "check-mcp-config.py"
SENTINEL = "synthetic-secret-never-print"


class TestBootstrapFixture(unittest.TestCase):
    def run_case(self, content, missing_scm=False, extra_paths=False,
                 settings="{}", envrc="source .env\n", push_only=False):
        with tempfile.TemporaryDirectory(prefix="onboarding-fixture-") as directory:
            root = Path(directory)
            project, tools, home = root / "project", root / "bin", root / "home"
            project.mkdir()
            tools.mkdir()
            home.mkdir()
            (project / "scripts").mkdir()
            (project / ".claude").mkdir()
            (project / "scripts" / "onboarding.sh").write_bytes(ONBOARDING.read_bytes())
            (project / "scripts" / "check-mcp-config.py").write_bytes(CHECKER.read_bytes())
            (project / ".mcp.json").write_text(content, encoding="utf-8")
            (project / ".envrc").write_text(envrc, encoding="utf-8")
            (project / ".claude" / "settings.json").write_text(settings, encoding="utf-8")
            (project / ".meta").write_text("{}", encoding="utf-8")
            if extra_paths:
                for relative in ("BackDocs/archive", "submodules/example", "docs/repo-template", "projects/example"):
                    folder = project / relative
                    folder.mkdir(parents=True)
                    (folder / ".envrc").write_text("# synthetic fixture\n", encoding="utf-8")
                (project / "linked").mkdir()
                (project / "linked" / ".envrc").symlink_to(project / ".envrc")
            git = '''#!/bin/sh
case "$1" in
  rev-parse) printf '%s\\n' "$PROJECT_ROOT" ;;
  --version) echo 'git version 2.40.0' ;;
  config)
    if [ "$PUSH_ONLY" = "1" ]; then
      printf '%s\\n' 'url.example.pushinsteadof upstream:' 'url.example.pushinsteadof upstream-user:' 'url.example.pushinsteadof darepo:' 'url.example.pushinsteadof scm:'
    else
      printf '%s\\n' 'url.example.insteadof upstream:' 'url.example.insteadof upstream-user:' 'url.example.insteadof darepo:'
      if [ "$MISSING_SCM" = "1" ]; then echo 'url.scm:example.insteadof wrong:'; else echo 'url.example.insteadof scm:'; fi
    fi | awk -v pattern="$4" '$1 ~ pattern { print; found=1 } END { if (!found) exit 1 }' ;;

  submodule) : > "$ACTION_SUBMODULE" ;;
  check-ignore) exit 0 ;;
esac
'''
            direnv = '''#!/bin/sh
if [ "$1" = "--version" ]; then echo '2.0'; elif [ "$1" = "allow" ]; then printf '%s\\n' "$2" >> "$ACTION_DIRENV"; fi
'''
            meta = '''#!/bin/sh
if [ "$1" = "--version" ]; then echo '1.0'; else : > "$ACTION_META"; fi
'''
            jq = "#!/bin/sh\necho 'jq-1.7'\n"
            for name, script in (("git", git), ("direnv", direnv), ("meta", meta), ("jq", jq)):
                path = tools / name
                path.write_text(script, encoding="utf-8")
                path.chmod(0o755)
            env = {"PATH": str(tools) + ":/usr/bin:/bin", "HOME": str(home), "PROJECT_ROOT": str(project),
                   "ACTION_SUBMODULE": str(root / "submodule"), "ACTION_META": str(root / "meta"),
                   "ACTION_DIRENV": str(root / "direnv"), "MISSING_SCM": "1" if missing_scm else "0",
                   "PUSH_ONLY": "1" if push_only else "0"}
            result = subprocess.run(["/bin/bash", str(project / "scripts" / "onboarding.sh"), "--reviewed"],
                                    cwd=project, env=env, text=True, capture_output=True)
            self.assertNotIn(SENTINEL, result.stdout + result.stderr)
            allowed = (root / "direnv").read_text().splitlines() if (root / "direnv").exists() else []
            return result.returncode, [(root / name).exists() for name in ("submodule", "meta", "direnv")], allowed

    def test_literal_credential_stops_before_actions(self):
        status, actions, _ = self.run_case(json.dumps({"headers": {"Authorization": "Bearer " + SENTINEL}}))
        self.assertEqual(status, 1)
        self.assertEqual(actions, [False, False, False])

    def test_invalid_json_stops_before_actions(self):
        status, actions, _ = self.run_case('{"password": "' + SENTINEL)
        self.assertEqual(status, 1)
        self.assertEqual(actions, [False, False, False])

    def test_duplicate_keys_stop_before_actions(self):
        content = '{"token": "' + SENTINEL + '", "token": "${TOKEN}"}'
        status, actions, _ = self.run_case(content)
        self.assertEqual(status, 1)
        self.assertEqual(actions, [False, False, False])

    def test_placeholder_continues_to_fake_actions(self):
        status, actions, _ = self.run_case(json.dumps({"headers": {"Authorization": "Bearer ${TOKEN}"}}))
        self.assertEqual(status, 0)
        self.assertEqual(actions, [True, True, True])

    def test_failed_preflight_stops_before_actions(self):
        cases = (
            {"settings": '{"enableAllProjectMcpServers": true}'},
            {"envrc": "# missing source directive\n"},
        )
        for case in cases:
            with self.subTest(case=case):
                status, actions, _ = self.run_case('{}', **case)
                self.assertEqual(status, 1)
                self.assertEqual(actions, [False, False, False])

    def test_missing_alias_stops_all_actions(self):
        status, actions, _ = self.run_case('{"headers": {"Authorization": "Bearer ${TOKEN}"}}', missing_scm=True)
        self.assertEqual(status, 1)
        self.assertEqual(actions, [False, False, False])

    def test_push_only_aliases_stop_before_actions(self):
        status, actions, _ = self.run_case('{}', push_only=True)
        self.assertEqual(status, 1)
        self.assertEqual(actions, [False, False, False])

    def test_directory_exclusions_and_regular_files(self):
        status, _, allowed = self.run_case('{"headers": {"Authorization": "Bearer ${TOKEN}"}}', extra_paths=True)
        self.assertEqual(status, 0)
        self.assertEqual(set(allowed), {".", "./projects/example"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
