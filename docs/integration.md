# Integration Guide: Using rpax-corpuses as Test Corpus

This document describes how to integrate `rpax-corpuses` into other repositories (e.g., `xaml-parser`, `rpax-lake`) for testing purposes.

## Overview

The `rpax-corpuses` repository is designed to be referenced as a **subfolder** in other repositories, providing standardized UiPath project fixtures for parser and lake testing.

## Recommended Approaches

### Option 1: Git Submodule (Recommended)

**Best for:** Production use, CI/CD pipelines, version pinning

#### Adding to Your Repository

```bash
# In your parser/lake repository
git submodule add https://github.com/rpapub/rpax-corpuses.git test-corpus

# Commit the submodule reference
git commit -m "Add rpax-corpuses as test corpus submodule"
```

#### Cloning Repository with Submodules

```bash
# Option A: Clone with submodules in one step
git clone --recurse-submodules https://github.com/your/xaml-parser.git

# Option B: Initialize submodules after clone
git clone https://github.com/your/xaml-parser.git
cd xaml-parser
git submodule init
git submodule update
```

#### Updating Corpus Version

```bash
# Update to latest corpus
cd test-corpus
git pull origin development
cd ..
git add test-corpus
git commit -m "Update test corpus to latest"

# Or update all submodules at once
git submodule update --remote
```

#### Using in Tests

```python
# Python example
corpus_path = Path(__file__).parent / "test-corpus"
project = corpus_path / "c25v001_CORE_00000001" / "project.json"
```

**Pros:**
- ✅ Version pinning ensures reproducible tests
- ✅ Standard Git feature, well-supported
- ✅ Works in CI/CD environments
- ✅ Multiple repos can reference different corpus versions

**Cons:**
- ⚠️ Requires `--recurse-submodules` flag when cloning
- ⚠️ Each parent repo gets its own corpus copy (disk usage)

### Option 2: Symlink (Development)

**Best for:** Local development, quick iteration

#### Setup

```bash
# Clone corpus once in a shared location
git clone https://github.com/rpapub/rpax-corpuses.git ~/projects/rpax-corpuses

# In your parser repository
cd xaml-parser
ln -s ~/projects/rpax-corpuses test-corpus

# Ignore the symlink
echo "test-corpus" >> .gitignore
```

**Windows (requires admin/developer mode):**
```cmd
mklink /D test-corpus C:\projects\rpax-corpuses
```

**Pros:**
- ✅ Simple setup
- ✅ Single corpus copy for all projects
- ✅ Instant updates across all consuming repos

**Cons:**
- ⚠️ Not version-controlled (manual setup per developer)
- ⚠️ No version pinning (always latest)
- ⚠️ Platform-specific considerations

### Option 3: Git Subtree

**Best for:** When you want corpus embedded in parent repo history

```bash
# Add corpus as subtree
git subtree add --prefix=test-corpus \
  https://github.com/rpapub/rpax-corpuses.git development --squash

# Update corpus later
git subtree pull --prefix=test-corpus \
  https://github.com/rpapub/rpax-corpuses.git development --squash
```

**Pros:**
- ✅ No submodule complexity
- ✅ Single `git clone` operation

**Cons:**
- ⚠️ Corpus files duplicated in parent repo
- ⚠️ More complex update process

## CI/CD Integration

### GitHub Actions

```yaml
- name: Checkout with submodules
  uses: actions/checkout@v4
  with:
    submodules: recursive

- name: Run tests against corpus
  run: pytest tests/ --corpus-path=test-corpus
```

### GitLab CI

```yaml
variables:
  GIT_SUBMODULE_STRATEGY: recursive

test:
  script:
    - pytest tests/ --corpus-path=test-corpus
```

## Why NOT Git Worktree?

Git worktree is **not suitable** for this use case because:

- Worktrees are for managing multiple branches of the **same repository**
- Cannot link different repositories (rpax-corpuses ↔ xaml-parser)
- Would require duplicating rpax-corpuses inside each consumer repo

## Corpus Structure Reference

```
test-corpus/
├── c25v001_CORE_00000001/    # Multiple entry points
│   ├── project.json
│   ├── myEntrypointOne.xaml
│   └── ...
├── c25v001_CORE_00000010/    # REFramework pattern
│   ├── project.json
│   ├── Main.xaml
│   └── Framework/
├── c25v001_EDGE_*/           # Edge cases
├── c25v001_REGR_*/           # Regression tests
└── c25v001_STRS_*/           # Stress tests
```

## Recommendations

| Scenario | Recommended Approach |
|----------|---------------------|
| Production/CI | Git Submodule (Option 1) |
| Local development | Symlink (Option 2) |
| Embedded corpus | Git Subtree (Option 3) |
| Multiple corpus versions | Git Submodule (Option 1) |

## Support

For issues or questions:
- Main repo issues: [rpapub/rpax/issues](https://github.com/rpapub/rpax/issues)
- Corpus-specific: [rpapub/rpax-corpuses/issues](https://github.com/rpapub/rpax-corpuses/issues)
