## 1. Executive Summary and Global Index

- [x] 1.1 Replace static text in the Executive Summary with `{{ average_score }}`, `{{ level }}` and `{% for p in summary_paragraphs %}`.
- [x] 1.2 Update the Global Index section with dynamic values for group average, max, and min results.

## 2. Dynamic Tables

- [x] 2.1 Implement `{% for %}` loop for the "Distribución de participantes" table.
- [x] 2.2 Implement `{% for %}` loop for the "Resultados por área de gestión" table.
- [x] 2.3 Implement `{% for %}` loop for the "Ranking de los 13 temas" table.

## 3. Heatmap and Strategic Reading

- [x] 3.1 Refactor the Heatmap table to use nested `{% for %}` loops for participants and theme scores.
- [x] 3.2 Update the "Lectura estratégica" section to render categorized lists of participants.
- [x] 3.3 Make the "Señal Prioritaria" action lists dynamic.

## 4. View and Context Data

- [x] 4.1 Expand the `preview_report_pdf` view in `survey/views.py` with comprehensive mock data for all new dynamic sections.
- [x] 4.2 Verify the final PDF rendering at `/preview-report-pdf/`.
