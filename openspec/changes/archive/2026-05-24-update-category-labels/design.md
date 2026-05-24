## Context

The project uses a set of 6 fixed categories for summary scores and PDF report sections. These categories are identified by codes (CD, TN, CS, IP, TMA, EDC) and have human-readable labels. One of these labels ("Tecnología y medio ambiente") needs to be updated to "Futuro sustentable e inclusivo".

## Goals / Non-Goals

**Goals:**
- Update the human-readable label for the `TMA` category throughout the system.
- Ensure all business logic that relies on these labels (string comparisons, mappings) is updated.
- Update UI templates (PDF reports) to display the new label.
- Update tests and fixtures to align with the new labeling.

**Non-Goals:**
- Changing the underlying codes (e.g., `TMA` stays `TMA`).
- Changing the scoring logic itself (how averages are calculated).

## Decisions

- **Model Choices**: Update `TEXT_TYPE_CHOICES` in `survey/models.py`. This is the primary source for the admin interface and display names.
- **Fixtures**: Update `survey/fixtures/survey/TextPDFSummary.json` and `survey/fixtures/survey/QuestionGroup.json` (if applicable) to use the new label.
- **Business Logic**:
    - Update `utils/survey_calcs_group.py` dictionary `name_to_letter` to use the new string "Futuro sustentable e inclusivo" as a key.
    - Update `utils/survey_calcs_group.py` hardcoded strings in the `summaries` dictionary within `get_priority_summary`.
    - Update `PRIORITY_ACTIONS_MAPPING` in `utils/survey_calcs_group.py`.
- **Templates**: Update `survey/templates/survey/pdf/group_report_template.html` to replace the hardcoded "Tecnología y medio ambiente" (and "Tecnología y Medio Ambiente") with "Futuro sustentable e inclusivo".
- **Tests**: Update `survey/tests/test_survey_calcs_group.py` to assert the new label.

## Risks / Trade-offs

- **[Risk]**: Hardcoded string comparisons in `utils/survey_calcs_group.py` might fail if not all instances are found.
  - **Mitigation**: Comprehensive grep search for the old string and replacement.
- **[Risk]**: Existing reports in the database might still have the old label if they were generated/saved with it.
  - **Mitigation**: The labels are usually derived from choices or re-calculated. Since we are changing the choice label, it should reflect immediately on display.
