# Tasks

- [x] 1. Update `.name-list` in `group_report_style.css` to remove `columns: 2` and `column-gap` rules, returning the layout to a single column.
- [x] 2. Add a `.classification-detail p + .name-list` rule in `group_report_style.css` with a `margin-top: 30px;` to provide proper spacing after paragraphs.
- [x] 3. Fix the weakness areas references in `group_report_template.html` on page 11 (e.g., removing `.name` from `weakness_areas.0|safe`) to ensure correct rendering.
- [x] 4. Add `get_priority_actions()` method to `SurveyCalcsGroupTexts` in `utils/survey_calcs_group.py` to identify the two lowest scoring areas and dynamically build the priority actions list from a text mapping.
- [x] 5. Modify `GroupReportPDFView.get()` in `survey/views.py` to retrieve `priority_actions` using `calcs.get_priority_actions()` and remove the hardcoded actions list.