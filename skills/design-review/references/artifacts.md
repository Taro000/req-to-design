# Artifacts

## Contents
- Layout
- Common fields
- design-context.yaml (stage 1)
- DRV: architecture driver (stage 1)
- DEC: design decision (stages 2 to 4)
- ELM: element (stage 2)
- IFC: interface (stage 3)
- DAT: data entity (stage 3)
- MOD: module (stage 4)
- HND: hand-off (stages 1 to 4)
- FND: finding (stages 2 to 4 and the review)
- DAS: assumption (every stage and the review)
- The detailed design index (stage 4)

## Layout

All design skills write under `docs/design/`, unless the project already keeps its design somewhere else. In that case, use that location and say so in the report. The quality chain's `docs/quality/` is read only.

```
docs/design/
├── 1-architecture-drivers.md          stage 1 report
├── 2-architecture.md                  stage 2 report, views included
├── 3-high-level-design.md             stage 3 report, flows included
├── 4-detailed-design.md               stage 4 index: every component and its status
├── 4-detailed-design/ELM-02.md        stage 4 report, one per component
├── reviews/3-high-level-design.md     review report, one per reviewed stage (stage 4: per component, reviews/4-detailed-design-ELM-02.md): the latest review
├── design-context.yaml                the design context: constraints, teams, changes, stakeholders, current structure
├── drv/DRV-01.yaml …                  stage 1: architecture drivers
├── dec/DEC-01.yaml …                  stages 2–4: design decisions
├── elm/ELM-01.yaml …                  stage 2: elements
├── ifc/IFC-01.yaml …                  stage 3: interfaces
├── ifc/specs/checkout.openapi.yaml    stage 3: OpenAPI and AsyncAPI documents
├── dat/DAT-01.yaml …                  stage 3: data entities
├── mod/MOD-01.yaml …                  stage 4: modules
├── hnd/HND-01.yaml …                  stages 1–4: hand-offs, the points a stage leaves to a later stage or to implementation
├── fnd/FND-01.yaml …                  stages 2–4 and the review: findings
└── das/DAS-01.yaml …                  every stage and the review: assumptions made without asking
```

- One item per file. The file name is the ID: `dec/DEC-07.yaml`.
- IDs are the prefix plus a zero-padded number (`DEC-07`, then `DEC-100` when needed). Never reuse or renumber an ID.
- Write every ID in full wherever you cite it, in lists inside a text too ("FND-30, FND-31", not "FND-30, 31" or "FND-30・31"). The scripts find a citation by its full ID only.
- The YAML items are the source of truth. A report summarizes and indexes them and never restates what an item says; it holds what only the report records (views, flows, walkthroughs, budgets, reasons, decisions, issues for the quality chain). Its index tables are written from the items by `scripts/tables.py` ("Scripts" in `conventions.md`). The items are written while the stage drafts, and answers change them in place. If the report and an item disagree, ask which one is right; do not silently pick one.
- Items hold the current state only: no changelog, no version, no dates of changes. Git keeps the history (`conventions.md`, "Current state only").
- `design-context.yaml` holds the design context that the other items refer to. Stage 1 writes it; later stages and reviews only add facts the user gives them (`conventions.md`, "Judgment basis"). It is the only file that holds more than one entry.
- Views, flows, state diagrams and decision tables live in the reports, as Mermaid diagrams and tables. Items refer to them by the report's section heading.
- Keep the YAML valid. Quote a free-text value when it contains `: ` or ` #`, or starts with one of `[ { * & ! | > ' " % @` or a backtick, and quote any value inside `[ ]` or `{ }` that contains a comma or `: `. Cite decisions and questions without `#` ("decision 12", "design stage 3, decision 4"): an unquoted ` #` starts a comment and silently cuts off the rest of the value.
- The comments in the schemas below explain the fields; do not copy them into the items. In an item, a comment after an unquoted value is reported as a value cut off at ` #`.

## Common fields

Every item file except `design-context.yaml` and the assumption files (DAS, which have their own fields) has these fields, first:

```yaml
id: DEC-07
title: Short name, in the working language
status: active             # active | retired   (HND: open | decided | retired; FND: open | accepted | rejected; DAS: open | confirmed | overturned | retired)
basis: inferred            # stated | inferred | assumed | confirmed: the weakest basis of the judgments in the item
basis_note: null           # which parts are stated, inferred, assumed or confirmed, when they differ; findings accepted and hand-offs decided
premises: []               # what the item depends on that could change under it: TC, PC, TEAM, CHG, STK, DAS, and the quality chain's CON, EXT, OPF, QAS
# ... the fields of the item type ...
```

