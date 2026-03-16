# Tasks

1.  [ ] Refactor `utils/survey_calcs.py` to implement dynamic scoring lookup.
    -   Update `get_resulting_titles` to use `min_score__lte=total`.
    -   Update `get_resulting_paragraphs` to use `min_score__lte=score`.
    -   Remove `get_target_threshold` if unused.
2.  [ ] Fix tests in `survey/tests/test_commands.py`.
    -   Correct `test_generate_pdf_summary_with_99` to actually use score 99.
    -   Correct `test_generate_pdf_summary_with_49` to actually use score 49.
    -   Update reference to `test_generate_pdf_summary_with_0` if needed.
    -   Update `__validate_title_and_text` to support verifying the correct expected text for the new dynamic logic.
3.  [ ] Run tests to verify the fix: `python manage.py test survey.tests.test_commands.GenerateNextReportTextPDFSummaryTestCase`.
