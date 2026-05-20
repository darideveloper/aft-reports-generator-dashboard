# report-persistence Specification

## Purpose
Formalize the requirements for persisting calculated survey results to enable efficient reporting and historical analysis.
## Requirements
### Requirement: Persistence of knowledge area scores
The system SHALL store the calculated total score for each `QuestionGroup` associated with a `Report`.

#### Scenario: Saving report totals
- **WHEN** a report is generated
- **THEN** a `ReportQuestionGroupTotal` record is created for each question group, containing the percentage-weighted score.

### Requirement: Persistence of competency category scores
The system SHALL store the average scores for competency categories (CD, TN, CS, IP, TMA, EDC).

#### Scenario: Saving summary scores
- **WHEN** a report is generated
- **THEN** a `ReportSummaryScore` record is created for each competency category identified in the survey.

