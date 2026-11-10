# Conventions shared by the design skills

Five skills turn a system's requirements into its design. Four are stages that run in order; the fifth reviews the output of stages 2 to 4.

| Stage | Skill | Reads | Writes |
|---|---|---|---|
| 1 | `requirements-to-architecture-drivers` | the quality chain's artifacts, the design context the user gives (technology, budget, deadline, team, anticipated changes), existing code | `design-context.yaml`, architecture drivers (DRV), assumptions (DAS) |
| 2 | `architecture-drivers-to-architecture` | DRV, the design context, functional requirements and CUJs | design decisions (DEC), elements (ELM), views, DAS |
| 3 | `architecture-to-high-level-design` | ELM, DEC, DRV, acceptance criteria, SLI definitions | interfaces (IFC) and their specs, data entities (DAT), DEC, DAS |
| 4 | `high-level-design-to-detailed-design` | one component per run, with its IFC, DAT, DEC, DRV and functions | modules (MOD), DEC, DAS, the detailed design index |
| Review | `design-review` | the output of stage 2, 3 or 4, and what it was built from | a review report, findings (FND), DAS |

Each stage turns the decisions of the stage above into obligations for the stage below: an architecture decision binds the high-level design, and an interface binds the modules that realize it. Every item traces up to what it serves, so anyone can walk from a module back to the driver, the quality requirement and the user behind it.

## The quality chain

The quality chain is the set of four skills that write `docs/quality/`. It produces what the design starts from: users, CUJs and shared facts (`context.yaml`), quality-in-use requirements (QIU), functional requirements (FR) with acceptance criteria, product and data quality requirements (QR) with their handling, non-functional requirements (NFR), SLI definitions (SLI), error budget policies (EBP) and its own assumptions (QAS).

The quality chain states requirements and never decides design. What it leaves to the design:

- The design decisions it found in its inputs, under `design_inputs` (DIN) in `context.yaml`. Stage 1 takes each one in as a technology constraint candidate.
- Platforms and device support. The quality chain names only kinds of device and situations in its contexts of use. Operating systems, browsers, versions, and native or web are a technology constraint when the input fixes them, and otherwise a stage 2 decision.
- Mechanisms. Its functional requirements state behaviour observable from outside; the keys, tokens, IDs, caches, retries and queues that produce that behaviour are design decisions.
- Where SLI events come from. Its SLIs are defined in the terms of the domain: the unit event, the vantage (`user-side`, `system-boundary`, `synthetic` or `data`), the counting rules. Stage 3 binds every SLI to the interface or data that produces its events, with the fields and the method (`sli_bindings`), without changing what the SLI counts.

Rules for using it:

- Read it; never write to it. Do not edit, add or retire anything under `docs/quality/`, do not write function proposals there, and do not record answers in its QAS files.
- When the design shows that something in the quality chain should change, write it in the report's "Issues for the quality chain" section: the issue, the chain items it concerns, the change you suggest, and which quality-chain stage would make it. Typical issues: a target that no design within the budget can meet, a conflict between quality requirements that no design resolves, a missing function, a CUJ step that no element can perform, a limit of the chosen technology that changes what users can do. The user decides whether to re-run that quality-chain stage; afterwards, the design stages that the change reaches are re-run.
- Refer to chain items by their IDs, including its shared facts (CON, EXT, OPF). Do not copy their statements into design items; trace to them.
- A chain item's `basis_note` may say what the design must confirm. Stage 1 turns each such point into a driver, a constraint, a question, an assumption (DAS), or an open gap addressed to the stage that designs the part. That stage confirms the point, citing it in `basis_note`, or raises an issue for the quality chain.
- An issue for the quality chain stays in the report until the quality chain has applied it, which shows in `docs/quality/` on a later run; then remove its row.
- When `docs/quality/` does not exist, accept the same information from the user (users, CUJs and their steps, functional requirements with acceptance criteria, quality requirements with their priority, targets that can be measured) and record where it came from in the report's "Inputs" table. In trace fields, write the source instead of an ID ("PRD, section 3").

## Findings between design stages

