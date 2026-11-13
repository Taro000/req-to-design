<p align="center">
  <img src=".github/assets/logo.png" alt="req-to-design logo" width="640">
</p>

# req-to-design

English | [日本語](README.ja.md)

Agent skills that turn a system's requirements into its design: first the drivers that should shape the architecture, then the architecture, the technical policy, the high-level design and the detailed design, with a review after each design stage. They start from the artifacts of [cuj-to-slo](https://github.com/Taro000/cuj-to-slo) (users, CUJs, functional requirements, quality requirements, NFRs and SLOs), so every design decision can be followed back to the requirement and the user it serves.

> **Status: experimental (0.3.0).** Version 0.3.0 has been run once end to end on a demo project with `design-chain`, and compared with the first run of 0.1.0 on the same project ("Results on the demo" below). On the same scope it wrote 30% of the lines, and the findings of each review were no more than those of the review before it. It did not keep each stage to two runs, its reviews still found copies that had drifted, and it stopped at its limit with one major finding open in the server's money paths. Nobody answered its questions: each one took its drafted option. Check the results of your first runs closely.

## The stages

| Stage | Skill | Input | Output |
|---|---|---|---|
| 1 | `requirements-to-architecture-drivers` | The quality chain's artifacts (`docs/quality/`), including the design decisions it found in its inputs; the design context, which never comes from users (technology constraints, the organization's engineering standards among them; budget, deadline and team; how the teams are split; anticipated changes); existing code | Architecture drivers: quality and change scenarios, constraints, principles, and a ranking |
| 2 | `architecture-drivers-to-architecture` | Stage 1 output | Design decisions with their options and rationale, elements with the runtime and platform of each, four views (context, runtime, deployment, information), a threat model |
| 2b | `architecture-to-technical-policy` | Stage 2 output; the gates and audits of the quality chain; the organization's engineering standards and the conventions of the existing code | The technical policy that the later stages and the code follow: the stack of each kind of component; the repositories, directories and dependency rules that CI enforces; the test strategy, with where and by what each gate of the quality chain is checked and where each audit is held; the pipeline and the conventions inside the code; whether each kind of interface's spec is written by hand or generated from the code; how coding agents find the design and bring findings back |
| 3 | `architecture-to-high-level-design` | Stage 2 and 2b output | Interfaces (with OpenAPI and AsyncAPI documents for those whose spec the technical policy says is written by hand), end-to-end flows with latency budgets, data entities, the conventions that interfaces share, and where every SLI's events come from |
| 4 | `high-level-design-to-detailed-design` | Stage 3 output and the technical policy, one component per run | Modules with contracts, placed in the policy's directories, and a verification approach at its test layers; states, decision tables and data constraints only for the modules where a mistake in the code is costly; the hand-off to implementation |
| Review | `design-review` | The output of stage 2, 2b, 3 or 4 | Findings addressed to the stage that must decide |

In Claude Code, a seventh skill, `design-chain`, runs the stages and reviews for you ("Run the chain with design-chain" below).

Run the review in a fresh session, not in the one that wrote the design. Findings go back to the stage that owns the items; re-run that stage to accept or reject them when a finding is critical or major. Minor findings wait until the stage runs again for another reason. Review a stage again only after a critical or major finding has changed its items; that review looks only at what changed since the last one. The skills never write to `docs/quality/`, and never decide what the quality chain owns, such as a target or a check before release: when the design shows that a requirement should change, or that one is missing, a stage writes a request to the quality chain, and `docs/design/quality-chain-requests.md` collects the requests for you to answer and hand to the quality chain.

## Install

```sh
# all seven skills, into the current project
npx skills add Taro000/req-to-design

# list the skills without installing
npx skills add Taro000/req-to-design --list

# one skill, for Claude Code only, available in every project
npx skills add Taro000/req-to-design --skill design-review -a claude-code -g
```

The skills work best after the quality chain (`npx skills add Taro000/cuj-to-slo`). Without it, give the same information yourself: users and CUJs, functional requirements with acceptance criteria, prioritized quality requirements, and measurable targets.

## Use

Run each step in a fresh request:

