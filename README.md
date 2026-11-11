<p align="center">
  <img src=".github/assets/logo.png" alt="req-to-design logo" width="640">
</p>

# req-to-design

English | [日本語](README.ja.md)

Agent skills that turn a system's requirements into its design: first the drivers that should shape the architecture, then the architecture, the technical policy, the high-level design and the detailed design, with a review after each design stage. They start from the artifacts of [cuj-to-slo](https://github.com/Taro000/cuj-to-slo) (users, CUJs, functional requirements, quality requirements, NFRs and SLOs), so every design decision can be followed back to the requirement and the user it serves.

> **Status: experimental (0.2.0).** The skills have been used once on a real demo project. Version 0.2.0 changes how they ask questions, record assumptions and keep history, and takes over the design decisions that the requirements no longer make (platforms, mechanisms, where SLI events come from); it has not been run end to end yet, so check its first results closely.

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

## Maintaining

`references/conventions.md`, `references/artifacts.md`, `references/glossary.md` and the scripts in `scripts/` are identical in every skill, because `npx skills add --skill` installs a single skill directory. Edit them in `shared/` and `shared/scripts/`, then run:

```sh
scripts/sync-shared.sh          # copy shared/ into every skill
scripts/sync-shared.sh --check  # fail if any copy differs
python3 -m unittest discover -s tests   # test the scripts, and that the YAML examples in the skills parse
```

## License

MIT
