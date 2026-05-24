## 1. Documentation and Mock Updates

- [x] 1.1 Update `openspec/project.md`:
    - Change "Technology & Environment" to "Sustainable & Inclusive Future" in the summary paragraph (line 4).
    - Change "(Technology & Environment)" to "(Sustainable & Inclusive Future)" in the competency areas list (line 125).
- [x] 1.2 Update `utils/mock_up_scores.json`:
    - Replace "medio ambiente" with "Futuro sustentable e inclusivo" in the 12th object (pk index 11).
    - Update the text to include "inclusión" alongside sustainability.

## 2. Fixture Refinement

- [x] 2.1 Update `survey/fixtures/survey/QuestionGroup.json`: Topic 12 (pk 14) `details` and `details_bar_chart` to replace "medio ambiente" with "Futuro sustentable e inclusivo" and include "inclusión".
- [x] 2.2 Update `survey/fixtures/survey/TextPDFQuestionGroup.json`: Feedback paragraphs for Topic 14 (pk 34, 35, 36) to replace "medio ambiente" with "Futuro sustentable e inclusivo" and include "inclusión".
- [x] 2.3 Update `survey/fixtures/survey/TextPDFSummary.json`: Add the `question_groups` relationship field to all records and populate them according to the design mapping:
    - CD (pk 1,2,3): `[2, 3]`
    - TN (pk 4,5,6): `[4, 11]`
    - CS (pk 7,8,9): `[7, 9]`
    - IP (pk 10,11,12): `[8, 13, 15]`
    - TMA (pk 13,14,15): `[12, 14]`
    - EDC (pk 16,17,18): `[5, 10]`

## 3. Template Synchronization

- [x] 3.1 Update `survey/templates/survey/pdf/group_report_template.html` to standardize category labels:
    - Change "Cultura Digital" to "Cultura digital"
    - Change "Tecnología y Negocio" to "Tecnología y negocios"
    - Change "Ciberseguridad" to "Ciberseguridad"
    - Change "Impacto Personal" to "Impacto personal"
    - Change "Futuro Sustentable e Inclusivo" to "Futuro sustentable e inclusivo"
    - Change "Ecosistema Digital de Colaboración" to "Ecosistema digital de colaboración"

## 4. Verification

- [x] 4.1 Run `python manage.py loaddata survey/fixtures/survey/*.json` to apply fixture changes to the local environment.
- [x] 4.2 Verify that `ReportSummaryScore` records are correctly updated when generating a report (ensure `save_report_summary_scores` picks up the new mapping).
- [x] 4.3 Verify PDF output for correct label casing and terminology.
