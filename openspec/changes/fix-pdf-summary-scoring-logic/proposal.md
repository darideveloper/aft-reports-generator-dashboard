# Fix PDF Summary Scoring Logic

## Background
The application generates PDF reports that include summary texts based on the participant's score in various competency areas (question groups). These texts are configured in the database (`TextPDFSummary` and `TextPDFQuestionGroup`) with a `min_score` field.

Currently, the logic for selecting which text to display is rigid and uses hardcoded buckets (49, 79, 100), meaning it strictly looks for texts with `min_score` exactly equal to those values, rather than finding the most appropriate text for a given score. This prevents administrators from configuring granular score thresholds (e.g., a text for > 65).

Additionally, the corresponding tests (`survey/tests/test_commands.py`) contain copy-paste errors where the test method name suggests one score (e.g., 99), but the implementation uses another (e.g., 100).

## Objectives
- **Refactor Scoring Logic**: Update `SurveyCalcs` to dynamically select the summary text with the highest `min_score` that is less than or equal to the participant's obtained score.
- **Fix Tests**: Correct the unit tests in `test_commands.py` to use the intended scores and verify the dynamic logic works as expected.

## Scope
- `utils/survey_calcs.py`: Refactor `get_resulting_paragraphs` and `get_resulting_titles`.
- `survey/tests/test_commands.py`: Fix `test_generate_pdf_summary_with_*` methods.

## Risks
- Existing text configurations in the database might need review if they rely on the previous hardcoded "bucket" behavior, though strictly speaking, the new logic should be compatible if the `min_score` values match the old buckets.
- Performance impact of the query change is negligible.
