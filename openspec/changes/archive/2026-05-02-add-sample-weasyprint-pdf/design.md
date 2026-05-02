## Context
The current PDF generation relies on ReportLab and Playwright. However, there is a need to utilize advanced CSS (specifically Paged Media CSS like `@page`, `running()`) for simpler templating of complex documents.

## Goals / Non-Goals
- Goals: Introduce a sample WeasyPrint PDF generator that uses HTML templates with fixed headers/footers and multi-page tables.
- Non-Goals: Replace existing ReportLab/Playwright PDF generation right now. This is an initial sample/proof-of-concept.

## Decisions
- Decision: Use WeasyPrint for the sample because it natively supports CSS Paged Media specifications.
- Decision: Use dynamic CSS variables (like `primary_color`) and template logic for logos to demonstrate high-quality reporting capabilities.
- Decision: Implement the sample as a Django management command to easily trigger it and pass the required base URL for static assets.

## Risks / Trade-offs
- Risk: WeasyPrint has dependencies on system libraries (like Pango, Cairo). Mitigation: Ensure that standard installation is sufficient or document system dependencies if required later.

## Migration Plan
No migration required. This adds a new standalone sample capability.

## Open Questions
- Should this eventually replace ReportLab for all reports?