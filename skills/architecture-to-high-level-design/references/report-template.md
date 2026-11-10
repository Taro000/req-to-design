# Stage 3 report template and worked example

## Contents
- Report template (`docs/design/3-high-level-design.md`)
- Worked example: online store
- Example items

Write the report in the working language. Translate the headings. Keep the IDs, paths, field names and codes as they are, and write the basis marks and statuses with the glossary's terms for the working language.

The report never restates what an item says: no operations, error contracts, timings, fields, bindings, or other text or values copied from the YAML. It indexes the items by ID, title, enum values and references, and holds what only the report records: the flows, the latency budgets and the worst cases behind the timeouts, the screen flows, the data model diagram, the states across elements, the shared conventions, the acceptance criteria trace, the issues for the quality chain and the decisions.

## Report template

```markdown
# High-level design: <system name>

Status: draft | answers applied · Updated: <date> · Inputs as of: <commit, or "none"> · Stage 3 of 4

## Summary
<Two or three sentences: how many interfaces, specs, flows and entities; which latency budgets fit and which do not; the main conventions; how many questions were decided and how many assumptions are open.>

## Inputs
| Source | What it gave |
|---|---|

## Shared conventions
| Convention | DEC |
|---|---|
<One row per shared convention, with the DEC that records it. What was decided lives in the DEC only; stage 4 reads the conventions from those DECs.>

## Interfaces
| IFC | Title | Kind | Provider | Consumers | FRs | Spec | Basis |
|---|---|---|---|---|---|---|---|

## SLI bindings
| SLI | Title | Vantage | Bound on | Existing source |
|---|---|---|---|---|
<One row per quality-chain SLI. "Bound on" is the IFC or DAT that holds the binding; for an SLI that cannot be bound, the number of its issue for the quality chain.>

## End-to-end flows
### <CUJ-xx name>
<A sequence diagram with its failure paths.>
### <DRV-xx>
<A sequence diagram of the driver's scenario.>

## Latency budgets and timeouts
### <NFR-xx>
<Where the SLI's binding observes the flow, the hop table, the failure paths, and the script's output.>
### Timeouts
<For each call path, the timeouts and waits in the IFCs' `timing`, settlement waits included, and the worst case each caller waits for, from the same script.>

## Screens
### <CUJ-xx name>
<A flowchart of the screens and their actions, error and empty states included.>

## Data
<The entity-relationship diagram, then:>
| DAT | Title | Owner | Store | Classification | Basis |
|---|---|---|---|---|---|
### Data quality flows

## States across elements
<One state diagram per entity whose life spans several elements.>

## Acceptance criteria trace
| FR | Criterion | IFCs | Flow |
|---|---|---|---|
<One row per acceptance criterion, by its number in the FR.>

## Findings
| FND | Raised by | To | Targets | Severity | Status |
|---|---|---|---|---|---|
<The findings addressed to this stage, and those this stage raised.>

## Issues for the quality chain
| # | Issue | Chain items | Suggested change | Quality-chain stage |
|---|---|---|---|---|

## Decisions
| # | Question | Answer | Items |
|---|---|---|---|
<Questions asked and the answers in effect, numbered per stage and continued on re-runs; an overturning answer replaces the row.>

## Open assumptions
| ID | Title | Kind | Breadth | Severity | Items that depend on it |
|---|---|---|---|---|---|
<The DAS this stage wrote, and the open DAS and QAS its items depend on.>

## Placeholders
| Name | Stands for | Used in |
|---|---|---|

## Open gaps
## Out of scope
## Next
<Run `design-review` on this stage in a fresh context when it has not been reviewed yet, or when a critical or major finding changed its items in this run; re-run this stage for the critical or major findings a review addresses to it, not for minor ones; then run `high-level-design-to-detailed-design` once per component: list them.>
```

## Worked example: online store

Interfaces (excerpt). The operations, error contracts, timing and bindings are in each IFC's file; the report only indexes them.

| IFC | Title | Kind | Provider | Consumers | FRs | Spec | Basis |
|---|---|---|---|---|---|---|---|
| IFC-01 | Checkout API | http | ELM-02 | ELM-01 | FR-01 | checkout.openapi.yaml | assumed |
| IFC-02 | Payment provider A | http | ELM-05 | ELM-02 | FR-01 | the provider's own | assumed |
| IFC-03 | Stock changed events from the warehouse | event | ELM-07 | ELM-03 | FR-04, FR-05 | the warehouse's own | inferred |
| IFC-04 | Checkout screen | screen | ELM-01 | USR-01 | FR-01 | none | inferred |
| IFC-05 | Cart screen | screen | ELM-01 | USR-01 | FR-04, FR-05 | none | inferred |

The consumers of a screen are the users who use it (USR-01, the buyer). Provider A's stated latencies for a charge, a lookup and a cancel come from its API documentation, which the user gave for this run; this stage added them to `design-context.yaml` as TC-04 and lists the document under "Inputs" (`conventions.md`, "Judgment basis"). IFC-02 cites TC-04 and does not restate it.

