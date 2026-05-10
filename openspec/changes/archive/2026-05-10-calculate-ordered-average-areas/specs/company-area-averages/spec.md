## ADDED Requirements

### Requirement: Ordered average scores for knowledge areas
The `SurveyCalcsGroup` class SHALL provide a method `get_average_areas_ordered` that calculates the average score for each knowledge area (QuestionGroup) across all reports in its context.

#### Scenario: Multiple reports with different scores
- **WHEN** `get_average_areas_ordered` is called with multiple reports present
- **THEN** it returns a list of results, each containing the area and its average score, sorted from highest average to lowest average.

### Requirement: Support for summary category averages
The system SHALL check for the existence of `ReportQuestionGroupTotal` or `ReportSummaryScore` data and calculate averages accordingly.

#### Scenario: Calculating based on report summary scores
- **WHEN** summary category data is available
- **THEN** it calculates the average for each paragraph type and returns them ordered by score.

### Requirement: Graceful handling of no data
The system SHALL handle cases where no reports or no scoring data exists without raising errors.

#### Scenario: No reports found
- **WHEN** `get_average_areas_ordered` is called on a `SurveyCalcsGroup` instance with an empty QuerySet
- **THEN** it returns an empty list.
