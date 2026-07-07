## MODIFIED Requirements

### Requirement: Consistent row height regardless of content length
The nominal ranking table SHALL render all data rows at a consistent height, regardless of whether cell content wraps to a single line or multiple lines, by using a reduced font size and reduced cell padding scoped to this table. Header cells SHALL use a smaller font size and reduced horizontal padding to prevent text overflow in narrow columns.

#### Scenario: Column headers use abbreviated text for narrow columns
- **WHEN** the nominal ranking table is rendered in the PDF
- **THEN** the column header text SHALL be "Rank." (not "Ranking")
- **AND** the column header text SHALL be "Semáf." (not "Semáforo")

#### Scenario: Font size is reduced for the table
- **WHEN** the nominal ranking table is rendered in the PDF
- **THEN** table data cells SHALL use `font-size: 10pt`
- **AND** table header cells SHALL use `font-size: 8pt`

#### Scenario: Cell padding is reduced for the table
- **WHEN** the nominal ranking table is rendered in the PDF
- **THEN** table data cells SHALL use `padding: 8px 6px`
- **AND** table header cells SHALL use `padding: 8px 3px`
