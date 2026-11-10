"""Tests for shared/scripts: the YAML reader, the checks and the generated tables.

Run from the repository root:  python3 -m unittest discover -s tests
"""

import glob
import io
import os
import re
import shutil
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "shared", "scripts"))
sys.dont_write_bytecode = True

import check  # noqa: E402
import design_lib as lib  # noqa: E402
import tables  # noqa: E402
import yaml_lite  # noqa: E402

S1, S2, S3, S4 = (lib.STAGE_SKILLS[n] for n in (1, 2, 3, 4))


def d(text):
    return textwrap.dedent(text).lstrip("\n")


QUALITY = {
    "context.yaml": d("""
        system: {name: Online store, boundary: Storefront and checkout, purpose: Sell online, basis: stated}
        constraints: []
        external_systems:
          - {id: EXT-01, role: Payment provider, creates_data: true, source: PRD, basis: stated}
        design_inputs: []
        users:
          - {id: USR-01, name: Buyer, category: primary, data_role: consumer, considered: true, exclusion_reason: null, basis: stated}
        cujs:
          - {id: CUJ-01, name: Purchase, users: [USR-01], user_goal: Buy items, steps: [Cart, Payment], outcomes: [], basis: stated, basis_note: null}
        operational_facts:
          - {id: OPF-01, fact: Load balancer logs exist, source: Architecture notes, basis: stated}
        """),
    "fr/FR-01.yaml": d("""
        id: FR-01
        title: Checkout
        status: active
        basis: stated
        basis_note: null
        premises: []
        statement: The buyer pays for the cart.
        acceptance_criteria:
          - Given a cart, when the buyer pays, then an order is created.
          - Given a declined card, when the buyer pays, then the decline is shown.
        """),
    "fr/FR-02.yaml": d("""
        id: FR-02
        title: Order history
        status: active
        basis: stated
        basis_note: null
        premises: []
        statement: The buyer sees past orders.
        acceptance_criteria:
          - Given past orders, when the buyer opens the history, then they are listed.
        """),
    "sli/SLI-01.yaml": d("""
        id: SLI-01
        title: Checkout latency
        status: active
        basis: inferred
        basis_note: null
        premises: [OPF-01]
        vantage: system-boundary
        existing_source: OPF-01
        """),
    "qas/QAS-01.yaml": d("""
        id: QAS-01
        title: Target of checkout latency
        status: open
        stage: 4
        kind: decision
        statement: Checkouts answer within the provisional target.
        why_unsure: No baseline
        breadth: low
        severity: high
        rating_note: One NFR rests on it
        answer: null
        answered_in: null
        """),
}

