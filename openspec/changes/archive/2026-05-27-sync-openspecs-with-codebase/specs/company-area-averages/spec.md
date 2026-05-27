## MODIFIED Requirements

### Requirement: Support for summary category averages
The system SHALL calculate averages for competency areas using persistent scoring data from `ReportQuestionGroupTotal` and `ReportSummaryScore` models.

#### Scenario: Calculating based on persistent per-area scores
- **WHEN** `get_average_areas_ordered` is called
- **THEN** it SHALL query `ReportQuestionGroupTotal` for the reports in the current context
- **AND** calculate the mean score for each unique `QuestionGroup`
- **AND** return the results ordered by average score.
