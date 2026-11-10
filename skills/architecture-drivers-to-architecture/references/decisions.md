# Design decisions

## Contents
- When to write a decision
- Options
- Comparing options
- Sensitive points and trade-offs
- Business decisions
- Design parameters
- Debt
- Deferral
- Existing systems and transition
- Example

## When to write a decision

A decision answers one question the design must settle ("how does checkout survive a provider outage?"), for named drivers. Write one when:

- a driver needs a response that the design does not produce yet;
- a functional requirement states behaviour that needs a mechanism spanning elements, or a demanding one (failover, idempotency, reconciliation);
- the platforms and device support are not all fixed by a technology constraint (`structures-and-mechanisms.md`, "Platforms and device support");
- a design concern has more than one sensible answer;
- a constraint leaves a choice open (which managed database the platform offers);
- a later stage would otherwise make the choice silently.

Do not write decisions for what any competent implementation would do the same way. Those go in the "standard practice is enough" lines.

## Options

Write at least two options that someone could really choose. "Keep what exists" or "do nothing" is a real option when it could meet the driver. When only one option is possible because a constraint forces it, write that option and name the constraint.

For each option, write what it does for the drivers in question (`effect`) and what it costs (`cost`: work, money, complexity, risk). Keep the options comparable: the same drivers, at the same level of detail.

## Comparing options

1. Drop the options that break a non-negotiable constraint, and say which and why.
2. Compare the rest driver by driver, in rank order: does each option meet the driver, meet it in part, or fail it? A short table in the report is enough.
3. Prefer the option that meets the highest-ranked drivers. Use the lower-ranked drivers to choose between options that tie.
4. Do not add up scores across unlike drivers unless the business has set the weights. Adding latency points to cost points hides a choice the business should make.
5. When options tie on every driver, choose the one that is easier to undo, and say so.

Record the chosen option, the rationale (which drivers decided it), each rejected option with the reason it lost, the gains and the costs. Write in `assumptions` what the decision relies on (a provider's promise, a fact about the users' devices). One that you were unsure of and did not ask about is a DAS: list it in `premises` as well. Refer to the quality chain's items and the design context's entries by ID; do not copy their statements into the decision.

## Sensitive points and trade-offs

- A sensitive point is a property of the decision that the response depends on strongly: a timeout, a threshold, a cache lifetime, the number of instances. Name it, so that later stages treat it as a design parameter, and so that the people who run the system know what to tune.
- A trade-off is a decision that helps one driver and hurts another. Record it on the decision (`trade_offs`) and in both drivers' walkthroughs, with the size of the effect as far as you can judge it ("adds up to 0.2 s to checkout").

## Business decisions

These are business decisions as much as technical ones: a decision that accepts a risk, a cost in money or contracts, a weaker driver or a debt; the deferral of a point of this stage's full-depth kinds, or of one that rates high ("Deferral"); a provisional design parameter; and the rejection of a finding that leaves a risk in place. Every decision lists its costs; that alone does not make it a business decision. Rate each one like any uncertain point ("Decisions" in `conventions.md`):

- If either rating is high, ask. The answer is the decision: the judgment becomes `confirmed`, and the question and its answer go under "Decisions" in the report.
- Otherwise, adopt the drafted decision provisionally: write a DAS of kind `decision`, list it in the `premises` of the decision and of every item that depends on it, and mark those items `assumed`.

Never write a provisional decision as if it were decided.

## Design parameters

Timeouts, retry counts, pool sizes and cache lifetimes are design decisions too. Propose a provisional value with its basis (a stated number it derives from, a calculation, the default of a named library or service), and list it as a sensitive point when the response depends on it.

A provisional parameter is a business decision. Most rate low or medium, because they change one element and are tuned in operation anyway, so they become a DAS of kind `decision`. Ask about one when either rating is high: it sizes something that is paid for or hard to change later (the capacity in a contract, the number of partitions of stored data), or a primary driver fails when the value is wrong and nobody notices. A parameter that is part of an option you ask about anyway is answered with it.

## Debt

When a decision knowingly takes a cheaper option that weakens a driver, to meet the deadline or to save money, record the debt in the decision's `debt`: what is weaker, why it was accepted, and when or on which event it must be repaid. Debt is a business decision. Debt that nobody decided on is a defect that will be found later.

## Deferral

Deferring is the default for what this stage need not decide in full: "Decision depth" and "Hand-offs" in `conventions.md` give the rule for every stage, and the full-depth kinds of stage 2. A point outside those kinds that does not rate high gets its bounds here when several elements or later stages must keep one promise about it, and its detail is left to the stage that decides it, with a hand-off where `conventions.md` asks for one. That is not a business decision, and it is neither asked nor recorded as an assumption. For example, decide here the order of the timeouts along a call path and what idempotency keys cover, and leave to later stages the values of the timeouts and the key of each operation.

Deferring a point of stage 2's full-depth kinds, or one that rates high, is a business decision ("Business decisions"): a vendor chosen only once its contract is signed, or a structure settled only after a pilot. Address its hand-off to this stage, with the event that settles it as the trigger.

## Existing systems and transition

For an existing system, the first option of every decision is to keep what exists, and a change must earn its cost against the drivers. When several elements change, write the order of the changes as decisions, so that the system works after each step. For example: first put the payment adapter in front of the current provider, then add the second provider behind it.

## Example

How does checkout survive a provider outage (DRV-02)?

| Driver (rank) | One provider, retries with back-off | Second provider with failover |
|---|---|---|
| DRV-02 survive an outage (2) | fails: retries cannot help during an outage | meets |
| DRV-09 release date (3) | meets | in part: it cannot be ready before the sale, so it ships right after it |
| DRV-10 add a provider later (10) | in part | meets |
| DRV-07 running cost (11) | meets | in part: a second contract |

DRV-02 ranks above DRV-09, so the second provider wins. The business already chose when it ships (stage 1, question 5): right after the spring sale, and until then an outage of the provider stops checkout. That is not asked again; the decision records it as a debt, repaid right after the sale. The second contract ties the system to another vendor, which is high severity, so it is asked (question 2), with the starting failover threshold as part of the drafted option. The decision records that threshold as a sensitive point, and a trade-off with DRV-07.
