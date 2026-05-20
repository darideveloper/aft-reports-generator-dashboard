# Proposal: Synchronize Codebase with OpenSpec

## Problem
The project has evolved with several significant features and architectural changes that were implemented without corresponding OpenSpec proposals. This has created a gap between the documented requirements and the actual codebase, leading to potential confusion for future development and maintenance.

## Why
Synchronization is necessary to maintain a "source of truth" in the OpenSpec documentation. This ensures that the AI assistant and developers have accurate context for future features, scoring adjustments, and architectural decisions. Without this, the documentation becomes obsolete and misleading.

## Solution
Create a comprehensive set of specifications that document the current state of the codebase. This includes documenting the batch report download system, the custom benchmarking (target scores) logic, the persistence models for scores, and existing developer utilities.

## What Changes
This proposal adds 6 new specification files and modifies 1 existing specification to reflect the current codebase state. It covers:
- Batch Download Infrastructure
- Custom Benchmarking Logic
- Result Persistence Models
- Dynamic Content Selection
- Structural Form Modifiers
- Developer Management Commands

## Scope
- Document the `ReportsDownload` model and its integration with n8n.
- Document the `CompanyDesiredScore` model and its role in report generation.
- Formally define `ReportQuestionGroupTotal` and `ReportSummaryScore` as persistence requirements.
- Document `TextPDFQuestionGroup` and `TextPDFSummary` for score-based dynamic text.
- Document `QuestionGroupModifier` for structural flexibility.
- Update existing models in specs (e.g., `QuestionGroup.details_bar_chart`).
- Document existing management commands used for development and data loading.

## Non-Goals
- Implementing new features.
- Modifying existing logic (except where necessary for consistency with the new documentation).
- Synchronizing uncommitted local changes (specifically in `survey/views.py` and report templates).
