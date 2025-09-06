# rpax-corpuses

> Satellite repository — main development happens in [rpapub/rpax](https://github.com/rpapub/rpax).

rpax tests to crawl, walk, fail… and rise.

## Purpose

This repository hosts **test corpuses** of UiPath Studio projects.  
They serve as foundational material to exercise the rpax parser and lake, ensuring coverage across critical aspects such as project metadata, workflows, invocations, activities, and call graphs.


### 🧩 Corpus Naming Pattern

```
c25v001_<CATEGORY>_<SERIAL>
```

Example:
`c25v001_CORE_00000001`

* **c25** → Corpus batch year (`2025` → abbreviated `c25`)
* **v001** → Parser/lake version alignment (`v0.0.1` → shortened)
* **CATEGORY** → Class of corpus (see below)
* **SERIAL** → 8-digit zero-padded ID for readability in noisy test logs

---

### 📚 Corpus Categories

| Category | Meaning                                   | Purpose                                                         |
| -------- | ----------------------------------------- | --------------------------------------------------------------- |
| **CORE** | Foundational, guaranteed-to-work examples | Baseline validation of parser/lake correctness                  |
| **EDGE** | Edge-case behavior                        | Push parser limits (odd constructs, deep nesting, broken files) |
| **REGR** | Regression scenarios                      | Ensure stability across parser/lake refactors                   |
| **STRS** | Stress tests                              | Measure performance and resilience under load                   |
| **EXPL** | Exploratory / future                      | Experiments for upcoming features or schema changes             |
| **DEMO** | Demonstration examples                    | Human-friendly samples for docs, screenshots, or videos         |

---

### 💡 Usage Philosophy

* Each **Corpus Project** may cover multiple **Aspects** (e.g., multiple entry points, argument passing, invisible activities).
* Corpuses are **synthetic** — not production automations.
* Serve as **external fixtures** for systematic parser and lake debugging.
* Centralized in **`rpapub/rpax-corpuses`**, which acts as the canonical test dataset repo.

## Usage

These corpuses are not production automations.
They exist purely for **testing, validation, and demonstration** of rpax features.

### Integration into Other Repositories

To use this corpus in your parser/lake repository (e.g., `xaml-parser`, `rpax-lake`), see the [Integration Guide](docs/integration.md).

**Quick Start:**
```bash
# Add as git submodule
git submodule add https://github.com/rpapub/rpax-corpuses.git test-corpus
```

For detailed instructions, alternatives (symlink, subtree), and CI/CD setup, see [docs/integration.md](docs/integration.md).


## License & Support

- **License**: [Creative Commons Attribution (CC-BY)](https://creativecommons.org/licenses/by/4.0/) — see [LICENSE](LICENSE) for details.  
- **Issues**: Please [open issues in the parent repo](https://github.com/rpapub/rpax/issues).  
- **Authors**: See [AUTHORS.md](AUTHORS.md) for contributors.
