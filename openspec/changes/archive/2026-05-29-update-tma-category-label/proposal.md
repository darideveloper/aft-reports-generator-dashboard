## Why

The organization has decided to update the high-level competency category label for the category code `"TMA"` (formerly `"Tecnología y medio ambiente"`) to `"Futuro sustentable e inclusivo"`. This change aligns the terminology with current branding and the expanded thematic scope of the evaluation.

## What Changes

- **Category Label Update**: Re-label the category code `TMA` from `"Tecnología y medio ambiente"` to `"Futuro sustentable e inclusivo"` in models, views, templates, fixtures, and logic throughout the system.
- **Priority Action Title Alignment**: The title and substring mapping in `get_priority_actions()` will remain matched to `"Tecnología y medio ambiente"` or be updated accordingly to reflect `"Futuro sustentable e inclusivo"` depending on design choices.
- **Fixture Updates**: Update `TextPDFSummary.json`, `QuestionGroup.json`, and `TextPDFQuestionGroup.json` fixtures to ensure consistency with the new category name and fix any typos.
- **Group Report & PDF Styling Updates**: Synchronize PDF report rendering and headers to match the new `"Futuro sustentable e inclusivo"` label.
- **Specification Documentation**: Synchronize the primary project specification `openspec/project.md`.

## Capabilities

### New Capabilities

*(None)*

### Modified Capabilities

- `summary-scoring-logic`: The `TMA` category name choice must be updated to `"Futuro sustentable e inclusivo"`, affecting scoring, ordering, and presentation rules.
- `dynamic-pdf-report`: The group PDF report rendering must display `"Futuro sustentable e inclusivo"` instead of `"Tecnología y medio ambiente"`.
- `standardized-pdf-styling`: The strict category label validation must check for `"Futuro sustentable e inclusivo"` instead of `"Tecnología y medio ambiente"`.
- `dynamic-text-content`: The text content selection rules for category TMA must refer to `"Futuro sustentable e inclusivo"`.

## Impact

- **Models**: `survey.models.TextPDFSummary` choices.
- **Fixtures**: `survey/fixtures/survey/QuestionGroup.json` (theme name and description texts) and `survey/fixtures/survey/TextPDFQuestionGroup.json` (feedback paragraph texts).
- **Logic**: `utils/survey_calcs_group.py` (specifically `get_priority_summary` map, heatmap theme headers, and priority actions mapping).
- **Templates**: `survey/templates/survey/pdf/group_report_template.html` (hardcoded references).
- **Specifications**: `openspec/project.md` competency areas definition.
- **Tests**: `survey/tests/` codebase tests that assert label names.
