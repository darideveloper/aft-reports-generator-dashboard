# admin-download-ux Specification

## Purpose
Define the user experience requirements for file downloads within the Django admin interface.

## Requirements

### Requirement: Global Admin Download Target Blank
The system SHALL ensure that all generated HTML links in the Django admin interface that serve as file downloads (PDFs, ZIPs) include the `target="_blank"` attribute.

#### Scenario: Individual Report download link
- **WHEN** an admin views the Report list
- **THEN** the "Ver Reporte" link SHALL have the `target="_blank"` attribute.

#### Scenario: Batch Download ZIP link
- **WHEN** an admin views the Descarga de Reportes list
- **THEN** the "Descargar Reportes" link SHALL have the `target="_blank"` attribute.

#### Scenario: Group Report PDF link
- **WHEN** an admin views the Reporte Grupal list
- **THEN** the "Descargar PDF" link SHALL have the `target="_blank"` attribute.
