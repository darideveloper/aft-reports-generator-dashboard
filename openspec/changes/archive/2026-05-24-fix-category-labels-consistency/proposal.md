## Why

The recent update to category labels (`update-category-labels`) left several inconsistencies across fixtures, mock data, and documentation. Specifically, "medio ambiente" terminology persists in thematic descriptions, there are capitalization and singular/plural discrepancies between logic and templates, and a missing field in the `TextPDFSummary` fixture impacts the accuracy of the scoring logic.

## What Changes

- Update thematic descriptions and feedback paragraphs in fixtures (`QuestionGroup.json`, `TextPDFQuestionGroup.json`) to replace "medio ambiente" with "Futuro sustentable e inclusivo" and include "inclusión" as a core concept.
- Synchronize labels in the PDF group report template with the model's `TEXT_TYPE_CHOICES` to ensure consistency in capitalization and wording (e.g., "Tecnología y negocios" instead of "Tecnología y Negocio").
- Fix the `TextPDFSummary.json` fixture by adding the missing `question_groups` Many-to-Many relationship field, ensuring proper topic-to-category mapping for summary scores.
- Align `openspec/project.md` documentation with the new branding (including summary description on line 4).
- Update `mock_up_scores.json` to reflect the new terminology.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `summary-scoring-logic`: Requirement for accurate data mapping via fixtures to ensure category-level scoring works as intended.
- `dynamic-text-content`: Requirement for updated text content that reflects the expanded scope of the TMA category (sustainability and inclusion).
- `standardized-pdf-styling`: Requirement for consistent terminology and labeling across all PDF reports.

## Impact

- **Fixtures**: `survey/fixtures/survey/QuestionGroup.json`, `survey/fixtures/survey/TextPDFQuestionGroup.json`, `survey/fixtures/survey/TextPDFSummary.json`.
- **Templates**: `survey/templates/survey/pdf/group_report_template.html`.
- **Documentation**: `openspec/project.md`.
- **Utilities**: `utils/mock_up_scores.json`.
