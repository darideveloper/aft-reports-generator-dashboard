## 1. Model and Data Updates

- [x] 1.1 Update `TEXT_TYPE_CHOICES` in `survey/models.py` to change "Tecnología y medio ambiente" to "Futuro sustentable e inclusivo" for the `TMA` code.
- [x] 1.2 Generate and apply a Django migration for the choice list update.
- [x] 1.3 Update `survey/fixtures/survey/QuestionGroup.json` to change the name of "TEMA 12 - Tecnología y medio ambiente" to "TEMA 12 - Futuro sustentable e inclusivo".
- [x] 1.4 Update `openspec/project.md` to reflect the new label for the `TMA` category.

## 2. Business Logic Updates

- [x] 2.1 Update the `name_to_letter` mapping in `utils/survey_calcs_group.py` to use the new category label.
- [x] 2.2 Update the hardcoded summary strings in `get_priority_summary` within `utils/survey_calcs_group.py` to reflect the new label.
- [x] 2.3 Update `PRIORITY_ACTIONS_MAPPING` keys and internal titles in `utils/survey_calcs_group.py`.

## 3. Template and View Updates

- [x] 3.1 Update `survey/templates/survey/pdf/group_report_template.html` to replace all occurrences of the old label with "Futuro sustentable e inclusivo".

## 4. Testing and Validation

- [x] 4.1 Update `survey/tests/test_survey_calcs_group.py` to use the new labels in assertions.
- [x] 4.2 Run tests in `survey/tests/` to ensure no regressions.
- [x] 4.3 Verify that the `TMA` category displays correctly in the Django Admin for `TextPDFSummary` and `ReportSummaryScore`.
