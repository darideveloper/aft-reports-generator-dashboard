# company-area-averages Specification

## Purpose
Specify requirements for calculating and ordering average scores across different knowledge areas for group reporting and benchmarking.
## Requirements
### Requirement: Ordered average scores for knowledge areas
The `SurveyCalcsGroup` class SHALL provide a method `get_average_areas_ordered` that calculates the average score for each knowledge area (QuestionGroup) across all reports in its context.

#### Scenario: Multiple reports with different scores
- **WHEN** `get_average_areas_ordered` is called with multiple reports present
- **THEN** it returns a list of results, each containing the area and its average score, sorted from highest average to lowest average.

### Requirement: Support for summary category averages
The system SHALL calculate averages for competency areas using persistent scoring data from `ReportQuestionGroupTotal` and `ReportSummaryScore` models.

#### Scenario: Calculating based on persistent per-area scores
- **WHEN** `get_average_areas_ordered` is called
- **THEN** it SHALL query `ReportQuestionGroupTotal` for the reports in the current context
- **AND** calculate the mean score for each unique `QuestionGroup`
- **AND** return the results ordered by average score.

### Requirement: Graceful handling of no data
The system SHALL handle cases where no reports or no scoring data exists without raising errors.

#### Scenario: No reports found
- **WHEN** `get_average_areas_ordered` is called on a `SurveyCalcsGroup` instance with an empty QuerySet
- **THEN** it returns an empty list.

