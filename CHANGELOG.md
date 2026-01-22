---

# Changelog

All notable changes to BOF (Behavioral Orchestration Framework) will be documented in this file.

## [1.1-public] - 2025-12-18

### Changed
- Simplified for public demonstration
- Writing skill only (reading skill reserved)
- Evaluation harness not included

### Note
This version was created to provide public access while reserving full orchestration logic for institutional collaboration.

---

## [1.0-whitepaper] - 2025-10-31

### Added
- Initial BOF prototype
- WritingSkill with L1-L5 layers
- Baseline comparison (writing_phi3mini_alone.py)
- N=3 validation runs
- Zenodo whitepaper publication

### Implementation Details
- **Model:** phi3:mini (3.8B parameters)
- **Evaluator:** phi3:mini (self-evaluation)
- **Rubric:** 0.0-1.0 scale
- **Prompt:** "Rephrase and slightly expand the following text while keeping its meaning and tone natural."

### Known Limitations
- N=3 (insufficient for statistical significance)
- phi3:mini self-evaluation (potential bias)
- 0.0-1.0 rubric (limited discrimination)
- Fallback heuristics present

**DOI:** [10.5281/zenodo.17491151](https://doi.org/10.5281/zenodo.17491151)

---
