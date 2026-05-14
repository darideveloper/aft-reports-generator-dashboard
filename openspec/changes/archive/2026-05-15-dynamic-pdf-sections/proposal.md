## Why

The PDF report template contains many static data points (scores, level interpretations, participant lists, action items) that were previously hardcoded. To make the report truly dynamic and reflective of the data in the database, these sections must be converted into Django template variables and logic blocks.

## What Changes

- **Executive Summary**: Replace static scores and text with variables for average score, level, and dynamic descriptive paragraphs.
- **Global Index**: Replace static participant statistics and interpretation text with dynamic values.
- **Distribution & Results Tables**: Use `{% for %}` loops to render tables for participant distribution, management area results, and the ranking of themes.
- **Heatmap**: Convert the static heatmap table into a dynamic one that renders participants and their scores for each theme.
- **Strategic Reading**: Use dynamic lists to display participants categorized as "Embajador Estratégico", "Champion de Transformación", and "Riesgo Crítico".
- **Priority Signal**: Replace static action lists with dynamic content based on the assessment findings.

## Capabilities

### New Capabilities
- `dynamic-report-sections`: Comprehensive dynamic data injection for all major sections of the organizational PDF report.

### Modified Capabilities
- None

## Impact

- **survey/templates/survey/pdf/report_template.html**: Extensive updates to use Django template tags and variables.
- **survey/views.py**: The `preview_report_pdf` view will need an expanded context dictionary to provide all the necessary data for the new dynamic sections.
