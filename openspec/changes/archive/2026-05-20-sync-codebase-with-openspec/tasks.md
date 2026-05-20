# Tasks: Synchronize Codebase with OpenSpec

## Documentation Verification
- [x] Verify `batch-report-downloads` against `survey/models.py` and `survey/management/commands/create_reports_download_file.py`
- [x] Verify `custom-benchmarking` against `Company.save()` logic and `CompanyDesiredScore` model
- [x] Verify `report-persistence` against `ReportQuestionGroupTotal` and `ReportSummaryScore` usage in `utils/survey_calcs.py` (or related handlers)
- [x] Verify `dev-utilities` against existing management commands in `survey/management/commands/`
- [x] Verify `model-updates` against `QuestionGroup` model and PDF templates

## Finalization
- [x] Run `openspec validate sync-codebase-with-openspec --strict`
- [x] Merge the changes into the main specification library using `openspec archive sync-codebase-with-openspec`