1. "Derive the architecture drivers from docs/quality/. Technology constraints: … Engineering standards: … Budget and deadline: … Teams: … Roadmap: …"
2. "Design the architecture from the drivers."
3. In a new session: "Review the architecture." If there are critical or major findings: "Re-run the architecture stage to resolve the findings." If that changed the architecture, review it again in a new session.
4. "Decide the technical policy." Review it in a new session, and resolve its findings the same way. It decides once, for every component, what the later stages and the code follow: the stack of each kind of component, the repositories and the dependency rules, the test strategy with where every gate of the quality chain is checked, the pipeline and the conventions inside the code, and how each kind of interface gets its spec. The other stages decide none of these: the architecture stops at the runtime and platform of each component, the high-level design writes a spec only where the policy says to, and the detailed design builds each component on the stack of its kind.
5. "Write the high-level design." Review it in a new session, and resolve its findings the same way.
6. "Write the detailed design of ELM-02." Repeat for every component listed in `docs/design/4-detailed-design.md`, and review each one.
7. Implement from `docs/design/4-detailed-design.md`, within the technical policy of `docs/design/2b-technical-policy.md`. The hand-off to implementation tells the coding agent what the design decides, what the code decides, and how to raise a finding when the code cannot keep a design decision or a policy.

Requests to the quality chain gather in `docs/design/quality-chain-requests.md`. A stage asks you about a request at once only when its answer could change a primary driver, or a decision that is hard to undo; the other requests wait, and the design follows the requirements as they stand. Write an answer after "Answer:" under a request whenever you know it: the next run records it. Then hand the document to the quality-chain stages it names, and re-run them; the design stages follow what changed when they next run.

Each stage drafts everything first. It then rates every point it was unsure of by breadth (how much depends on it) and severity (the harm if the draft is wrong), and asks you only about the points where either is high. The ranking and the decisions that accept a risk, a cost or a debt are rated the same way; when they are asked, your answer is the decision. Every other point is kept as drafted and recorded as an assumption, which the skill lists at the end for you to skim and correct if you want. Every judgment is marked `stated`, `inferred`, `assumed` or `confirmed`, so you can see what came from you, what the agent decided, and what nobody has checked yet.

When you run a stage yourself, it asks you during the run. When it cannot ask you, because it runs as a subagent of another agent or where nobody watches, it writes the questions in its report under "Unanswered questions", with the same options, sets the report's status to "waiting for answers", commits its draft and stops. Write each answer in its question's row and run the stage again: it applies the answers and moves them to "Decisions". Until then, run no later stage and no review of it.

A stage needs to run again when it is stale: since its last run, something it reads changed, a critical or major finding was addressed to it, a hand-off to it fell due, or an assumption its items rest on was overturned; or an answer waits under its "Unanswered questions" (`conventions.md`, "Re-running a stage"). `scripts/status.py` lists the stale stages with their reasons, and what runs next.

Each stage decides in full only what is hard to change later: the kinds of point that `conventions.md` lists for it, and any point whose breadth or severity is high. It hands the rest off, with the bounds to keep, to the later stage or to the implementation that will decide it, and each stage takes up the hand-offs addressed to it.

Each stage is a long task. The detailed design runs once per component; it writes in detail only the modules where a mistake in the code is costly, and hands the rest to implementation. Plan time to review the documents and to answer the questions that matter most.

Reports and items show only the current state; git keeps the history. Each skill ends its run by committing the files it wrote, with the reasons in the commit message, and the next run reads what changed since then.

Before it commits, each skill runs two scripts from its `scripts/` directory. `tables.py` writes the index tables of the reports, and the request document, from the YAML items, so that neither is a hand-made copy that can drift. `check.py` checks what needs no judgment, so that reviews do not spend findings on it: that every YAML file parses and no value is cut off at an unquoted ` #`, that every ID points at an item that exists, that the basis marks match the assumptions, that functions and drivers are allocated consistently from elements to interfaces and modules, that the OpenAPI and AsyncAPI documents have the operations, error statuses and codes of their interfaces, and that every gate and audit of the quality chain has its place in the technical policy. The skill fixes what the check reports in its own files. A third script, `status.py`, shows the state of the chain: which stages are stale and why, which wait for answers, which reviews are due, and what runs next. The scripts need Python 3.8 or later and no packages. To run the check yourself, from the project's root: `python3 <skill directory>/scripts/check.py` (for Claude Code, the skill directory is `.claude/skills/<skill>/`).

Questions and artifacts follow your language and your project's documentation language. The skills themselves are written in English.

### Run the chain with design-chain

