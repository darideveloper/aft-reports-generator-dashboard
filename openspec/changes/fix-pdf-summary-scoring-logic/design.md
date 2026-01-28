# Design: Dynamic Scoring Logic

## Current Limitatioms
The current implementation in `SurveyCalcs` uses an explicit mapping:
- If score < 50: fetch text where `min_score` == 49
- If score < 80: fetch text where `min_score` == 79
- Else: fetch text where `min_score` == 100

This is problematic because:
1. It ignores any text records with `min_score` other than 49, 79, or 100.
2. It hardcodes business logic into the code rather than letting the data drive the thresholds.

## Proposed Solution
We will change the lookup strategy to be "floored" or "range-based".

For a given participant score `S`:
1. Query the `TextPDFSummary` (or `TextPDFQuestionGroup`) table.
2. Filter for records where `min_score <= S`.
3. Order by `min_score` descending.
4. Take the first result.

### Example
Suppose we have texts with `min_score`: 0, 50, 75, 90.

- If User Score is 45: `min_score <= 45` -> `[0]`. Result: Text for 0.
- If User Score is 60: `min_score <= 60` -> `[50, 0]`. Result: Text for 50.
- If User Score is 80: `min_score <= 80` -> `[75, 50, 0]`. Result: Text for 75.

### Implementation Details
The method `get_target_threshold` in `utils/survey_calcs.py` can likely be removed or deprecated in favor of direct query logic inside `get_resulting_paragraphs` and `get_resulting_titles`.

```python
# Pseudo-code for get_resulting_titles
target_text = TextPDFSummary.objects.filter(
    paragraph_type=type,
    min_score__lte=total_score
).order_by('-min_score').first()
```

This allows for full flexibility. If the admin wants 10 different feedback levels, they just add rows to the database.

## Test Updates
The tests currently set up data for a specific score but then assert against `100` or `79` explicitly in `__validate_title_and_text`. We need to update this helper to assert that the text corresponding to the *expected* threshold was returned.