SLI bindings (excerpt):

| SLI | Title | Vantage | Bound on | Existing source |
|---|---|---|---|---|
| SLI-02 | Checkout latency | system-boundary | IFC-01 | OPF-02 |

Latency budget for NFR-02: SLI-02's vantage is the system boundary, and its binding observes it at the load balancer in front of ELM-02 (IFC-01). ELM-01's checkout script runs in the buyer's browser and calls IFC-01 through that load balancer, so the script's own time and the buyer's network are outside the budget. The hop table in `flows-and-budgets.md` budgets three serial hops at the 99.67th percentile, 1.30 s in all, plus a 0.20 s margin, against the 1.5 s threshold. The failover path makes at most 3,000 checkouts slow per provider outage at the sale peak (OPF-03), 3.6% of the error budget ("Failure paths and the error budget"). The script's output is pasted under the table.

Timeouts on the payment path, from the same script: IFC-02's provider_timeout and payment_wait at A, then the same values at B, whose interface keeps them, plus the 0.3 s that the budget gives ELM-02's own work and the database, make a worst case of 2.0 + 3.0 + 2.0 + 3.0 + 0.3 = 10.3 s. IFC-01's timeout of 15 s is above it, so the storefront never abandons a payment that is still running. The three values are provisional and share DAS-06; stage 4 uses them by IFC ID and sets none of them.

Acceptance criteria trace (excerpt):

| FR | Criterion | IFCs | Flow |
|---|---|---|---|
| FR-01 | 1 | IFC-01 (`idempotency`) | Checkout, duplicate request path |

Decisions (excerpt):

| # | Question | Answer | Items |
|---|---|---|---|
| 1 | When a provider times out and its charge cannot be settled within payment_wait, should checkout keep the buyer waiting until it is settled, or answer that the payment is being confirmed and leave the order to reconciliation? | Answer that the payment is being confirmed and leave the order to reconciliation. Never tell the buyer that nothing was charged until every provider tried has confirmed it, and never keep the buyer waiting beyond IFC-01's timeout. | IFC-01, IFC-02, DAT-01 |
| 2 | Public order IDs are drafted as random IDs that cannot be guessed. Do support staff also need a short order number they can read out on the phone? | No. Support staff never read order IDs aloud, so the random ID is enough. | DEC-13 |

Open assumptions (excerpt):

| ID | Title | Kind | Breadth | Severity | Items that depend on it |
|---|---|---|---|---|---|
| DAS-06 | Timeouts on the payment path adopted provisionally | decision | medium | low | IFC-01, IFC-02 |

## Example items

`docs/design/ifc/IFC-01.yaml`:

```yaml
id: IFC-01
title: Checkout API
status: active
basis: assumed
basis_note: The binding of SLI-02 uses the load balancer logs that already exist (OPF-02), and counts a checkout submitted again once, following FND-03; the handling of unsettled payments follows FND-01 and is confirmed (question 1); the timeout is a provisional decision (DAS-06); the rest is inferred from DEC-02, DRV-05 and the shared conventions
premises: [OPF-02, DAS-06]
kind: http
name: Checkout API
provider: ELM-02
consumers: [ELM-01]                      # the storefront's checkout script, running in the buyer's browser
functions: [FR-01]
operations:
  - {name: POST /v1/checkout, does: Confirms the cart as an order and charges the buyer}
format: JSON
protocol: HTTPS, request and response
auth: Buyer session cookie
errors:
  - {case: Card declined, signal: 402 with code CARD_DECLINED, caller_does: Show the decline and keep the cart}
  - {case: No provider could take the payment and every provider tried confirmed that nothing was charged, signal: 503 with code PAYMENT_UNAVAILABLE, caller_does: Ask the buyer to try again later}
  - {case: The outcome of the payment is not settled yet because a provider timed out, signal: 202 with code PAYMENT_PENDING and the order ID, caller_does: Show that the payment is being confirmed and poll the order; never submit again with a new key}
  - {case: The same key while the first request is still running, signal: 409 with code CHECKOUT_IN_PROGRESS, caller_does: Wait and poll the order}
  - {case: The same key with a different cart, signal: 422 with code KEY_REUSED, caller_does: Start a new checkout with a new key}
idempotency: One Idempotency-Key per order - the storefront creates it when the buyer first submits the cart and reuses it on every retry; the same key returns the first result
timing:
  timeout: 15 s (provisional, DAS-06; above the worst case of the payment path, 10.3 s, so that a payment still running is never abandoned; the 1.5 s of NFR-02 is a target, not a timeout)
  ordering: null
  delivery: null
versioning: Version in the path; only additive changes within v1
observability: Logs request_id and outcome in the service, for investigations
sli_bindings:
  - sli: SLI-02
    events: Each POST /v1/checkout request that reaches the load balancer in front of ELM-02 (the SLI's vantage is the system boundary); requests with the same Idempotency-Key are one checkout, counted by the first request
    fields: [request_id, idempotency_key, status, elapsed, user_agent]
    method: The load balancer's access logs, which already exist (OPF-02), with the Idempotency-Key header added to the logged fields
spec: ifc/specs/checkout.openapi.yaml
as_is: new
```

