# GitHub Issue Workflow

When asked to implement a GitHub issue, whether by issue number or GitHub URL:

1. Read the issue and identify its number and purpose.
2. Before making any code changes, create and switch to a dedicated Git branch.
3. Use the following branch naming convention:
   `<issue-number>-<short-description>`
4. The description must:
   - Contain 2–5 meaningful words describing the issue.
   - Use lowercase letters.
   - Use hyphens between words (kebab-case).
   - Be based on the issue title or requirements.
5. Create the branch from the repository's default branch unless another base is specified.
6. Check for uncommitted changes before switching branches. Never discard existing work.
7. If the branch already exists, do not overwrite it. Reuse it only when appropriate and safe.
8. Start implementing the issue only after switching to the correct branch.

Example:
- Issue #66: Fix robot connection status
- Branch: `66-fix-robot-connection-status`

This workflow applies to all GitHub repositories.

## Git Merge Strategy

- Use `git merge --no-ff` by default when merging branches,
  unless explicitly instructed otherwise.
- Preserve feature branch history with a dedicated merge commit.
- Do not merge branches without explicit user authorization.
