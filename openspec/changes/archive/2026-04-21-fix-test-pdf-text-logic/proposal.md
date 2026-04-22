# Proposal: Fix Test PDF Text Logic

## Why
The test suite `GenerateNextReportTextPDFQuestionGroupTestCase` is failing for several scores (specifically 69 and 99) because the test expectation logic for `min_score` does not match the application's actual logic. The test "rounds up" scores to the next threshold, while the application correctly treats `min_score` as a floor that must be reached or exceeded. This discrepancy causes 26 tests to fail even though the application logic is correct.

## What Changes
Update the helper method `_test_pdf_text_generation` in `survey/tests/test_commands.py` to correctly calculate the `expected_min_score` based on the application's threshold logic (floor instead of ceiling-like rounding).

Specifically:
- Remove the `effective_score` calculation which was used for rounding.
- Implement floor-based logic for thresholds at 50, 70, and 100.

## Impact
- **Main Codebase**: No impact.
- **Test Suite**: Fixes 26 failing tests in `survey/tests/test_commands.py`.
- **Reliability**: Ensures tests correctly validate the PDF generation logic as it was intended.
