## REMOVED Requirements

### Requirement: Persistence of company-wide average total
**Reason**: The cached `average_total` field in the `Company` model is redundant and prone to stale data.
**Migration**: Replace with dynamic aggregation query in `SurveyCalcs.get_company_average()`.

#### Scenario: Submitting a survey does not update company model
- **WHEN** a participant submits a survey
- **THEN** the `Company` model record SHALL NOT be modified
- **AND** the `average_total` field SHALL BE removed from the schema.
