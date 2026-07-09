## Why

Column headers "Semáf." (with accented á) and "Rank." in the nominal ranking table use special characters and abbreviations that differ from the project's naming conventions. "Semáf." causes encoding/rendering issues in some PDF viewers, and "Rank." is inconsistently abbreviated compared to other table headers.

## What Changes

- Rename "Semáf." column header to "Semaf." in the group report PDF template
- Rename "Rank." column header to "Rkg." in the group report PDF template

## Capabilities

### New Capabilities
- (none)

### Modified Capabilities
- `group-report-generation`: Nominal ranking table column headers updated

## Impact

- Single HTML template file: `survey/templates/survey/pdf/group_report_template.html`
- No data model, logic, or API changes
- No migration needed
