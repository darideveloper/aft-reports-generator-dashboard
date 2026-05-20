# standardized-pdf-styling Specification

## Purpose
Define and enforce consistent PDF styling across all WeasyPrint-based reports, including page size, font sizes, and the use of CSS variables for easy adjustments.

## Requirements

### Requirement: Standardized PDF Styling Variables
The system SHALL define global CSS variables for PDF page size and font sizes in all WeasyPrint-based templates to facilitate easy adjustments.

#### Scenario: Configuration variables are available
- **WHEN** the CSS for a WeasyPrint report is loaded
- **THEN** the variables `--page-size`, `--font-size-normal`, and `--font-size-heading` MUST be defined in the `:root` or `@page` scope.

### Requirement: Uniform Font Sizes for Reports
The system SHALL ensure that all body text in WeasyPrint-based reports is 11pt and all headings are 12pt bold.

#### Scenario: Body text font size check
- **WHEN** a WeasyPrint-based report is rendered
- **THEN** the body text MUST have a font-size of 11pt.

#### Scenario: Heading styling check
- **WHEN** a WeasyPrint-based report is rendered
- **THEN** all headings (h1, h2, etc. or specific title classes) MUST have a font-size of 12pt and a font-weight of bold.

#### Scenario: Sub-heading (A., B., etc.) styling check
- **WHEN** a WeasyPrint-based report is rendered
- **THEN** sub-headings starting with A., B., etc. (e.g. h4 or specific sub-heading classes) MUST have a font-size of 11pt and a font-weight of bold.

### Requirement: Letter Page Size
The system SHALL ensure that all WeasyPrint-based reports are generated with a Letter (8.5" x 11") page size.

#### Scenario: Page size verification
- **WHEN** a WeasyPrint-based report is rendered
- **THEN** the `@page` size property MUST be set to `Letter`.