A later stage, or a review, that finds a problem in an earlier design stage's items writes a finding (FND) addressed to that stage. It never edits that stage's items itself, so that every item has exactly one stage that writes its content. (Assumption files and findings also record answers and statuses from other stages, as described in "Assumptions" and below.)

- A finding names the skill it is addressed to, the items it concerns, its severity, the evidence and a suggested resolution.
- Every stage reads the open findings addressed to it, on every run. For each one, it accepts (changes its items and cites the finding in their `basis_note`) or rejects (writes why in `resolution`), and sets the finding's status. A rejection that leaves a risk in place is a business decision ("Decisions").
- Only a critical or major finding is a reason to run the stage it is addressed to. A minor finding waits until the stage runs for another reason, such as a change upstream or a critical or major finding, and that run processes it with the others. Never name a stage to run when its only reason would be its open minor findings.
- `design-review` reviews each of stages 2 to 4 after its first run (stage 4 after the first run for each component). The review of a stage is repeated only when the stage's items changed to accept a critical or major finding, and the repeated review covers only what changed since the last one. Items changed only for minor findings, or only to follow a change upstream, call for no review: the next review of the stage covers them too.
- When an accepted finding changes items, tell the user which later stages to re-run and whether to repeat the review, as "Finishing a run" describes.
- A finding is about this design. A problem in the quality chain goes to "Issues for the quality chain", not into a finding.

## Scope

These skills design software for the system inside the boundary in `context.yaml`, or inside the boundary the user gives: its structure, interfaces, data, modules and deployment. The infrastructure the software runs on (runtime environments, networks, managed services) is in scope as part of the deployment design.

Business procedures, operating runbooks and training are not. When only they can meet a need, write one line in the report's "Out of scope" section saying what and why. Systems outside the boundary appear only as external systems. What an external system promises (an SLA, a rate limit) is a technology constraint (TC) that decisions and interfaces cite by ID; what the design assumes beyond that is a DAS.

## Working language

- Ask questions in the language the user writes in.
- Write artifacts in the language of the project's existing documentation. If the project has none, use the user's language.
- Keep YAML keys, IDs and enum values in English exactly as `artifacts.md` defines them, so that every stage can read every other stage's files. Write free-text values in the working language.
- Use the terms in `glossary.md` for the working language, and use each one consistently.
- When you name a quality characteristic, use the name the quality chain's own report uses for the working language.
- Write diagram labels in the working language and keep IDs in them as they are.
- In reports, write the basis marks and statuses with the glossary's terms for the working language. In YAML, use the English enum values.

## Judgment basis

Mark every judgment with where it came from:

- `stated`: written in the input, in the quality chain's artifacts or in an earlier design stage's items. Rewording that keeps the meaning is still `stated`.
- `inferred`: your own judgment, made with enough evidence that you are not unsure. Anything the input does not say is `inferred` or `assumed`, even when it seems obvious. A design decision you make is `inferred` until the user confirms it.
- `assumed`: your own judgment that you were unsure about and did not ask about, because it fell below the bar for questions ("Draft first, ask afterwards"). It is recorded as an assumption (DAS), and every item that depends on it lists the DAS in `premises`.
- `confirmed`: the user answered a question about it.

Never present an `inferred` or `assumed` judgment as if it were `stated`. People tend to accept a confident-looking draft without checking it; the basis mark tells them where to look.

An item holds several judgments, and its `basis` is the weakest of them, from weakest to strongest: `assumed`, `inferred`, then `stated` and `confirmed`. An item is `confirmed` only when every judgment in it that is not stated has been answered. When the parts differ, say in `basis_note` which parts are stated, inferred, assumed and confirmed. Most design items stay `inferred`: they are proposals built on the stages above.

Stage 1 writes `design-context.yaml`. A later stage or a review that learns a new fact from the user (an SLA, a volume, a change in the team) adds the entry itself and says so in its report.

An item lists in `premises` what it relies on directly that could change under it (it does not copy the premises of the items it traces to, which are found by following the traces): the design context's entries (TC, PC, TEAM, CHG, STK), assumptions (DAS), and the quality chain's shared facts and assumptions (CON, EXT, OPF, QAS). Refer to such an entry by its ID, and copy neither its values nor its wording beyond a short label.

## Numbers

