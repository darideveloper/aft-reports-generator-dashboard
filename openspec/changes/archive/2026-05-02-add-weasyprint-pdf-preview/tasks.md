## 1. Implementation
- [x] 1.1 Add a new `PreviewPDFSampleView` (or functional view) to `survey/views.py` that constructs context with random data, renders `survey/pdf_sample.html`, and generates the PDF via WeasyPrint `write_pdf()`.
- [x] 1.2 Return the PDF bytes as an `HttpResponse` with `content_type='application/pdf'` and `Content-Disposition: inline`.
- [x] 1.3 Add the URL path `/preview-pdf/` to `project/urls.py` pointing to the new view.
- [x] 1.4 Test the URL by running the development server and opening `http://localhost:8000/preview-pdf/`.