## Context

The group report PDF's "6. Ranking nominal" section renders a table of participants sorted by score. A previous fix (change `fix-nominal-ranking-table-pagination`) introduced `table-layout: fixed` with explicit `<colgroup>` column widths to prevent text wrapping from destabilizing pre-computed page chunks. That fix reduced the table font-size to 10pt and cell padding to `8px 6px`.

The current column allocation (sum = 100%):

| Column   | Width | mm    | Purpose       |
|----------|-------|-------|---------------|
| Ranking  | 6%    | 10.6  | Position #    |
| Nombre   | 35%   | 61.6  | Name          |
| Posición | 32%   | 56.3  | Job title     |
| Índice   | 8%    | 14.1  | Score         |
| Nivel    | 12%   | 21.1  | Level text    |
| Semáforo | 7%    | 12.3  | Color dot     |

At 10pt bold Arial, the header text "Ranking" requires ~14.5mm and "Semáforo" requires ~16.2mm. Both exceed their column widths, causing visible text overflow.

## Goals / Non-Goals

**Goals:**
- Eliminate header text overflow in the "Ranking" and "Semáforo" columns
- Preserve all existing fixes: column widths, `table-layout: fixed`, data row sizing, chunk-based pagination
- Change only the header cells — data rows must remain exactly as-is

**Non-Goals:**
- Changing column widths (would risk name/position wrapping → empty pages)
- Modifying data row font-size or padding (would risk the chunk-fit guarantee)
- Truncating participant names or positions (spec requires full display)
- Using `overflow: hidden` or `word-break` (poor visual quality)
- Changing the chunking mechanism or `NOMINAL_RANKING_CHUNK_SIZE`

## Decisions

### Decision 1: Abbreviate header text ("Ranking" → "Rank.", "Semáforo" → "Semáf.")

**Rationale**: At 10pt bold, "Rank." (~9.5mm) and "Semáf." (~11.7mm) are far closer to column boundaries. Combined with the header font reduction (Decision 2), they fit comfortably. The trailing period is a well-understood abbreviation convention in any language.

**Alternatives considered**:
- *Keep full text, reduce font only* — would need ~6.5pt to fit "Semáforo" in 12.3mm, which looks too small and inconsistent even for headers.
- *Truncate "Semáforo" more aggressively (e.g., "Sem.")* — ambiguous with other Spanish words. "Semáf." is clearly an abbreviation of "Semáforo".
- *Abbreviate only one, not the other* — inconsistent styling across the header row.

### Decision 2: Split th/td CSS rules, reduce th font-size to 8pt, reduce th horizontal padding to 3px

**Rationale**: The previous CSS combined th and td in a single rule:
```css
.nominal-ranking-table th,
.nominal-ranking-table td {
  padding: 8px 6px;
}
```
Splitting into separate rules allows header-only adjustments without touching data rows.

- `font-size: 8pt` (from 10pt): At 8pt bold, "Rank." is ~7.6mm and "Semáf." is ~9.4mm. Both fit within their columns even after padding.
- `padding: 8px 3px` (horizontal from 6px to 3px): Saves 6px (1.6mm) of horizontal padding per cell, giving more space for the text. Vertical padding unchanged.

**Size verification**:

| Header text | 8pt bold width | Available after 3px pads | Column | Fits? |
|------------|----------------|-------------------------|--------|-------|
| "Rank."    | ~21.6pt → 7.6mm | ~9.0mm               | 10.6mm | yes   |
| "Semáf."   | ~26.5pt → 9.4mm | ~10.7mm              | 12.3mm | yes   |
| "Nombre"   | ~31pt → 11.0mm   | ~53.5mm              | 61.6mm | yes   |
| "Posición" | ~33pt → 11.7mm   | ~48.3mm              | 56.3mm | yes   |
| "Índice"   | ~25pt → 8.8mm    | ~10.3mm              | 14.1mm | yes   |
| "Nivel"    | ~20pt → 7.1mm    | ~17.4mm              | 21.1mm | yes   |

**Alternatives considered**:
- *7.5pt + no abbreviations* — "Semáforo" still barely overflows (12.2mm vs 12.3mm with 3px pad), too close to the margin.
- *9pt + abbreviations* — "Semáf." (~10.6mm) vs available (~9.7mm with 6px pad) → overflows. Requires both abbreviation and the 3px padding reduction.
- *Keep 6px padding, reduce font further* — would need ~7pt, headers look disproportionately small.

## Risks / Trade-offs

- **8pt headers vs 10pt data rows**: The header row will be subtly smaller than the data rows. This is an intentional visual hierarchy — headers at 8pt in dark blue (#003366) remain clearly distinguishable as column labels.
- **Abbreviation readability**: "Rank." and "Semáf." are non-standard abbreviations but unambiguous in context (a table listing ranking position and a color-dot indicator). Spanish readers will understand them instantly.
- **All headers get 8pt**: The rule applies to all six `th` cells, not just the two that overflow. This keeps the header row visually uniform. The wider columns (Nombre, Posición) have abundance of space anyway.
