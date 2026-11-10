# Review procedures

## Contents
- Rules for every review
- Stage 2: architecture
- Stage 3: high-level design
- Stage 4: detailed design
- Every stage
- Risks, non-risks, sensitive points and trade-offs

## Rules for every review

- Work from the artifacts. What is not written down does not exist; when it matters, that is a finding.
- Every activity has a result: what you computed, traced or walked, and what it showed. Record the activities that found nothing too.
- Quote the evidence with IDs and numbers. Compute with a script when there is arithmetic.
- Address each finding to the skill that owns its cause, and give it a severity as `artifacts.md` defines.
- Check the stage against its own exit criteria as well; an unmet exit criterion is a finding.

## Stage 2: architecture

| # | Activity | Result to record |
|---|---|---|
| A1 | Walk each primary driver's scenario through the design: where the stimulus enters, which elements and decisions shape the response, whether the response can meet the measure | Per driver: risks, non-risks, sensitive points, trade-offs |
| A2 | Walk each CUJ, step by step, through the elements and their interactions | Per step: the elements, the interactions, any gap |
| A3 | Answer four questions, with evidence: Is the design fit for its use (the CUJs and the drivers)? Will it hold up over its life and its planned changes (the change scenarios, the debts)? Can this team build and run it by the deadline and within the budget, and is it worth its cost? Is it clear to those who will build, use and maintain it? | One short paragraph each |
| A4 | Check every decision: real options, a rationale tied to drivers, rejected options with reasons, gains and costs, constraints respected | The decisions that fall short, and how |
| A5 | Check the views against the consistency rules of stage 2 | Each rule: holds, or where it fails |
| A6 | Check the allocation: every FR to a component, every driver to elements, every component to a team when teams are given | Gaps |
| A7 | Check the threat model: every flow that crosses a trust boundary, walked for the six kinds of threat | Flows or threats not covered |
| A8 | Check the eight design concerns: each settled by a decision, or set aside with a reason that holds | Concerns with a weak reason |
| A9 | Check debts and deferrals: each debt has its condition to repay; each deferral of a point of stage 2's full-depth kinds, or of one that rates high, is a hand-off with its trigger | Missing conditions |
| A10 | Check the fit with the teams: components that most change scenarios make two teams change together | The pairs found |
| A11 | Check the design inputs and platforms: every DIN in the quality chain's `context.yaml` is a technology constraint in `design-context.yaml`, or set aside with a reason in stage 1's report; the platforms (operating systems, browsers and their versions, native or web) are decided, by a technology constraint or a stage 2 decision, for every kind of device the contexts of use name | DINs neither taken in nor set aside; kinds of device with no platform decided |

A DIN that stage 1 neither took in nor set aside is a finding addressed to `requirements-to-architecture-drivers`. A platform that nothing decides is a finding addressed to `architecture-drivers-to-architecture`.

## Stage 3: high-level design

