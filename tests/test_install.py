"""Exercise the installer in isolated home directories, without agent dependencies."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


INSTALLER = Path(__file__).resolve().parents[1] / "scripts" / "install.sh"


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="agent installer ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "checkout with spaces"
        self.script = self.repo / "scripts" / "install.sh"
        self.script.parent.mkdir(parents=True)
        shutil.copy2(INSTALLER, self.script)
        (self.repo / "AGENTS.md").write_text("# Shared rules\n", encoding="utf-8")
        self.skill = self.repo / "skills" / "review"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text(
            "---\nname: review\ndescription: Review code\n---\nCheck correctness.\n",
            encoding="utf-8",
        )
        (self.skill / "reference.txt").write_text("Review checklist\n", encoding="utf-8")
        placeholder = self.repo / "skills" / "unfinished"
        placeholder.mkdir()
        (placeholder / "SKILL.md").touch()
        (self.repo / "skills" / "no-manifest").mkdir()
        self.home = self.root / "alternate home"
        self.working_dir = self.root / "another directory"
        self.working_dir.mkdir()

    def install(self, *arguments, success=True):
        result = subprocess.run(
            ["bash", str(self.script), "--home-dir", str(self.home), *arguments],
            cwd=self.working_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def assert_link(self, destination, source):
        self.assertTrue(destination.is_symlink(), str(destination))
        self.assertEqual(destination.resolve(), source.resolve())

    def backups(self, destination):
        return list(destination.parent.glob(destination.name + ".backup.*"))

    def test_help_and_invalid_arguments_do_not_write(self):
        self.install("--help")
        for arguments in [(), ("--agent",), ("--agent", "gemini"), ("--unknown",),
                          ("--agent", "codex", "--agent", "claude"),
                          ("--agent", "codex", "--home-dir", "relative")]:
            with self.subTest(arguments=arguments):
                self.install(*arguments, success=False)
                self.assertFalse(self.home.exists())

    def test_dry_run_does_not_even_create_the_home(self):
        result = self.install("--agent", "all", "--dry-run")
        self.assertIn("WOULD LINK", result.stdout)
        self.assertIn("SKIP unfinished", result.stdout)
        self.assertFalse(self.home.exists())

    def test_codex_only_and_empty_skills_are_skipped(self):
        self.install("--agent", "codex")
        self.assert_link(self.home / ".codex/AGENTS.md", self.repo / "AGENTS.md")
        self.assert_link(self.home / ".agents/skills/review", self.skill)
        self.assertFalse((self.home / ".claude").exists())
        self.assertFalse((self.home / ".agents/skills/unfinished").exists())
        self.assertFalse((self.home / ".agents/skills/no-manifest").exists())

    def test_claude_only(self):
        self.install("--agent", "claude")
        self.assert_link(self.home / ".claude/CLAUDE.md", self.repo / "AGENTS.md")
        self.assert_link(self.home / ".claude/skills/review", self.skill)
        self.assertFalse((self.home / ".codex").exists())
        self.assertFalse((self.home / ".agents").exists())

    def test_only_placeholders_installs_instructions_without_skill_directories(self):
        (self.skill / "SKILL.md").write_text("", encoding="utf-8")
        self.install("--agent", "all")
        self.assert_link(self.home / ".codex/AGENTS.md", self.repo / "AGENTS.md")
        self.assert_link(self.home / ".claude/CLAUDE.md", self.repo / "AGENTS.md")
        self.assertFalse((self.home / ".agents").exists())
        self.assertFalse((self.home / ".claude/skills").exists())

    def test_relative_invocation_ignores_shell_directory_search_paths(self):
        alternate_tree = self.root / "directory search path"
        (alternate_tree / "scripts").mkdir(parents=True)
        environment = dict(os.environ, CDPATH=str(alternate_tree))
        result = subprocess.run(
            ["bash", "scripts/install.sh", "--agent", "all", "--home-dir", str(self.home)],
            cwd=self.repo,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_link(self.home / ".codex/AGENTS.md", self.repo / "AGENTS.md")

    def test_both_agents_follow_later_source_edits_and_supporting_files(self):
        self.install("--agent", "all")
        (self.repo / "AGENTS.md").write_text("Updated rules\n", encoding="utf-8")
        for destination in [self.home / ".codex/AGENTS.md", self.home / ".claude/CLAUDE.md"]:
            self.assertEqual(destination.read_text(), "Updated rules\n")
        for directory in [self.home / ".agents/skills/review", self.home / ".claude/skills/review"]:
            self.assert_link(directory, self.skill)
            self.assertEqual((directory / "reference.txt").read_text(), "Review checklist\n")

    def test_repeat_run_preserves_links_without_backups(self):
        self.install("--agent", "all")
        destination = self.home / ".codex/AGENTS.md"
        original_inode = destination.lstat().st_ino
        result = self.install("--agent", "all", "--backup")
        self.assertIn("UNCHANGED", result.stdout)
        self.assertEqual(destination.lstat().st_ino, original_inode)
        self.assertEqual(list(self.home.rglob("*.backup.*")), [])

    def test_late_conflict_stops_the_entire_install(self):
        destination = self.home / ".claude/CLAUDE.md"
        destination.parent.mkdir(parents=True)
        destination.write_text("Personal Claude rules\n", encoding="utf-8")
        result = self.install("--agent", "all", success=False)
        self.assertIn("CONFLICT", result.stderr)
        self.assertFalse((self.home / ".codex").exists())
        self.assertFalse((self.home / ".agents").exists())
        self.assertEqual(destination.read_text(), "Personal Claude rules\n")

    def test_existing_skill_directory_is_not_overwritten(self):
        destination = self.home / ".agents/skills/review"
        destination.mkdir(parents=True)
        (destination / "notes.txt").write_text("Keep me", encoding="utf-8")
        self.install("--agent", "all", success=False)
        self.assertFalse((self.home / ".codex").exists())
        self.assertEqual((destination / "notes.txt").read_text(), "Keep me")

    def test_backups_preserve_regular_file_and_skill_directory(self):
        instructions = self.home / ".claude/CLAUDE.md"
        instructions.parent.mkdir(parents=True)
        instructions.write_text("Personal rules", encoding="utf-8")
        skill = self.home / ".claude/skills/review"
        skill.mkdir(parents=True)
        (skill / "notes.txt").write_text("Personal skill", encoding="utf-8")
        self.install("--agent", "claude", "--backup")
        self.assert_link(instructions, self.repo / "AGENTS.md")
        self.assert_link(skill, self.skill)
        self.assertEqual(len(self.backups(instructions)), 1)
        self.assertEqual(self.backups(instructions)[0].read_text(), "Personal rules")
        self.assertEqual((self.backups(skill)[0] / "notes.txt").read_text(), "Personal skill")

    def test_backup_preserves_a_dangling_symlink(self):
        destination = self.home / ".codex/AGENTS.md"
        destination.parent.mkdir(parents=True)
        destination.symlink_to("missing-rules.md")
        self.install("--agent", "codex", success=False)
        self.install("--agent", "codex", "--backup")
        self.assertEqual(os.readlink(self.backups(destination)[0]), "missing-rules.md")
        self.assert_link(destination, self.repo / "AGENTS.md")

    def test_backup_preserves_a_directory_at_an_instruction_path(self):
        destination = self.home / ".codex/AGENTS.md"
        destination.mkdir(parents=True)
        (destination / "saved.txt").write_text("Preserve directory", encoding="utf-8")
        self.install("--agent", "codex", "--backup")
        self.assert_link(destination, self.repo / "AGENTS.md")
        self.assertEqual((self.backups(destination)[0] / "saved.txt").read_text(), "Preserve directory")

    def test_dry_run_with_backup_preserves_existing_configuration(self):
        destination = self.home / ".claude/CLAUDE.md"
        destination.parent.mkdir(parents=True)
        destination.write_text("Original rules", encoding="utf-8")
        result = self.install("--agent", "all", "--backup", "--dry-run")
        self.assertIn("WOULD BACK UP", result.stdout)
        self.assertEqual(destination.read_text(), "Original rules")
        self.assertEqual(self.backups(destination), [])
        self.assertFalse((self.home / ".codex").exists())

    def test_dry_run_conflicts_return_failure_without_changes(self):
        destination = self.home / ".claude/CLAUDE.md"
        destination.parent.mkdir(parents=True)
        destination.write_text("Original rules", encoding="utf-8")
        self.install("--agent", "all", "--dry-run", success=False)
        self.assertEqual(destination.read_text(), "Original rules")
        self.assertFalse((self.home / ".codex").exists())

    def test_obstructed_parent_is_not_replaced_even_with_backup(self):
        self.home.mkdir()
        obstruction = self.home / ".claude"
        for dangling in [False, True]:
            with self.subTest(dangling=dangling):
                if dangling:
                    obstruction.symlink_to("missing-directory")
                else:
                    obstruction.write_text("Not a directory", encoding="utf-8")
                self.install("--agent", "all", "--backup", success=False)
                self.assertFalse((self.home / ".codex").exists())
                self.assertTrue(os.path.lexists(obstruction))
                self.assertEqual(self.backups(obstruction), [])
                obstruction.unlink()

    def test_equivalent_relative_link_is_left_in_place(self):
        destination = self.home / ".codex/AGENTS.md"
        destination.parent.mkdir(parents=True)
        relative_source = os.path.relpath(self.repo / "AGENTS.md", destination.parent)
        destination.symlink_to(relative_source)
        self.install("--agent", "codex")
        self.assertEqual(os.readlink(destination), relative_source)

    def test_existing_parent_links_never_move_the_source(self):
        self.home.mkdir()
        (self.home / ".codex").symlink_to(self.repo, target_is_directory=True)
        (self.home / ".agents").mkdir()
        (self.home / ".agents/skills").symlink_to(self.repo / "skills", target_is_directory=True)
        self.install("--agent", "codex", "--backup")
        self.assertFalse((self.repo / "AGENTS.md").is_symlink())
        self.assertFalse(self.skill.is_symlink())
        self.assertEqual(list(self.repo.rglob("*.backup.*")), [])

    def test_unrelated_installed_skills_are_preserved(self):
        unrelated = self.home / ".claude/skills/another-skill"
        unrelated.mkdir(parents=True)
        (unrelated / "SKILL.md").write_text("Existing skill", encoding="utf-8")
        self.install("--agent", "all")
        self.assertEqual((unrelated / "SKILL.md").read_text(), "Existing skill")

    def test_empty_global_instructions_abort_without_changes(self):
        (self.repo / "AGENTS.md").write_text("", encoding="utf-8")
        self.install("--agent", "all", success=False)
        self.assertFalse(self.home.exists())


if __name__ == "__main__":
    unittest.main()
