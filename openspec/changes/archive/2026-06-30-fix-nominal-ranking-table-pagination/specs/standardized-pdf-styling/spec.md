## MODIFIED Requirements

### Requirement: Uniform Font Sizes for Reports
The system SHALL ensure that all body text in WeasyPrint-based reports is 11pt and all headings are 12pt bold, with the exception of the nominal ranking table which SHALL use 10pt for body text to accommodate long participant names and position titles without destabilizing page boundaries.

#### Scenario: Body text font size check
- **WHEN** a WeasyPrint-based report is rendered
- **THEN** the body text MUST have a font-size of 11pt, unless scoped to a table with an explicit override

#### Scenario: Nominal ranking table font size check
- **WHEN** the nominal ranking table is rendered
- **THEN** the table body text MUST have a font-size of 10pt

#### Scenario: Heading styling check
- **WHEN** a WeasyPrint-based report is rendered
- **THEN** all headings (h1, h2, etc. or specific title classes) MUST have a font-size of 12pt and a font-weight of bold.

#### Scenario: Sub-heading (A., B., etc.) styling check
- **WHEN** a WeasyPrint-based report is rendered
- **THEN** sub-headings starting with A., B., etc. (e.g. h4 or specific sub-heading classes) MUST have a font-size of 11pt and a font-weight of bold.