- Business numbers (targets, deadlines, thresholds, volumes, budgets) come from the inputs: the quality chain's items, the design context or the user. Never invent one. Use the chain's values and the names of its placeholders as they are. A number the design needs that no input gives is a gap: ask for the fact that would settle it, or write a named placeholder whose name no other placeholder uses, and list it in the report under "Placeholders".
- Design parameters (timeouts, retry counts and back-off, pool and batch sizes, cache lifetimes, partition counts) are design decisions. Propose a provisional value and say what it is based on (a stated number it derives from, a calculation, the default of a named library or service). A provisional parameter is a decision ("Decisions").
- Show in the report how every derived number (a latency budget, a capacity estimate, a storage estimate) follows from stated numbers. Compute with a script, not by hand.

## Existing systems

When the repository holds code or infrastructure definitions for the system:

1. Stage 1 reads them before drafting and records the current structure in `design-context.yaml`: elements, data stores, deployment, dependencies, and the conventions the code follows.
2. Later stages read the parts they design, and design changes as deltas: every element, interface, data entity and module is marked `keep`, `change`, `new` or `remove`.
3. Say in the report what was read, and what the code cannot tell (runtime behaviour, production configuration, real volumes). Never present a guess about runtime behaviour as something read.

When there is no code, every item is `new`.

## Draft first, ask afterwards

1. Read every input: the quality chain's artifacts (or what the user gave instead), `design-context.yaml`, this stage's existing items and the items of the stages above it, the open findings addressed to this stage, and the code the stage needs. On a re-run, start from what changed ("Re-running a stage").
2. If an essential input is missing, so that no meaningful draft is possible (each skill names its essential inputs), ask only for that input before drafting. This is a request for input, not a judgment question.
3. Draft the whole stage without stopping. Make every judgment yourself, using the rules in the skill. Write the items as you draft them, and the draft report that indexes them. Work in parts small enough to write as you go (one group of related items at a time, such as the interfaces of one element), and write each part's items before you start the next: a stage worked out in full before the first file is written saves nothing if the run stops.
4. List every point you were unsure of. A point is uncertain when:
   - the input is silent or ambiguous about a fact the choice depends on, and the choice changes this stage or a later one;
   - two or more reasonable options exist, and the wrong one would cause rework downstream;
   - inputs contradict each other, the quality chain or an earlier design stage;
   - it depends on facts that only the user's organization knows: budgets, contracts, team skills, existing systems, operating practice, volumes;
   - it is a business decision ("Decisions").

   A design choice you make with the skill's rules from what the inputs state is not uncertain only because the inputs did not make it for you: making it is this stage's job, and it stays `inferred`. Never list anything the input already states, wording, or how the method works; do list the facts that a judgment made with the method depends on. Merge points that hinge on the same fact.
5. Rate each point on two scales:
   - Breadth, read from the structure rather than guessed:
     - high: it changes the structure (an element, a boundary between elements, the owner of a data entity, the deployment), a technology constraint, the ranking of the primary drivers, a shared convention, or an interface that more than one element uses; or five or more items depend on it, counting the items of later stages through their traces once those exist;
     - medium: two to four items depend on it;
     - low: one item depends on it.
   - Severity, the harm if the draft is wrong and nobody notices until later:
     - high: legal, safety, financial or personal-data harm; something hard to reverse later (the shape of stored data, a published interface, a contract or a vendor the system becomes tied to); or a primary driver, a non-negotiable constraint or a CUJ that the design no longer meets;
     - medium: several items would have to be redone, but no harm reaches users or the business;
     - low: easy to change later, such as a choice inside one module or a provisional parameter that is tuned in operation anyway.