In Claude Code, `design-chain` runs the steps above for you. It finds the stages that are stale and runs each one with its skill as a subagent, one at a time from the top of the chain down. It runs a review after a stage's first run, and again only after a critical or major finding changed the stage. Findings, hand-offs and requests that the quality chain applied start the runs they call for, and you are asked nothing on the way, except the questions that only you can answer.

- Start: "Run the design chain from docs/quality/. Technology constraints: … Engineering standards: … Budget and deadline: … Teams: … Roadmap: …". It runs stage 1 with what you gave, and goes on down to the detailed design of each component.
- Continue: "Continue the design chain." after you answered questions in the reports, corrected an assumption, handed the request document to the quality chain and re-ran it, or after implementation raised findings, or when the chain stopped at a limit.
- See the status: "Show the status of the design chain." It runs nothing, and says what is stale and why, what waits for answers, what runs next, and what will make a stage stale later. You can also run the script yourself: `python3 .claude/skills/design-chain/scripts/status.py`.

When runs wrote questions that nobody could answer during them, it runs every stage that does not depend on them first, then asks you all of the questions together, grouped by stage, writes your answers into the reports, and resumes those stages. Stages below a stage that waits for answers stay stopped until then.

It stops on its own when an item goes back to a value it had earlier in the same invocation, at its limits (10 runs per invocation and 3 runs of one stage, by default), or when critical findings remain after two rounds, and says why. Change the limits in the request ("continue, with up to 20 runs") or in `docs/design/design-chain.yaml`. It ends with the runs and their commits, the questions with your answers, the open assumptions, which you may correct, and the requests to the quality chain that are open or answered, with the stages that each one will make stale. Each stage commits its own run as usual; `design-chain` commits nothing itself and never pushes.

Because no one checks a stage before it runs, an assumption that is wrong and not rated high flows down the chain. Each run re-rates the open assumptions it depends on, and asks about one once enough items rest on it; skim the open assumptions at the end, and correct the ones that are wrong.

In other agents, `design-chain` runs nothing: it shows the next stage to run, what to ask it in a new session, and the questions that wait.

## Artifacts

```
docs/design/
├── 1-architecture-drivers.md … 3-high-level-design.md   one report per stage, 2b-technical-policy.md included
├── 4-detailed-design.md, 4-detailed-design/              an index with the hand-off to implementation, and one report per component
├── reviews/                                              the latest review of each stage
├── design-context.yaml                                   the design context: constraints, teams, changes, stakeholders, current structure
├── design-chain.yaml                                     optional: the limits of design-chain
├── drv/  dec/  elm/  pol/  ifc/  dat/  mod/  fnd/       one YAML file per item
├── hnd/                                                  one YAML file per hand-off: a point a stage leaves for a later stage or the implementation to decide
├── das/                                                  one YAML file per assumption made without asking
├── qcr/                                                  one YAML file per request to the quality chain
├── quality-chain-requests.md                             the requests to the quality chain, in one document to hand over
└── ifc/specs/                                            OpenAPI and AsyncAPI documents, for the interfaces whose spec the technical policy says is written by hand
```

YAML keys and IDs are fixed in English, so every stage can read every other stage's files. Views, flows and state diagrams are Mermaid diagrams inside the reports. The index tables of the reports, between `<!-- generated: ... -->` marks, are written from the YAML items; edit the items, not those tables.

## What the skills will not do

- Write to the quality chain, or decide what it owns: requirements, targets, thresholds, and gates (checks that must pass before a merge, a demo or a release). Changes to the requirements that the design calls for are written as requests to the quality chain, gathered in one document; you answer them and decide when to hand them over.
- Invent business numbers. Targets, deadlines, volumes and budgets come from you or from the quality chain; missing ones stay named placeholders. Design parameters such as timeouts are proposed as provisional values, with what they are based on.
- Write code. The detailed design stops where coding starts, and uses a language-neutral notation.
- Decide business priorities for you. The driver ranking, accepted risks and debts, deferring what a stage would otherwise decide in full, and design parameters are business decisions: the ones with high breadth or severity are asked, and the rest are adopted provisionally and recorded as assumptions, never presented as decided.
- Write runbooks, business procedures or training. The design of the infrastructure is in scope; operating it is not.

## Results on the demo

