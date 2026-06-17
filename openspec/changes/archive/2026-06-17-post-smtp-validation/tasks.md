## 1. Backend Implementation

- [x] 1.1 Update `ValidateEmailView` in `core/views.py` to accept POST requests instead of GET requests.
- [x] 1.2 Parse input parameters (`token`, `real`, `email`) from `request.data` instead of `request.query_params`.
- [x] 1.3 Handle DRF `ParseError` during request body parsing to return a `400 Bad Request` response with a clear error message.

## 2. Test Suite Updates

- [x] 2.1 Update `SMTPValidationEndpointTests` in `core/tests.py` to inherit from `rest_framework.test.APITestCase` instead of `django.test.TestCase`.
- [x] 2.2 Update existing tests in `core/tests.py` to perform POST requests with JSON payloads instead of GET requests.
- [x] 2.3 Add new test case to verify behavior when request has malformed/invalid JSON.

## 3. Verification

- [x] 3.1 Run all tests using Django's test runner to verify everything works correctly.
