## Context

The current group report generation logic processes summary-level data for strengths and weaknesses. While sufficient for high-level overviews, users require more granular insights at the question group level to identify specific areas for improvement. Additionally, the report template's wording needed minor refinements for better readability in Spanish.

## Goals / Non-Goals

**Goals:**
- Refine wording in the group report PDF template for better flow.
- Extend the calculation utility to support question-group-level analysis.
- Inject granular weakness data into the PDF generation context.
- Update internal keys to match current branding.

**Non-Goals:**
- Changing the fundamental structure of the PDF report.
- Modifying individual report generation logic.
- Changing how data is collected or stored in the database.

## Decisions

- **Parameterizing Calculations**: Modified `get_weakness_areas` and the helper `_get_extreme_areas` in `SurveyCalcsGroupTexts` to accept a `summary` boolean flag. This allows reusing the same sorting and selection logic for both broad areas and specific question groups.
- **Context Extension**: Added `weakness_question_groups` to the context in `generate_group_report_pdf`. This ensures the template has access to the granular data without changing existing variables, maintaining backward compatibility if needed.
- **Linguistic Refinement**: Replaced simple "y" conjunctions with more descriptive phrases like ", a la vez que" and ", al igual que" to improve the professional tone of the Spanish report.

## Risks / Trade-offs

- **[Risk] Data Overload** → Mitigation: Limit the question group reporting to the bottom 2 (as already implemented in the calculation logic) to prevent overwhelming the user.
- **[Risk] Broken Keys** → Mitigation: Ensure that the hardcoded key update ("Futuro sustentable e inclusivo") matches the keys produced by the underlying data processing logic.
