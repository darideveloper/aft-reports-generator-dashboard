## 1. Template Updates

- [x] 1.1 Update `survey/templates/survey/pdf/group_report_template.html` to add `|floatformat:2` to `max_score` in the Global Index section.
- [x] 1.2 Update `survey/templates/survey/pdf/group_report_template.html` to add `|floatformat:2` to `min_score` in the Global Index section.
- [x] 1.3 Update `survey/templates/survey/pdf/group_report_template.html` to add `|floatformat:2` to `participant.score` in the "Ranking nominal" table.
- [x] 1.4 Update `survey/templates/survey/pdf/group_report_template.html` to add `|floatformat:2` to `val.score_min` and `val.score_max_display` in the "Nivel de dominio tecnológico" table.

## 2. Utility Verification

- [x] 2.1 Ensure `get_max_score` in `utils/survey_calcs_group.py` consistently returns rounded values.
- [x] 2.2 Ensure `get_min_score` in `utils/survey_calcs_group.py` consistently returns rounded values.
- [x] 2.3 Verify all average calculations in `SurveyCalcsGroup` class (`get_average`, `get_average_areas_ordered`, etc.) include a `round(..., 2)` call.

## 3. Testing and Validation

- [x] 3.1 Trigger a group report generation (via admin action or management command) and visually verify the PDF output.
- [x] 3.2 Ensure all decimal values in the "6. Ranking nominal" section of the PDF show exactly two decimals (e.g., 85.00).
