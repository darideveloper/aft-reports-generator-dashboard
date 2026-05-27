## Context

The codebase has advanced significantly, introducing persistent scoring models (`ReportQuestionGroupTotal`, `ReportSummaryScore`) and dynamic content generation logic (Priority Actions) that were not present in the original specifications. Additionally, several spec files have "TBD" placeholders.

## Goals / Non-Goals

**Goals:**
- Eliminate all "TBD" placeholders in `openspec/specs/`.
- Document the current scoring persistence architecture.
- Specification of the dynamic "Priority Actions" mapping logic.
- Align all category labels and ordering requirements with the current Spanish implementation.

**Non-Goals:**
- This is a documentation-only change. No new code will be implemented.
- We will not refactor existing logic, only document it accurately.

## Decisions

- **Centralized Logic vs Spec Localization**: We will update existing specs where appropriate but create new "delta" specs within the change directory to reflect the new capabilities as per OpenSpec conventions.
- **Language Consistency**: All new requirements and scenarios will be written in English to match the OpenSpec standard, while referencing the Spanish labels (e.g., "Futuro sustentable e inclusivo") literally where required for correctness.

## Risks / Trade-offs

- **[Risk] Outdated Specs**: If the codebase changes again during this documentation sync, the specs might become immediately outdated. → **Mitigation**: Perform a final check against the latest `survey/models.py` and `utils/survey_calcs.py` before archiving.
