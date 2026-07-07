## Why

The "6. Ranking nominal" table uses `table-layout: fixed` with explicit column widths (6% / 35% / 32% / 8% / 12% / 7%) to prevent text wrapping from destabilizing pre-computed page chunks. However, the 6% "Ranking" column (10.6mm) and 7% "Semáforo" column (12.3mm) are too narrow to display their header text at 10pt bold — "Ranking" needs ~14.5mm and "Semáforo" needs ~16.2mm. The text overflows the column boundaries, looking broken in the PDF.

## What Changes

- Abbreviate column headers: "Ranking" → "Rank." and "Semáforo" → "Semáf." in the nominal ranking table template
- Split the combined `.nominal-ranking-table th, td` CSS rule into separate `th` and `td` rules
- Reduce table header font size to 8pt and horizontal padding to 3px (from 10pt / 6px) for `th` cells only, while keeping `td` cells at 10pt / 6px

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `fixed-table-layout`: Header cell styling requirements change — column header text is abbreviated and header cells use a smaller font with reduced horizontal padding, while data cells remain unchanged.

## Impact

- **Template**: `survey/templates/survey/pdf/group_report_template.html` — two text changes in `<th>` elements
- **CSS**: `survey/templates/survey/pdf/group_report_style.css` — one rule split into two, with modified `th` styles
- **No changes** to Python code, column widths, chunking logic, or WeasyPrint pipeline
- **No risk** to the existing empty-page fix — data rows and column widths are untouched
