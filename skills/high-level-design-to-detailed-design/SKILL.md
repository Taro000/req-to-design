---
name: high-level-design-to-detailed-design
description: Stage 4 of 4 in the design chain. Designs the inside of one component of the high-level design from architecture-to-high-level-design, far enough that a developer or a coding agent can implement it with no design decision left - modules with one responsibility each, their dependencies, frameworks, contracts (preconditions, postconditions, invariants, errors) in a language-neutral notation, state diagrams, decision tables, algorithms, concurrency, error handling, the physical data model, caches, screens, a verification approach per module, and provisional design parameters. Every component gets the same depth, and an index tracks their status. Writes documents only, never code. Drafts first, then asks only about points of high breadth or severity and records the rest as assumptions. Use it when someone wants a detailed design, module design, a database schema, state machines or decision tables for a component whose interfaces are designed. Review it with design-review.
license: MIT
metadata:
  version: "0.2.0"
---

# High-level design → detailed design

Stage 4, the last stage of the design chain. It takes one component (or a few, when they are small and closely related) from the high-level design and designs its inside: modules (MOD), their interfaces and behaviour, the data structures, and how each module will be verified. Run it once per component; the index `docs/design/4-detailed-design.md` tracks which components are done.

Detailed design ends where coding starts. The test: a developer, or a coding agent, could implement the component from it without making a design decision, and a reviewer could check the code against it. Every component gets the same depth. A component that looks simple still gets its modules, contracts, states and data written down, because "simple" is where unstated assumptions hide.

This stage writes documents, not code. Interfaces are written in a language-neutral notation, so that the design survives a change of language or framework.

## Read first

- `references/conventions.md`: the design chain, findings, the working language, judgment basis marks, the question protocol, decisions, assumptions, re-runs and how a run finishes. Follow it exactly.
- `references/artifacts.md`: where files go, the schemas for MOD, DEC, FND and DAS, and the detailed design index.
- `references/modules.md`: splitting a component into modules, dependencies, frameworks, contracts and allocation.
- `references/behaviour-and-data.md`: states, decision tables, algorithms, concurrency, error handling, physical data, caches, screens and the verification approach.
- `references/report-template.md`: the component report, the index, and a worked example.
- `references/glossary.md`: terms for the working language.

## Inputs

- The component or components to design, named by their element IDs. If the user does not name them, ask, offering the components the index shows as not started.
- `docs/design/`: the element (`elm/`), its interfaces (`ifc/` and `ifc/specs/`), its data entities (`dat/`), the decisions that bind it (`dec/`), the drivers it carries (`drv/`), the shared conventions, read from the DEC items that record them (the "Shared conventions" table of `3-high-level-design.md` lists them), the points that stage 1's report (`1-architecture-drivers.md`) addresses to this stage under "Open gaps", and the index.
- `docs/quality/`, read only: the FRs allocated to the component, with their acceptance criteria; the QRs behind its drivers, internal quality included; and the SLIs that its interfaces and data entities bind (`sli_bindings`), for the events and fields the component must produce.
- The open assumptions in the `premises` of the items you read: DAS under `docs/design/das/`, and the quality chain's QAS.
- Open findings addressed to this stage for this component.
- The component's existing code, as recorded under `as_is`: read the parts being designed in full.

Essential input: the IFCs of the component. If there are none, ask for the high-level design (or suggest running `architecture-to-high-level-design`) before drafting.

## Workflow

### 1. Scope

Confirm the component for this run. One component per run is the default; take several only when they are small and closely related. Add every component element to the index if it is not there yet. When the component already has a report, start from what changed since its `Inputs as of` commit ("Re-running a stage" in `conventions.md`).

### 2. Modules

Split the component into modules, following `modules.md`: one responsibility each, what changes together kept together, decisions likely to change hidden behind interfaces, dependencies pointing toward stable modules, no cycles. Choose frameworks and off-the-shelf parts as decisions. For an existing component, start from its current modules and mark each `keep`, `change`, `new` or `remove`.

### 3. Allocation

Allocate every acceptance criterion of every FR allocated to the component to a module, and every operation of every IFC it provides or consumes to exactly one module of the component, which realizes it. When an SLI binding on those IFCs, or on the DATs the component owns, needs the component to produce events or fields, allocate that to a module too. Allocate the drivers the element carries to the modules that realize them.

### 4. Module interfaces

For every public operation of every module, write the signature in a language-neutral notation, with preconditions, postconditions, invariants and errors ("Contracts" in `modules.md`). Use the types of the shared conventions. The contracts belong in the MOD items; the report does not repeat them.

### 5. Behaviour

For each module, as it applies, following `behaviour-and-data.md`: a state diagram with every state and transition, timeouts and errors included; sequences inside the component; decision tables for rules with several conditions; algorithms with their steps, cost and edge cases; concurrency (what runs at the same time, what is locked, what is idempotent); error handling (what is handled where, what is passed on, what is logged). A timeout on a call that changes something leads to a state that settles its outcome, never to a failure.

### 6. Data structures

Design the physical data of the data entities the component owns (the DAT items whose owner is this component), wherever they are stored: tables, columns, types, constraints, indexes tied to the queries that need them, and, for an existing schema, migrations that keep the running version working. When another component reads these tables directly, keep them as stable as an interface. Design caches and in-memory structures with their keys, lifetimes and size bounds.

### 7. Screens

When the component serves people, design each screen: its components, the data each shows and takes, its states (loading, empty, error, success, and any the acceptance criteria name), input validation and messages, and what the accessibility requirements need.

