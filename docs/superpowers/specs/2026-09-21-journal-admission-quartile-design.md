# Journal Admission Quartile Design

_Journal ranking admission and unindexed-source cleanup · status: plan_

## Goal

Replace numeric-JCI journal admission with a best-quartile rule and remove Collective Dynamics
literature from active collection assets because the journal is not indexed by either verified
ranking source.

## Scope

This change covers:

- the maintained literature admission standard;
- the offline governance contract, validation helpers, samples, and tests;
- active candidate and incoming-batch assets for Collective Dynamics;
- active collection lists that would otherwise continue to propose the excluded journal.

It does not change citation-age thresholds, content scoring, integrity checks, topic controls,
PDF technical preflight, chunking, retrieval, or indexes.

## Ranking normalization

The journal metrics table remains the lossless source with one row per journal and JCR category.
Before a paper is approved, its journal metrics are normalized as follows:

1. `cas_zone` is the best available value across the CAS major category and every CAS minor
   category. Numerically, the best value is the minimum populated zone.
2. `jci_quartile` is the best available JCI quartile across every JCR category.
3. `jif_quartile` is the best available JIF quartile across every JCR category.
4. The overall journal rank is the best populated value among `cas_zone`, `jci_quartile`, and
   `jif_quartile`, using `1/Q1` as rank 1 through `4/Q4` as rank 4.

The literature Manifest stores these normalized best values rather than every source category.
The complete category-level evidence remains in `journal_metrics.csv`.

## Admission rule

A regular journal paper satisfies the journal-ranking gate when at least one official ranking
system qualifies:

- CAS best zone is 1 or 2; or
- JCI best quartile is Q1 or Q2; or
- JIF best quartile is Q1 or Q2.

The other ranking systems may be worse or unavailable. An unavailable value remains blank and is
not treated as a failing zero. A journal that is unindexed in every verified system fails the
regular journal gate.

Quality tiers use the same OR rule:

- tier A requires at least one official `1/Q1` result;
- tier B requires at least one official `1-2/Q1-Q2` result;
- tier X retains the existing exception reason and approver requirements.

Numeric `jci_value` remains optional reference metadata and no longer affects admission or tier
assignment.

Each populated ranking value must retain official provenance:

- CAS uses `cas_source=cas_journal_partition`;
- JCI uses `jci_source=clarivate_jcr`;
- JIF uses `jif_source=clarivate_jcr`.

At least one populated official ranking value is required for an approved A- or B-tier paper.
Snapshot freshness checks continue to apply to whichever metric families are populated.

## Contract changes

Extend the governance literature contract with optional `jif_quartile`, `jif_year`, and
`jif_source` fields. Keep `jci_value` for reporting compatibility, but remove it from required
approval evidence and tier thresholds.

Implement a small ranking helper that converts CAS zones and JCR quartiles to comparable numeric
ranks. The contract uses the best rank to validate tiers. Source validation is conditional: a
source is required only for its populated metric family, and at least one metric family must be
present.

## Collective Dynamics cleanup

Preserve the `journal_metrics.csv` row marked `not_indexed` as rejection evidence. Remove the
journal from active collection assets:

- delete all four Collective Dynamics rows from the canonical candidate table;
- remove `b3-07` from the Batch 3 incoming Manifest;
- delete `Boomers_2023_CollectiveDynamics_CroMaExperiments.pdf` from the Batch 3 incoming
  directory;
- remove Collective Dynamics entries from active pilot and expansion candidate lists;
- mark retained batch metadata reports as excluded so they remain historical evidence rather
  than active collection instructions.

No chunk or index cleanup is needed because index assets were already cleared and these papers
have not been admitted into the rebuilt index.

## Expected journal outcomes

With the verified 2025 metrics:

| Journal | Best qualifying evidence | Result |
| --- | --- | --- |
| Physica A | JCI Q1 / CAS 2 | pass |
| Scientific Reports | JCI Q1 / JIF Q1 | pass |
| Transportation Letters | JCI Q2 / JIF Q2 | pass |
| Scientific Data | JCI Q1 / JIF Q1 / CAS 2 | pass |
| Frontiers in Physics | JCI Q2 / JIF Q2 | pass |
| Physical Review E | JCI Q1 / JIF Q1 | pass |
| Collective Dynamics | unindexed in verified systems | reject |

These are journal-gate results only. Each individual paper must still satisfy formal-version,
PDF, citation, integrity, content-score, and controlled-topic requirements.

## Validation

- Unit-test A-tier acceptance through each of CAS 1, JCI Q1, and JIF Q1 independently.
- Unit-test B-tier acceptance through each of CAS 2, JCI Q2, and JIF Q2 independently.
- Reject A/B records when all populated rankings are below tier thresholds or all are absent.
- Reject populated metrics with missing or non-official provenance.
- Preserve citation-age, integrity, content-score, topic, and X-tier tests.
- Confirm no Collective Dynamics rows remain in active candidate tables or incoming Manifests.
- Confirm its downloaded Batch 3 PDF is absent while the `not_indexed` journal audit row remains.
- Run the Knowledge-Base test suite and the repository CSV/JSONL parsing checks.
