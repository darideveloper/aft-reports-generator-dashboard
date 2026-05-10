## Why

The company-wide report needs to display knowledge areas ordered by their average performance across all employees. This helps identify strengths and weaknesses at the organization level.

## What Changes

- Add a new method `get_average_areas_ordered` to the `SurveyCalcsGroup` class in `utils/survey_calcs_group.py`.
- This method will calculate the average score for each "area" (Knowledge Area/Question Group or Summary Category) across all participant reports associated with the company.
- The results will be returned as a list of dictionaries, each containing the area name and its calculated average, sorted from highest to lowest average.
- The logic will dynamically check for the existence of `ReportQuestionGroupTotal` or `ReportSummaryScore` data to perform these calculations.

## Capabilities

### New Capabilities
- `company-area-averages`: Logic to aggregate and order average scores for knowledge areas across all company participants.

### Modified Capabilities
None.

## Impact

- `utils/survey_calcs_group.py`: New method implementation.
- `survey/tests/test_survey_calcs_group.py`: New test cases to verify the ordering and calculation logic.
