# Interfaces

## Contents
- What every interface specifies
- By kind
- Error contracts
- Idempotency and retries
- Unknown outcomes
- Timing
- Versioning
- SLI bindings
- Specs

## What every interface specifies

| Field | Says |
|---|---|
| provider, consumers | Which element offers it, which elements use it; for a screen, the users (USR IDs) who use it |
| functions | The FRs whose acceptance criteria pass through it |
| operations | HTTP: method and path. Event: message name. File or batch: the file or the job. Screen: the screen |
| format | JSON, CSV, a binary format; the character encoding where it matters |
| protocol | HTTPS request and response, a message broker, a file transfer, a browser |
| auth | Who may call it, and how that is proven |
| errors | Every error case, how it is signalled, and what the caller does |
| idempotency | Whether the operation can be repeated safely, and how |
| timing | Every timeout and wait on the call, settlement waits included; ordering guarantee; delivery guarantee ("Timing") |
| versioning | How the interface changes without breaking its consumers |
| observability | What it logs and emits for investigations and operations |
| sli_bindings | For each quality-chain SLI whose events it produces: which events, the fields the counting rules need, and the method ("SLI bindings") |
| spec | The OpenAPI or AsyncAPI document |

An FR names an interface by its kind and, for an external system, its EXT ID (`interface: ["screen: buyer checkout", EXT-01]`). Everything in this table is decided here, with one exception: an FR may name the endpoint of an interface that already exists in a running product. That endpoint is a fact about the current system, not a design input and not an issue for the quality chain; the IFC keeps it (`as_is: keep`) unless a decision changes it.

## By kind

| Kind | Also specify |
|---|---|
| http | Resource paths and methods; request and response schemas; status codes; paging for lists; rate limits |
| event | The channel or topic; the message schema; who publishes and who subscribes; the ordering key; the delivery guarantee; how consumers recognize duplicates; how long messages are kept |
| file | The name pattern; layout and encoding; who writes it and when; how the reader knows it is complete; what happens to a malformed file |
| screen | Its purpose in the CUJ step; the data it shows and takes; its actions and where each leads; error and empty states |
| batch | The schedule or trigger; input and output; how a failed run restarts; how long a run may take (from the NFRs) |

A component's access to its own data store is not an interface; stage 4 designs it. When another component reads that store directly, the tables it reads become part of the owner's interface ("Ownership" in `data-and-conventions.md`).

For an external system, write the interface as what the design relies on (operations, errors, the timeouts and waits of our calls to it). What the system promises (an SLA, a rate limit, a stated latency) is a technology constraint: cite it by the ID of the TC that records it, or of the OPF in `context.yaml` that states it, and never restate it (`conventions.md`, "Scope"). What the design assumes beyond that is a DAS. List its EXT ID from `context.yaml` in `premises`, with those TC, OPF and DAS IDs. Do not write a spec for it; link the owner's.

## Error contracts

For each operation, list every error case the caller must handle differently:

| Group | Typical signal | The caller |
|---|---|---|
| The request is wrong | 400, 422 | Fixes the request; never resends it unchanged |
| Not signed in, or not allowed | 401, 403 | Signs in again, or stops |
| The thing does not exist | 404 | Stops, or refreshes what it shows |
| The current state forbids it | 409 | Reloads and decides again |
| Too many requests | 429, with a time to wait | Waits as told |
| A dependency failed | 502, 503, 504 | Retries only if the operation is idempotent; otherwise checks the outcome first |
| The outcome is not known yet | 202, with a status to poll | Polls; never repeats the request with a new key |
| A business refusal (card declined, out of stock) | A specific code with a reason | Shows the reason, and offers what the CUJ allows next |

Every interface uses the one error format of the shared conventions: a stable code for programs, a message for people, the request ID.

## Idempotency and retries

- Reads are safe to repeat.
- For each operation that changes state, decide: naturally idempotent (setting a value); made idempotent by a key the caller supplies; or not idempotent, in which case the caller never retries blindly and checks the outcome instead.
- Scope the key by what must happen once: one key per order for a payment, not one per attempt. The caller reuses the key on every retry.
- A request whose key belongs to a request still running gets "in progress" (409) or waits for the first result; it never starts a second run.
- A key reused with a different request gets an error (422); it never returns the first result for a different request.
- Operations that move money are always made idempotent.
- Retries happen in one place on each call path, with back-off and a limit. Retries at several layers multiply each other.

## Unknown outcomes

A timeout, a dropped connection or an unclear error on a call that changes something (a charge, a booking, a dispatch) leaves the outcome unknown: the other side may have done it, may still be doing it, or may not have started.

- Never report an unknown outcome as a failure. Say "nothing was charged" only when every party that was asked has confirmed it.
- Settle it with the same party before trying another one: look the request up by its key, and cancel it there if it went through or is still running. Some providers separate authorization from capture, which makes cancelling cheap.
- If it cannot be settled within a set time, hold the record in its own "unknown" state, tell the caller that the outcome is pending, and let reconciliation settle it. Draw that state and its ways out.
- A key is known only to the party that received it. A second provider does not know the first provider's key, so failing over a charge without settling the first one can charge twice.

## Timing

