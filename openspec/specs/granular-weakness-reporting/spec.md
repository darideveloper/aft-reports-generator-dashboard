# granular-weakness-reporting Specification

## Purpose
Define requirements for analyzing and reporting granular weaknesses (question group level) across a dataset of reports.

## Requirements

### Requirement: Granular weakness analysis
The system SHALL provide a mechanism to analyze and extract the bottom-performing question groups for a collective set of reports, distinct from summary-level area analysis.

#### Scenario: Extract question group weaknesses
- **WHEN** calculation is requested for question group weaknesses
- **THEN** the system returns the two lowest-scoring question groups across the dataset
- **AND** these are used to provide specific improvement recommendations in the report
