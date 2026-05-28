## 1. Specifications Updates

- [x] 1.1 Update `openspec/project.md` to restore "Tecnología y medio ambiente".
- [x] 1.2 Remove strict MUST requirement from `openspec/specs/summary-scoring-logic/spec.md`.
- [x] 1.3 Update `openspec/specs/dynamic-pdf-report/spec.md` to reference the restored label.
- [x] 1.4 Update `openspec/specs/standardized-pdf-styling/spec.md` to reference the restored label.

## 2. Codebase Updates

- [x] 2.1 Update `survey/models.py` `TextPDFSummary` choices to "Tecnología y medio ambiente".
- [x] 2.2 Update `utils/survey_calcs_group.py` priority summary text to use the restored label.
- [x] 2.3 Update `survey/templates/survey/pdf/group_report_template.html` to display the restored label.
- [x] 2.4 Update test files in `survey/tests/test_survey_calcs_group.py` to assert against "Tecnología y medio ambiente".

## 3. Database Updates

- [x] 3.1 Update `survey/fixtures/survey/QuestionGroup.json` to replace "Futuro sustentable e inclusivo" with "Tecnología y medio ambiente".
- [x] 3.2 Update `survey/fixtures/survey/TextPDFQuestionGroup.json` to replace the text.
- [x] 3.3 Create a new database migration using `python manage.py makemigrations survey` to update the model choices.
- [x] 3.4 Run a one-off Django shell script to update the `name` and `text` attributes of existing `QuestionGroup` and `TextPDFQuestionGroup` rows in the database.