6. Ask about a point when either rating is high. Ask also, whatever the ratings, about a contradiction between inputs, with the quality chain or with an earlier design stage, and about the content of a law, standard, contract or policy that the inputs name but do not give, when a judgment in this stage depends on it. There is no fixed number of questions; the ratings decide. Every other point becomes an assumption ("Assumptions"): keep the drafted judgment, mark it `assumed`, and write a DAS item.
7. Ask in order of breadth × severity, high and high first, grouped by theme. For each question, give what you drafted, why you are unsure, and the options, with your drafted answer first. When a question asks for a fact (a budget, a name), the drafted option says what the draft does without it ("left as a placeholder"), and the user types the value.
   - When several items share one yes-or-no judgment ("which of these components does the team already run?"), ask it as one multi-select question rather than one question per item.
   - If a structured question tool is available (for example, AskUserQuestion in Claude Code), ask up to 4 questions per call with 2 to 4 options each, put your drafted option first and label it as recommended, and call the tool again for the next batch. Ask multi-select questions with up to 4 items each, splitting longer lists over several questions.
   - Otherwise, ask in chat as a numbered list and wait for the answers.
8. Apply the answers and mark the affected judgments `confirmed`. If an answer overturns a premise, redo the affected part of the draft, then rate the new uncertain points the same way. A redone item keeps its ID while it serves the same purpose, even when its content changes. If an answer drops a drafted item, set its `status: retired`, so that its number is never used again.
9. Check the stage's exit criteria and set the report's status to "answers applied". The items are the source of truth throughout, and the report must match them.
10. Finish the run ("Finishing a run").

## Decisions

The driver ranking, provisional design parameters, decisions that accept a risk, a cost in money or contracts, a weaker driver or a debt, deferred decisions, and rejections of findings that leave a risk in place are business decisions as much as technical ones. A design nobody decided on is reopened at the first incident or the first budget review. Rate such a decision like any other point:

- If either rating is high, ask the user to decide. The answer is the decision: mark the judgment `confirmed` and record the question and its answer under "Decisions" in the report.
- Otherwise, adopt the drafted decision provisionally: write a DAS item with `kind: decision`, and mark the judgments that depend on it `assumed`.

Never present a provisional decision as decided.

## Assumptions

An assumption (DAS) records one judgment made without asking: what was drafted, why it was uncertain, and its ratings. Each one is a file in `das/`. The DAS files are shared by the design stages and the review: any of them may record an answer in one.

- Every item that depends on an assumption lists it in `premises`. Find the dependent items by searching `premises`; a DAS does not list them. In a report, "Items that depend on it" means exactly the items whose `premises` name it.
- A DAS is `open` until someone settles it: `confirmed` when the user says it holds, `overturned` when the user says it does not, `retired` when nothing depends on it any more, answered or not (another answer can make it moot). A correction that changes part of an assumption sets `overturned`, records the change in `answer`, and leaves the parts it does not mention as they were drafted, now held.
- On every run, re-rate the open assumptions that this stage's judgments depend on, and update their `breadth`, `severity` and `rating_note` in place, whichever stage wrote them (a QAS is re-rated in this stage's report only: `docs/quality/` is never written). When a judgment you would ask about depends on an open assumption, or items now depend on an assumption so widely that its breadth is high, ask about the assumption in this run, whichever stage wrote it, and record the question and its answer under "Decisions" like any other. Write the answer in the DAS (`answer`, `answered_in`) and set its status. If the answer overturns it, redo this stage's dependent items, and tell the user to re-run the stage that wrote it.
- When the stage that wrote an assumption runs again, it applies the answer recorded in the DAS to its own items: the dependent judgments become `confirmed`, or are redone when the assumption was overturned.
- The quality chain's open assumptions (QAS) follow the same rule, except that the answer cannot be written in `docs/quality/`. When a design judgment you would ask about depends on an open QAS, ask about the QAS, and record the answer under "Decisions" and under "Issues for the quality chain", so that the quality chain applies it on its next run. The design items that depend on it cite the answer in `basis_note` and are no longer `assumed` on its account; they keep the QAS in `premises` until the quality chain has applied the answer.

## Current state only

Reports and items describe what holds now. They never record how they got there: no sections about earlier runs, no lists of changes, no changelogs, no version numbers, no "what changed" columns, no dates of changes inside items. The history lives in git, and the reasons for each change live in its commit message ("Finishing a run").

- When an answer overturns an earlier decision, replace the earlier row under "Decisions" and keep its number, so that citations of it stay valid; do not keep both.
- The report's header gives the date it was updated and the commit at which its inputs were read (`Inputs as of`): the commit that was current when the run started, or "none" outside git.
- A review report describes the latest review of its stage (for stage 4, of one component). A new review of the same stage replaces it, keeping its decisions in effect and their numbering; findings keep their own status.

