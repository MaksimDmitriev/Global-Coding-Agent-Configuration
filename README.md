# Global Coding Agent Configuration

Personal agent instructions and reusable skill scaffolds.

```text
Global-Coding-Agent-Configuration/
├── README.md
├── AGENTS.md
├── skills/
│   ├── figma-review/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── .gitkeep
│   ├── code-review/
│   │   └── SKILL.md
│   └── project-qa/
│       └── SKILL.md
└── scripts/
    └── install.sh
```

`AGENTS.md` contains the supplied GitHub issue workflow and merge rules. The three `SKILL.md` files and `scripts/install.sh` are empty placeholders. The `.gitkeep` file preserves the empty references directory when this scaffold is added to Git.

Before using a skill, add its metadata and workflow instructions as described in the [official OpenAI documentation](https://developers.openai.com/plugins/build/skills). Keep project-specific QA commands and hardware requirements in the relevant project's own skill.