| # | Activity | Result to record |
|---|---|---|
| B1 | Trace every acceptance criterion of every allocated FR through the IFCs and flows | The criteria that cannot be traced |
| B2 | Recompute every latency budget with a script: the normal path, counting only the time that the SLI's binding observes, with each serial hop at its share of the SLO's tail; each failure path's duration and the number of valid events that take it, against the error budget volume | The normal path's sum against the threshold; each failure path's share of the error budget |
| B3 | Check every IFC's error contract: every case has a signal and says what the caller does; retries only on idempotent operations; a timeout on a call that changes something is an unknown outcome, settled with the same party before any other is tried; "nothing happened" is said only when every party asked has confirmed it | Gaps; unsafe retries; unknown outcomes reported as failures |
| B4 | Check every timeout: above its dependency's slowest healthy response, within the caller's remaining time, and below the caller's own timeout with settlement included; no SLO threshold used as a timeout | Timeouts that cut healthy calls; callers that give up on running work |
| B5 | Check every event IFC: delivery guarantee, duplicate handling, ordering key, versioning | Gaps |
| B6 | Check every DAT: one writer; every reader goes through the owner's interface, a copy fed by the owner's events, or a recorded read-only decision; a consistency rule, a retention period, a classification | Second writers; unrecorded readers; missing rules |
| B7 | Check the SLI bindings: every SLI of the quality chain has an `sli_bindings` entry on an IFC or a DAT; the bound events are the SLI's unit event, observed at its vantage, from the environment and traffic its `applicability` names and where its `lifecycle` says it is measured; the fields carry what its VALID and GOOD definitions, exclusions and counting rules need; the method names a source that exists (the SLI's `existing_source`, or one the design provides); nothing in the binding changes what the SLI counts | SLIs without a binding; bindings that observe another event or from another vantage, or count by other rules; missing fields |
| B8 | Check that every IFC and every spec follows the shared conventions | Deviations |
| B9 | Check every state diagram across elements: every state has a way out; timeouts and cancellations are present; no state that money, goods or a booking can still leave is final | Dead ends; final states that hide an unknown outcome |
| B10 | Compare the specs with the IFC items: same operations, errors and schemas | Mismatches |

An SLI that no design within the constraints can bind as defined (its unit event cannot be seen from its vantage, or a counting rule is ambiguous) is an issue for the quality chain, not a finding.

## Stage 4: detailed design

| # | Activity | Result to record |
|---|---|---|
| C1 | Check the allocation: every acceptance criterion of the component goes to a module; each operation of an IFC the component provides or consumes has exactly one module in it, since each operation has exactly one module in each component that takes part in it; every event and field that the `sli_bindings` on its IFCs and DATs need it to produce goes to a module | Gaps; operations with two modules in the component |
| C2 | Check every module: one responsibility, contracts with errors, behaviour, data structures, a verification approach | Missing parts |
| C3 | Check every state diagram: every event defined in every state; a final state or a named wait reachable from each state; every timeout on a call that changes something leads to a state that settles it | Undefined events; dead ends; timeouts that skip settlement |
| C4 | Check every decision table: count the combinations; every one covered once | Missing or overlapping rows |
| C5 | Check the module dependencies: no cycles, direction toward stable modules, a CI rule written down | Cycles; inversions |
| C6 | Check concurrency and idempotency: shared state; what must be atomic; money movement that stays idempotent with a duplicate arriving while the first request runs, with a key reused for a different request, and with failover after an unknown outcome | Races; double effects |
| C7 | Check the data: every query has its index; constraints match the contracts; migrations keep the running version working | Missing indexes; mismatches |
| C8 | Check that the design parameters fit the stage 3 budgets and timeouts, and that the component sets no timeout or wait on a call to another element: those are in the IFCs' `timing`, referred to by IFC ID | Overruns; timeouts or waits set in the component that belong to an IFC |
| C9 | Check verifiability: every criterion and contract has a verification approach | Items that cannot be verified |
| C10 | Check the component against the shared conventions: errors, IDs, time, money, logs | Deviations |

## Every stage

Do these in every review, after the stage's own activities. They check what the protocol in `conventions.md` leaves in the items: findings, premises, assumptions, decisions, traces, and the points that the quality chain leaves for the design to confirm.