Version 0.3.0 was run on [ride-hailing-app-demo](https://github.com/Taro000/ride-hailing-app-demo) (branch `design/trial-0.3.0`), from stage 1 to the detailed design of two of its three components, with `design-chain` running each stage and review as a subagent: 41 runs, about 23 hours. The baseline is the first run of 0.1.0 on the same project, made by hand over six days (branch `design/trial-1`).

| Measure | 0.1.0 | 0.3.0 | Target |
|---|---|---|---|
| Runs of one stage | Stage 1: 4, stage 2: 5, stage 3: 2 | Stage 1: 3, stage 2: 6, stage 2b: 2, stage 3: 5, stage 4: 4 for each component. 4 of the 41 runs only applied answers, in 3 to 5 minutes each | At most 2: not met |
| Findings of the successive reviews of a stage | Stage 2: 14, 9, 17. Stage 3: 20, 9 | Stage 2: 8, 1, 1. Stage 2b: 7, 3. Stage 3: 13, 5, 1, 1, 1. Stage 4: 6, 3, 0 (admin screens) and 13, 2, 2 (server) | Fewer each time: met in that no review found more than the one before it, though major findings rose once in stage 3 and stayed at one in the server |
| Findings about a copy that drifted or a wrong reference | 25 of 80 | 21 of 78 | None: not met |
| Lines on the same scope (stages 1 to 3, the admin screens' detailed design, reviews) | 42,961 | 12,932 (30%) | Half or less: met. Without 0.1.0's 21,925 lines of hand-written OpenAPI and AsyncAPI, 61% |
| Decisions handed to a later stage or to implementation | None of 66 | 22 hand-offs | — |
| Primary drivers | 16 | 12 | — |
| Modules of stage 4 designed in detail | 20 of 20 (admin screens) | 2 of 19 (admin screens), 25 of 49 (server) | — |
| Questions for a person | 58 in the runs, and 16 issues for the quality chain | 15 in the runs, and 10 requests to the quality chain | — |

Where it fell short, and what to try next:

- **Runs of one stage.** Three things added runs. Each stop for questions takes a short run to apply the answers. Findings came back from later stages: an answer in stage 2 added a constraint to stage 1, and the server's detailed design sent two major findings to stage 3, which made the finished admin screens stale again. And in the server's money paths (holds, captures, re-holds), each major finding that was fixed led the next review to a new one, until the limit stopped the chain with one open. Next: count the runs that only apply answers apart from the others; run first the component with the most modules at full depth, so that its findings reach stage 3 before the others build on it; have a stage that fixes a major finding in a module at full depth walk that module's decision tables again before it commits.
- **Copies that drifted.** The same kinds of review found them as often as in 0.1.0 (in stage 3, 43% of the findings against 41%). The kinds left: stage 4's allocation of acceptance criteria to modules, written by hand, disagreed with the modules' functions in three reviews; stage 3's flows restate what the interfaces carry; items rely on an assumption or a constraint that their premises leave out. Next: write stage 4's allocation table from the modules, or check it with `check.py`, and check that an item citing a DAS, a QAS or a TC lists it in its premises.

What the comparison does not show:

- What a person would answer. The 15 questions took their drafted options. The input was the quality chain 0.3.0's replay of the demo, whose answers came from the 0.1.0 trial's records, so it already held choices (Stripe, Google Maps, iOS Safari) that 0.1.0 had to find. Both flatter 0.3.0's questions, and two drafts went another way than the person did in 0.1.0: the system is designed for deployment but runs only on a local machine, and the fare counts a base fare and distance only.
- How much one run differs from another: this is one run. The server's detailed design, which 0.1.0 never reached, has no baseline, and one component, the passengers' and drivers' web app, has no detailed design.
- The fixes of this version. The run found two defects that this version fixes after it: a commit that only rewrote the generated tables of another report counted as a run of that report's unit, which made the chain stop at its limits early, and a re-run that stopped on the way did not show as stale.

## Maintaining

`references/conventions.md`, `references/artifacts.md`, `references/glossary.md` and the scripts in `scripts/` are identical in every skill, because `npx skills add --skill` installs a single skill directory. Edit them in `shared/` and `shared/scripts/`, then run:

```sh
scripts/sync-shared.sh          # copy shared/ into every skill
scripts/sync-shared.sh --check  # fail if any copy differs
python3 -m unittest discover -s tests   # test the scripts, and that the YAML examples in the skills parse
```

## License

MIT