An item whose `premises` include an open DAS, or an open QAS that no design question has answered, has `basis: assumed`.

Every item that describes part of the system also has `as_is: keep | change | new | remove` (see "Existing systems" in `conventions.md`). In a system with no code, it is always `new`.

The examples below follow one fictional online store through all the stages.

## design-context.yaml (stage 1)

```yaml
read_from:
  quality_chain: docs/quality/           # null when the user gave the requirements directly
  other: [Architecture notes (wiki), Roadmap 2026, Kick-off notes, Security team memo]
technology_constraints:
  - id: TC-01
    statement: Card payments go through the payment provider's API; card numbers never reach our servers
    kind: external-service               # mandated | prohibited | platform | external-service
    source: context.yaml CON-01; security team memo
    basis: stated
  - id: TC-02
    statement: Runs in the company's existing cloud account, in one region
    kind: platform
    source: Architecture notes
    basis: stated
  - id: TC-03
    statement: The storefront stays a web app this year; no native app
    kind: platform
    source: context.yaml DIN-01                # every design input of the quality chain is taken in as a candidate
    basis: stated
project_constraints:                     # kind: budget | deadline | team | other
  - id: PC-01
    kind: deadline
    statement: First release before the spring sale
    source: Kick-off notes
    basis: stated
  - id: PC-02
    kind: team
    statement: Four developers (TypeScript, PostgreSQL); no dedicated operations engineer
    source: Kick-off notes
    basis: stated
  - id: PC-03
    kind: budget
    statement: Not set until the funding review in March
    source: Stage 1, question 3
    basis: confirmed
teams:
  - {id: TEAM-01, name: Store team, owns: Storefront and checkout and stock, basis: stated}
anticipated_changes:
  - {id: CHG-01, change: Add a second payment provider, expected: Within a year, source: Roadmap 2026, basis: stated}
stakeholders:                            # roles that are not users in context.yaml, but whose concerns the design must meet
  - {id: STK-01, role: Product owner, concerns: [Release date, Running cost], source: Kick-off notes, basis: stated}
as_is:                                   # only when the repository holds code or infrastructure definitions; the online store in these examples has none, so this block only shows the shape
  read: [src/, infra/terraform/]
  not_learned: Production volumes and runtime behaviour
  elements:
    - {name: storefront, kind: component, technology: Next.js, note: Server-rendered pages and the cart}
    - {name: orders-db, kind: data-store, technology: PostgreSQL 15, note: Orders and payments and stock}
  conventions: [REST under /api/v1, "errors as {code, message}"]
```

## DRV: architecture driver (stage 1), `drv/DRV-01.yaml`

```yaml
id: DRV-01
# ... the other common fields ...  (premises: [OPF-03, QAS-08]; QAS-08, the provisional target behind NFR-02, was asked in stage 1, question 6, and is listed under "Issues for the quality chain"; the ranking is a business decision, see "Decisions" in conventions.md)
kind: quality                            # quality | change | constraint | function | observability | security | principle
statement: Checkout confirms orders without keeping buyers waiting, up to sale-peak load
sources: [QR-02, NFR-02, SLI-02]         # quality-chain IDs and design-context IDs (TC, PC, TEAM, CHG, STK)
concern_of: [USR-01]                     # user IDs from context.yaml, stakeholder IDs from design-context.yaml
scenario:                                # quality, change, observability and security drivers; optional for function drivers; null for constraints and principles
  source: Buyers on smartphones (USR-01)
  stimulus: Submit the checkout during a sale
  artifact: Checkout (FR-01)
  environment: Sale peak (OPF-03); normal operation
  response: The order is confirmed and the confirmation page is shown
  measure: NFR-02's SLO, counted by SLI-02     # name the chain's measure by ID; do not copy its statement
negotiable: null                         # constraints and principles: true | false
derived_from: []                         # principles: the drivers a principle serves
priority:                                # every driver except principles
  business: high                         # high | medium | low
  business_reason: QR-02 is emphasized for CUJ-01
  difficulty: high                       # high | medium | low: how hard to achieve, and how hard to undo
  difficulty_reason: The payment provider's latency and its fraud screening both sit inside the 1.5 s
  rank: 1
primary: true                            # primary drivers decide stage 2's first decisions
conflicts:
  - {with: DRV-06, note: Fraud screening adds latency to the same request}
placeholders: []                         # named placeholders from the quality chain, kept as they are
```

A principle is a rule for the whole system that follows from several drivers ("every operation that moves money can be repeated without moving it twice"). It has a `statement`, `derived_from` and `negotiable`, and no scenario and no priority.

