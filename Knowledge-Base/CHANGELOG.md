# Changelog

## [v6] - 2026-09-28

### Added
- **Solution B: Dual-layer evidence structure** (`metrics_v2_solution_b.py`)
  - New schema: `evidence_groups` (OR) + `required_evidence` (AND)
  - Supports complex evidence logic: (A1 AND A2) OR (B1 AND B2)
  - Backward compatible with single-group samples
  - Exported as `evaluate_rankings_v2_solution_b`, `GoldQuestionV2B`, `EvidenceGroupV2B`, `EvaluationReportV2B`

### Changed
- **Gold dataset v6** (`evidence_planned_candidate_v6.jsonl`)
  - 105 samples auto-migrated from v5
  - 15 samples manually annotated with dual-layer structure
  - Total: 120 samples (105 single-group + 14 multi-evidence AND + 1 multi-group OR)

### Fixed
- **rgq-073** now correctly scored with OR logic (Moussaid-2016 OR Haghani-2020)
- **14 multi-evidence samples** now correctly enforce AND logic

### Testing
- 14 unit tests for Solution B (all passed)
- 105-sample regression test (0 score mismatches)
- Demo script validates all three evidence structures

---

## [v5] - 2026-09-23

### Changed
- Integrated 120 questions with cross-source and bilingual semantic review
- Revised cross-page and numerical conflict cases
- Adjusted leaked questions

---

## [v4] - Previous

### Changed
- Clarified u021 (East/West tunnel distinction)
- Independent AI review

---

## [v3] - Previous

### Added
- 120 answerable intents, 20 refusal intents
- 280 Chinese/English query variants
- AI review of all samples

---

## [v2] - Previous

### Added
- Initial 20 development + 100 test + 20 refusal intents
- Page-level evidence notes
- Multi-source AND evidence groups

---

## [v1] - Initial

### Added
- Initial 28-intent snapshot
- Evidence candidate structure
