## ADDED Requirements

### Requirement: Persistent Storage of Per-Area Scores
The system SHALL store the calculated total score for each question group (competency area) in a dedicated `ReportQuestionGroupTotal` model associated with each report.

#### Scenario: Save scores on report generation
- **WHEN** a report is generated for a participant
- **THEN** the system SHALL create or update `ReportQuestionGroupTotal` records for every question group in the survey
- **AND** each record SHALL store the absolute score for that specific participant and area.

### Requirement: Unique Scoring Records
The system SHALL enforce uniqueness for the combination of Report and QuestionGroup in the `ReportQuestionGroupTotal` model.

#### Scenario: Prevent duplicate score entries
- **WHEN** the system attempts to save a score for a question group that already has a record for that report
- **THEN** it SHALL update the existing record instead of creating a new one.
