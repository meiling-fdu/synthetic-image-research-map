import subprocess
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from scripts import admin_publish_changes


class RecordingRunner:
    def __init__(self, responses=None):
        self.commands = []
        self.responses = responses or {}

    def __call__(self, command, repository_root):
        command = tuple(command)
        self.commands.append(command)
        returncode, stdout = self.responses.get(command, (0, ""))
        return subprocess.CompletedProcess(command, returncode, stdout=stdout)


class AdminPublishChangesTests(unittest.TestCase):
    def git(self, repository, *arguments):
        return subprocess.run(
            ("git", *arguments),
            cwd=repository,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()

    def test_refresh_failure_stops_before_validation_and_git(self):
        first_refresh = tuple(
            admin_publish_changes.ALLOWED_WORKFLOWS["full_refresh"][0]
        )
        runner = RecordingRunner({first_refresh: (3, "refresh error\n")})

        result = admin_publish_changes.publish_changes(
            repository_root=Path("/repo"),
            runner=runner,
        )

        self.assertEqual(result, 1)
        self.assertEqual(runner.commands, [first_refresh])

    def test_no_eligible_staged_files_does_not_commit_or_push(self):
        runner = RecordingRunner()

        result = admin_publish_changes.publish_changes(
            repository_root=Path("/repo"),
            runner=runner,
        )

        self.assertEqual(result, 0)
        self.assertFalse(any(command[:2] == ("git", "commit") for command in runner.commands))
        self.assertNotIn(("git", "push"), runner.commands)

    def test_commit_is_scoped_and_pushes_after_commit(self):
        staged_command = (
            "git",
            "diff",
            "--cached",
            "--name-only",
            "--",
            *admin_publish_changes.PUBLISH_PATHSPECS,
        )
        runner = RecordingRunner(
            {
                staged_command: (0, "data/curated/papers.csv\nweb/data/public_preview_papers.json\n"),
                ("git", "branch", "--show-current"): (0, "main\n"),
                ("git", "rev-parse", "HEAD"): (0, "abc123\n"),
            }
        )

        result = admin_publish_changes.publish_changes(
            repository_root=Path("/repo"),
            runner=runner,
            now=lambda: datetime(2026, 7, 1, 14, 30),
        )

        self.assertEqual(result, 0)
        commit = next(
            command for command in runner.commands
            if command[:2] == ("git", "commit")
        )
        self.assertIn("--only", commit)
        self.assertIn(
            "Update curated data and public preview 2026-07-01 14:30",
            commit,
        )
        self.assertIn(
            ":(exclude,glob)data/manual/key_papers_missing_*",
            commit,
        )
        self.assertIn(
            ":(exclude,glob)data/manual/key_papers_query_failed_*",
            commit,
        )
        self.assertEqual(runner.commands[-1], ("git", "push"))

    def test_real_git_commit_excludes_temporary_and_unrelated_staged_files(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            curated = repository / "data/curated/papers.csv"
            temporary_batch = (
                repository / "data/manual/key_papers_missing_batch.csv"
            )
            preview = repository / "web/data/public_preview_papers.json"
            test_marker = repository / "tests/.gitkeep"
            unrelated = repository / "notes.txt"
            for path in (
                curated,
                temporary_batch,
                preview,
                test_marker,
                unrelated,
            ):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("original\n", encoding="utf-8")

            self.git(repository, "init")
            self.git(repository, "config", "user.name", "Admin Publish Test")
            self.git(
                repository,
                "config",
                "user.email",
                "admin-publish@example.test",
            )
            self.git(repository, "add", ".")
            self.git(repository, "commit", "-m", "Initial")

            curated.write_text("published\n", encoding="utf-8")
            preview.write_text("published\n", encoding="utf-8")
            temporary_batch.write_text("temporary\n", encoding="utf-8")
            unrelated.write_text("unrelated\n", encoding="utf-8")
            self.git(repository, "add", "notes.txt")
            self.git(
                repository,
                "add",
                "data/manual/key_papers_missing_batch.csv",
            )

            def real_git_runner(command, repository_root):
                if command[0] == "python3":
                    return subprocess.CompletedProcess(command, 0, stdout="")
                if tuple(command) == ("git", "push"):
                    return subprocess.CompletedProcess(
                        command,
                        0,
                        stdout="Push mocked for local test.\n",
                    )
                return subprocess.run(
                    command,
                    cwd=repository_root,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )

            result = admin_publish_changes.publish_changes(
                repository_root=repository,
                runner=real_git_runner,
                now=lambda: datetime(2026, 7, 1, 14, 30),
            )

            self.assertEqual(result, 0)
            self.assertEqual(
                self.git(repository, "show", "HEAD:data/curated/papers.csv"),
                "published",
            )
            self.assertEqual(
                self.git(
                    repository,
                    "show",
                    "HEAD:web/data/public_preview_papers.json",
                ),
                "published",
            )
            self.assertEqual(
                self.git(
                    repository,
                    "show",
                    "HEAD:data/manual/key_papers_missing_batch.csv",
                ),
                "original",
            )
            self.assertEqual(
                self.git(repository, "show", "HEAD:notes.txt"),
                "original",
            )


if __name__ == "__main__":
    unittest.main()
