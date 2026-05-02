## Context
To facilitate the development of advanced PDF layouts using WeasyPrint, developers need a way to preview changes in real time. Standard browsers don't support `@page` rules properly, so simply serving the HTML is insufficient. 

## Goals / Non-Goals
- Goals: Create a Django view that directly serves the generated WeasyPrint PDF to the browser to enable a rapid refresh workflow for template styling.
- Non-Goals: Implement hot-reloading (live reload). The user will still need to manually refresh the browser after saving the template.

## Decisions
- Decision: WeasyPrint can generate a PDF to bytes via `write_pdf()` without a target path. The view will capture these bytes and return them as an inline `application/pdf` `HttpResponse`.
- Decision: Add the URL `/preview-pdf/` directly to `project/urls.py`. 

## Risks / Trade-offs
- Risk: Generating PDFs synchronously in a view can be slow and block threads.
- Mitigation: This is strictly a development/preview feature. It shouldn't be exposed to heavy production traffic.

## Migration Plan
No migration required.