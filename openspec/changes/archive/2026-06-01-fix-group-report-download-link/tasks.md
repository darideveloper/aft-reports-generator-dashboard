## 1. Update Report Admin

- [x] 1.1 Add `target="_blank"` to the "Ver Reporte" link in `ReportAdmin.custom_links` in `survey/admin.py`.

## 2. Update ReportsDownload Admin

- [x] 2.1 Add `target="_blank"` to the "Descargar Reportes" link in `ReportsDownloadAdmin.custom_links` in `survey/admin.py`.

## 3. Update GroupReport Admin

- [x] 3.1 Fix the download link in `GroupReportAdmin.custom_links` to use `f"{obj.pk}/download/"`.
- [x] 3.2 Add `target="_blank"` to the "Descargar PDF" link in `GroupReportAdmin.custom_links`.

## 4. Verification

- [x] 4.1 Verify that all three admin download links open in a new tab.
- [x] 4.2 Verify that the GroupReport download link correctly serves the PDF from the list view.