## Re-running a stage

- Find what changed since this stage last ran. Its last run is the last commit whose first line names this skill (`git log -1 --format=%h --grep='^<skill name>' -- <report>`). List the files under `docs/quality/`, `docs/design/` and the code the stage reads that changed after that commit, and read their diffs (`git diff --name-status <commit> -- docs/quality/ docs/design/`, then `git diff <commit> -- <file>`), together with any uncommitted changes. Do not diff from `Inputs as of`: that header records which inputs the report reflects, and a diff from it shows this stage's own last output as changes too. If someone else committed between `Inputs as of` and the skill's commit (`git log --oneline <inputs as of>..<commit>`), read those changes as well. If the project is not under git, or the commits cannot be found, read every input again and compare it with this stage's items.
- A re-run handles what changed: new or changed upstream items (in the quality chain or in an earlier design stage), the open findings addressed to this stage, minor ones included, and the answers recorded in the assumptions this stage wrote. Leave the other items as they are unless a change reaches them. A change that only rewords an upstream item, without changing its meaning, needs nothing here. Keep changes the user made by hand to this stage's items, unless they contradict an input; then ask. To find them, look at the changes to this stage's own files after its last run: one that no skill's commit made, including one not committed yet, is a hand edit; a change made by another skill's commit (its first line names the skill) is an input. An answer given in another stage that changes this stage's items is cited where it is used ("design stage 3, decision 4"); it gets no row under this stage's "Decisions".
- Update in place. Keep existing IDs and never renumber. A new item takes the number after the highest one in use, retired items included.
- When an item is no longer needed, set `status: retired`. Do not delete the file: other items may trace to it. When a retired item is needed again for the same purpose, set it back to `active` instead of writing a new one.
- Artifacts written by an earlier version of these skills may carry `changelog`, `version`, `needs_agreement` and `approver_candidates` fields, statuses `draft` or `agreed`, sections about earlier runs, and reports with no `Inputs as of`. On the first re-run that touches such a file, drop those fields and sections, set `draft` and `agreed` to `active` (an agreement the file records counts as `confirmed` for what it covered), and read every input again, since there is no commit to diff from.
- Keep the decisions in effect. Do not ask the same question again unless the inputs it depended on have changed. Number the rows of "Decisions" per stage, and in stage 4 per component report, questions and corrections in one sequence, and continue the numbering on a re-run, so that `basis_note` can cite them ("decision 7", or "question 7" for a question); when citing another stage's, name the stage ("stage 2, decision 4", "stage 4 ELM-02, decision 3").

## Finishing a run

1. List the open assumptions that this run wrote or depends on (DAS and QAS), one line each with their ratings, highest first. Say that no answer is needed, and that any correction the user gives is applied like an answer. Record a correction under "Decisions" with the next number, and set a DAS to `overturned` or `confirmed` as the user says. Silence, or "no corrections", leaves an assumption `open`. When applying the corrections creates new assumptions, list them in the closing message as well.
2. Tell the user what to run next, following "Findings between design stages": the later stages whose inputs this run changed, and for which items; the stages this run addressed a critical or major finding to, but not a stage it addressed only minor findings to; and, after a run of stage 2, 3 or 4, the review of this stage (in stage 4, of this component) when there is none yet, or when this run changed items to accept a critical or major finding. Say also which issues for the quality chain are still open.
3. Check that every YAML file this run wrote, and every item file of this stage, still parses and that no value is cut off at ` #`, with a YAML parser when one is available; fix any that is, whichever run wrote it. List a value cut off in another stage's file under "Open gaps" for that stage. If the project is under git, commit the files this run wrote, and only those, to the current branch. Add the new files, then commit with the paths named, so that nothing else the user has staged is included (`git add -- <paths>`, then `git commit -m "<message>" -- <paths>`). Write the message in the language of the project's recent commit messages, or in the working language when there are none. The first line names the skill and what the run did; the body says what triggered the run, which items were added, changed or retired and why, and what to run next (step 2). Never push. If the commit fails, say so and leave the files as they are.
