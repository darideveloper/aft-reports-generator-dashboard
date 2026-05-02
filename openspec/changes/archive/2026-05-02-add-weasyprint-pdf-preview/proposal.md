# Change: Add live WeasyPrint PDF preview view

## Why
When modifying the HTML and CSS for a WeasyPrint-generated PDF, running the management command repeatedly and opening the file is slow. Browsers also do not natively support CSS Paged Media attributes (`@page`, `running()`). A real-time preview is needed. By creating a Django view that renders the WeasyPrint PDF on the fly and returns it to the browser as `application/pdf`, the user can simply edit the template, refresh the browser page, and instantly see the accurately rendered PDF complete with headers, footers, and complex multi-page tables.

## What Changes
- Add a new view `PreviewPDFSampleView` to `survey/views.py` that utilizes WeasyPrint to render `pdf_sample.html` into a PDF byte string.
- Register this new view in `project/urls.py` on the `/preview-pdf/` route.
- The view will return an `HttpResponse` with `content_type="application/pdf"`.

## Impact
- Affected specs: `pdf-generation`
- Affected code: `survey/views.py`, `project/urls.py`