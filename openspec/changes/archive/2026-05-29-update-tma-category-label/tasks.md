## 1. Models and Fixtures Updates

- [x] 1.1 Update `TEXT_TYPE_CHOICES` in `survey/models.py` to change `"Tecnología y medio ambiente"` to `"Futuro sustentable e inclusivo"` for the `TMA` code option.
- [x] 1.2 Update `survey/fixtures/survey/QuestionGroup.json` to replace `"TEMA 12 - Tecnología y medio ambiente"` with `"TEMA 12 - Futuro sustentable e inclusivo"`, and update `details` and `details_bar_chart` fields to replace `"tecnología y medio ambiente"` with `"Futuro sustentable e inclusivo"` and include `"inclusión"`.
- [x] 1.3 Update feedback paragraphs in `survey/fixtures/survey/TextPDFQuestionGroup.json` for Topic 14 (pk `34`, `35`, `36`) to replace `"tecnología y medio ambiente"` and grammatical typos with `"futuro sustentable e inclusivo"`.
- [x] 1.4 Create and run database migrations to reflect the new category label choices.

## 2. Calculation and Logic Updates

- [x] 2.1 Update `name_to_letter` mapping in `get_priority_summary` in `utils/survey_calcs_group.py` to change `"Tecnología y medio ambiente"` to `"Futuro sustentable e inclusivo"`.
- [x] 2.2 Update `PRIORITY_ACTIONS_MAPPING` keys in `get_priority_actions` in `utils/survey_calcs_group.py` to change `"Tecnología y medio ambiente"` to `"Futuro sustentable e inclusivo"`.

## 3. PDF Template and Specs Updates

- [x] 3.1 Update hardcoded list item on Page 14 of `survey/templates/survey/pdf/group_report_template.html` to change `"Tecnología y medio ambiente."` to `"Futuro sustentable e inclusivo."`.
- [x] 3.2 Update competency area list in `openspec/project.md` to replace `"Tecnología y medio ambiente"` with `"Futuro sustentable e inclusivo"`.

## 4. Verification and Testing

- [x] 4.1 Update all references and assertions from `"Tecnología y medio ambiente"` to `"Futuro sustentable e inclusivo"` in test files (specifically `survey/tests/test_survey_calcs_group.py`).
- [x] 4.2 Execute the test suite to ensure all unit and integration tests pass successfully.
