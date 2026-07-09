## Context

The group report PDF template (`survey/templates/survey/pdf/group_report_template.html`) renders a "Ranking nominal" table in section 6. Two column headers use values that deviate from project conventions: "Semáf." includes a special character (á) and "Rank." is an abbreviation that doesn't match other headers.

## Goals / Non-Goals

**Goals:**
- Replace "Semáf." with "Semaf." in the nominal ranking table header
- Replace "Rank." with "Rkg." in the nominal ranking table header

**Non-Goals:**
- No changes to data, logic, or backend code
- No changes to other tables or sections in the report
- No CSS/styling changes

## Decisions

- **Minimal change**: Only modify the `<th>` elements in the HTML template. No need to change `group_report_generator.py` since the template renders static header text.
- **Direct replacement**: Use exact string replacement in the single template file rather than adding dynamic/translatable headers.

## Risks / Trade-offs

- **None**: These are cosmetic label-only changes with zero risk to functionality. If someone has automated PDF parsing that matches the old header strings, they'd need updating.
