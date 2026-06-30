## ADDED Requirements

### Requirement: Fixed table layout for nominal ranking
The nominal ranking table in the group report SHALL use `table-layout: fixed` with explicit column widths defined via a `<colgroup>` element.

#### Scenario: Column widths are explicitly defined
- **WHEN** the group report HTML template is rendered
- **THEN** the nominal ranking table SHALL contain a `<colgroup>` element with six `<col>` elements defining percentage widths: Ranking 6%, Nombre 35%, Posición 32%, Índice 8%, Nivel 12%, Semáforo 7%

#### Scenario: Column widths sum to 100%
- **WHEN** the `<colgroup>` is parsed
- **THEN** the six column width percentages SHALL sum to exactly 100%

### Requirement: Consistent row height regardless of content length
The nominal ranking table SHALL render all data rows at a consistent height, regardless of whether cell content wraps to a single line or multiple lines, by using a reduced font size and reduced cell padding scoped to this table.

#### Scenario: Font size is reduced for the table
- **WHEN** the nominal ranking table is rendered in the PDF
- **THEN** the table text SHALL use `font-size: 10pt`

#### Scenario: Cell padding is reduced for the table
- **WHEN** the nominal ranking table is rendered in the PDF
- **THEN** table header and data cells SHALL use `padding: 8px 6px`

### Requirement: Chunks fit on one Letter page
The system SHALL ensure that a chunk of `NOMINAL_RANKING_CHUNK_SIZE` participant rows in the nominal ranking table — including the header row and the section title (on the first chunk) — fits within a single Letter page (279.4mm × 215.9mm) with 25mm top and bottom margins. The chunk size SHALL be configurable via the `NOMINAL_RANKING_CHUNK_SIZE` environment variable with a default of 18.

#### Scenario: All rows fit on one page with single-line content
- **WHEN** the `NOMINAL_RANKING_CHUNK_SIZE` is set to 18
- **AND** all participant rows render as single-line (no text wrapping)
- **THEN** the total section height SHALL not exceed the available page content area (229mm)

#### Scenario: All rows fit on one page with mixed-line content
- **WHEN** the `NOMINAL_RANKING_CHUNK_SIZE` is set to 18
- **AND** some participant rows wrap to 2 lines due to long names or positions
- **THEN** the total section height SHALL not exceed the available page content area (229mm)

#### Scenario: Default chunk size is configurable via env var
- **WHEN** the `NOMINAL_RANKING_CHUNK_SIZE` environment variable is not set
- **THEN** the system SHALL use a default chunk size of 18

#### Scenario: Chunk size can be overridden via env var
- **WHEN** the `NOMINAL_RANKING_CHUNK_SIZE` environment variable is set to a positive integer
- **THEN** the system SHALL use that value as the chunk size

### Requirement: No data truncation
The nominal ranking table SHALL display the complete participant name and position as stored in the database, without truncation or ellipsis.

#### Scenario: Long name is fully displayed
- **WHEN** a participant has a name exceeding 30 characters
- **THEN** the full name SHALL be displayed in the table cell without truncation

#### Scenario: Long position is fully displayed
- **WHEN** a participant has a job position title exceeding 20 characters
- **THEN** the full position SHALL be displayed in the table cell without truncation

### Requirement: PDF bytes stored directly via ContentFile
The system SHALL store generated PDF bytes to the Django storage backend using `ContentFile` instead of intermediate temp files, to work reliably across all deployment environments (local and Docker/S3).

#### Scenario: PDF saved without temp file
- **WHEN** the management command `create_group_report` processes a pending GroupReport
- **THEN** the PDF bytes SHALL be saved to the `GroupReport.pdf_file` field using `ContentFile`
- **AND** no intermediate temp file SHALL be created on the filesystem
