#!/usr/bin/env python3
"""Smoke tests for the aspace-claude-video-adapter (stdlib only, unittest).

Run: python3 aspace-claude-video-adapter/smoke_test.py
All tests run offline; test 5 runs `doctor` under `unshare -n` (no network
namespace) when the tool is available.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ADAPTER_DIR = Path(__file__).resolve().parent
REPO_ROOT = ADAPTER_DIR.parent
VALIDATE = ADAPTER_DIR / "validate.py"


def run(*args: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATE), *args],
        capture_output=True, text=True, timeout=60, **kwargs)


class TestAdapter(unittest.TestCase):
    def test_version(self):
        proc = run("--version")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("0.3.2", proc.stdout)
        self.assertIn("03ceb42", proc.stdout)

    def test_validate_repo(self):
        proc = run("validate", str(REPO_ROOT))
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("OK:", proc.stdout)

    def test_validate_broken_missing_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / "repo"
            shutil.copytree(REPO_ROOT / "skills", broken / "skills",
                            ignore=shutil.ignore_patterns("__pycache__"))
            (broken / "skills" / "watch" / "SKILL.md").unlink()
            proc = run("validate", str(broken))
            self.assertEqual(proc.returncode, 2)
            self.assertIn("SKILL.md", proc.stdout)

    def test_validate_version_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / "repo"
            shutil.copytree(REPO_ROOT, broken,
                            ignore=shutil.ignore_patterns(".git", "__pycache__"))
            plugin = broken / ".claude-plugin" / "plugin.json"
            data = json.loads(plugin.read_text(encoding="utf-8"))
            data["version"] = "9.9.9"
            plugin.write_text(json.dumps(data), encoding="utf-8")
            proc = run("validate", str(broken))
            self.assertEqual(proc.returncode, 2)
            self.assertIn("9.9.9", proc.stdout)

    def test_doctor_offline(self):
        if shutil.which("unshare") is None:
            self.skipTest("unshare not available")
        proc = subprocess.run(
            ["unshare", "-n", sys.executable, str(VALIDATE), "doctor"],
            capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("offline posture", proc.stdout)

    def test_contract(self):
        contract = json.loads((ADAPTER_DIR / "contract.json").read_text())
        for key in ("name", "version", "module", "entry", "surface", "telemetry"):
            self.assertIn(key, contract)
        self.assertEqual(contract["module"], "claude-video")
        self.assertEqual(contract["upstream"]["frozen_commit"],
                         "03ceb42f7fa2c4439aca01752118044baabffb8f")
        self.assertEqual(contract["telemetry"]["third_party_sdks"], 0)

    def test_no_network_imports(self):
        # AST-based: only real imports count, not words in docstrings.
        import ast
        tree = ast.parse(VALIDATE.read_text(encoding="utf-8"))
        banned = {"urllib", "requests", "httpx", "aiohttp", "socket"}
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertEqual(imported & banned, set(),
                         f"validate.py imports network modules: {imported & banned}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
