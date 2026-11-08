# Review report template and worked example

## Contents
- Report template (`docs/design/reviews/<stage>.md`)
- Worked example: review of the online store's high-level design
- Example items

Write the report in the working language. Translate the headings. Keep the IDs as they are, and write the basis marks, severities and statuses with the glossary's terms for the working language.

Each reviewed stage has one report at a fixed path, and the next review of the same stage replaces it: `reviews/2-architecture.md`, `reviews/3-high-level-design.md`, and one per component for stage 4, such as `reviews/4-detailed-design-ELM-02.md`. The report describes the latest review only. Earlier reviews are in git, and their findings keep their own status in `fnd/`.

The report holds what only the review records: the activities and their results, and for stage 2 the risks, non-risks, sensitive points and trade-offs. It indexes the findings and assumptions, and never restates their evidence or statements: those live in the FND and DAS files.

## Report template

```markdown
# Design review: <stage, with the component for stage 4> of <system name>

Status: draft | answers applied · Updated: <date> · Inputs as of: <commit, or "none"> · Context: fresh | the conversation that wrote the design (weaker) · Items reviewed: <IDs>

## Summary
<The number of findings by severity and by addressed skill; the most serious ones in a sentence each; the main risks.>

## Activities and results
| # | Activity | What was done | Result | Findings |
|---|---|---|---|---|
<Every activity in review-procedures.md for the stage, then those for every stage, in order, including those that found nothing. A result too long for its row (stage 2's four questions, stage 3's recomputed budgets with the script's output) goes in a subsection under the table, headed with the activity's number and name.>

## Risks, non-risks, sensitive points and trade-offs
<Stage 2 only: what the driver walkthroughs showed.>
| DRV | Risks | Non-risks | Sensitive points | Trade-offs |
|---|---|---|---|---|

## Findings
| FND | Title | Severity | To | Targets |
|---|---|---|---|---|
<Ordered by severity: the findings this review raised, and the open findings that earlier reviews raised at this path and that still hold. Under the table, cite in one line the rejected findings not raised again.>

## Issues for the quality chain
| # | Issue | Chain items | Suggested change | Quality-chain stage |
|---|---|---|---|---|

## Decisions
| # | Question | Answer | Items |
|---|---|---|---|
<The questions about facts the review needed, and their answers: those of this review, and those of earlier reviews at this path that are still in effect. Items: the items, findings and activities the answer bears on.>

## Open assumptions
| ID | Title | Kind | Breadth | Severity | Items that depend on it |
|---|---|---|---|---|---|
<The DAS this review wrote, and the open DAS and QAS that the items in scope or the findings depend on, highest first, with their ratings after activity E3.>

## Open gaps
<What the review could not check, and why: an input that is missing, a stage report still in draft.>
```

## Worked example: review of the online store's high-level design

`docs/design/reviews/3-high-level-design.md`, with this header:

Status: answers applied · Updated: 2026-11-10 · Inputs as of: 4f2c9e1 · Context: fresh · Items reviewed: IFC-01 to IFC-05, DAT-01 to DAT-06, DEC-11 and DEC-13

Activities (excerpt):

| # | Activity | What was done | Result | Findings |
|---|---|---|---|---|
| B1 | Trace acceptance criteria | Traced the 14 criteria of FR-01 to FR-05 through IFC-01 to IFC-05 and the flows | 13 traced; FR-05's second criterion (a sold-out item is shown as unavailable in the open cart) has no interface that carries stock to the cart | FND-02 |
| B2 | Recompute latency budgets | A script added NFR-02's three serial hops inside the load balancer, where SLI-02's binding observes checkouts, each at the 99.67th percentile (1.30 s, plus a 0.20 s margin), and counted the failover path: at most 3,000 slow checkouts per provider outage at peak | The normal path fits; the failover path uses 3.6% of the error budget per outage, which holds while outages stay rare | none |
| B3 | Check error contracts | Followed every error case of IFC-01 and IFC-02, and what each caller does | When provider A times out, the flow charges provider B at once, while A's outcome is still unknown; A's key does not cover B | FND-01 |
| B6 | Check data entities | Checked the writers and readers of DAT-01 to DAT-06 | One writer each; ELM-02 reads DAT-04 directly under a recorded read-only decision (DEC-11); reservations are a separate entity (DAT-06) | none |
| B7 | Check SLI bindings | Compared SLI-02's unit event (one checkout submitted), vantage (system boundary) and counting rules with the binding on IFC-01 | The vantage holds: the load balancer is the system boundary. The binding counts requests, though, and none of its fields ties a resubmitted checkout to the first, so a checkout submitted again counts twice, against SLI-02's counting rule | FND-03 |
| E3 | Re-rate open assumptions | Counted the items whose `premises` name each open DAS and QAS | DAS-06 keeps its ratings (medium, low): IFC-01 and IFC-02 depend on it. None is high, so none was asked. DAS-01, which IFC-03 rests on, is confirmed (stage 2, question 3) and is not open | none |
| E5 | Look for copied statements | Read IFC-01 to IFC-05 and DAT-01 to DAT-06 for quality-chain wording | None; IFC-01's timing names NFR-02's 1.5 s next to its ID, a label rather than a copy | none |

Findings:

| FND | Title | Severity | To | Targets |
|---|---|---|---|---|
| FND-01 | Failover after a timeout can charge the buyer twice | critical | architecture-to-high-level-design | IFC-02 |
| FND-02 | The open cart never learns that an item sold out | major | architecture-to-high-level-design | IFC-05 |
| FND-03 | SLI-02's binding counts a resubmitted checkout twice | major | architecture-to-high-level-design | IFC-01 |

Open assumptions (excerpt):

| ID | Title | Kind | Breadth | Severity | Items that depend on it |
|---|---|---|---|---|---|
| DAS-06 | Timeouts on the payment path adopted provisionally | decision | medium | low | IFC-01, IFC-02 |

## Example items

Every finding the review raises sets `raised_in` to the report's path, which stays the same from one review of the stage to the next.

`docs/design/fnd/FND-02.yaml`:

```yaml
id: FND-02
title: The open cart never learns that an item sold out
status: open
basis: inferred
basis_note: null
premises: []
raised_by: design-review
raised_in: reviews/3-high-level-design.md
to: architecture-to-high-level-design
targets: [IFC-05]
severity: major
evidence: FR-05's second criterion says a sold-out item is shown as unavailable in the cart; IFC-05 (the cart screen) loads availability once, when the cart opens, and no other IFC updates it
suggestion: Return availability with every cart read (a cart IFC operation), and recheck it when the buyer starts checkout
resolution: null
```
