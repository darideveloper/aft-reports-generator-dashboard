## Context

The organizational PDF report was recently migrated from a static HTML string to a Django template (`report_template.html`). However, much of the content within the template remains static. This change focuses on identifying and replacing these static elements with dynamic variables and template logic.

## Goals / Non-Goals

**Goals:**
- Implement dynamic data injection for the Executive Summary, Global Index, Distribution, area results, theme rankings, heatmap, and strategic reading sections.
- Ensure the template can handle varying amounts of data (e.g., different number of participants or themes) without breaking the layout.
- Update the preview view to provide a comprehensive set of mock data that exercises all dynamic sections.

**Non-Goals:**
- Database schema changes (we assume the required data can be calculated and passed in the context).
- Changing the PDF styling (this is purely a data injection task).

## Decisions

- **Data Structure for Tables**: Use lists of dictionaries for tabular data (e.g., `area_results`, `theme_ranking`). This is idiomatic for Django templates and allows for clean `{% for %}` loops.
- **Heatmap Logic**: The heatmap requires nested loops: one for participants and another for their scores across the 13 themes. We will pass a `participants_data` list where each participant object has a `theme_scores` list.
- **Strategic Profiles**: Group participants by profile in the context (e.g., `profiles: { 'ambassadors': [...], 'champions': [...], 'risks': [...] }`) for easy rendering.
- **Dynamic Text Blocks**: For sections with multiple paragraphs of generated text (like the executive summary), we will pass them as a list of strings (`summary_paragraphs`) and render them with a loop to maintain flexibility.

## Risks / Trade-offs

- **[Risk] Layout Overflow** → [Mitigation] The paged media CSS handles most layout issues, but we must ensure that dynamic tables don't exceed page bounds in ways that break the template's section-based structure.
- **[Risk] Performance with many participants** → [Mitigation] Rendering a large heatmap for 100+ participants might be slow. However, this is currently a preview feature, and for production, we will ensure efficient data retrieval.