## DEC: design decision (stages 2 to 4), `dec/DEC-02.yaml`

```yaml
id: DEC-02
# ... the other common fields ...  (premises: [TC-01, CHG-01, DAS-02])
stage: architecture                      # architecture | high-level-design | detailed-design
question: How does checkout keep confirming orders when the payment provider fails?
addresses: [DRV-02, DRV-10]              # the drivers, interfaces or findings the decision answers, or the FR, QR, NFR or SLI it answers directly
options:
  - name: One provider, retries with back-off
    effect: Rides out short errors; an outage still stops checkout
    cost: Little work
  - name: Fail over to a second provider
    effect: Checkout continues while either provider is down
    cost: A second contract and integration; reconciliation across two providers
chosen: Fail over to a second provider
rationale: DRV-02 asks checkout to continue through a provider outage, which retries cannot do; CHG-01 already plans a second provider
rejected:
  - {option: "One provider, retries with back-off", reason: Does not meet DRV-02 during an outage}
gains: [Checkout survives an outage of either provider]
costs: [A second integration to build and test, Reconciliation must cover two providers]
sensitive_points: [The error threshold that opens a provider's breaker - too low switches back and forth; too high keeps buyers waiting on a failing provider]
trade_offs: [{with: DRV-07, note: A second contract raises running cost}]
assumptions: ["The second provider works like the first: hosted card fields, and fraud screening inside its charge (DAS-02)"]   # what the decision relies on; one you were unsure of and did not ask about is a DAS in premises
depends_on: [DEC-01]
parameters:                              # provisional design values: decisions (see "Numbers" and "Decisions" in conventions.md)
  - {name: failover_after, value: 5 consecutive errors or 10 s of timeouts, basis: "Provisional starting value, answered with the second provider (stage 2, question 2); tune with the providers' error rates"}
debt:                                    # {what, why_accepted, repay_when}; null when the decision accepts none
  what: Failover ships right after the spring sale; until then an outage of the provider stops checkout
  why_accepted: "The business keeps the date and accepts the risk (stage 1, question 5)"
  repay_when: Right after the spring sale
as_is: new
```

What a decision leaves to a later stage, or to an event, is a hand-off (HND) whose `origin` names the decision.

## ELM: element (stage 2), `elm/ELM-02.yaml`

```yaml
id: ELM-02
# ... the other common fields ...
kind: component                          # component | data-store | external-system | node
name: Store API
responsibility: Serves the catalog, cart, checkout and order history; confirms orders and takes payment
functions: [FR-01, FR-03, FR-04]         # FRs allocated to it; [] for nodes
drivers: [DRV-01, DRV-02, DRV-05]        # drivers it carries
decisions: [DEC-01, DEC-02, DEC-04]
team: TEAM-01                            # null when no team structure is given
technology: TypeScript on Node.js (DEC-04)   # null until decided
runs_on: ELM-08                          # the node it is deployed to; null for external systems
depends_on: [ELM-04, ELM-05, ELM-06]
as_is: new
```

For an external system, `responsibility` says what the design assumes it does and `functions` stays empty; what it promises (an SLA, a rate limit) goes in `assumptions` of the decisions that rely on it.

## IFC: interface (stage 3), `ifc/IFC-01.yaml`

```yaml
id: IFC-01
# ... the other common fields ...
kind: http                               # http | event | file | screen | batch
name: Checkout API
provider: ELM-02
consumers: [ELM-01]                      # elements; for a screen, the users (USR IDs) who use it. Here: the storefront's checkout script, running in the buyer's browser
functions: [FR-01]                       # the FRs whose acceptance criteria pass through it
operations:                              # http: method and path; event: message; file and batch: the file or job; screen: the screen
  - {name: POST /v1/checkout, does: Confirms the cart as an order and charges the buyer}
format: JSON
protocol: HTTPS, request and response
auth: Buyer session cookie
errors:                                  # the error contract
  - {case: Card declined, signal: 402 with code CARD_DECLINED, caller_does: Show the decline and keep the cart}
  - {case: No provider could take the payment and every provider tried confirmed that nothing was charged, signal: 503 with code PAYMENT_UNAVAILABLE, caller_does: Ask the buyer to try again later}
  - {case: The outcome of the payment is not settled yet because a provider timed out, signal: 202 with code PAYMENT_PENDING and the order ID, caller_does: Show that the payment is being confirmed and poll the order; never submit again with a new key}
  - {case: The same key while the first request is still running, signal: 409 with code CHECKOUT_IN_PROGRESS, caller_does: Wait and poll the order}
  - {case: The same key with a different cart, signal: 422 with code KEY_REUSED, caller_does: Start a new checkout with a new key}
idempotency: One Idempotency-Key per order - the storefront creates it when the buyer first submits the cart and reuses it on every retry; the same key returns the first result
timing:
  timeout: 15 s (provisional; above the worst case of the payment path, 10.3 s, so that a payment still running is never abandoned; the 1.5 s of NFR-02 is a target, not a timeout)
  ordering: null                         # events: the ordering guarantee and its key
  delivery: null                         # events: at-most-once | at-least-once, and how duplicates are handled
versioning: Version in the path; only additive changes within v1
observability: Logs request_id and outcome in the service, for investigations
sli_bindings:                            # how this interface yields the events of quality-chain SLIs, without changing what the SLI counts
  - sli: SLI-02
    events: Each POST /v1/checkout request that reaches the load balancer in front of ELM-02 (the SLI's vantage is the system boundary); requests with the same Idempotency-Key are one checkout, counted by the first request
    fields: [request_id, idempotency_key, status, elapsed, user_agent]
    method: The load balancer's access logs, which already exist (OPF-02), with the Idempotency-Key header added to the logged fields
spec: ifc/specs/checkout.openapi.yaml    # null for screens, and for interfaces whose spec belongs to an external system
as_is: new
```

