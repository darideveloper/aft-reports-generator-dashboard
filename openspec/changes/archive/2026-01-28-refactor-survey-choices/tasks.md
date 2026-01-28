
1. [x] Create `survey/choices.py` file with `GENDER_CHOICES`, `BIRTH_RANGE_CHOICES`, and `POSITION_CHOICES`.
2. [x] Update `survey/models.py` to import and use choices from `survey/choices.py`.
3. [x] Update `survey/serializers.py` to import choices and dynamically generate valid choice lists (e.g. `[c[0] for c in choices]`).
4. [x] Update `survey/management/commands/load_response_from_xlsx.py` if feasible to reference shared keys.
5. [x] Verify application startup/migrations (check logic only, no DB changes expected).
