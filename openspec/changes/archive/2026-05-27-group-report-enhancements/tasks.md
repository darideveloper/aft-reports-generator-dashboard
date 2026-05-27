## 1. Calculation Logic Enhancements

- [x] 1.1 Update `_get_extreme_areas` in `SurveyCalcsGroupTexts` to accept `use_summary` flag.
- [x] 1.2 Update `get_weakness_areas` in `SurveyCalcsGroupTexts` to accept `summary` flag.
- [x] 1.3 Update hardcoded key `"Tecnología y medio ambiente"` to `"Futuro sustentable e inclusivo"`.

## 2. Report Generation Updates

- [x] 2.1 Update `generate_group_report_pdf` in `utils/group_report_generator.py` to fetch `weakness_question_groups`.
- [x] 2.2 Inject `weakness_question_groups` into the PDF template context.

## 3. Template Refinements

- [x] 3.1 Update strength area wording in `group_report_template.html` to use ", a la vez que".
- [x] 3.2 Update weakness area wording in `group_report_template.html` to use ", al igual que".

## 4. Verification

- [x] 4.1 Verify PDF generation still works for summary areas.
- [x] 4.2 Verify new granular weakness data is available in context (even if not yet heavily used in template layout).
- [x] 4.3 Confirm template wording changes reflect correctly in generated PDF.
