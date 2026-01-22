READ ME FIRST (BOF_CORE Workspace)

Purpose

* This repository hosts the mini Behavioral Orchestration Framework (BOF) demo and its supporting documents.
* Before making changes, review the structure and existing history to avoid duplicating work or overwriting artifacts.

Critical References

* Vision Documents: `docs/1BOF_vision/` (core architectural intent and strategy).
* Mini Demo Topology: `docs/2BOF_minidemo/` (original architecture and code snapshots that seeded the whitepaper).
* Whitepaper & Appendices: `docs/3BOF_mini_whitepaper/` (published materials on Zenodo).
* Change History & Diffs: `docs/_history/` (e.g., `2025-11-03_mini_bof_update.txt`, `2025-11-03_diff_original_vs_current.txt`).
* Conscious Gaps: `docs/_txt_conscious_gaps/00_CONSCIOUS_GAPS_OVERVIEW.txt` (tracks pending work split between integration hooks and local enhancements). Codex should suggest updating this file if it determines that these gaps have already been filled or resolved, and record the corresponding updates in `docs/_history/`, even if the exact dates of the underlying changes are unknown â€” use the modification date as reference.

Backups & Snapshots

* Full backup ZIP: `BOF_CORE_respaldo_20251103_164102.zip`. Do not modify or delete; use only for recovery or comparison.

Code Structure Highlights

* Meta layer (`meta/`): `bof_core.py` (base orchestrator), `bof_core_adaptive.py` (Sense â†’ Interpret â†’ Plan â†’ Consent â†’ Execute â†’ Reflect), `acf_adapter.py`, `ais_surface.py`.
* Execution layer (`core_exec/`): `bpb_core.py` (L1â€“L5), `meth/` for intent discovery & RLHF, `skills/` with Writing, Reading, and Honesty demos. Deterministic evaluation rubrics are documented in `scripts/calibrate_writing_eval.py` and `scripts/calibrate_honesty_eval.py`. Model providers live under `core_exec/providers/`.
* Logging: `data/log/logger.py` and runtime traces stored in `data/log/records/`.
* Entry points: `main.py`, `main_honesty.py`, `chat_phi3mini_logger.py`, and tests under `test/`.
* Chat CLI commands: `/alone` (Writing baseline), `/alone_reading` (Reading baseline), `/bof` (Writing + Reading via BOF), `/honesty` (Honesty baseline), `/honesty-bof` (Honesty via BOF Adaptive).
* Operational commands: `/alone_reading` -> launches standalone ReadingSkill baseline (mirrors `/alone` for Writing).
* MS MARCO MVP (local intent clustering) lives under `ms_marco_mvp/` with config at `config/ms_marco_mvp.yaml` and runner `scripts/run_ms_marco_mvp.py`.

Current Hooks (for new integrations)

* Pluggable model providers (`core_exec/providers/model_provider.py`) shared by `WritingSkill(provider=...)` and `HonestySkill(provider=...)`.
* Functional entry points: `skill_writing(text)` and `skill_honesty(text)` â€” both callable from MCP/Agents or other orchestrators.
* Policy, routing, and skill executor hooks live in `meta/bof_core_adaptive.py` and `core_exec/bpb_core.py`.

Local Work to Develop (value-add)

* Policy ruleset, heuristic intent routing, persistence, user/cultural profiles, deterministic evaluation, and observability. See the conscious gaps overview for details.

Working Guidelines

* Never edit or delete backups or historical documents.
* Keep all new documentation in English; console/code comments must follow project tone.
* When making substantial changes, update `docs/_history/` with a dated log and, if applicable, a diff summary.
* Use existing hooks rather than modifying core files; extend modules incrementally.
* If new to this repository: read `docs/1BOF_vision`, then the mini demo notes, then inspect the conscious gaps before coding.

---

### Adding a New Skill (Mandatory Audit Protocol)

Before integrating any new skill:

Perform a **full-system inspection** of the BOF framework focusing on the complete `WritingSkill` pipeline. This includes every file, function, and orchestration hook that references or activates `WritingSkill` â€” not only `core_exec/skills/writing.py`, but also its dependencies, calibration scripts, test files, and how it is routed through BPB, ACF, AIS, and the adaptive orchestration layers in `main.py`.

**Objective**
Map exactly how `WritingSkill` operates end-to-end across the BOF system: initialization, invocation, evaluation, logging, calibration, and adaptive reflection.

**Deliverable (audit only â€” no code changes yet):**

* Identify which BOF modules call or reference `WritingSkill` (by file and line range).
* Trace data flow during a complete adaptive cycle.
* List any missing or inconsistent connections for the new skill.

**Do not modify any code yet.**
Produce a complete functional comparison and integration audit so that we can ensure the new skill reaches the same systemic completeness as Writing before proceeding with implementation.

---

**Deletion Protocol (Reversibility Rule)**
To safely remove any experimental skill (e.g., Honesty):

```
rm -rf core_exec/skills/*honesty*.py scripts/*honesty*.py test/*honesty*.py main_honesty.py
# Optionally remove the marked HONESTY block in core_exec/bpb_core.py
```


