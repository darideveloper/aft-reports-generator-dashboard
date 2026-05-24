## 1. Research and Preparation

- [x] 1.1 Verify no other parts of the codebase use `Company.average_total` (e.g. frontend, other models).

## 2. Model and Serializer Changes

- [x] 2.1 Remove `average_total` field from `Company` model in `survey/models.py`.
- [x] 2.2 Generate and apply database migration to drop the `average_total` column.
- [x] 2.3 Remove calculation and save logic for `average_total` in `ResponseSerializer` within `survey/serializers.py`.

## 3. Real-time Calculation Implementation

- [x] 3.1 Implement `get_company_average()` and `get_global_average()` methods in `SurveyCalcs` class in `utils/survey_calcs.py`.
- [x] 3.2 Add a test case to verify both real-time aggregation methods.

## 4. Report Generation and PDF Cleanup

- [x] 4.1 Update `generate_next_report` management command to use the new `SurveyCalcs` methods for both company and global averages.
- [x] 4.2 Remove inline `np.mean` calculation and related logic from `utils/pdf_generator.py`.
- [x] 4.3 Update `generate_report` signature to accept `global_average_total` and inject it into the bell curve plot.
- [x] 4.4 Verify individual report PDF generation correctly displays both "Media de grupo" and "Media Global" using the new dynamic values.

## 5. Testing and Verification

- [x] 5.1 Update assertions in `survey/tests/test_views.py` that rely on `Company.average_total`.
- [x] 5.2 Run all survey tests to ensure no regressions in survey submission or report generation.
- [x] 5.3 Remove any stale code or comments related to the cached average.
