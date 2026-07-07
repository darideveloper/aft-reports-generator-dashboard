## 1. Template Changes

- [x] 1.1 Abbreviate column header "Ranking" to "Rank." in `survey/templates/survey/pdf/group_report_template.html`
- [x] 1.2 Abbreviate column header "Semáforo" to "Semáf." in `survey/templates/survey/pdf/group_report_template.html`

## 2. CSS Changes

- [x] 2.1 Split combined `.nominal-ranking-table th, .nominal-ranking-table td` rule into separate `th` and `td` rules in `survey/templates/survey/pdf/group_report_style.css`
- [x] 2.2 Add `font-size: 8pt` and `padding: 8px 3px` to `.nominal-ranking-table th` rule
- [x] 2.3 Keep `padding: 8px 6px` on `.nominal-ranking-table td` rule (unchanged from original)

## 3. Verification

- [x] 3.1 Generate a group report and visually confirm column headers "Rank." and "Semáf." no longer overflow their column boundaries
- [x] 3.2 Confirm data rows remain unchanged (10pt font, 8px 6px padding)
- [x] 3.3 Confirm no empty pages introduced in the nominal ranking section
- [x] 3.4 Confirm all other sections of the PDF render correctly
