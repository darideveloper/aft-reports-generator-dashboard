# Project: AFT Reports Generator Dashboard

## Overview
Django 4.2 survey + report platform for "Alfabetización Tecnológica" (Technological Literacy). Companies invite employees to surveys; generates individual PDF reports (bell curves, bar charts) and organizational group reports (heatmaps, strategic profiles). Spanish language throughout.

## Stack
- **Framework:** Django 4.2.7 + DRF 3.15.2
- **Python:** 3.12
- **DB:** PostgreSQL (prod), SQLite (testing), MySQL supported
- **PDF:** ReportLab + PyPDF2 (individual), WeasyPrint (group reports)
- **Charts:** matplotlib + scipy + numpy
- **Admin:** django-jazzmin 3.0.1 (white/red theme)
- **Auth:** DRF TokenAuthentication + SessionAuthentication
- **Infra:** Gunicorn, Whitenoise, S3 (optional), Docker (Playwright base image)

## Django Apps
| App | Purpose |
|-----|---------|
| `core` | Branding context processor, choices, admin CSS/JS, reusable test base classes |
| `survey` | Main engine: models, views, serializers, admin, management commands, PDF templates |
| `events` | Event registration forms, lead capture, email dispatch (admin + client) |
| `utils` | Standalone: `survey_calcs.py`, `survey_calcs_group.py`, `pdf_generator.py`, `group_report_generator.py`, `graphics_generator.py`, `text_generation.py` |

## API Endpoints
- `POST /api/invitation-code/` — validate code, return company + survey info
- `GET /api/surveys/{id}/` — survey structure with questions/options
- `GET /api/options/` — all form choices
- `POST /api/participant/has-answer/` — check if email already answered
- `POST /api/response/` — submit answers, triggers calc + report generation
- `GET/POST/DELETE /api/progress/` — form progress CRUD (30-day expiry)
- `POST /api/events/{slug}/submit/` — public lead submission
- `GET /group-report-pdf/{company_id}/` — staff-only group PDF download
- `POST /tests/validate-email/` — SMTP validation (token-protected)

## Key Models
- `Company` — name, details, logo, invitation_code, use_average, additional_recommendations
- `Survey` — name, description, active
- `QuestionGroup` — survey FK, survey_index, survey_percentage, modifiers (JSON)
- `Question` / `QuestionOption` — standard FK chain
- `Participant` — name, email, gender, birth_range, position, company
- `Report` — participant FK, JSON fields for scores, chart data, grade
- `ReportsDownload` — select reports, n8n webhook for ZIP generation
- `FormProgress` — email + survey_key based, 30-day TTL
- `Event` / `Lead` — event reg with per-field configurable active/required toggles, honeypot spam

## Conventions
- **Naming:** Spanish verbose names (e.g., verbose_name="Nombre"), model classes in English
- **IDs:** Custom `AutoField(primary_key=True)` on models (not Django default BigAutoField)
- **Media:** `ImageField(upload_to="companies/logos/")`, JSON fields for structured data
- **Views:** Mix of `APIView`, `ViewSet`, and plain Django `View` with `@method_decorator(staff_member_required)`
- **Serializers:** `ModelSerializer` for CRUD, plain `Serializer` for validation-only endpoints
- **Admin:** Custom `SimpleListFilter` for 3-4 level deep FK filtering, custom actions, `@admin.action`
- **PDF:** WeasyPrint for group reports (HTML+CSS), ReportLab for individual (programmatic)
- **Settings:** Environment-based config, `.env.dev` / `.env.prod`, database defaults via `os.environ.get`

## Testing
- **Location:** `survey/tests/` (7 modules)
- **DB:** SQLite auto-switched when `IS_TESTING=True` (detected via `pytest` or `test` in argv)
- **Base classes:** `core/tests_base/` — reusable model/view/admin test classes
- **Run:** `python manage.py test survey` or `pytest`
- **No typing/linting config** — no ruff, mypy, flake8, pyproject.toml, setup.cfg, or .editorconfig

## Management Commands
`survey/management/commands/`: `create_group_report`, `create_reports_download_file`, `create_test_responses`, `delete_expired_progress`, `delete_test_responses`, `generate_next_report`, `generate_next_report_group`, `initial_loaddata`, `link_summary_topics`, `load_response_from_xlsx`

## Known Limitations (see `docs/security-fix.md`)
1. **IDOR** — FormProgressView accessible by email+survey_id without auth
2. **Data leakage** — InvitationCodeView exposes internal company `details` field
3. **Missing answer validation** — ResponseSerializer doesn't validate option→question membership
4. **DoS risk** — ReportsDownload.save() calls `requests.get` without timeout
5. **Email enumeration** — HasAnswerView lets anyone check if email participated
6. **Ambiguous auth** — No explicit `AllowAny` on participant-facing views; shared token pattern

## Load Testing
- `locustfile.py` with `SequentialTaskSet` simulating full survey flow, uses `.env.dev`
- `TEST_API_KEY` + `TEST_INVITATION_CODE` env vars

## Key Env Vars
`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DB_*`, `STORAGE_AWS`, `AWS_*`, `N8N_BASE_WEBHOOKS`, `NOMINAL_RANKING_CHUNK_SIZE` (default 18), `SMTP_TEST_TOKEN`, `EMAIL_*`, `PDF_REPORT_TITLE`, `PDF_REPORT_ACRONYM`