DESIGN = {
    "design-context.yaml": d("""
        read_from:
          quality_chain: docs/quality/
          other: [Kick-off notes]
        technology_constraints:
          - id: TC-01
            statement: Card payments go through the provider
            kind: external-service
            source: context.yaml EXT-01
            basis: stated
        project_constraints:
          - {id: PC-01, kind: deadline, statement: Release before the sale, source: Kick-off notes, basis: stated}
        teams:
          - {id: TEAM-01, name: Store team, owns: Everything, basis: stated}
        anticipated_changes: []
        stakeholders: []
        as_is: null
        """),
    "drv/DRV-01.yaml": d("""
        id: DRV-01
        title: Checkout answers quickly
        status: active
        basis: inferred
        basis_note: The target rests on QAS-01, answered in question 1
        premises: [OPF-01, QAS-01]
        kind: quality
        statement: Checkout confirms orders quickly
        sources: [FR-01, SLI-01]
        concern_of: [USR-01]
        scenario:
          source: Buyers (USR-01)
          stimulus: Submit the checkout
          artifact: Checkout (FR-01)
          environment: Normal operation
          response: The order is confirmed
          measure: SLI-01
        negotiable: null
        derived_from: []
        priority: {business: high, business_reason: Emphasized, difficulty: high, difficulty_reason: Provider latency, rank: 1}
        primary: true
        conflicts:
          - {with: DRV-02, note: Latency work takes time}
        placeholders: []
        """),
    "drv/DRV-02.yaml": d("""
        id: DRV-02
        title: Release before the sale
        status: active
        basis: stated
        basis_note: null
        premises: [PC-01]
        kind: constraint
        statement: First release before the sale
        sources: [PC-01]
        concern_of: [USR-01]
        scenario: null
        negotiable: false
        derived_from: []
        priority: {business: high, business_reason: Stated, difficulty: medium, difficulty_reason: Small team, rank: 2}
        primary: true
        conflicts:
          - {with: DRV-01, note: Latency work takes time}
        placeholders: []
        """),
    "dec/DEC-01.yaml": d("""
        id: DEC-01
        title: One application and a managed database
        status: active
        basis: assumed
        basis_note: The database size is assumed (DAS-01)
        premises: [TC-01, DAS-01]
        stage: architecture
        question: How is the system split?
        addresses: [DRV-01, DRV-02]
        options:
          - {name: One application, effect: Simple, cost: Little}
          - {name: Services, effect: Independent, cost: More work}
        chosen: One application
        rationale: The deadline (DRV-02) leaves no time for services
        rejected:
          - {option: Services, reason: Too much work before the sale}
        gains: [Simple]
        costs: [One deployable]
        sensitive_points: []
        trade_offs: []
        assumptions: ["The database fits one instance (DAS-01)"]
        depends_on: []
        parameters:
          - {name: pool_size, value: 10, basis: Library default}
        debt: null
        as_is: new
        """),
    "dec/DEC-02.yaml": d("""
        id: DEC-02
        title: Web framework of the Store API
        status: active
        basis: inferred
        basis_note: null
        premises: []
        stage: detailed-design
        question: Which framework serves the Store API?
        addresses: [IFC-01]
        options:
          - {name: Framework A, effect: Known to the team, cost: None}
          - {name: Framework B, effect: Faster, cost: New to the team}
        chosen: Framework A
        rationale: The team knows it (DRV-02)
        rejected:
          - {option: Framework B, reason: New to the team}
        gains: [Speed of work]
        costs: [Slower than B]
        sensitive_points: []
        trade_offs: []
        assumptions: []
        depends_on: [DEC-01]
        parameters: []
        debt: null
        as_is: new
        """),
    "das/DAS-01.yaml": d("""
        id: DAS-01
        title: The database fits one instance
        status: open
        stage: 2
        kind: judgment
        statement: The order volume fits one database instance
        why_unsure: No volume is given
        breadth: low
        severity: medium
        rating_note: Only DEC-01 depends on it
        answer: null
        answered_in: null
        """),
    "elm/ELM-01.yaml": d("""
        id: ELM-01
        title: Store API
        status: active
        basis: inferred
        basis_note: Follows DEC-01; the database link follows FND-01
        premises: []
        kind: component
        name: Store API
        responsibility: Checkout and orders
        functions: [FR-01, FR-02]
        drivers: [DRV-01]
        decisions: [DEC-01]
        team: TEAM-01
        technology: A web framework (DEC-02)
        runs_on: ELM-03
        depends_on: [ELM-02, ELM-04]
        as_is: new
        """),
    "elm/ELM-02.yaml": d("""
        id: ELM-02
        title: Store database
        status: active
        basis: inferred
        basis_note: null
        premises: []
        kind: data-store
        name: Store database
        responsibility: Holds orders
        functions: []
        drivers: [DRV-01]
        decisions: [DEC-01]
        team: TEAM-01
        technology: PostgreSQL
        runs_on: ELM-03
        depends_on: []
        as_is: new
        """),
    "elm/ELM-03.yaml": d("""
        id: ELM-03
        title: Platform
        status: active
        basis: inferred
        basis_note: null
        premises: []
        kind: node
        name: Platform
        responsibility: Runs the containers
        functions: []
        drivers: [DRV-02]
        decisions: [DEC-01]
        team: TEAM-01
        technology: Managed containers
        runs_on: null
        depends_on: []
        as_is: new
        """),
    "elm/ELM-04.yaml": d("""
        id: ELM-04
        title: Payment provider
        status: active
        basis: stated
        basis_note: null
        premises: [EXT-01]
        kind: external-system
        name: Payment provider
        responsibility: Takes card payments
        functions: []
        drivers: [DRV-01]
        decisions: []
        team: null
        technology: null
        runs_on: null
        depends_on: []
        as_is: new
        """),
    "elm/ELM-05.yaml": d("""
        id: ELM-05
        title: Storefront
        status: active
        basis: inferred
        basis_note: null
        premises: []
        kind: component
        name: Storefront
        responsibility: Pages and the cart
        functions: [FR-01, FR-02]
        drivers: [DRV-01]
        decisions: [DEC-01]
        team: TEAM-01
        technology: A web framework
        runs_on: ELM-03
        depends_on: [ELM-01]
        as_is: new
        """),
    "ifc/IFC-01.yaml": d("""
        id: IFC-01
        title: Checkout API
        status: active
        basis: inferred
        basis_note: The binding of SLI-01 decides HND-01
        premises: [OPF-01]
        kind: http
        name: Checkout API
        provider: ELM-01
        consumers: [ELM-05]
        functions: [FR-01, FR-02]
        operations:
          - {name: POST /v1/checkout, does: Confirms the cart as an order}
          - {name: "GET /v1/orders/{orderId}", does: Reads an order}
        format: JSON
        protocol: HTTPS
        auth: Session cookie
        errors:
          - {case: "POST /v1/checkout: the card is declined", signal: 402 with code CARD_DECLINED, caller_does: Show the decline}
          - {case: "GET /v1/orders/{orderId}: no such order", signal: 404 NOT_FOUND, caller_does: Show the history again}
        idempotency: One key per order
        timing:
          timeout: 15 s
          ordering: null
          delivery: null
        versioning: Version in the path
        observability: Logs request_id
        sli_bindings:
          - sli: SLI-01
            events: Each POST /v1/checkout at the load balancer
            fields: [request_id, status, elapsed]
            method: The load balancer logs (OPF-01)
        spec: ifc/specs/checkout.openapi.yaml
        as_is: new
        """),
    "ifc/IFC-02.yaml": d("""
        id: IFC-02
        title: Checkout screen
        status: active
        basis: inferred
        basis_note: null
        premises: []
        kind: screen
        name: Checkout screen
        provider: ELM-05
        consumers: [USR-01]
        functions: [FR-01, FR-02]
        operations:
          - {name: Checkout, does: Pays for the cart}
        format: HTML
        protocol: A browser
        auth: Session cookie
        errors:
          - {case: The card is declined, signal: A message on the screen, caller_does: Choose another card}
        idempotency: null
        timing: {timeout: null, ordering: null, delivery: null}
        versioning: null
        observability: null
        sli_bindings: []
        spec: null
        as_is: new
        """),
    "ifc/specs/checkout.openapi.yaml": d("""
        openapi: 3.1.0
        info: {title: Checkout API, version: 1.0.0}
        paths:
          /v1/checkout:
            post:
              responses:
                '201': {description: Created}
                '402': {description: CARD_DECLINED}
          /v1/orders/{orderId}:
            get:
              responses:
                '200': {description: The order}
                '404': {description: NOT_FOUND}
        """),
    "dat/DAT-01.yaml": d("""
        id: DAT-01
        title: Order
        status: active
        basis: inferred
        basis_note: null
        premises: []
        entity: Order
        owner: ELM-01
        store: ELM-02
        key_attributes: [order_id]
        relations: []
        consistency: One transaction
        retention: T_order_retention
        classification: personal
        drivers: [DRV-01]
        sli_bindings: []
        as_is: new
        """),
    "mod/MOD-01.yaml": d("""
        id: MOD-01
        title: Checkout handler
        status: active
        basis: inferred
        basis_note: null
        premises: []
        component: ELM-01
        name: Checkout handler
        responsibility: Turns a cart into an order
        visibility: public
        interface:
          - {operation: "checkout(cart: Cart) -> Order", pre: The cart is not empty, post: An order exists, errors: []}
        invariants: []
        depends_on: []
        functions: [FR-01, FR-02]
        realizes: ["IFC-01 POST /v1/checkout", "IFC-01 GET /v1/orders/{orderId}"]
        drivers: [DRV-01]
        decisions: [DEC-02]
        behaviour: "Report section: MOD-01 Checkout handler"
        verification:
          - {checks: FR-01, how: Unit tests}
        parameters:
          - {name: cart_limit, value: 50, basis: Library default}
        as_is: new
        """),
    "hnd/HND-01.yaml": d("""
        id: HND-01
        title: Where checkouts can be counted
        status: decided
        basis: inferred
        basis_note: The point is stated in SLI-01's basis_note
        premises: [OPF-01]
        from: requirements-to-architecture-drivers
        to: architecture-to-high-level-design
        component: null
        origin: [SLI-01]
        what: Where the system can see each checkout, so that SLI-01 counts it at its vantage
        bounds: SLI-01's unit event and counting rules, unchanged
        trigger: The next run of stage 3
        resolution: Decided in IFC-01's sli_bindings
        """),
    "hnd/HND-02.yaml": d("""
        id: HND-02
        title: Where the cart limit is kept
        status: open
        basis: inferred
        basis_note: null
        premises: []
        from: high-level-design-to-detailed-design
        to: implementation
        component: ELM-01
        origin: [MOD-01]
        what: Where cart_limit is kept and how MOD-01 reads it
        bounds: MOD-01's interface
        trigger: When MOD-01 is implemented
        resolution: null
        """),
    "fnd/FND-01.yaml": d("""
        id: FND-01
        title: The Store API does not say where orders live
        status: accepted
        basis: inferred
        basis_note: null
        premises: []
        raised_by: design-review
        raised_in: reviews/2-architecture.md
        to: architecture-drivers-to-architecture
        targets: [ELM-01]
        severity: minor
        evidence: ELM-01 depends on no data store
        suggestion: Add ELM-02 to depends_on
        resolution: Added ELM-02 to the dependencies of ELM-01
        """),
}

