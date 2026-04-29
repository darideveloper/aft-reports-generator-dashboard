# Tasks: Update Summary Scoring Logic

- [x] **Research & Discovery**
    - [x] Confirm IDs of all 13 QuestionGroups in the current environment.
    - [x] Confirm IDs/choices of the 6 TextPDFSummary types.

- [x] **Model Development**
    - [x] Add `question_groups` ManyToManyField to `TextPDFSummary` in `survey/models.py`.
    - [x] Create `ReportSummaryScore` model in `survey/models.py`.
    - [x] Register new model/fields in `survey/admin.py`.
    - [x] Generate and run migrations.

- [x] **Data Initialization**
    - [x] Create a management command or script to link QuestionGroups to TextPDFSummary categories based on the mapping.
    - [x] Run the script to populate relations.

- [x] **Core Logic Implementation**
    - [x] Implement `save_report_summary_scores` in `utils/survey_calcs.py`.
    - [x] Update `survey/serializers.py` to call `save_report_summary_scores()` after `save_report_question_group_totals()`.
    - [x] Update `get_resulting_titles` in `utils/survey_calcs.py` to use `score <= min_score` selection logic.
    - [x] Modify `get_resulting_titles` in `utils/survey_calcs.py` to use `ReportSummaryScore`.
    - [x] Update `generate_next_report` management command to call `save_report_summary_scores` before PDF generation.


- [x] **PDF Generator Updates**
    - [x] Verify `pdf_generator.py` correctly handles the output from the updated `get_resulting_titles`.
    - [x] **Fix**: Implement strict rendering order (CD, TN, CS, IP, TMA, EDC) in `pdf_generator.py`.

- [x] **Verification & Testing**
    - [x] **Model & Admin Tests**
        - [x] Add tests for `ReportSummaryScore` creation and field validation in `survey/tests/test_models.py`.
        - [x] Add tests for `TextPDFSummary` ManyToMany mapping functionality.
    - [x] **Unit Tests (`SurveyCalcs`)**
        - [x] Add unit tests for `save_report_summary_scores` to verify averaging logic (including multiple topics and rounding).
        - [x] Add unit tests for `get_resulting_titles` to verify retrieval from `ReportSummaryScore`.
        - [x] Add tests for edge cases: category with no mapped topics, missing topic scores.
    - [x] **Integration Tests**
        - [x] Create an integration test that verifies different summary levels for different categories in a single PDF.
        - [x] Verify that `generate_next_report` correctly triggers the full scoring workflow.
        - [x] Verify that re-running a report updates existing summary scores correctly.
    - [x] **Migration & Data Tests**
        - [x] Verify that the initial data migration correctly applies the 6-to-13 mapping.
