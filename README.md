<p align="center">
  <img src=".github/assets/logo.png" alt="req-to-design logo" width="640">
</p>

# req-to-design

English | [日本語](README.ja.md)

Agent skills that turn a system's requirements into its design: first the drivers that should shape the architecture, then the architecture, the high-level design and the detailed design, with a review after each design stage. They start from the artifacts of [cuj-to-slo](https://github.com/Taro000/cuj-to-slo) (users, CUJs, functional requirements, quality requirements, NFRs and SLOs), so every design decision can be followed back to the requirement and the user it serves.

> **Status: experimental (0.2.0).** The skills have been used once on a real demo project. Version 0.2.0 changes how they ask questions, record assumptions and keep history, and takes over the design decisions that the requirements no longer make (platforms, mechanisms, where SLI events come from); it has not been run end to end yet, so check its first results closely.

## The stages

| Stage | Skill | Input | Output |
|---|---|---|---|
| 1 | `requirements-to-architecture-drivers` | The quality chain's artifacts (`docs/quality/`), including the design decisions it found in its inputs; the design context, which never comes from users (technology constraints; budget, deadline and team; how the teams are split; anticipated changes); existing code | Architecture drivers: quality and change scenarios, constraints, principles, and a ranking |
| 2 | `architecture-drivers-to-architecture` | Stage 1 output | Design decisions with their options and rationale, elements, five views, a threat model |
| 3 | `architecture-to-high-level-design` | Stage 2 output | Interfaces with OpenAPI and AsyncAPI documents, end-to-end flows with latency budgets, data entities, shared conventions, and where every SLI's events come from |
| 4 | `high-level-design-to-detailed-design` | Stage 3 output, one component per run | Modules with contracts, states, decision tables, physical data and a verification approach |
| Review | `design-review` | The output of stage 2, 3 or 4 | Findings addressed to the stage that must decide |

Run the review in a fresh session, not in the one that wrote the design. Findings go back to the stage that owns the items; re-run that stage to accept or reject them when a finding is critical or major. Minor findings wait until the stage runs again for another reason. Review a stage again only after a critical or major finding has changed its items; that review looks only at what changed since the last one. The skills never write to `docs/quality/`: when the design shows that a requirement should change, the report says so, and you decide whether to re-run the quality chain.

## Install

```sh
# all five skills, into the current project
npx skills add Taro000/req-to-design

# list the skills without installing
npx skills add Taro000/req-to-design --list

# one skill, for Claude Code only, available in every project
npx skills add Taro000/req-to-design --skill design-review -a claude-code -g
```

The skills work best after the quality chain (`npx skills add Taro000/cuj-to-slo`). Without it, give the same information yourself: users and CUJs, functional requirements with acceptance criteria, prioritized quality requirements, and measurable targets.

## Use

Run each step in a fresh request:

1. "Derive the architecture drivers from docs/quality/. Technology constraints: … Budget and deadline: … Teams: … Roadmap: …"
2. "Design the architecture from the drivers."
3. In a new session: "Review the architecture." If there are critical or major findings: "Re-run the architecture stage to resolve the findings." If that changed the architecture, review it again in a new session.
4. "Write the high-level design." Review it in a new session, and resolve its findings the same way.
5. "Write the detailed design of ELM-02." Repeat for every component listed in `docs/design/4-detailed-design.md`, and review each one.

Each stage drafts everything first. It then rates every point it was unsure of by breadth (how much depends on it) and severity (the harm if the draft is wrong), and asks you only about the points where either is high. The ranking and the decisions that accept a risk, a cost or a debt are rated the same way; when they are asked, your answer is the decision. Every other point is kept as drafted and recorded as an assumption, which the skill lists at the end for you to skim and correct if you want. Every judgment is marked `stated`, `inferred`, `assumed` or `confirmed`, so you can see what came from you, what the agent decided, and what nobody has checked yet.

Each stage is a long task. The detailed design runs once per component and, for a mid-sized system, produces more documents than the requirements did. Plan time to review them and to answer the questions that matter most.

Reports and items show only the current state; git keeps the history. Each skill ends its run by committing the files it wrote, with the reasons in the commit message, and the next run reads what changed since then.

Questions and artifacts follow your language and your project's documentation language. The skills themselves are written in English.

## Artifacts

```
docs/design/
├── 1-architecture-drivers.md … 3-high-level-design.md   one report per stage
├── 4-detailed-design.md, 4-detailed-design/              an index, and one report per component
├── reviews/                                              the latest review of each stage
├── design-context.yaml                                   the design context: constraints, teams, changes, stakeholders, current structure
├── drv/  dec/  elm/  ifc/  dat/  mod/  fnd/             one YAML file per item
├── das/                                                  one YAML file per assumption made without asking
└── ifc/specs/                                            OpenAPI and AsyncAPI documents
```

YAML keys and IDs are fixed in English, so every stage can read every other stage's files. Views, flows and state diagrams are Mermaid diagrams inside the reports.

## What the skills will not do

- Write to the quality chain. Changes to the requirements that the design calls for are written in the reports as issues; you decide what to do with them.
- Invent business numbers. Targets, deadlines, volumes and budgets come from you or from the quality chain; missing ones stay named placeholders. Design parameters such as timeouts are proposed as provisional values, with what they are based on.
- Write code. The detailed design stops where coding starts, and uses a language-neutral notation.
- Decide business priorities for you. The driver ranking, accepted risks and debts, deferrals and design parameters are business decisions: the ones with high breadth or severity are asked, and the rest are adopted provisionally and recorded as assumptions, never presented as decided.
- Write runbooks, business procedures or training. The design of the infrastructure is in scope; operating it is not.

## Maintaining

`references/conventions.md`, `references/artifacts.md` and `references/glossary.md` are identical in every skill, because `npx skills add --skill` installs a single skill directory. Edit them in `shared/`, then run:

```sh
scripts/sync-shared.sh          # copy shared/ into every skill
scripts/sync-shared.sh --check  # fail if any copy differs
```

## License

MIT
