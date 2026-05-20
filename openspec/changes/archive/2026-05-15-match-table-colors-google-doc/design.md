## Context

The user provided a side-by-side comparison of the Google Doc and the current PDF output. The colors in the PDF are too bright/vibrant compared to the muted, professional palette of the Google Doc.

## Goals / Non-Goals

**Goals:**
- Update `survey/templates/survey/pdf/style.css` with accurate hex codes derived from the Google Doc screenshot.
- Ensure the "Indicador" table correctly distinguishes between its two columns' backgrounds.

**Non-Goals:**
- Change table borders or font sizes (unless absolutely necessary for visual parity).

## Decisions

- **Color Mapping**:
  - `th` (generic/interpretation): `#d9e2f3` (Light Steel Blue)
  - `indicators-table th:first-child`: `#fce5cd` (Very Light Orange/Gold)
  - `indicators-table th:last-child`, `indicators-table td:last-child`: `#fff2cc` (Very Light Yellow/Gold)
- **Specificity**: Use class-based selectors to avoid leaking "Indicador" table styles into other tables.

## Risks / Trade-offs

- **[Risk] PDF Rendering Variance** → [Mitigation] Use standard web colors that translate well to PDF via WeasyPrint.
