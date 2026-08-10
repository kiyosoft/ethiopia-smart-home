---
name: release
description: >-
  Cut a full release for Ethiopian Smart Home: bump integration versions,
  update CHANGELOG.md, commit, annotated tag, push, and create a GitHub
  Release. Use when the user asks to release, cut a version, ship, tag a
  release, publish, or bump the integration version.
---

# Release (full ship)

End-to-end release for this multi-integration Home Assistant repo.

## When to run

Only when the user explicitly asks to release / ship / tag / publish.
Do **not** release unprompted after feature work.

## Preconditions

1. Working tree may have uncommitted release-ready changes; do not discard them.
2. Confirm current branch (prefer `main`) and that it tracks `origin`.
3. Run tests: `python -m pytest tests/ -v` (use project `.venv` if present).
   Stop if tests fail.
4. Do **not** update git config. Do **not** use `--no-verify` or force-push
   unless the user explicitly asks.

## Versioning

- Git tags: `vMAJOR.MINOR.PATCH` (example: `v0.1.2`). Existing tag style: `v0.1.1`.
- Bump these files to the **same** new version for every integration that
  changed since the previous tag (and always bump any integration the user names):
  - `custom_components/*/manifest.json` → `"version"`
  - `pyproject.toml` → `version`
- If the user gives an explicit version (e.g. `0.2.0`), use it.
- If they say patch/minor/major, bump from the latest `v*` tag.
- Default bump: **patch** on the latest tag.
- Integrations with **no** changes since the last tag may keep their old
  manifest version unless the user asks to sync all manifests.

## Workflow

Copy and track:

```
Release Progress:
- [ ] 1. Inspect state (status, diff, last tag, commits since tag)
- [ ] 2. Run tests
- [ ] 3. Choose version
- [ ] 4. Bump manifests / pyproject
- [ ] 5. Update CHANGELOG.md
- [ ] 6. Commit
- [ ] 7. Create annotated tag
- [ ] 8. Push branch + tag
- [ ] 9. Create GitHub Release
- [ ] 10. Verify and report URLs
```

### 1. Inspect

Run in parallel:

```bash
git status
git diff
git diff --staged
git tag -l 'v*' --sort=-v:refname | head
git log "$(git describe --tags --abbrev=0 2>/dev/null || echo HEAD)...HEAD" --oneline
git log -5 --oneline
```

List which `custom_components/*` paths changed since the last tag.

### 2–4. Tests, version, bump

- Run pytest; abort on failure.
- Compute `NEW` (without `v`) and `TAG=v$NEW`.
- Update changed manifests and `pyproject.toml`.

### 5. CHANGELOG.md

Create the file if missing. Prepend a section at the top (newest first):

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- …

### Changed
- …

### Fixed
- …

```

- Derive bullets from commits + diff since the previous tag.
- Omit empty subsections.
- Keep bullets user-facing (HA entities, behavior), not file churn.
- Date = today (user-local / conversation date).

### 6. Commit

Stage only release-related files (manifests, pyproject, CHANGELOG, and the
feature files that belong in this release). Never stage secrets (`.env`, credentials).

Follow the repo’s commit-message style. Example:

```bash
git add CHANGELOG.md pyproject.toml custom_components/**/manifest.json
# plus any uncommitted feature files included in this release
git commit -m "$(cat <<'EOF'
Release vX.Y.Z

Summarize the why in 1–2 sentences.
EOF
)"
git status
```

If the commit fails due to a hook, fix and create a **new** commit (do not amend
unless the user’s amend rules are fully satisfied).

### 7. Annotated tag

```bash
git tag -a "vX.Y.Z" -m "$(cat <<'EOF'
vX.Y.Z

Short release summary (1–3 lines).
EOF
)"
```

### 8. Push

```bash
git push -u origin HEAD
git push origin "vX.Y.Z"
```

### 9. GitHub Release

Use notes from the new CHANGELOG section:

```bash
gh release create "vX.Y.Z" \
  --title "vX.Y.Z" \
  --notes "$(cat <<'EOF'
## What's changed

- Bullet points from CHANGELOG for this version
EOF
)"
```

If the tag already exists on the remote, stop and report; do not delete remote
tags unless the user asks.

### 10. Report

Return:

- Version / tag
- Commit SHA
- CHANGELOG summary (short)
- GitHub release URL (`gh release view vX.Y.Z --json url -q .url`)

## Safety rails

- No force-push to `main`/`master`.
- No `git tag -d` / remote tag deletion unless explicitly requested.
- No empty releases: if there are no changes since the last tag and no
  uncommitted work, stop and say so.
- Ask before including unrelated dirty files that look accidental.

## Additional resources

- Changelog and notes shape: [changelog.md](changelog.md)