### 8. Verification approach

For each module, write which acceptance criteria, contracts, budgets and internal quality requirements it must pass, and how they will be checked: unit tests from a decision table, contract tests against the IFC spec, property tests for an algorithm, a load test for a budget, a check in CI. Do not write test code. Each module's checks go in its MOD item; the report describes what serves several modules (test doubles, environments, load tests, checks in CI).

### 9. Design parameters

Propose the remaining values inside the component (timeouts on its own data store, retry limits, pool sizes, batch sizes, cache lifetimes, schedules) with their basis. Every timeout and wait on a call that crosses an element boundary, settlement waits included, is stage 3's and lives in the IFC's `timing`: use it as it is, refer to it by the IFC's ID, and never set it here. The values set here must fit the latency budgets and timeouts of stage 3; when they cannot, or when a value in an IFC's timing must change, write a finding addressed to `architecture-to-high-level-design`. Each value is a provisional decision, rated like any other point ("Decisions" in `conventions.md`). Most stay inside one module and are tuned in operation, so they are adopted as an assumption of kind `decision`; values that hinge on the same fact share one.

### 10. Points to confirm

A quality-chain item's `basis_note` may leave a point for the design to confirm, and stage 1 addresses the ones it could not settle to the stage that designs the part, under "Open gaps" in its report. Confirm each point addressed to this stage for this component, citing it in the `basis_note` of the item that confirms it, or raise an issue for the quality chain when the design shows that it does not hold.

### 11. Findings, report, questions, items, index

Process every open finding addressed to this stage for this component. When an interface, an entity or an architecture decision does not work, write a finding addressed to the stage that owns it; do not change its items yourself. Write the MOD, DEC and FND items as you draft them in steps 2 to 10, and the draft component report that indexes them, following `report-template.md`, and mark the component `draft` in the index.

Then list and rate the uncertain points, ask about the ones `conventions.md` says to ask about, and record the rest as assumptions ("Draft first, ask afterwards"). The rules in `modules.md` and `behaviour-and-data.md` settle most choices here; a choice they settle from what the inputs state stays `inferred` and is not a point. Most of the points that remain stay inside one module and are easy to change later, so both ratings are low and they become assumptions. The points of high severity here are typically those that move money, touch personal data, fix the shape of stored data or tie the component to a vendor; breadth is high when five or more modules depend on a point, as they do on a framework they all use.

Re-rate the open assumptions this component's judgments depend on, whichever stage wrote them, and ask about one when a judgment you would ask about depends on it ("Assumptions" in `conventions.md`). Number the questions per component report and continue the numbering when the component is re-run; from elsewhere, cite one as "stage 4 ELM-02, question 3".

Apply the answers to the items in place, check the exit criteria, set the report's status to "answers applied", and update the component's row in the index.

## Exit criteria

- Every acceptance criterion of every FR allocated to the component is allocated to a module.
- Every operation of every IFC the component provides or consumes is realized by exactly one module of the component.
- Every SLI binding that needs the component to produce events or fields has a module that produces them.
- Every module has one responsibility, an interface with contracts, its behaviour, its data structures and a verification approach.
- Every module with states has all its states and transitions, timeouts and errors included. Every decision table covers every combination of its conditions, without overlaps.
- The module dependencies have no cycles and follow the shared conventions.
- Every table of the data entities the component owns has its columns, constraints, and the indexes its queries need.
- Every call that changes something has a state that settles its outcome after a timeout.
- Every design parameter has a value and a basis, fits the stage 3 budgets, and is either decided under "Decisions" or recorded as an assumption of kind `decision`. None is a timeout or wait on a call that crosses an element boundary: those are used from the IFCs' `timing`, by IFC ID.
- Every item that depends on an assumption lists it in `premises`, and an item whose `premises` include an open DAS, or an open QAS that no design question has answered, has `basis: assumed`.
- The index lists every component with its current status, and its header gives the date and the `Inputs as of` commit.
- Every point that stage 1 addressed to this stage for this component, from what a quality-chain item leaves for the design to confirm, is confirmed in the `basis_note` of an item, or raised as an issue for the quality chain.
- Every open finding addressed to this stage for this component is accepted or rejected.

## Pitfalls

- Designing only the happy path. States and errors are where two implementations of the same design differ.
- Modules named only after technical layers (controllers, services, repositories) with no business responsibility. Every change then touches every layer.
- Contracts without errors. The caller then learns them in production.
- Decision tables with gaps. Each missing combination is a behaviour someone will implement differently.
- Indexes chosen without the queries. Write the query first.
- Copying the items into the report. A contract written in two places drifts, and nobody can tell which copy is right.
- Writing code. The design must survive a change of language; code is the next step, not this one.
- Leaving a component shallower than the others because it looked simple.

## Finish

Finish the run as `conventions.md` describes ("Finishing a run"). List the open assumptions this run wrote or depends on, highest ratings first, and say that no answer is needed. Tell the user which files were written, how many modules, how many questions were asked, the findings processed and raised, the issues for the quality chain, the components still not designed according to the index, and the next steps: run `design-review` on this component in a fresh context, re-run the stages that this run's findings are addressed to, re-run this stage for the component to resolve the findings the review addresses to it, and run this stage for the next component. Then commit the files this run wrote (the component report, the index, the MOD, DEC, DAS and FND files, and the DAS files of other stages that it re-rated or answered), with a message that names the component.
