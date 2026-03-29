# Project Memory

## GitHub API Notes

### Branch Protection
- `bypass_pull_request_allowances` only works for **organization repos**, not personal repos
- Use `enforce_admins: false` to allow admin bypass, but personal repos can't set specific users to bypass
- When `enforce_admins: false`, admins can merge without approval on web UI

### Branch Cleanup
- `git branch -r --merged main` may not catch all merged branches (e.g., those merged via web UI)
- Always check PRs via GitHub API: `GET /repos/{owner}/{repo}/pulls?state=closed`
- Use API to delete merged branches: `DELETE /repos/{owner}/{repo}/git/refs/heads/{branch}`
- Fetch with prune after deletion to update local refs

### Merging
- Personal repos: Merge via web UI (Merge pull request button)
- Cannot self-approve PRs, but can merge own PRs via web UI
- If blocked by status checks, wait for CI then merge

## Workflow Notes

### Worktrees
- Use `<repo-name>-<branch-name>` naming for worktrees
- Delete worktree after PR merged: `git worktree remove ../worktree-name`

### PR Flow
1. Create feature branch via worktree
2. Commit and push
3. Create PR via API or web UI
4. Wait for CI
5. Merge via web UI
6. Delete merged branches via API
7. Remove worktree

## Global Config

Stored in `~/.config/` - see INSTRUCTIONS.md for details.
