# custom-benchmarking Specification

## Purpose
Specify the requirements for company-specific target scores (benchmarks) and how they override global averages in reporting.
## Requirements
### Requirement: Custom company target scores
The system SHALL support the definition of custom target scores per knowledge area for each company.

#### Scenario: Switching to custom targets
- **WHEN** a company's `use_average` field is set to `False`
- **THEN** the system SHALL use `CompanyDesiredScore` values for comparison in report charts.

### Requirement: Automatic target score scaffolding
The system SHALL ensure that target score records exist for all question groups when custom targets are enabled.

#### Scenario: New company or target switch
- **WHEN** a company is saved with `use_average=False`
- **THEN** `CompanyDesiredScore` records are automatically created for every `QuestionGroup` if they do not already exist.

