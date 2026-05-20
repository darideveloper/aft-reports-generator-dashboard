## Context

The application generates PDF reports using WeasyPrint via Django templates and CSS. Currently, these templates use various page sizes (e.g., A4 in `group_report.css`) and non-standardized font sizes. The user wants to unify these to **Letter** size with **11pt** normal text and **12pt bold** headings. 

Note: Legacy ReportLab generation in `utils/` is explicitly out of scope for this change.

## Goals / Non-Goals

**Goals:**
- Set page size to Letter (8.5" x 11") in WeasyPrint CSS.
- Set base font size to 11pt for normal text.
- Set heading font size to 12pt bold.
- Ensure all WeasyPrint-based templates adhere to these standards.

**Non-Goals:**
- Modifying any files in the `utils/` directory (e.g., `utils/pdf_generator.py`).
- Complete redesign of the report layouts.

## Decisions

### 1. Page Size Standardization
- **WeasyPrint CSS**: Update `@page { size: Letter; }` in `group_report.css` and ensure it is consistent in `style.css`.
- **Rationale**: Direct alignment with user requirements for modern reports.

### 2. Font Size Standardization
- **Normal Text**: Set global or body font-size to `11pt`.
- **Headings**: Set `h1`, `h2`, `h3`, etc., or specific class-based headers (like `.section-title`) to `12pt` with `font-weight: bold`.
- **Sub-Headings (A., B., etc.)**: Set specific sub-headings (like those in the Annex or h4 tags) to `11pt` with `font-weight: bold`.
- **Rationale**: Adherence to specific client branding/formatting requirements.

### 3. CSS Variables for Flexibility
- Define variables in `:root` or `@page` scope:
  - `--page-size: Letter;`
  - `--font-size-normal: 11pt;`
  - `--font-size-heading: 12pt;`
  - `--font-size-sub-heading: 11pt;`
- **Rationale**: Allows for quick global changes across multiple templates if requirements evolve.

### 4. CSS Units
- Use `pt` (points) instead of `px` (pixels) for these specific sizes to ensure precision in print media.

## Risks / Trade-offs

- **[Risk] Visual Hierarchy Compression** → 11pt vs 12pt is very subtle.
- **[Mitigation]** Use bolding for 12pt headings to ensure they are visually distinct from the 11pt body text. 
- **[Risk] Layout Shifting** → Changing from A4 to Letter (wider but shorter) or changing font sizes may cause text to flow differently, potentially causing unexpected page breaks.
- **[Mitigation]** Perform visual inspection of generated PDFs after changes to ensure important sections don't break awkwardly.
