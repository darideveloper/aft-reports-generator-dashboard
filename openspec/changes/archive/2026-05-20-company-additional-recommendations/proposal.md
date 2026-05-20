# Add dynamic company recommendations

## Why
Currently, the "Recomendaciones adicionales" section in the group report PDF is hardcoded with static text. This prevents administrators from providing tailored recommendations for different companies. 

## What Changes
This change replaces the hardcoded "Recomendaciones adicionales" in the PDF group report with dynamic data pulled from the `Company` model. It introduces an `additional_recommendations` `TextField` to the `Company` model and updates the `GroupReportPDFView` and template to use this data, hiding the section if no recommendations are present.