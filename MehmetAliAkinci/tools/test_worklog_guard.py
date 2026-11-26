import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import worklog_guard as guard


class GuardTests(unittest.TestCase):
    def test_prepend_preserves_history(self):
        old = b"# Log\r\n\r\n### 2026-11-14 - Old\r\ntext\r\n"
        new = b"# Log\r\n\r\n### 2026-11-26 - New\r\nnew\r\n### " + old.split(b"### ", 1)[1]
        self.assertEqual(guard.log_errors(new, old), [])

    def test_history_edit_rejected(self):
        self.assertTrue(guard.log_errors(b"# Log\n", b"# Log\n### Old\ntext\n"))

    def test_git_checkout_line_endings(self):
        self.assertEqual(guard.log_errors(b"# Log\r\n### Old\r\ntext\r\n", b"# Log\n### Old\ntext\n"), [])

    def test_duplicate_ids_rejected(self):
        entry = b"### New\n- **Record ID:** same-id\n"
        self.assertTrue(guard.log_errors(entry * 2, b"# Log\n"))

    def test_stop_blocks_once_without_writing(self):
        with patch.object(guard, "check", return_value=[]) as check:
            self.assertEqual(guard.stop({})["decision"], "block")
            self.assertEqual(guard.stop({"stop_hook_active": True}), {})
            check.assert_called_once()

    def test_pull_once_per_session_and_failure_retry(self):
        # All temporary files stay under the personal folder.
        with tempfile.TemporaryDirectory(dir=guard.PERSONAL) as directory:
            with patch.object(guard, "PERSONAL", Path(directory)):
                ok = subprocess.CompletedProcess([], 0, b"Already up to date.", b"")
                fail = subprocess.CompletedProcess([], 1, b"", b"network unavailable")
                with patch.object(guard, "git", side_effect=[fail, ok]) as git:
                    self.assertIn("FAILED", json.dumps(guard.start({"session_id": "a"})))
                    guard.start({"session_id": "a"})
                    guard.start({"session_id": "a"})
                    self.assertEqual(git.call_count, 2)
                    git.assert_called_with("pull", "--ff-only")

    def test_staged_scope_and_size(self):
        with tempfile.TemporaryDirectory(dir=guard.PERSONAL) as directory:
            folder = Path(directory)
            (folder / "LOG.md").write_bytes(b"# Log\n")
            responses = [subprocess.CompletedProcess([], 0, b"# Log\n", b""),
                         subprocess.CompletedProcess([], 0, b"other/file\0MehmetAliAkinci/big\0", b""),
                         subprocess.CompletedProcess([], 0, b"50000001", b"")]
            with patch.object(guard, "PERSONAL", folder), patch.object(guard, "git", side_effect=responses):
                errors = guard.check()
                self.assertTrue(any("Out-of-scope" in e for e in errors))
                self.assertTrue(any("exceeds 50 MB" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
