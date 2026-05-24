## Why

The current category labels in the report generator need to be updated to better reflect the final terminology of the project. Specifically, "Tecnología y medio ambiente" is being replaced by "Futuro sustentable e inclusivo" to align with the desired branding and scope of the evaluation.

## What Changes

- Update the label for the category code `TMA` from "Tecnología y medio ambiente" to "Futuro sustentable e inclusivo" throughout the codebase.
- Ensure all business logic, text generation, and PDF templates reflect this change.
- Update tests and fixtures to use the new label.
- **BREAKING**: Existing database records for `TextPDFSummary` and `ReportSummaryScore` using the `TMA` choice will display the new label. Any hardcoded string comparisons (if any) will need to be updated.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `summary-scoring-logic`: The labels for summary categories are updated.
- `dynamic-text-content`: The text content associated with the updated category label must be verified and updated if necessary.
- `dynamic-pdf-report`: The PDF report layout and section headers must reflect the new category label.

## Impact

- **Models**: `survey/models.py` choice list in `TextPDFSummary`.
- **Utilities**: `utils/survey_calcs_group.py` where labels are hardcoded for mapping or logic.
- **Fixtures**: `survey/fixtures/survey/QuestionGroup.json`.
- **Templates**: `survey/templates/survey/pdf/group_report_template.html` and other PDF-related templates.
- **Documentation**: `openspec/project.md`.
- **Tests**: `survey/tests/test_survey_calcs_group.py` and other test files checking for these strings.
- **Data**: Existing migrations might need to be considered if the choice list change needs to be propagated to the DB (Django handle this usually with a migration).
