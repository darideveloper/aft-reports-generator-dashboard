# Project Context

## Purpose
AFT Reports Generator Dashboard is a comprehensive Django-based web application designed to manage surveys, collect participant responses, and automatically generate detailed PDF reports for digital competency assessments. The system evaluates participants across multiple competency areas (Digital Culture, Technology & Business, Cybersecurity, Personal Impact, Technology & Environment, Digital Collaboration Ecosystem) and provides personalized feedback based on their performance.

**Key Goals:**
- Enable companies to assess employee digital competencies through structured surveys
- Automatically generate personalized PDF reports with scores, charts, and recommendations
- Provide a centralized admin dashboard for managing companies, surveys, participants, and reports
- Support batch report generation and downloads
- Integrate with external services (AWS S3, n8n) for scalable file storage and workflow automation

## Tech Stack

### Backend
- **Django 4.2.7** - Main web framework
- **Django REST Framework 3.15.2** - API development
- **PostgreSQL** (via psycopg2-binary 2.9.10, psycopg 3.2.3) - Primary database
- **SQLite** - Testing database
- **Gunicorn 20.1.0** - WSGI HTTP server for production

### Frontend/UI
- **Django Jazzmin 3.0.1** - Modern admin interface theme
- **Django Templates** - Server-side rendering

### File Storage & Media
- **AWS S3** (via boto3 1.26.137, django-storages 1.13.2) - Production file storage
- **Pillow 11.0.0** - Image processing
- **WhiteNoise 6.2.0** - Static file serving

### Report Generation
- **ReportLab 4.4.2** - PDF generation
- **PyPDF2 3.0.1** - PDF manipulation
- **Matplotlib 3.10.3** - Chart generation
- **NumPy 1.26.4** - Numerical computations
- **SciPy 1.16.0** - Scientific computing
- **Pandas 2.3.3** - Data analysis
- **Playwright 1.54.0** - Browser automation for report generation

### Testing & Scraping
- **Selenium 4.20.0** - Browser automation testing
- **BeautifulSoup4 4.13.4** - HTML parsing

### Utilities
- **python-dotenv 1.1.1** - Environment variable management
- **django-cors-headers 4.1.0** - CORS handling
- **django-filter 24.3** - Filtering for DRF
- **requests 2.32.3** - HTTP library
- **openpyxl 3.1.5** - Excel file handling
- **thefuzz[speedup] 0.22.1** - Fuzzy string matching

## Project Conventions

### Code Style
- **Language**: Python 3.x
- **Naming Conventions**:
  - Models: PascalCase (e.g., `QuestionGroup`, `ReportQuestionGroupTotal`)
  - Variables/functions: snake_case (e.g., `question_group_index`, `get_survey_for_admin`)
  - Constants: UPPER_SNAKE_CASE (e.g., `GENDER_CHOICES`, `STATUS_CHOICES`)
- **Spanish Language**: All user-facing text, verbose names, and help text are in Spanish (es-mx)
- **Docstrings**: Use for complex functions and classes
- **Line Length**: Follow PEP 8 guidelines
- **Imports**: Organized in groups (standard library, Django, third-party, local)

### Architecture Patterns
- **Monolithic Django Application**: Single Django project with multiple apps (`core`, `survey`, `utils`)
- **App Structure**:
  - `core`: Base app with shared static files and utilities
  - `survey`: Main business logic (models, views, serializers, admin)
  - `utils`: Helper functions and utilities
- **Model-Driven Design**: Rich domain models with business logic in model methods
- **Admin-Centric**: Heavy use of Django Admin for CRUD operations
- **API Layer**: Django REST Framework for external integrations
- **Signal-Based Automation**: Use Django signals for automated workflows (e.g., report generation)
- **Environment-Based Configuration**: Separate `.env.dev` and `.env.prod` files

### Testing Strategy
- **Test Framework**: Django's built-in test framework
- **Database**: SQLite for testing (configured via `IS_TESTING` flag)
- **Browser Testing**: Selenium and Playwright for end-to-end tests
- **Test Location**: Tests in `survey/tests/` and `core/tests_base/`
- **Headless Mode**: Configurable via `TEST_HEADLESS` environment variable
- **Fixtures**: Located in `survey/fixtures/survey/`

