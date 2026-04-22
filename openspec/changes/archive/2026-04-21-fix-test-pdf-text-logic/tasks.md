# Tasks: Fix Test PDF Text Logic

- [x] Update `_test_pdf_text_generation` in `survey/tests/test_commands.py` <!-- id: 0 -->
    - Replace the `effective_score` and `if/elif/else` block with the corrected floor-based threshold logic.
- [x] Validate changes by running the tests <!-- id: 1 -->
    - Run `python manage.py test survey.tests.test_commands.GenerateNextReportTextPDFQuestionGroupTestCase` and ensure all tests pass.