## DAT: data entity (stage 3), `dat/DAT-01.yaml`

```yaml
id: DAT-01
# ... the other common fields ...
entity: Order
owner: ELM-02                            # the one element that writes it
store: ELM-04
key_attributes: [order_id, buyer_id, total, payment_state, created_at]
relations:
  - {to: DAT-02, kind: one-to-many, note: Order lines}
  - {to: DAT-03, kind: one-to-many, note: Payment attempts}
consistency: The order and its lines are written in one transaction, as pending; each payment attempt and the order's final state are written in a second transaction once the provider answers
retention: T_order_retention             # a stated period, or a named placeholder listed under "Placeholders" when no input gives one
classification: personal                 # public | internal | personal | payment | other (say which)
drivers: [DRV-05]
sli_bindings: []                         # data SLIs: how this entity yields the SLI's events (which timestamps or attributes), as in IFC
as_is: new
```

## MOD: module (stage 4), `mod/MOD-02.yaml`

```yaml
id: MOD-02
# ... the other common fields ...
component: ELM-02
name: Order total calculator
responsibility: Calculates an order's total from its lines, shipping, coupons and points
visibility: internal                     # public: other components call it through an IFC | internal: only modules of the same component call it
interface:
  - operation: "calculateTotal(order: OrderDraft) -> Money"
    pre: Every line has a positive quantity and a price
    post: The total is the sum of the lines plus shipping, minus discounts, and never below zero
    errors: ["CouponExpired: the coupon was valid when added and has expired since"]
invariants: []                           # what always holds for the module's state; [] when it holds no state
depends_on: [MOD-05]
functions: [FR-03]
realizes: []                             # the IFC operations this module implements, each as the IFC ID and the operation's name ("IFC-01 POST /v1/checkout"); each operation has exactly one module in each component that takes part in it (MOD-01 realizes IFC-01 in ELM-02)
drivers: [DRV-04]
decisions: [DEC-14]
behaviour: "Report section: MOD-02 Order total calculator"   # where its states, decision tables and algorithms are drawn
verification:
  - {checks: "FR-03, criteria 1 to 3", how: Unit tests generated from the decision table}
parameters: []
as_is: new
```

## HND: hand-off (stages 1 to 4), `hnd/HND-01.yaml`

A stage decides each point at one of three depths: full (every detail), bounds (only the promise later stages keep) or hand-off (none of it) (`conventions.md`, "Decision depth"). A hand-off carries one point that a stage defers, whole or in its detail, to the stage that will decide it or to implementation ("Hand-offs" there). The stage that writes it owns `what`, `bounds` and `origin`; the stage it is addressed to records `status`, `to`, `component`, `trigger` and `resolution` as it takes it up.

A point that a quality-chain item leaves for the design to confirm, which stage 1 hands to the stage that designs the part:

