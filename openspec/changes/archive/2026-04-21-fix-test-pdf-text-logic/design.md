# Design: Correcting expected_min_score in Tests

## Analysis
The application selects PDF text using the following logic:
```python
text_entry = models.TextPDFQuestionGroup.objects.filter(
    question_group=question_group, 
    min_score__lte=score
).order_by("-min_score").first()
```
This selects the highest `min_score` that is $\le$ the actual score.

Available thresholds in `TextPDFQuestionGroup.json` are typically `50`, `70`, and `100`.

### Incorrect Test Logic (Current)
```python
effective_score = int(score / 10) * 10
if effective_score <= 50:
    expected_min_score = 50
elif effective_score <= 70:
    expected_min_score = 70
else:
    expected_min_score = 100
```
- If `score=69`, `effective_score=60`. Since $60 \le 70$, it expects `70`. But the app sees $69 \ge 50$ (and $69 < 70$), so it chooses `50`.
- If `score=99`, `effective_score=90`. Since $90 > 70$, it expects `100`. But the app sees $99 \ge 70$ (and $99 < 100$), so it chooses `70`.

## Proposed Solution
Align the test's `expected_min_score` calculation with the application's floor-based selection.

```python
if score >= 100:
    expected_min_score = 100
elif score >= 70:
    expected_min_score = 70
else:
    expected_min_score = 50
```
This correctly identifies the threshold reached by the participant.
