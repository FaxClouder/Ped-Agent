# Journal metrics long-form schema

_Multi-category journal-metric storage design · status: plan_

## Goal

Persist the journal information manually verified from 2025 JCR and the 2025 CAS journal
partition table without discarding journals that have more than one JCR category.

## Scope

- Extend `memPed/knowledge/literature/records/journal_metrics.csv` in place.
- Store one row per journal and JCR category.
- Repeat journal-level and CAS major-category fields on each category row.
- Match each JCR category to its corresponding CAS minor category when available.
- Record unavailable and not-indexed values explicitly through status fields and notes rather
  than inventing metrics.
- Do not change admission rules, candidate records, the Catalog, PDFs, chunks, or indexes.

## Columns

The table keeps the existing identifying and provenance concepts and adds lossless category-level
fields:

- identity: `venue`, `issn`, `eissn`, `edition`, `publisher`;
- JCR context: `jcr_year`, `jcr_category`, `jcr_status`;
- JCI: `jci_value`, `jci_rank`, `jci_quartile`, `jci_percentile`;
- JIF: `jif_value`, `jif_rank`, `jif_quartile`, `jif_percentile`;
- supporting journal metric: `total_citations`;
- CAS: `cas_major_category`, `cas_major_zone`, `cas_minor_category`,
  `cas_minor_zone`, `cas_year`, `cas_status`;
- provenance: `jci_source`, `cas_source`, `verified_at`, `verified_by`, `notes`.

Blank values mean the supplied evidence did not contain the metric. `not_indexed` is used only
when the source was checked and the journal was confirmed absent.

## Initial records

Write the seven journals already verified in the conversation: Physica A, Scientific Reports,
Transportation Letters, Scientific Data, Frontiers in Physics, Collective Dynamics, and Physical
Review E. Transportation Letters and Physical Review E each produce two category rows; the other
journals produce one row each, for nine rows total.

## Validation

- Parse the CSV successfully and require a unique `(venue, jcr_year, jcr_category)` key.
- Require nine data rows and seven distinct venues.
- Verify every populated quartile is one of `Q1` through `Q4` and every populated CAS zone is
  between 1 and 4.
- Reconcile representative screenshot values, including multi-category ranks and `not_indexed`.
- Confirm no files outside the design document, documentation index, and journal metrics table
  are changed by this work.