- A timeout is not a budget. The latency budget checks that the flow is fast enough when things are healthy; timeouts decide what happens when they are not.
- This stage owns every timeout and wait on a call that crosses an element boundary, settlement waits included (how long the caller tries to settle an unknown outcome with the same party before it holds the record for reconciliation). Write them in the IFC's `timing`, so that the worst case each caller waits for is computed here, and back each provisional value with a DAS of `kind: decision` or an answered question. Stage 4 sets only the values inside one component, refers to the IFC's timing by its ID, and raises a finding addressed to this stage when it needs a change. A component's access to its own data store is not an interface; stage 4 sets those timeouts.
- Set each call's timeout above the slowest response the dependency gives when healthy (its stated 99.9th percentile, or its stated maximum), so that healthy calls almost never time out. On a call that changes something, every timeout creates an unknown outcome.
- Set each caller's timeout above the worst case of everything it waits for, settlement included, so that no caller abandons work that is still running. Each callee's own timeouts stay within its caller's remaining time.
- Never use an SLO's threshold as a timeout.
- Each timeout, retry limit and back-off is a design parameter, and so a decision ("Decisions" in `conventions.md`). Say what it is based on: the dependency's stated percentile, the worst case it must cover, a library's default. Most are low or medium on both scales and are recorded as a DAS of `kind: decision`; the item that holds the value lists the DAS in `premises`. Values that hinge on the same fact share one DAS, whose statement names them and leaves their values in the IFCs.
- Ordering: for events, say whether order matters and, if so, per which key (per order, per vehicle). Order across all events is rarely needed and is expensive.
- Delivery: at-least-once with consumers that recognize duplicates is the usual choice. Say how duplicates are recognized (an event ID).

## Versioning

- Additive changes (a new optional field, a new operation) keep the version.
- A breaking change needs a new version, run alongside the old one until every consumer has moved.
- Consumers ignore fields they do not know.
- Events carry their schema version in the message.

## SLI bindings

The quality chain defines each SLI in the terms of the domain: its unit event (one checkout submitted by a buyer), its vantage (where the events are observed: `user-side`, `system-boundary`, `synthetic` or `data`, with the reason in `vantage_reason`), its counting rules (the definitions of its elements, their exclusions and `counting_rule`), its `applicability` (the environment and traffic in which its value holds) and `lifecycle` (where it is measured), and, when telemetry already exists, `existing_source` (an OPF ID). It does not say which interface, log or field carries the events. That is decided here, in `sli_bindings`:

| Field | Says |
|---|---|
| sli | The SLI's ID |
| events | Which events of this interface (or records of this entity) are the SLI's unit events, and where they are observed |
| fields | What the counting rules need: the outcome, the time taken, what tells excluded traffic and traffic outside the SLI's applicability apart, what makes a repeated event count once |
| method | How the events are collected: an existing log, a new log line or event, a beacon from the person's device, a probe, a query on stored data |

Write the binding on the IFC that produces the events, or on the DAT for an SLI whose vantage is `data` ("Data quality flows and data SLIs" in `data-and-conventions.md`). Usually one interface produces all of an SLI's events; when several do (every screen of a CUJ), bind the SLI on each of them, so that together they yield every unit event once. When the fields come from more than one source (the load balancer's log and an event of the service), the method says how they are joined, for example by the request ID.

A binding decides where and how the events are observed, never what is counted:

- Keep the unit event. When the SLI counts checkouts, a checkout submitted again is one event, even though it reaches the system as two requests; the fields must carry what joins them.
- Keep the vantage:
  - `user-side`: observed on the person's device, such as a timing the page reports when the result is shown. A binding at the server does not realize it: the server misses the time on the device and the network, and the requests that never arrive.
  - `system-boundary`: observed where requests enter the system, before any of its own processing: the load balancer or gateway in front of the first component.
  - `synthetic`: a probe that acts as a person would, on a schedule. Say where it runs, how often and what it does, and mark its traffic so that the other SLIs can exclude it.
  - `data`: observed in the data that the SLI's target entity is about: which timestamps or attributes, compared with what. When people see a copy (a cache, a search index), observe the copy, not only the store that feeds it.
- Keep the counting rules. Every definition, exclusion and counting rule must be computable from the fields.
- Keep the applicability and the lifecycle. Bind only events of the environment and traffic that `applicability` names ("production, normal traffic"), collected where `lifecycle` says the SLI is measured. Events of other environments or traffic (staging, load tests, synthetic checks that a separate SLI counts) stay out, through where the binding collects or through a field that tells them apart; load-test values are estimates and never feed the SLI.

When the vantage cannot be realized (the system cannot reach the person's devices), or the design would like the same events observed from a second place, do not move the vantage or add one in the binding: a second vantage is a second SLI. Write an issue for the quality chain, as for a counting rule that nothing the system can observe would compute.

Where the events come from:

- When the SLI has an `existing_source`, bind to that telemetry, list the OPF in the item's `premises`, and add only the fields it lacks.
- When nothing produces the events, design it here: the log line, the event or the probe, the element that emits it, and its fields. Follow the shared conventions for logs; personal and payment data never go into the fields unmasked.
- When producing them needs a new behaviour of the system, something no FR provides (the system never learns that a parcel was delivered), write an issue for the quality chain and do not add the behaviour. Telemetry that people do not see (a log line, a timing beacon, a probe) is design, and is added here.

## Specs

Write the decided parts only, and mark provisional values, with the DAS that records each one.

- OpenAPI, for each HTTP interface: paths and methods; request and response schemas with required fields and formats; every error response, using the shared error schema; the security scheme; the idempotency header where it applies.
- AsyncAPI, for each event interface this system publishes or defines: channels; messages with their payload schemas and headers (event ID, schema version, the time the event happened); who publishes and who subscribes; the delivery and ordering notes from the IFC.

Name each file after its interface (`checkout.openapi.yaml`, `order-events.asyncapi.yaml`) and keep one document per interface, so that each can change on its own. For an external system's interface, link the owner's document instead of writing one.