```yaml
id: HND-01
title: Where the time of a stock change at the warehouse can be read
status: decided                          # open | decided | retired
basis: inferred
basis_note: The point is stated in SLI-03's basis_note; the stage it goes to is inferred
premises: [EXT-02]
from: requirements-to-architecture-drivers   # the skill that wrote it
to: architecture-to-high-level-design    # the skill that decides it, or implementation; a stage that passes it on changes it
component: null                          # for a hand-off to stage 4 or to implementation: the component (ELM ID) it concerns
origin: [SLI-03]                         # the items the point comes from; for stage 1, the quality-chain item that leaves it to the design
what: Whether the store learns when each stock count changed at the warehouse, so that SLI-03 can compare that time with the time buyers see the change
bounds: SLI-03's unit event and counting rules, unchanged; DRV-03   # what the decision must keep, by the IDs of the items that set it
trigger: The next run of stage 3         # that stage's next run, its run for a component, the implementation of a named part, or an event outside the chain (a measurement in operation, a signed contract, a date)
resolution: "Confirmed in DAT-04: changed_at keeps the time of the change, which IFC-03's messages carry"   # written by the stage that takes it up: the items that decide it, or why it passed it on
```

A detail that stage 4 leaves to implementation, inside a module it designs in full:

```yaml
id: HND-02
title: Where the coupon rules are kept
status: open                             # a hand-off to implementation stays open: the code and its tests decide it
basis: inferred
basis_note: null
premises: []
from: high-level-design-to-detailed-design
to: implementation
component: ELM-02
origin: [MOD-05]
what: Where the coupon rules are kept (a table, a file or code) and how MOD-05 reads them
bounds: MOD-05's interface, and the decision table in its report section
trigger: When MOD-05 is implemented
resolution: null
```

## FND: finding (stages 2 to 4 and the review), `fnd/FND-01.yaml`

```yaml
id: FND-01
title: Failover after a timeout can charge the buyer twice
status: open                             # open | accepted | rejected; a rejection that leaves a risk in place is a decision
basis: inferred
basis_note: null
premises: []
raised_by: design-review                 # or the stage skill that found it
raised_in: reviews/3-high-level-design.md
to: architecture-to-high-level-design    # the skill that must decide
targets: [IFC-02]
severity: critical                       # critical | major | minor
evidence: The checkout flow sends the charge to provider B as soon as provider A times out. A may still complete its charge, and A's idempotency key does not cover B, so the buyer can be charged twice (DRV-05)
suggestion: Treat A's timeout as an unknown outcome and settle it at A (look up the key and cancel it if found) before charging B; if A cannot be settled within payment_wait, keep the order pending for reconciliation and tell the buyer the payment is being confirmed
resolution: null                         # written by the addressed stage: what changed, or why the finding is rejected
```

Severity:

- `critical`: a primary driver, a non-negotiable constraint or principle, or a CUJ cannot be met as designed.
- `major`: a driver, a function or an interface is met only in part, or two items contradict each other.
- `minor`: a detail is unclear, inconsistent or incomplete, and nothing fails because of it.

## DAS: assumption (every stage and the review), `das/DAS-02.yaml`

One judgment made without asking, because neither of its ratings was high (`conventions.md`, "Draft first, ask afterwards"). The items that depend on it list it in `premises`.

```yaml
id: DAS-02
title: The second payment provider works like the first
status: open                             # open | confirmed | overturned | retired
stage: 2                                 # 1 | 2 | 3 | 4 | review-2 | review-3 | review-4: the stage, or the review of a stage, that wrote it
kind: judgment                           # judgment | decision (a business decision adopted provisionally, such as a design parameter)
statement: The second provider offers hosted card fields, so card numbers still never reach our servers (TC-01), and screens for fraud inside its charge, as the first does (DRV-06)
why_unsure: CHG-01 names a second provider but not which one; most providers offer hosted fields, not all
breadth: medium                          # high | medium | low
severity: low                            # high | medium | low
rating_note: A few items of stages 2 and 3 depend on it; checked when the provider is chosen, before any of it is built
answer: null                             # the user's answer, when someone asked about it later
answered_in: null                        # where, e.g. "stage 3, question 4" or "review of stage 3, question 2"
```

## The detailed design index (stage 4), `docs/design/4-detailed-design.md`

Stage 4 keeps one row per element of kind `component`. The tables of a data store are designed by the components that own the entities stored in it; external systems and nodes get no detailed design. `scripts/tables.py` writes the table from the elements, the component reports and the modules.

```markdown
# Detailed design index: <system name>

Updated: <date> · Inputs as of: <commit, or "none">

<!-- generated: components -->
| Component | Name | Status | Report | Modules |
|---|---|---|---|---|
| ELM-01 | Storefront | not started | — | — |
| ELM-02 | Store API | answers applied | 4-detailed-design/ELM-02.md | MOD-01 to MOD-10 |
| ELM-03 | Stock sync worker | not started | — | — |
<!-- /generated -->
```

Status: `not started` when the component has no report, otherwise the status in its report's header (`draft`, `waiting for answers` or `answers applied`), written with the glossary's terms in the working language.