### Git Workflow
- **Repository**: GitHub (darideveloper/aft-reports-generator-dashboard)
- **Branching**: Feature branches merged to main
- **Commit Messages**: Descriptive, action-oriented
- **Version Control**: Git with `.gitignore` for Python/Django projects

## Domain Context

### Survey System
- **Companies**: Organizations that conduct surveys, each with unique invitation codes
- **Surveys**: Collections of question groups representing competency assessments
- **Question Groups**: Thematic sections with weighted percentages (e.g., "Digital Culture" = 20%)
- **Questions**: Individual assessment items (text or select type)
- **Question Options**: Multiple choice answers with point values (typically 0 or 1)
- **Participants**: Employees taking surveys, with demographic data (gender, birth range, position)
- **Answers**: Participant responses to questions

### Reporting System
- **Reports**: Generated PDF documents with participant scores and analysis
- **Report Question Group Totals**: Scores per competency area
- **Text PDF Question Group**: Dynamic text paragraphs based on score thresholds
- **Text PDF Summary**: Summary paragraphs categorized by competency type
- **Company Desired Scores**: Target scores per question group (when not using averages)
- **Reports Download**: Batch ZIP file generation for multiple reports

### Scoring Logic
- Questions have options with point values (0 or 1)
- Question groups have percentage weights
- Total score is calculated across all question groups
- Companies can use either average scores or custom desired scores for benchmarking
- Reports include bar charts comparing participant scores to targets

### Competency Areas (Paragraph Types)
- **CD**: Cultura digital (Digital Culture)
- **TN**: Tecnología y negocios (Technology & Business)
- **CS**: Ciber seguridad (Cybersecurity)
- **IP**: Impacto personal (Personal Impact)
- **TMA**: Tecnología y medio ambiente (Technology & Environment)
- **EDC**: Ecosistema digital de colaboración (Digital Collaboration Ecosystem)

## Important Constraints

### Technical Constraints
- **Timezone**: America/Mexico_City (TIME_ZONE setting)
- **Language**: Spanish (es-mx) for all user-facing content
- **Database**: PostgreSQL in production, SQLite in testing
- **File Storage**: Must support both local and AWS S3 storage (toggled via `STORAGE_AWS` env var)
- **Django Version**: 4.2.7 (LTS version)
- **Python Version**: 3.x (check requirements.txt for specific version)

### Business Constraints
- **Unique Invitation Codes**: Each company must have a unique invitation code
- **Unique Participant Emails**: Email addresses must be unique across all participants
- **Report Status Workflow**: Reports go through pending → processing → completed/error states
- **Question Group Percentages**: Must total 100% for accurate scoring
- **Score Range**: All scores are 0-100

### Security Constraints
- **Authentication**: Token-based authentication for API endpoints
- **CORS**: Configured via `CORS_ALLOWED_ORIGINS` environment variable
- **CSRF**: Trusted origins configured via `CSRF_TRUSTED_ORIGINS`
- **Secret Key**: Must be set via environment variable
- **DEBUG Mode**: Must be False in production

## External Dependencies

### AWS Services
- **S3 Bucket**: For storing static files, media files (logos, PDFs, ZIPs)
- **Configuration**: Requires `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`
- **Storage Backends**: Custom storage backends in `project/storage_backends.py`

### n8n Workflow Automation
- **Base URL**: Configured via `N8N_BASE_WEBHOOKS` environment variable
- **Webhook**: `/aft-create-reports-download-file` - Triggers ZIP file generation for batch downloads
- **Usage**: Called when creating `ReportsDownload` instances

### External Chart Service
- **Bar Chart Endpoint**: Configured via `BAR_CHART_ENDPOINT` (and `TEST_BAR_CHART_ENDPOINT` for testing)
- **Purpose**: Generates bar chart images for PDF reports
- **Integration**: HTTP requests to external service

### Database
- **Production**: PostgreSQL (requires `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`)
- **Testing**: SQLite (automatically configured)
- **MySQL Support**: Optional, with charset configuration for utf8mb4

### Browser Automation
- **Playwright**: Requires browser binaries (install via `playwright install`)
- **Selenium**: Requires WebDriver for browser testing
