## Why

The current public registration forms and confirmation emails for the `events` application use a generic styling framework (with a primary blue theme) and lack any official brand alignment. Centralizing the branding with the company's official color palette and corporate logo will improve visual identity and brand consistency across all events.

## What Changes

- **Centralized Configuration (DRY)**: To prevent color and asset path duplication across multiple templates, define a single global source of truth for the company branding in the Django configuration module.
- **Corporate Styling**: Standardize brand styling across all public event registration forms using the centralized color palette:
  - Primary Color / Text Highlights: Deep Navy (`#0a3c58`)
  - Primary Hover Color: Dark Accent (`#072a3e`)
  - Accent / Highlight Color: Soft Sand (`#f3d39c`)
  - Secondary Accent / Soft Background Color: Soft Sage (`#bcd3cd`)
  - Apply these brand colors dynamically to submit buttons, input focus borders, text accents, success alert cards, and email layouts.
- **Form Logo**: Add the company logo (pointing to the remote URL `https://aft-reports-generator.s3.amazonaws.com/static/core/imgs/logo-leadforward.jpg`) at the top of all public registration forms.
- **Email Branding**: Update the client confirmation email templates to display the company logo, use the centralized corporate color palette, and update the footer signature to "El equipo LeadForward Global Solutions MJ".

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `event-forms`: The form page layout and confirmation email templates will be modified to reference the centralized corporate branding configuration and assets.

## Impact

- Affected settings:
  - `project/settings.py` (defining the new global `BRANDING` configuration)
- Affected templates:
  - `events/templates/events/form.html` (rendering styles and logo from context)
  - `events/templates/events/emails/client_confirmation.html` (rendering styles, logo, and footer from context)
- Affected views / utilities:
  - `events/views.py` (injecting branding config into email rendering context)
  - `core/context_processors.py` (injecting branding config globally into template rendering)
