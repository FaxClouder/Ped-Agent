# Layer 3 独立答案语义评审指令

*校准与真实答案共用的评审规则 · status: current · r01 · 2026-10-04*

Read only the supplied anonymous packets and the frozen rubric. Each packet contains
the query, actual answer and semantic reference. Do not read private mappings, generation
model or arm, actual contexts, L2 labels, prior scores or expected calibration labels.

Actually read every answer against its frozen reference. Label every target, condition and
claim ID as correct, incorrect, missing or unknown. A composite key target is correct only
when its whole definition is met; if only part is stated without a contradictory assertion,
label that target missing. Claim coverage records the separately stated parts. A wrong
requested direction or explicit contradiction of the required scope is substantive;
omitting a necessary condition differs from explicitly asserting an incorrect condition.

Judge applicable integration as yes only when the required relationship is actually
established. Listing the two findings alone does not satisfy a required relationship.
Use no for failed applicable integration, unknown only for a concrete unresolved ambiguity.
N/A integration may be recorded as na; the scoring schema ignores it for inapplicable tasks.

Extract each requested numeric value and the unit actually expressed. Normalize unambiguous
unit notation to an equivalent canonical unit, such as cm, m, %, ped/m2 or m2/person.
Do not correct an incorrect unit into the reference unit. If a target value is absent,
record missing; preserve actual parsed values for numerical diagnostics. Reference tolerance
and legal discrete alternatives are already frozen and must not be fitted to answers.

Record contradiction, refusal, integration, numeric extraction and a concise rationale.
Unknown requires a specific semantic ambiguity; unread material is not unknown. Review
extra statements only when they materially contradict the requested reference, rather than
performing general Layer 4 factuality or faithfulness review. Citation presence does not
replace semantic correctness. Do not produce labels from string similarity or code.

Save packet identity, all explicit labels, actual_read=true, reviewer identity,
fork_turns=none provenance and the selected version. Model ID or billing data unavailable
from the review runtime stays null with its unavailability stated.
