## Context

The competency category code `"TMA"` is currently associated with the label `"Tecnología y medio ambiente"`. A decision has been made to rename this category to `"Futuro sustentable e inclusivo"` across the system. This change touches the model definitions, fixtures, report calculations, PDF templates, and test cases.

## Goals / Non-Goals

**Goals:**
- Update all direct and indirect user-facing instances of `"Tecnología y medio ambiente"` (when used as the `"TMA"` category label) to `"Futuro sustentable e inclusivo"`.
- Ensure all group report calculations, executive summary generation, priority actions, and heatmap headers are consistent with the new label.
- Update tests, migration files, and database fixtures to preserve data integrity and prevent regression.

**Non-Goals:**
- Modifying other category codes or their respective labels.
- Changing the underlying category code `"TMA"`.
- Changing the logic for how scores are averaged or calculated.

## Decisions

### Decision 1: Model Choices Update
- **Approach**: Modify `survey.models.TextPDFSummary.TEXT_TYPE_CHOICES` so that `"TMA"` maps to `"Futuro sustentable e inclusivo"`. Since `ReportSummaryScore.paragraph_type` references `TextPDFSummary.TEXT_TYPE_CHOICES`, it will automatically inherit the update.
- **Migration**: Generate a Django schema/data migration (`makemigrations`) to record this change in the database choices.

### Decision 2: Fixtures Synchronization
- **QuestionGroup.json**: The `QuestionGroup` named `"TEMA 12 - Tecnología y medio ambiente"` (pk `14`) must be updated to `"TEMA 12 - Futuro sustentable e inclusivo"`, and its `details` and `details_bar_chart` fields must be updated to replace `"tecnología y medio ambiente"` with `"Futuro sustentable e inclusivo"` and include `"inclusión"`. This ensures alignment with the new high-level label and seamless matching in priority actions.
- **TextPDFQuestionGroup.json**: The three feedback paragraph texts for Topic 14 (pk `34`, `35`, `36`) must be updated to replace the old `"tecnología y medio ambiente"` terminology and any grammatical typos with `"futuro sustentable e inclusivo"`.
- **TextPDFSummary.json**: No direct occurrences of `"Tecnología y medio ambiente"` exist in the raw JSON keys or values since it uses the choice code `"TMA"`.

### Decision 3: Calculation & Mapping Logic Update (`utils/survey_calcs_group.py`)
- **`get_priority_summary`**: Update `name_to_letter` mapping from `"Tecnología y medio ambiente": "E"` to `"Futuro sustentable e inclusivo": "E"`.
- **`get_priority_actions`**: Update the key `"Tecnología y medio ambiente"` in `PRIORITY_ACTIONS_MAPPING` to `"Futuro sustentable e inclusivo"`. This guarantees that if the topic `"TEMA 12 - Futuro sustentable e inclusivo"` is one of the lowest-scoring themes, the substring search (`key.lower() in area_name.lower()`) will correctly match and load the priority recommendations.

### Decision 4: Template and Specifications Updates
- **`group_report_template.html`**: Replace `<li>Tecnología y medio ambiente.</li>` under Page 14 (Annex C) with `<li>Futuro sustentable e inclusivo.</li>`.
- **`openspec/project.md`**: Update the TMA entry under Competency Areas to `"Futuro sustentable e inclusivo"`.

## Risks / Trade-offs

- **[Risk]** Substring matching in `get_priority_actions` might fail if topic name and mapping key mismatch.
  - *Mitigation*: Simultaneously rename the `QuestionGroup` theme to `"TEMA 12 - Futuro sustentable e inclusivo"` and update `PRIORITY_ACTIONS_MAPPING`'s key to `"Futuro sustentable e inclusivo"`.
- **[Risk]** Existing test cases failing due to outdated assertion strings.
  - *Mitigation*: Update all instances of `"Tecnología y medio ambiente"` in test files (e.g. `test_survey_calcs_group.py`) to `"Futuro sustentable e inclusivo"`.
