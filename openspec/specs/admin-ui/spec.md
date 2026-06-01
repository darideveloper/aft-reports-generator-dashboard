# admin-ui Specification

## Purpose
Define the iconography and sidebar ordering for the Django admin Jazzmin theme to ensure a consistent and intuitive user interface.
## Requirements
### Requirement: Admin Sidebar Icons
The Django admin SHALL display specific FontAwesome icons for the following models:
- `survey.ReportSummaryScore` SHALL use `fas fa-chart-pie`.
- `survey.GroupReport` SHALL use `fas fa-layer-group`.
- `authtoken.Token` SHALL use `fas fa-key`.
- `authtoken` SHALL use `fas fa-shield-alt`.

#### Scenario: Verify icons in settings
- **WHEN** the `project/settings.py` file is inspected
- **THEN** the `JAZZMIN_SETTINGS["icons"]` dictionary SHALL contain the correct mappings for `survey.ReportSummaryScore`, `survey.GroupReport`, `authtoken.Token`, and `authtoken`.

### Requirement: Admin Sidebar Ordering
The Django admin SHALL display models in the following order:
1. `survey.Company`
2. `survey.CompanyDesiredScore`
3. `survey.Survey`
4. `survey.QuestionGroup`
5. `survey.QuestionGroupModifier`
6. `survey.Question`
7. `survey.QuestionOption`
8. `survey.Participant`
9. `survey.FormProgress`
10. `survey.Answer`
11. `survey.Report`
12. `survey.ReportQuestionGroupTotal`
13. `survey.ReportSummaryScore`
14. `survey.GroupReport`
15. `survey.ReportsDownload`
16. `survey.TextPDFQuestionGroup`
17. `survey.TextPDFSummary`
18. `auth`
19. `authtoken`

#### Scenario: Verify ordering in settings
- **WHEN** the `project/settings.py` file is inspected
- **THEN** the `JAZZMIN_SETTINGS["order_with_respect_to"]` list SHALL contain all specified models in the exact order.

