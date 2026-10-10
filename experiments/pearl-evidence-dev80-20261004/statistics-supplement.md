# Layer 2 descriptive confidence interval supplement

*Pre-summary statistical supplement to the frozen assembly protocol · status: current · 2026-10-04*

This supplement implements [PEARL framework §5.3](../../paper/pearl-framework/PEARL-framework.md)
before the Stage C overall and paired scores are calculated or viewed. Individual reviewer
progress messages may already have described isolated semantic judgments. No aggregated
or paired result was used to choose this method, and the scoring implementer did not read
actual review files. This is a descriptive uncertainty supplement declared before summary
results; it does not add a hypothesis test or change the primary metric. The original
[assembly protocol](protocol.md), contexts, review prompt and blinded packets are preserved.

## Frozen resampling specification

Use 10,000 stratified paired bootstrap replicates with Python `random.Random(20261004)`.
Sort question types and stable intent IDs. Within each of the four types, independently
sample its original number of underlying intent IDs with replacement. A selected intent
carries all four configuration judgments together. The same resampled intent collection
is shared by all configuration and contrast calculations in each replicate. Thus Stage C
keeps 5 intents per type and total N=20; Stage D keeps 20 per type and total N=80. No review
packet, text version, requirement or context occurrence is an independent sampling unit.

Let `L(i,c)=1` exactly when configuration c is sufficient=yes, otherwise 0. Let
`U(i,c)=0` exactly when sufficient=no, otherwise 1. Unknown is `[0,1]` and remains in every
replicate and in the original total denominator. A configuration replicate reports the
means of L and U. For paired A−B, the per-intent lower and upper bounds are respectively
`L(i,A)−U(i,B)` and `U(i,A)−L(i,B)`; average these over the same paired draw.

The four contrasts remain C1−C0 at 4,096 and 8,192 tokens, and 8,192−4,096 within C0 and C1.
No sample or contrast is removed because of unknown support.

## Reporting and interpretation

For each configuration and contrast, save the original lower/upper point estimates and
the 2.5th/97.5th percentile interval of each bound's 10,000 bootstrap estimates. Quantiles
use linear interpolation at index `(10000−1)*q` in the ascending sorted estimates.
Report the descriptive 95% boundary envelope from the lower bound's 2.5th percentile to
the upper bound's 97.5th percentile, alongside both component intervals and unknown counts.
This combines sampling uncertainty with unresolved support bounds; it is not an interval
obtained by deleting unknown samples, nor a claim that unresolved semantic judgments have
been resolved. Four-type scores remain descriptive strata without extra tests.

Exact two-sided McNemar on fully resolved pairs and Holm adjustment across the original
four contrasts remain unchanged. The bootstrap envelopes are descriptive and receive no
new significance threshold or multiplicity-based selection. This is development-set
uncertainty conditional on the frozen requirements and semantic judgments; it does not
measure reviewer/model uncertainty or establish independent confirmatory generalization.

## Reproducibility

The implementation version is `layer2-stratified-paired-bootstrap-r01`. Saved score JSON
records `bootstrap_ci`, replication count, seed, Python version, stratum sizes, score code
SHA-256 and this supplement's SHA-256. The score sidecar manifest binds the same statistical
version and document SHA with input and output file hashes. Deterministic synthetic tests
check constant contrasts, unknown bounds, shared paired draws, input-order invariance and
invalid cluster matrices. Independent verification must recompute these intervals from
saved per-intent judgments; it must not call the scorer's bootstrap implementation.
