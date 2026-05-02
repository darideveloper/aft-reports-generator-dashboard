## Context
The group report generation is being finalized for production. A clean, modular structure for the HTML and CSS is required to support the long-term maintenance of the report layout.

## Goals / Non-Goals
- Goals: Establish the final `group_report.html` and `group_report.css` structure. Separate CSS for modularity.
- Non-Goals: Change the underlying WeasyPrint rendering engine.

## Decisions
- Decision: Use `{% include "survey/group_report.css" %}` within the `<style>` block of `group_report.html`. This ensures that dynamic variables (like `primary_color`) remain accessible to the CSS while keeping the files separate.

## Risks / Trade-offs
- Risk: Breaking existing preview links or commands.
- Mitigation: All internal references to the template name will be updated across the codebase.

## Migration Plan
No database migration required. This is a file-level refactoring.