The fields cover SLI-02's counting rules: `status` tells apart the checkouts the system failed (they belong to the availability SLI) and the requests that were not signed in, `user_agent` tells synthetic monitoring and load tests apart, and `idempotency_key` makes a checkout submitted again count once.

`docs/design/ifc/IFC-02.yaml` (excerpt), the interface of an external system. What provider A promises is cited by TC ID, and the timeouts and waits on calls to it are this stage's (`interfaces.md`, "Timing"):

```yaml
id: IFC-02
title: Payment provider A
status: active
basis: assumed
basis_note: Operations and errors as provider A's documentation gives them, linked in the report; its stated latencies are TC-04; settling a timed-out charge at A before trying another provider follows FND-01; the handling of unsettled payments is confirmed (question 1); the timing is a provisional decision (DAS-06); the rest is inferred
premises: [EXT-01, TC-01, TC-04, DAS-06]
kind: http
name: Payment provider A
provider: ELM-05
consumers: [ELM-02]
functions: [FR-01]
# ... operations, format, protocol, auth, errors and idempotency ...
timing:
  timeout: provider_timeout 2.0 s on each call to A (provisional, DAS-06; above the 99.9th percentile that TC-04 states for a charge, so that healthy charges almost never time out); payment_wait 3.0 s to settle an unknown outcome at A, by looking up the key and cancelling the charge there, before any other provider is tried (provisional, DAS-06; room for a lookup and a cancel at the latencies TC-04 states, and to repeat the lookup once)
  ordering: null
  delivery: null
# ... versioning and observability ...
sli_bindings: []
spec: null                               # provider A owns its document; the report links it
as_is: new
```

`docs/design/das/DAS-06.yaml`. The timing values that hinge on the providers' real latencies share it; its statement names them and leaves their values in IFC-01 and IFC-02, so that tuning them changes only those files:

```yaml
id: DAS-06
title: Timeouts on the payment path adopted provisionally
status: open
stage: 3
kind: decision
statement: IFC-02 uses the provisional provider_timeout and payment_wait in its timing, and IFC-01's timeout stays above the worst case of the payment path that they give, until operation shows the providers' real latencies
why_unsure: The values rest on the latencies that provider A states (TC-04), which our own traffic has not measured yet, and no input says how long buyers wait before they give up or press again
breadth: medium
severity: low
rating_note: IFC-01 and IFC-02 depend on it, and stage 4's payment router will through IFC-02's timing; tuned in operation, with IFC-01's timeout kept above the worst case whenever the others change
answer: null
answered_in: null
```

`docs/design/ifc/IFC-03.yaml`:

```yaml
id: IFC-03
title: Stock changed events from the warehouse
status: active
basis: inferred
basis_note: The warehouse sends one event per stock change (DAS-01, confirmed in stage 2, question 3); delivery and ordering are as the warehouse team's document gives them; the consumer's handling is inferred
premises: [EXT-02, DAS-01]
kind: event
name: Stock changed
provider: ELM-07
consumers: [ELM-03]
functions: [FR-04, FR-05]
operations:
  - {name: stock.changed, does: Tells that the count of one item at the warehouse changed}
format: JSON
protocol: The warehouse's message broker, one topic
auth: A client certificate issued by the warehouse team
errors:
  - {case: A message that does not match the schema, signal: Rejected by ELM-03 validation, caller_does: ELM-03 sets it aside and alerts; the next message for the item corrects the count}
idempotency: Each message carries an event ID; ELM-03 ignores IDs it has processed
timing:
  timeout: null
  ordering: Per item, by the warehouse's sequence number; ELM-03 drops a message older than the last one stored
  delivery: At-least-once
versioning: Schema version in the message header; ELM-03 ignores unknown fields
observability: ELM-03 logs the event ID, item, sequence number, and the delay between the event time and storing it, for investigating stale stock (DRV-03)
sli_bindings: []
spec: null                               # the warehouse team owns the document; the report links it
as_is: new
```

`docs/design/dat/DAT-04.yaml`:

```yaml
id: DAT-04
title: Stock level
status: active
basis: inferred
basis_note: null
premises: []
entity: Stock level
owner: ELM-03
store: ELM-04
key_attributes: [item_id, available_count, warehouse_sequence, changed_at]
relations:
  - {to: DAT-05, kind: one-to-one, note: Catalog item}
consistency: Written only by ELM-03, from IFC-03. ELM-02 never changes it; reservations are a separate entity that ELM-02 owns (DAT-06), and the stock offered to buyers is this count minus the active reservations. ELM-02 reads this table directly, with read-only rights (DEC-11), so the table is part of ELM-03's interface and changes only with a new version
retention: The current value only; history is not kept
classification: internal
drivers: [DRV-03]
sli_bindings: []
as_is: new
```
