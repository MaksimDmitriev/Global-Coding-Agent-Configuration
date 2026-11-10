# Global Coding Agent Configuration

Shared personal instructions and reusable skills for Codex and Claude Code. Keep one copy in this repository; the installer creates symbolic links in each agent's user configuration so edits here apply across your projects.

## Install

Requires macOS or Linux, Bash 3.2 or later, and standard command-line utilities. Install the coding agents separately. Clone this repository to a permanent location, then run:

```bash
git clone git@github.com:MaksimDmitriev/Global-Coding-Agent-Configuration.git
cd Global-Coding-Agent-Configuration

# Preview the links for both agents without changing anything.
bash scripts/install.sh --agent all --dry-run

# Install for both agents, or choose one.
bash scripts/install.sh --agent all
# bash scripts/install.sh --agent codex
# bash scripts/install.sh --agent claude
```

`--agent` is required. `all` means Codex and Claude Code only. The installer also works from another directory when invoked by its full path. Run `bash scripts/install.sh --help` for the options.

Start a new agent session after installation. Keep the checkout at its installed location: the links point back to it. If you move it, rerun with `--backup` to preserve and replace the old links.

## Installed locations

| Target | Shared instructions | Individual skills |
| --- | --- | --- |
| Codex | `~/.codex/AGENTS.md` | `~/.agents/skills/<skill-name>` |
| Claude Code | `~/.claude/CLAUDE.md` | `~/.claude/skills/<skill-name>` |

Both instruction files point to this repository's `AGENTS.md`. Each installed skill links to its entire folder here, including supporting references and scripts. Other installed skills are left in place.

The installer honors `CODEX_HOME` for Codex instructions and `CLAUDE_CONFIG_DIR` for Claude's configuration when set to absolute paths. Codex skills still go under `~/.agents/skills`. For an isolated preview or test, use `--home-dir /absolute/path`; this redirects all destinations to that home directory and ignores both profile overrides.

These paths follow the [official OpenAI configuration documentation](https://learn.chatgpt.com/docs/customization/overview), [Claude Code instructions documentation](https://code.claude.com/docs/en/memory), and [Claude Code skills documentation](https://code.claude.com/docs/en/skills). This installer configures local user profiles; it does not deploy configuration to cloud agent sessions.

## Existing configuration and backups

Repeated runs leave destinations that already resolve to the source unchanged. By default, any conflicting file, directory, or symlink stops installation before changes are made. Parent paths must be directories; `--backup` does not replace an obstructed parent.

To review and then preserve conflicting destinations before installing:

```bash
bash scripts/install.sh --agent all --backup --dry-run
bash scripts/install.sh --agent all --backup
```

Backups stay beside the original destination with a `.backup.<timestamp>.<process-id>` suffix. The installer prints each backup's exact path and never deletes an existing backup. `--dry-run` creates no directories, links, or backups; it exits unsuccessfully if conflicts remain without `--backup`.

To undo a link, use `unlink` on that installed destination. To restore previous configuration, unlink the installer-created link and move the printed backup back to its original path. For a skill, unlink only that skill's entry, leaving the shared skills directory and other skills intact.

## Instructions and skills

`AGENTS.md` contains the GitHub issue branching workflow and the default `--no-ff` merge rule. It supplies shared instructions to both agents. Project-level instructions can add to or override personal defaults according to each agent's loading rules; for example, a Codex `AGENTS.override.md` can take precedence over this installed file.

The three `SKILL.md` files are currently empty placeholders, so the installer skips them. To enable a skill, fill in its `SKILL.md` with a `name`, a `description`, and workflow instructions, then rerun the installer. Non-empty manifests are eligible for linking; the installer does not validate their YAML or the workflow itself. See [OpenAI's skill authoring documentation](https://learn.chatgpt.com/docs/build-skills) and [Claude's skill documentation](https://code.claude.com/docs/en/skills).

Keep shared skill instructions independent of a particular agent. Both support the Agent Skills format, but tool names, connectors, permissions, and agent-specific metadata can differ. Install any tools a workflow requires separately and verify the skill in each agent. Keep project-specific QA commands, simulator setup, and hardware constraints in that project's own skill.

## Repository layout

```text
Global-Coding-Agent-Configuration/
├── AGENTS.md
├── README.md
├── scripts/
│   └── install.sh
├── skills/
│   ├── code-review/
│   │   └── SKILL.md
│   ├── figma-review/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── .gitkeep
│   └── project-qa/
│       └── SKILL.md
└── tests/
    └── test_install.py
```

## Verify changes

Run the syntax check and integration tests (Python 3 standard library only):

```bash
bash -n scripts/install.sh
python3 -B -m unittest discover -s tests -v
```

Tests install into temporary directories via `--home-dir`. They cover both agents, paths with spaces, dry runs, repeat runs, placeholder skipping, conflicts, and preserving existing configuration in backups.
