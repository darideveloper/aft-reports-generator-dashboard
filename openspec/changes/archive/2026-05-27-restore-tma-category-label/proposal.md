## Why

The system's database and OpenSpec specs were previously enforcing the terminology "Futuro sustentable e inclusivo" for the TMA category. This strict enforcement caused a bug in `get_priority_actions` which was still using the old terminology ("Tecnología y medio ambiente"), and restricted the flexibility for the product/marketing team to change category names in the future. We need to revert this strict enforcement and restore the "Tecnología y medio ambiente" label across the codebase, database, templates, and specs to fix the bug and align with the current desired branding.

## What Changes

- Remove the strict OpenSpec rules that forced the "Futuro sustentable e inclusivo" naming.
- Update the OpenSpecs to use "Tecnología y medio ambiente".
- Update the Django models (`survey/models.py`) to use "Tecnología y medio ambiente".
- Update calculations (`utils/survey_calcs_group.py`) to reference the restored label.
- Update PDF HTML templates (`survey/templates/survey/pdf/group_report_template.html`).
- Update test files (`survey/tests/test_survey_calcs_group.py`).
- Update the database fixtures (`QuestionGroup.json` and `TextPDFQuestionGroup.json`).
- Run a data migration to update existing database records.

## Capabilities

### New Capabilities
None

### Modified Capabilities
- `summary-scoring-logic`: Remove the strict MUST rule that enforces the "Futuro sustentable e inclusivo" label.
- `dynamic-pdf-report`: Update scenarios and requirements to use the "Tecnología y medio ambiente" label instead of "Futuro sustentable e inclusivo".
- `standardized-pdf-styling`: Relax the exact string matching rule for the labels and update to "Tecnología y medio ambiente".

## Impact

- **Models**: `survey/models.py` (TextPDFSummary choices).
- **Utils**: `utils/survey_calcs_group.py` (Priority actions mapping).
- **Templates**: `survey/templates/survey/pdf/group_report_template.html`.
- **Database/Fixtures**: `survey/fixtures/survey/QuestionGroup.json`, `survey/fixtures/survey/TextPDFQuestionGroup.json`.
- **Tests**: `survey/tests/test_survey_calcs_group.py`.
- **OpenSpec**: `openspec/project.md` and related spec files.