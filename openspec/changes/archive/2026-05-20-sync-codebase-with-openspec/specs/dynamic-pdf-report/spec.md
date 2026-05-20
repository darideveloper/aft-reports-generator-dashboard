## ADDED Requirements

### Requirement: Dynamic Knowledge Area Details
The system SHALL support the display of area-specific details next to the results charts in the PDF report.

#### Scenario: Displaying bar chart details
- **WHEN** a `QuestionGroup` has the `details_bar_chart` field populated
- **THEN** that text SHALL be included in the report context and rendered adjacent to the corresponding bar chart.
