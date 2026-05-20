## 1. Research and Preparation

- [x] 1.1 Verify `ReportQuestionGroupTotal` and `ReportSummaryScore` field names and relationships.
- [x] 1.2 Confirm the exact output format requirements for area representation (e.g., name vs instance).

## 2. Implementation

- [x] 2.1 Add `get_average_areas_ordered` method to `SurveyCalcsGroup` in `utils/survey_calcs_group.py`.
- [x] 2.2 Implement logic to calculate averages for question groups across all reports in the queryset.
- [x] 2.3 Implement logic to calculate averages for summary categories if applicable.
- [x] 2.4 Add sorting logic to order areas by average score descending.

## 3. Testing

- [x] 3.1 Create test file `survey/tests/test_survey_calcs_group_ordered.py`.
- [x] 3.2 Implement test setup using `GenerateNextReportBase` as a reference for creating mock data.
- [x] 3.3 Add test cases for multiple reports with varied scores across multiple areas.
- [x] 3.4 Add test case for empty reports queryset.
- [x] 3.5 Verify the ordering of returned areas matches expected performance descending.