| # | Activity | Result to record |
|---|---|---|
| E1 | Read every finding in `fnd/`, whatever its status, that targets items in scope or whose `raised_in` is this report's path: an accepted one has its change in the items, cited in their `basis_note`; a rejected one is not raised again unless its inputs changed; an open one that still holds is listed again in the report, not written twice | Accepted findings whose change is missing; the findings not raised again, and why |
| E2 | Check the premises: every item in scope that relies on an assumption (as its text or its `assumptions` shows) lists it in `premises`; an item whose `premises` include an open DAS, or an open QAS that no design question has answered, has `basis: assumed`; an item that rests on a QAS that a design question answered cites the answer in `basis_note`; every item marked `assumed` lists such a DAS or QAS in `premises`; every ID in `premises` exists | Items with a missing premise or the wrong basis; IDs that do not exist |
| E3 | Re-rate every open DAS and QAS that the items in scope or the findings depend on, as `conventions.md` describes ("Draft first, ask afterwards"): breadth from the structure, now that later stages may depend on it too, and severity from the harm if it is wrong. Update each DAS's `breadth`, `severity` and `rating_note` in place; a QAS file is never written, so its ratings show only in the report. Ask in this run about each one that now rates high on either scale | Per assumption: its ratings now; those high on either scale, and the question that asked each, or the finding raised when no answer could be had |
| E4 | Check the business decisions in the items in scope (provisional design parameters; decisions that accept a risk, a cost in money or contracts, a weaker driver or a debt; deferrals of points of the stage's full-depth kinds, or of points that rate high; the stage's rejections of findings that leave a risk in place): each was asked and is under "Decisions" in the stage's report, or is a DAS of `kind: decision` that the items depending on it name in `premises`. Every decision lists its costs; that alone does not make it a business decision, nor does handing off any other point | Business decisions that nobody decided and no DAS records |
| E5 | Look for quality-chain statements copied into design items instead of traced by ID: the wording of a statement, an acceptance criterion or an SLI definition, or the value of a shared fact (CON, EXT, OPF), written as the item's own text | The copies found |
| E6 | Check the points that quality-chain items leave for the design to confirm (in their `basis_note`), which stage 1 turns into drivers, constraints, questions, DAS or hand-offs to the stage that designs the part: every point addressed to the stage under review or an earlier one is confirmed by the stage it is addressed to, cited in the `basis_note` of the item that confirms it, passed on to a later stage, or raised as an issue for the quality chain | Points neither confirmed, passed on nor raised, with the stage each is addressed to |

- E1: An open finding that no longer holds is said so in the result, for the addressed stage to settle, and is not listed again. To tell whether a rejected finding's inputs changed, diff the items it names since the commit that rejected it (`git log -1 --format=%h -- docs/design/fnd/FND-07.yaml`, then `git diff <commit> -- <files>`).
- E2: An item still marked `assumed` because its stage has not run since its assumptions were answered is not a finding: the stage applies the answers when it runs ("Assumptions" in `conventions.md`). Name the stage to re-run in the result.
- E3: An assumption whose breadth or severity is high after re-rating is asked in this run, whichever stage wrote it ("Assumptions" in `conventions.md`): record the question and its answer under "Decisions", write the answer in the DAS (`answer`, `answered_in`) and set its status; for a QAS, record the answer under "Issues for the quality chain" as well. If the answer overturns it, tell the user to re-run the stage that wrote it and the stages whose items depend on it. Only when the review cannot get an answer, write a finding instead: for a DAS, addressed to the stage that wrote it (its `stage`), suggesting that it ask on its next run; for a QAS, addressed to the stage under review.
- E5: A short label next to the ID is not a copy, nor is a number used in a calculation with its source. A copy that already differs from its source is a contradiction (major); one that still matches is minor.
- E6: A point addressed to the stage under review, or to an earlier design stage, that it neither confirmed, passed on nor raised as an issue is a finding addressed to that stage. A point that stage 1 turned into none of a driver, a constraint, a question, a DAS or a hand-off is a finding addressed to `requirements-to-architecture-drivers`. A point addressed to a later stage is not a finding yet.

## Risks, non-risks, sensitive points and trade-offs

- A risk is a decision, or a missing one, that may keep a driver's response from meeting its measure.
- A non-risk is a decision that was checked and holds, with the reason. Recording non-risks shows what was checked.
- A sensitive point is a property the response depends on strongly: a threshold, a timeout, a number of instances.
- A trade-off is a property that helps one driver and hurts another.

Every risk becomes a finding. A sensitive point with no design parameter written for it, and a trade-off recorded on only one of its drivers, are findings too: minor, unless they hide a risk.
