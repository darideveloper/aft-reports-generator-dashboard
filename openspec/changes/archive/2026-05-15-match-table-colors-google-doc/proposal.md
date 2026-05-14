## Why

The current table colors in the generated PDF report do not match the visual style of the original Google Doc. To ensure brand consistency and visual parity, the table header colors and cell backgrounds need to be updated.

## What Changes

- **Interpretation Table Styling**: Update the header background color of the "Escala de Interpretación" table to match the Google Doc's muted teal/gray.
- **Indicators Table Styling**: Update the background colors of the "Indicador" table headers to match the yellowish-orange/gold shades from the Google Doc.
- **Generic Table Header**: Refine the default `th` background color to be more consistent with the project's visual standards.

## Capabilities

### New Capabilities
- `table-style-consistency`: Refined table aesthetics for the PDF report, ensuring parity with source documents.

### Modified Capabilities
- None

## Impact

- **survey/templates/survey/pdf/style.css**: CSS rules for `th`, `.interpretation-table`, and `.indicators-table` will be updated.