HEADER = "Status: answers applied · Updated: 2026-11-10 · Inputs as of: none · Stage %s"


def blocks(*names, **hand):
    out = []
    for name in names:
        out.append("<!-- generated: %s -->\n%s<!-- /generated -->\n" % (name, hand.get(name.replace("-", "_"), "")))
    return "\n".join(out)


REPORTS = {
    "1-architecture-drivers.md": "# Architecture drivers\n\n" + HEADER % "1 of 4" + "\n\n" + blocks(
        "design-context", "drivers", "ranking", "conflicts", "findings", "assumptions",
        design_context="| ID | Label | Kind | Source | Basis |\n|---|---|---|---|---|\n"
                       "| TC-01 | Card payments through the provider | | | |\n| PC-01 | Release before the sale | | | |\n"
                       "| TEAM-01 | Store team | | | |\n",
        conflicts="| Drivers | Resolved by |\n|---|---|\n| DRV-01, DRV-02 | The business (question 2) |\n"),
    "2-architecture.md": "# Architecture\n\n" + HEADER % "2 of 4" + "\n\n" + blocks(
        "decisions", "elements", "parameters", "findings", "assumptions",
        parameters="| Parameter | DEC | Decided in |\n|---|---|---|\n| pool_size | DEC-01 | question 1 |\n"),
    "3-high-level-design.md": "# High-level design\n\n" + HEADER % "3 of 4" + "\n\n" + blocks(
        "decisions", "interfaces", "sli-bindings", "data", "criteria", "findings", "assumptions",
        criteria="| FR | Criterion | IFCs | Flow |\n|---|---|---|---|\n| FR-01 | 1 | | Checkout |\n"
                 "| FR-01 | 2 | | Checkout, declined card |\n| FR-02 | 1 | | Order history |\n"),
    "4-detailed-design.md": "# Detailed design index\n\nUpdated: 2026-11-10 · Inputs as of: none\n\n" + blocks("components"),
    "4-detailed-design/ELM-01.md": "# Detailed design of the Store API\n\n" + HEADER % "4 of 4" + "\n\n" + blocks(
        "modules", "decisions", "parameters", "findings", "assumptions",
        parameters="| Parameter | MOD | Decision | Budget or timeout it fits |\n|---|---|---|---|\n"
                   "| cart_limit | MOD-01 | question 1 | Inside every request |\n"),
    "reviews/2-architecture.md": "# Design review: architecture\n\n" + HEADER % "2" + "\n\n" + blocks(
        "findings", "assumptions"),
}


