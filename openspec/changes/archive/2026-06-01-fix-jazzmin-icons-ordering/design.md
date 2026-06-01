## Context

The Django admin interface uses the Jazzmin theme, which relies on a configuration dictionary in `project/settings.py`. Several models in the `survey` app were added recently and haven't been configured with specific icons or sidebar ordering, leading to a fragmented user experience.

## Goals / Non-Goals

**Goals:**
- Assign descriptive FontAwesome icons to all models.
- Ensure all models appear in a logical order in the sidebar.

**Non-Goals:**
- Changing model structures or admin class logic.
- Implementing new features.

## Decisions

### Icon Assignments
- **`survey.ReportSummaryScore`**: `fas fa-chart-pie`.
- **`survey.GroupReport`**: `fas fa-layer-group`.
- **`authtoken.Token`**: `fas fa-key`.
- **`authtoken`**: `fas fa-shield-alt`.

### Sidebar Ordering
The `order_with_respect_to` list will be updated to include:
- `survey.FormProgress` (following `survey.Participant`)
- `survey.ReportSummaryScore` (following `ReportQuestionGroupTotal`)
- `survey.GroupReport` (following `Report`)
- `survey.ReportsDownload` (following `GroupReport`)
- `auth` and `authtoken` apps at the bottom.

This ensures that related data (Reports -> Group Reports -> Downloads) is grouped together.

## Risks / Trade-offs

- **Risk**: Overcrowded sidebar.
- **Mitigation**: Jazzmin's search and grouping features handle this well; the current number of models is still manageable.
- **Risk**: Incorrect icon names causing display issues.
- **Mitigation**: Using verified FontAwesome 5 Free icons.
