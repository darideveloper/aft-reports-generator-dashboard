## 1. Model + migration

- [x] 1.1 Add `access_early_minutes = PositiveIntegerField(default=30, verbose_name="Anticipación de acceso (minutos)")` with help text to `Event` in `events/models.py`
- [x] 1.2 Generate migration (`makemigrations events`) and verify default backfill
- [x] 1.3 Expose field in `EventAdmin` fieldset alongside `event_datetime` / `duration_minutes` in `events/admin.py`

## 2. Gate + template

- [x] 2.1 Replace hardcoded `now + timedelta(hours=1)` with `now + timedelta(minutes=event.access_early_minutes or 0)` in `EventAccessView.get()` (`events/views.py`)
- [x] 2.2 Pass `early_seconds = (event.access_early_minutes or 0) * 60` in `EventAccessView.get_context_data()`
- [x] 2.3 Replace hardcoded `3600` with `early_seconds` context var in `events/templates/events/access.html` JS visibility check

## 3. Tests + verification

- [x] 3.1 Update `EventAccessGateTestCase` (`events/tests.py`): default-30 boundary (redirect at +20min, countdown at +60min), custom window (e.g. 90), zero-window case
- [x] 3.2 Add model/admin test: default is 30, rejects negatives, admin round-trip saves custom value
- [x] 3.3 Run `python manage.py test events` and manual check of `/events/<slug>/access/` + countdown button timing