class Fixture(object):
    """A small design that passes every check, written to a temporary directory."""

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="design-check-")
        self.design = os.path.join(self.root, "docs", "design")
        self.quality = os.path.join(self.root, "docs", "quality")
        for base, files in ((self.quality, QUALITY), (self.design, DESIGN), (self.design, REPORTS)):
            for rel, text in files.items():
                self.write(os.path.join(base, rel), text)
        self.tables()

    def write(self, path, text):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def read(self, rel):
        with open(os.path.join(self.design, rel), encoding="utf-8") as f:
            return f.read()

    def edit(self, rel, old, new):
        text = self.read(rel)
        if old not in text:
            raise AssertionError("%r not in %s" % (old, rel))
        self.write(os.path.join(self.design, rel), text.replace(old, new, 1))

    def tables(self):
        with redirect_stdout(io.StringIO()):
            return tables.main(["--design", self.design, "--quality", self.quality])

    def check(self, skill=None):
        project = lib.Project(self.design, self.quality)
        checker = check.Checker(project, lib.Glossary(), skill)
        return checker.run()

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)


def summary(problems):
    return ["%s %s:%s %s%s" % (p.rule, p.path, p.line, p.message, " (waiting for %s)" % p.waiting if p.waiting else "")
            for p in problems]


class YamlReaderTest(unittest.TestCase):
    def test_cut_value_and_duplicate_key(self):
        doc = yaml_lite.load("basis_note: Confirmed in question #4 and DEC-02\ntitle: a\ntitle: b\n")
        kinds = sorted(n.kind for n in doc.notes)
        self.assertEqual(kinds, ["comment-after-value", "duplicate-key"])
        self.assertEqual(doc.data["basis_note"], "Confirmed in question")

    def test_comment_after_closed_values_is_fine(self):
        doc = yaml_lite.load("a: null  # x\nb: []  # x\nc: 'q'  # x\nd: 3  # x\n")
        self.assertEqual(doc.notes, [])

    def test_errors_carry_the_line(self):
        with self.assertRaises(yaml_lite.YAMLError) as cm:
            yaml_lite.load("a: 1\nb: Retry: then fail\n")
        self.assertEqual(cm.exception.line, 2)

    def test_block_scalars_and_flow(self):
        doc = yaml_lite.load(d("""
            a: |
              one
                two
            b: >-
              x
              y
            c: [p, 'q, r', {k: v}]
            d:
            - e: 1
              f: 2
            """))
        self.assertEqual(doc.data, {"a": "one\n  two\n", "b": "x y", "c": ["p", "q, r", {"k": "v"}],
                                    "d": [{"e": 1, "f": 2}]})

    def test_examples_in_the_skills_parse(self):
        files = glob.glob(os.path.join(ROOT, "shared", "*.md")) + glob.glob(os.path.join(ROOT, "skills", "*", "**",
                                                                                         "*.md"), recursive=True)
        count = 0
        for path in files:
            with open(path, encoding="utf-8") as f:
                text = f.read()
            for m in re.finditer(r"```yaml\n(.*?)```", text, re.S):
                count += 1
                line = text.count("\n", 0, m.start()) + 2
                try:
                    doc = yaml_lite.load(m.group(1))
                except yaml_lite.YAMLError as e:
                    self.fail("%s:%d: %s" % (path, line, e))
                before = text[:m.start()].rstrip().split("\n")[-1]
                if re.search(r"`docs/design/[^`]+\.yaml`", before):
                    cut = [n for n in doc.notes if n.kind == "comment-after-value"]
                    self.assertEqual(cut, [], "%s:%d: an example item file has a comment after a value" % (path, line))
        self.assertGreater(count, 20)

    def test_same_as_pyyaml_when_installed(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML is not installed")
        for path in glob.glob(os.path.join(ROOT, "skills", "*", "references", "*.md")):
            with open(path, encoding="utf-8") as f:
                for m in re.finditer(r"```yaml\n(.*?)```", f.read(), re.S):
                    self.assertEqual(yaml_lite.load(m.group(1)).data, yaml.safe_load(m.group(1)))


class CheckTest(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def tearDown(self):
        self.f.close()

    def rules(self, skill=None):
        return sorted(set(p.rule for p in self.f.check(skill) if p.waiting is None))

    def assertFinds(self, rule, text=None, skill=None):
        problems = [p for p in self.f.check(skill) if p.rule == rule and p.waiting is None]
        if text:
            problems = [p for p in problems if text in p.message]
        self.assertTrue(problems, "%s%s not found in:\n%s" % (rule, " (%s)" % text if text else "",
                                                             "\n".join(summary(self.f.check(skill)))))
        return problems

    def test_fixture_is_clean(self):
        self.assertEqual(summary(self.f.check()), [])

    def test_yaml_error_and_cut_value(self):
        self.f.edit("dec/DEC-01.yaml", "title: One application and a managed database", "title: Retry: then fail")
        self.f.edit("dec/DEC-02.yaml", "basis_note: null", "basis_note: Confirmed in question #2")
        self.assertFinds("yaml")
        self.assertFinds("cut-value")

    def test_ifc_function_not_in_provider(self):
        self.f.edit("elm/ELM-01.yaml", "functions: [FR-01, FR-02]", "functions: [FR-01]")
        problems = self.assertFinds("allocation", "FR-02, which its provider ELM-01")
        self.assertEqual(problems[0].owner, S3)

    def test_waiting_for_an_open_finding(self):
        self.f.edit("elm/ELM-01.yaml", "functions: [FR-01, FR-02]", "functions: [FR-01]")
        self.f.write(os.path.join(self.f.design, "fnd/FND-02.yaml"), d("""
            id: FND-02
            title: ELM-01 lacks FR-02
            status: open
            basis: inferred
            basis_note: null
            premises: []
            raised_by: architecture-to-high-level-design
            raised_in: 3-high-level-design.md
            to: architecture-drivers-to-architecture
            targets: [ELM-01]
            severity: minor
            evidence: IFC-01 carries FR-02, and ELM-01 does not
            suggestion: Allocate FR-02 to ELM-01
            resolution: null
            """))
        waiting = [p for p in self.f.check() if p.rule == "allocation" and "FR-02, which its provider" in p.message]
        self.assertEqual([p.waiting for p in waiting], ["FND-02"])

    def test_module_driver_not_in_component(self):
        self.f.edit("mod/MOD-01.yaml", "drivers: [DRV-01]", "drivers: [DRV-01, DRV-02]")
        self.assertFinds("allocation", "DRV-02, which its component ELM-01")

    def test_operation_realized_twice_and_unknown_operation(self):
        self.f.write(os.path.join(self.f.design, "mod/MOD-02.yaml"), self.f.read("mod/MOD-01.yaml")
                     .replace("MOD-01", "MOD-02").replace('"IFC-01 GET /v1/orders/{orderId}"', '"IFC-01 GET /v1/order"'))
        self.assertFinds("allocation", "is realized by MOD-01, MOD-02")
        self.assertFinds("allocation", "has no operation named 'GET /v1/order'")

    def test_spec_operations_and_statuses(self):
        self.f.edit("ifc/specs/checkout.openapi.yaml", "'402': {description: CARD_DECLINED}", "'400': {description: x}")
        self.f.edit("ifc/specs/checkout.openapi.yaml", "  /v1/orders/{orderId}:", "  /v1/carts:\n    get: {}\n  /v1/orders/{id}:")
        self.assertFinds("spec", "has no 402 response")
        self.assertFinds("spec", "error code CARD_DECLINED")
        self.assertFinds("spec", "GET /v1/carts is in the spec")

    def test_unknown_retired_and_wrong_kind(self):
        self.f.edit("dec/DEC-01.yaml", "rationale: The deadline (DRV-02)", "rationale: The deadline (DRV-02, DEC-99)")
        self.f.edit("dec/DEC-01.yaml", "depends_on: []", "depends_on: [DRV-01]")
        self.f.edit("elm/ELM-01.yaml", "runs_on: ELM-03", "runs_on: ELM-02")
        self.f.edit("drv/DRV-02.yaml", "status: active", "status: retired")
        self.assertFinds("unknown-id", "DEC-99")
        self.assertFinds("wrong-kind", "depends_on holds DRV-01")
        self.assertFinds("wrong-kind", "runs_on names ELM-02, an element of kind data-store")
        self.assertFinds("retired-ref", "DRV-02")

    def test_basis_and_orphan_assumption(self):
        self.f.edit("dec/DEC-01.yaml", "basis: assumed", "basis: inferred")
        self.assertFinds("basis", "open DAS-01")
        self.f.edit("dec/DEC-01.yaml", "premises: [TC-01, DAS-01]", "premises: [TC-01]")
        self.assertFinds("orphan-assumption")
        self.f.edit("drv/DRV-01.yaml", "basis_note: The target rests on QAS-01, answered in question 1",
                    "basis_note: null")
        self.assertFinds("basis", "QAS-01 (not cited")

    def test_findings(self):
        self.f.edit("elm/ELM-01.yaml", "; the database link follows FND-01", "")
        self.f.edit("fnd/FND-01.yaml", "to: architecture-drivers-to-architecture", "to: design-review")
        self.assertFinds("finding", "no item cites FND-01")
        self.assertFinds("finding", "to is 'design-review'")

    def test_allocation_gaps(self):
        self.f.edit("elm/ELM-05.yaml", "functions: [FR-01, FR-02]", "functions: [FR-01]")
        self.f.edit("elm/ELM-01.yaml", "functions: [FR-01, FR-02]", "functions: [FR-01]")
        self.f.edit("elm/ELM-03.yaml", "drivers: [DRV-02]", "drivers: []")
        self.f.edit("elm/ELM-05.yaml", "team: TEAM-01", "team: null")
        self.assertFinds("allocation", "FR-02 is allocated to no component")
        self.assertFinds("allocation", "DRV-02 is carried by no element")
        self.assertFinds("allocation", "this component has none")

    def test_legacy_and_missing_fields(self):
        self.f.edit("dat/DAT-01.yaml", "status: active", "status: draft\nversion: 2")
        self.f.edit("dat/DAT-01.yaml", "retention: T_order_retention\n", "")
        self.assertFinds("legacy", "version, status: draft")
        self.assertFinds("missing-field", "retention")

    def test_handoffs(self):
        self.f.edit("hnd/HND-02.yaml", "component: ELM-01", "component: null")
        self.f.edit("hnd/HND-02.yaml", "trigger: When MOD-01 is implemented", "trigger: null")
        self.f.edit("ifc/IFC-01.yaml", "basis_note: The binding of SLI-01 decides HND-01", "basis_note: null")
        self.f.edit("hnd/HND-01.yaml", "to: architecture-to-high-level-design", "to: design-review")
        self.assertFinds("handoff", "names the component it concerns")
        self.assertFinds("handoff", "says when it falls due")
        self.assertFinds("handoff", "no item cites HND-01")
        self.assertFinds("handoff", "to is 'design-review'")

    def test_deferral_on_a_decision_is_legacy(self):
        self.f.edit("dec/DEC-01.yaml", "debt: null", "debt: null\ndeferred: true\nrevisit_when: After the pilot")
        self.assertFinds("legacy", "deferred, revisit_when")

    def test_module_cycle(self):
        self.f.write(os.path.join(self.f.design, "mod/MOD-02.yaml"), self.f.read("mod/MOD-01.yaml")
                     .replace("MOD-01", "MOD-02").replace("depends_on: []", "depends_on: [MOD-01]")
                     .replace("realizes: [\"IFC-01 POST /v1/checkout\", \"IFC-01 GET /v1/orders/{orderId}\"]",
                              "realizes: []"))
        self.f.edit("mod/MOD-01.yaml", "depends_on: []", "depends_on: [MOD-02]")
        self.assertFinds("cycle", "MOD-01 -> MOD-02 -> MOD-01")

    def test_conflict_on_one_driver(self):
        self.f.edit("drv/DRV-02.yaml", "conflicts:\n  - {with: DRV-01, note: Latency work takes time}", "conflicts: []")
        self.assertFinds("conflict")

    def test_stale_table_and_empty_cell(self):
        self.f.edit("dec/DEC-01.yaml", "title: One application and a managed database", "title: One application")
        self.f.edit("3-high-level-design.md", "| Checkout, declined card |", "|  |")
        self.assertFinds("table", "out of date")
        self.assertFinds("empty-cell", "FR-01 2")
        self.assertNotIn("table", self.rules(skill=S3))  # 2-architecture.md belongs to stage 2

    def test_unbound_sli(self):
        self.f.edit("ifc/IFC-01.yaml", "sli_bindings:\n  - sli: SLI-01", "sli_bindings: []\nx_binding:\n  - sli: SLI-01")
        self.assertFinds("sli-binding", "SLI-01")


class TablesTest(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def tearDown(self):
        self.f.close()

    def test_hand_cells_survive_and_rows_follow_the_items(self):
        text = self.f.read("3-high-level-design.md")
        self.assertIn("| FR-01 | 2 | IFC-01, IFC-02 | Checkout, declined card |", text)
        self.f.edit("elm/ELM-01.yaml", "functions: [FR-01, FR-02]", "functions: [FR-01]")
        self.f.edit("elm/ELM-05.yaml", "functions: [FR-01, FR-02]", "functions: [FR-01]")
        self.f.tables()
        text = self.f.read("3-high-level-design.md")
        self.assertIn("| FR-01 | 2 | IFC-01, IFC-02 | Checkout, declined card |", text)
        self.assertNotIn("| FR-02 | 1 |", text)

    def test_second_run_changes_nothing(self):
        before = dict((rel, self.f.read(rel)) for rel in REPORTS)
        self.f.tables()
        self.assertEqual(before, dict((rel, self.f.read(rel)) for rel in REPORTS))

    def test_index_and_assumptions(self):
        index = self.f.read("4-detailed-design.md")
        self.assertIn("| ELM-01 | Store API | answers applied | 4-detailed-design/ELM-01.md | MOD-01 |", index)
        self.assertIn("| ELM-05 | Storefront | not started | — | — |", index)
        stage1 = self.f.read("1-architecture-drivers.md")
        self.assertIn("| QAS-01 | Target of checkout latency | decision | low | high | DRV-01 |", stage1)
        stage2 = self.f.read("2-architecture.md")
        self.assertIn("| DAS-01 | The database fits one instance | judgment | low | medium | DEC-01 |", stage2)

    def test_every_mark_in_the_templates_works(self):
        templates = {
            "requirements-to-architecture-drivers": ("## Report template", "1-architecture-drivers.md", 6),
            "architecture-drivers-to-architecture": ("## Report template", "2-architecture.md", 5),
            "architecture-to-high-level-design": ("## Report template", "3-high-level-design.md", 7),
            "high-level-design-to-detailed-design": ("## Component report template", "4-detailed-design/ELM-01.md", 5),
            "design-review": ("## Report template", "reviews/2-architecture.md", 2),
        }
        for skill, (heading, rel, count) in templates.items():
            with open(os.path.join(ROOT, "skills", skill, "references", "report-template.md"), encoding="utf-8") as f:
                text = f.read()
            body = re.search(r"```markdown\n(.*?)\n```", text[text.index(heading):], re.S).group(1)
            self.assertEqual(len(tables.OPEN_RE.findall(body)), count, skill)
            project = lib.Project(self.f.design, self.f.quality)
            new_text, problems, written = tables.render_report(project, lib.Glossary(), rel, body)
            self.assertEqual(problems, [], skill)
            self.assertEqual(len(written), count, skill)
        with open(os.path.join(ROOT, "shared", "artifacts.md"), encoding="utf-8") as f:
            text = f.read()
        body = re.search(r"```markdown\n(# Detailed design index.*?)\n```", text, re.S).group(1)
        new_text, problems, written = tables.render_report(lib.Project(self.f.design, self.f.quality), lib.Glossary(),
                                                           "4-detailed-design.md", body)
        self.assertEqual((problems, len(written)), ([], 1))
        self.assertIn("| ELM-01 | Store API | answers applied |", new_text)

    def test_japanese_report(self):
        self.f.write(os.path.join(self.f.design, "2-architecture.md"),
                     "# アーキテクチャ\n\n状態: 下書き · 更新: 2026-11-10\n\n<!-- generated: elements -->\n<!-- /generated -->\n")
        self.f.tables()
        text = self.f.read("2-architecture.md")
        self.assertIn("| ELM | 名前 | 種類 | チーム | 今の構造との差分 |", text)
        self.assertIn("| ELM-02 | Store database | データの置き場所 | TEAM-01 | 新設 |", text)


if __name__ == "__main__":
    unittest.main()
