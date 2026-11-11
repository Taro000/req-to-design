"""Tests for shared/scripts/status.py: stale stages, waiting stages, due reviews and what runs next.

Run from the repository root:  python3 -m unittest discover -s tests
"""

import io
import os
import shutil
import subprocess
import sys
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "shared", "scripts"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True

import design_lib as lib  # noqa: E402
import status  # noqa: E402
from test_scripts import Fixture, HEADER, d  # noqa: E402

S1, S2, S3, S4 = (lib.STAGE_SKILLS[n] for n in (1, 2, 3, 4))
S2B = lib.STAGE_SKILLS["2b"]
QUESTIONS = ("\n## Unanswered questions\n\n| # | Question | Why unsure | Options | Items | Answer |\n"
             "|---|---|---|---|---|---|\n| 3 | Which test runner? | The team has used neither | 1. Vitest (drafted)"
             " 2. Jest | %s | %s |\n")
DIAGRAM = "\n## Views\n\n```mermaid\nflowchart LR\n  ELM-05 --> ELM-01\n```\n"


def finding(ident, to, severity, raised_by, raised_in, targets, status="open", resolution="null"):
    return d("""
        id: %s
        title: A problem
        status: %s
        basis: inferred
        basis_note: null
        premises: []
        raised_by: %s
        raised_in: %s
        to: %s
        targets: [%s]
        severity: %s
        evidence: What the activity showed
        suggestion: What to change
        resolution: %s
        """ % (ident, status, raised_by, raised_in, to, ", ".join(targets), severity, resolution))


@unittest.skipUnless(shutil.which("git"), "git is not installed")
class StatusTest(unittest.TestCase):
    """A design whose stages and reviews have all run, one commit each, in the order the chain runs them."""

    def setUp(self):
        self.f = Fixture()
        for rel, stage in (("reviews/2b-technical-policy.md", "2b"), ("reviews/3-high-level-design.md", "3"),
                           ("reviews/4-detailed-design-ELM-01.md", "4"), ("4-detailed-design/ELM-05.md", "4 of 4"),
                           ("reviews/4-detailed-design-ELM-05.md", "4")):
            self.write(rel, "# Report\n\n" + HEADER % stage + "\n")
        self.git("init", "-q")
        self.commit("requirements-to-architecture-drivers: first run", "../quality", "design-context.yaml", "drv",
                    "1-architecture-drivers.md", "qcr/QCR-01.yaml", "hnd/HND-01.yaml", "quality-chain-requests.md")
        self.commit("architecture-drivers-to-architecture: first run", "elm", "dec/DEC-01.yaml", "das/DAS-01.yaml",
                    "2-architecture.md")
        self.commit("design-review: stage 2", "reviews/2-architecture.md", "fnd/FND-01.yaml")
        self.commit("architecture-to-technical-policy: first run", "pol", "dec/DEC-03.yaml", "das/DAS-02.yaml",
                    "2b-technical-policy.md")
        self.commit("design-review: stage 2b", "reviews/2b-technical-policy.md")
        self.commit("architecture-to-high-level-design: first run", "ifc", "dat", "qcr/QCR-02.yaml",
                    "3-high-level-design.md")
        self.commit("design-review: stage 3", "reviews/3-high-level-design.md")
        self.commit("high-level-design-to-detailed-design: ELM-01", "mod", "dec/DEC-02.yaml", "hnd/HND-02.yaml",
                    "4-detailed-design.md", "4-detailed-design/ELM-01.md")
        self.commit("design-review: stage 4 ELM-01", "reviews/4-detailed-design-ELM-01.md")
        self.commit("high-level-design-to-detailed-design: ELM-05", "4-detailed-design/ELM-05.md")
        self.commit("design-review: stage 4 ELM-05", "reviews/4-detailed-design-ELM-05.md")
        self.assertEqual(self.git("status", "--porcelain"), "")

    def tearDown(self):
        self.f.close()

    def git(self, *args):
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@example.com")
        p = subprocess.run(["git"] + list(args), cwd=self.f.root, env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise AssertionError("git %s: %s" % (" ".join(args), p.stderr.decode()))
        return p.stdout.decode()

    def write(self, rel, text):
        self.f.write(os.path.join(self.f.design, rel), text)

    def touch(self, rel, mark):
        """Change a report's header, as every run does."""
        self.f.edit(rel, "Updated: 2026-11-10", "Updated: 2026-11-10 %s" % mark)

    def commit(self, subject, *paths):
        for path in paths:
            self.git("add", "-A", "--", os.path.join("docs", "design", path))
        self.git("commit", "-q", "-m", subject)
        return self.git("rev-parse", "HEAD").strip()

    def chain(self):
        project = lib.Project(self.f.design, self.f.quality)
        return status.Chain(project, lib.Glossary(), status.Git(self.f.design)).evaluate()

    def states(self, chain=None):
        return dict((u.key, u.state) for u in (chain or self.chain()).units)

    def unit(self, chain, key):
        return next(u for u in chain.units if u.key == key)

    def assertReason(self, chain, key, text):
        reasons = self.unit(chain, key).reasons
        self.assertTrue(any(text in r for r in reasons), "%r not in the reasons of %s: %r" % (text, key, reasons))

    def test_everything_up_to_date(self):
        chain = self.chain()
        self.assertEqual(set(self.states(chain).values()), {"up to date"})
        self.assertEqual(chain.next, [])
        self.assertEqual(chain.waiting, [])
        self.assertIn("Next: nothing; every stage and review is up to date", status.text_output(chain))

    def test_a_finding_of_stage_3_runs_the_chain_from_stage_1_down(self):
        self.write("fnd/FND-02.yaml", finding("FND-02", S1, "major", S3, "3-high-level-design.md", ["DRV-01"]))
        self.touch("3-high-level-design.md", "a")
        self.commit("architecture-to-high-level-design: raise FND-02", "fnd", "3-high-level-design.md")
        chain = self.chain()
        self.assertEqual(self.unit(chain, "1").state, "stale")
        self.assertReason(chain, "1", "FND-02 (major)")
        self.assertEqual([u.key for u in chain.next], ["1"])
        self.assertIs(self.unit(chain, "2").blocked_by, self.unit(chain, "1"))

        # stage 1 accepts it and changes DRV-01: the stages below follow, from the top, without a review
        self.write("fnd/FND-02.yaml", finding("FND-02", S1, "major", S3, "3-high-level-design.md", ["DRV-01"],
                                              "accepted", "Narrowed DRV-01's scenario"))
        self.f.edit("drv/DRV-01.yaml", "statement: Checkout confirms orders quickly",
                    "statement: Checkout confirms orders quickly, at the sale peak too")
        self.touch("1-architecture-drivers.md", "b")
        self.commit("requirements-to-architecture-drivers: accept FND-02", "fnd", "drv", "1-architecture-drivers.md")
        chain = self.chain()
        states = self.states(chain)
        self.assertEqual(states["1"], "up to date")
        for key in ("2", "2b", "3", "4 ELM-01", "4 ELM-05"):
            self.assertEqual(states[key], "stale", key)
            self.assertReason(chain, key, "inputs changed: DRV-01")
        self.assertEqual(states["review 2"], "up to date")
        self.assertEqual([u.key for u in chain.next], ["2"])

        for key, skill, report in (("2", S2, "2-architecture.md"), ("2b", S2B, "2b-technical-policy.md"),
                                   ("3", S3, "3-high-level-design.md")):
            self.touch(report, "c")
            self.commit("%s: follow DRV-01" % skill, report)
            chain = self.chain()
            self.assertEqual(self.unit(chain, key).state, "up to date")
        # stage 3 raised the finding but no review raised it: no review is due, and stage 4 follows
        self.assertEqual(self.states(chain)["review 3"], "up to date")
        self.assertEqual([u.key for u in chain.next], ["4 ELM-01", "4 ELM-05"])

    def test_a_minor_finding_alone_runs_nothing(self):
        self.write("fnd/FND-02.yaml", finding("FND-02", S2, "minor", lib.REVIEW_SKILL, "reviews/2-architecture.md",
                                              ["DEC-01"]))
        self.touch("reviews/2-architecture.md", "a")
        self.commit("design-review: stage 2 again", "fnd", "reviews/2-architecture.md")
        chain = self.chain()
        self.assertEqual(self.unit(chain, "2").state, "up to date")
        self.assertEqual(chain.later()["minor_findings"], {"stage 2": ["FND-02"]})

    def test_a_waiting_stage_holds_back_what_is_below_it_and_resumes_on_an_answer(self):
        self.f.edit("2b-technical-policy.md", "Status: answers applied", "Status: waiting for answers")
        self.f.write(os.path.join(self.f.design, "2b-technical-policy.md"),
                     self.f.read("2b-technical-policy.md") + QUESTIONS % ("POL-01", ""))
        self.commit("architecture-to-technical-policy: waiting for answers to question 3", "2b-technical-policy.md")
        chain = self.chain()
        self.assertEqual(self.unit(chain, "2b").state, "waiting")
        self.assertEqual(self.unit(chain, "2b").waiting_rows, ["3"])
        self.assertEqual(chain.next, [])
        self.assertEqual([u.key for u in chain.waiting], ["2b"])
        self.assertIs(self.unit(chain, "4 ELM-01").blocked_by, self.unit(chain, "2b"))
        self.assertIn("Which test runner?", status.text_output(chain, questions=True))

        # a stage above it still runs
        self.write("fnd/FND-02.yaml", finding("FND-02", S1, "major", S2B, "2b-technical-policy.md", ["DRV-02"]))
        chain = self.chain()
        self.assertEqual([u.key for u in chain.next], ["1"])

        # an answer written in the row, not committed yet, resumes it
        self.f.edit("2b-technical-policy.md", "| POL-01 |  |", "| POL-01 | Vitest, as drafted |")
        chain = self.chain()
        self.assertEqual(self.unit(chain, "2b").state, "stale")
        self.assertReason(chain, "2b", "answers under Unanswered questions: question 3")

    def test_a_question_about_a_request_is_answered_in_the_request(self):
        self.f.edit("3-high-level-design.md", "Status: answers applied", "Status: waiting for answers")
        self.f.write(os.path.join(self.f.design, "3-high-level-design.md"),
                     self.f.read("3-high-level-design.md") + QUESTIONS % ("QCR-02, IFC-02", ""))
        self.commit("architecture-to-high-level-design: waiting for answers to question 3", "3-high-level-design.md")
        self.assertEqual(self.unit(self.chain(), "3").state, "waiting")
        doc = self.f.read("quality-chain-requests.md")
        self.assertIn("### QCR-02", doc)
        start = doc.index("### QCR-02")
        at = doc.index("Answer: —", start)
        self.write("quality-chain-requests.md", doc[:at] + "Answer: Show an empty list" + doc[at + len("Answer: —"):])
        chain = self.chain()
        self.assertEqual(self.unit(chain, "3").state, "stale")
        self.assertReason(chain, "3", "question 3 (answered in QCR-02)")

    def test_a_review_is_due_again_only_after_a_major_finding_changed_its_stage(self):
        self.write("fnd/FND-02.yaml", finding("FND-02", S2, "major", lib.REVIEW_SKILL, "reviews/2-architecture.md",
                                              ["DEC-01"]))
        self.touch("reviews/2-architecture.md", "a")
        self.commit("design-review: stage 2 again", "fnd", "reviews/2-architecture.md")
        self.assertEqual(self.unit(self.chain(), "2").state, "stale")
        self.write("fnd/FND-02.yaml", finding("FND-02", S2, "major", lib.REVIEW_SKILL, "reviews/2-architecture.md",
                                              ["DEC-01"], "accepted", "Changed DEC-01"))
        self.f.edit("dec/DEC-01.yaml", "basis_note: The database size is assumed (DAS-01)",
                    "basis_note: The database size is assumed (DAS-01); FND-02")
        self.touch("2-architecture.md", "b")
        self.commit("architecture-drivers-to-architecture: accept FND-02", "fnd", "dec", "2-architecture.md")
        chain = self.chain()
        self.assertEqual(self.unit(chain, "review 2").state, "due")
        self.assertReason(chain, "review 2", "stage 2 accepted findings addressed to it since this review: FND-02")
        self.assertEqual([u.key for u in chain.next], ["review 2"])
        self.touch("reviews/2-architecture.md", "c")
        self.commit("design-review: diff review of stage 2", "reviews/2-architecture.md")
        chain = self.chain()
        self.assertEqual(self.unit(chain, "review 2").state, "up to date")
        self.assertEqual([u.key for u in chain.next], ["2b"])

    def test_a_review_is_due_when_its_stage_followed_a_finding_the_review_raised(self):
        self.write("fnd/FND-02.yaml", finding("FND-02", S2, "major", lib.REVIEW_SKILL,
                                              "reviews/3-high-level-design.md", ["DEC-01"]))
        self.touch("reviews/3-high-level-design.md", "a")
        self.commit("design-review: stage 3 again", "fnd", "reviews/3-high-level-design.md")
        self.write("fnd/FND-02.yaml", finding("FND-02", S2, "major", lib.REVIEW_SKILL,
                                              "reviews/3-high-level-design.md", ["DEC-01"], "accepted", "Changed it"))
        self.f.edit("dec/DEC-01.yaml", "chosen: One application", "chosen: One application, split later")
        self.touch("2-architecture.md", "b")
        self.commit("architecture-drivers-to-architecture: accept FND-02", "fnd", "dec", "2-architecture.md")
        self.assertEqual(self.unit(self.chain(), "review 3").state, "up to date")
        for skill, report in ((lib.REVIEW_SKILL, "reviews/2-architecture.md"), (S2B, "2b-technical-policy.md"),
                              (S3, "3-high-level-design.md")):
            self.touch(report, "c")
            self.commit("%s: follow" % skill, report)
        chain = self.chain()
        self.assertEqual(self.unit(chain, "review 3").state, "due")
        self.assertReason(chain, "review 3", "ran after an earlier stage accepted findings that this review raised")

    def test_only_what_concerns_a_component_makes_it_stale(self):
        self.f.edit("ifc/IFC-02.yaml", "format: HTML", "format: HTML, server-rendered")
        self.touch("3-high-level-design.md", "a")
        self.commit("architecture-to-high-level-design: change IFC-02", "ifc", "3-high-level-design.md")
        states = self.states()
        self.assertEqual(states["4 ELM-05"], "stale")  # it provides IFC-02
        self.assertEqual(states["4 ELM-01"], "up to date")
        self.f.edit("pol/POL-01.yaml", "One lockfile for the repository", "One lockfile, at the root")
        self.touch("2b-technical-policy.md", "b")
        self.commit("architecture-to-technical-policy: change POL-01", "pol", "2b-technical-policy.md")
        self.touch("3-high-level-design.md", "c")
        self.commit("architecture-to-high-level-design: follow POL-01", "3-high-level-design.md")
        states = self.states()
        self.assertEqual(states["4 ELM-01"], "stale")  # a policy binds every component

    def test_a_component_that_waits_holds_back_only_its_own_review(self):
        self.f.edit("4-detailed-design/ELM-01.md", "Status: answers applied", "Status: waiting for answers")
        self.f.write(os.path.join(self.f.design, "4-detailed-design/ELM-01.md"),
                     self.f.read("4-detailed-design/ELM-01.md") + QUESTIONS % ("MOD-01", ""))
        self.commit("high-level-design-to-detailed-design: ELM-01 waiting for answers", "4-detailed-design")
        self.write("fnd/FND-02.yaml", finding("FND-02", S4, "major", lib.REVIEW_SKILL,
                                              "reviews/4-detailed-design-ELM-05.md", ["ELM-05"]))
        chain = self.chain()
        self.assertEqual(self.unit(chain, "4 ELM-01").state, "waiting")
        self.assertEqual([u.key for u in chain.next], ["4 ELM-05"])
        self.assertIs(self.unit(chain, "review 4 ELM-01").blocked_by, self.unit(chain, "4 ELM-01"))

    def test_hand_offs_and_overturned_assumptions(self):
        self.write("hnd/HND-03.yaml", d("""
            id: HND-03
            title: The page size of the order history
            status: open
            basis: inferred
            basis_note: null
            premises: []
            from: architecture-drivers-to-architecture
            to: architecture-to-high-level-design
            component: null
            origin: [DEC-01]
            what: How many orders a page shows
            bounds: DEC-01
            trigger: The next run of stage 3
            resolution: null
            """))
        self.f.edit("das/DAS-02.yaml", "status: open", "status: overturned")
        self.f.edit("das/DAS-02.yaml", "answer: null", "answer: The team runs its own CI")
        self.touch("2-architecture.md", "a")
        self.commit("architecture-drivers-to-architecture: write HND-03 and overturn DAS-02", "hnd", "das",
                    "2-architecture.md")
        chain = self.chain()
        self.assertReason(chain, "3", "HND-03 (trigger: The next run of stage 3)")
        self.assertReason(chain, "2b", "assumptions overturned since its last run: DAS-02")
        self.assertEqual(self.unit(chain, "2").state, "up to date")
        self.assertEqual([h["id"] for h in chain.later()["handoffs"]], [])

    def test_diagrams_and_tables_of_an_earlier_report(self):
        self.write("2-architecture.md", self.f.read("2-architecture.md") + DIAGRAM)
        self.commit("architecture-drivers-to-architecture: draw the runtime view", "2-architecture.md")
        chain = self.chain()
        self.assertReason(chain, "2b", "diagrams or tables changed in 2-architecture.md")
        self.assertReason(chain, "4 ELM-01", "diagrams or tables changed in 2-architecture.md")
        for key, skill, report in (("2b", S2B, "2b-technical-policy.md"), ("3", S3, "3-high-level-design.md"),
                                   ("4 ELM-01", S4, "4-detailed-design/ELM-01.md"),
                                   ("4 ELM-05", S4, "4-detailed-design/ELM-05.md")):
            self.touch(report, "a")
            self.commit("%s: follow" % skill, report)
        self.write("2-architecture.md", self.f.read("2-architecture.md") +
                   "\n## Decisions\n\n| # | Question | Answer | Items |\n|---|---|---|---|\n| 1 | Q | A | DEC-01 |\n"
                   "\nA paragraph that sums the design up.\n")
        self.commit("architecture-drivers-to-architecture: record a decision", "2-architecture.md")
        self.assertEqual(self.unit(self.chain(), "2b").state, "up to date")

    def test_the_quality_chain(self):
        path = os.path.join(self.f.quality, "fr", "FR-02.yaml")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        self.f.write(path, text.replace("The buyer sees past orders.", "The buyer sees every past order."))
        chain = self.chain()
        for key in ("1", "2", "2b", "3", "4 ELM-01", "4 ELM-05"):
            self.assertReason(chain, key, "quality chain changed: FR-02")
        self.f.write(path, text)
        path = os.path.join(self.f.quality, "nfr", "NFR-02.yaml")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        self.f.write(path, text.replace("Every year", "Every half year"))
        states = self.states()
        self.assertEqual(states["2b"], "stale")
        self.assertEqual(states["4 ELM-01"], "up to date")  # nothing of ELM-01 names NFR-02

    def test_a_report_with_no_commit_of_its_skill(self):
        # a hand edit after the stage's last run is no reason: the run keeps it
        self.touch("2b-technical-policy.md", "a")
        self.commit("Edit the policy by hand", "2b-technical-policy.md")
        self.assertEqual(self.unit(self.chain(), "2b").state, "up to date")
        # a report that no commit of its skill ever changed: the run reads every input again
        self.write("elm/ELM-06.yaml", self.f.read("elm/ELM-05.yaml").replace("ELM-05", "ELM-06"))
        self.write("4-detailed-design/ELM-06.md", "# Report\n\n" + HEADER % "4 of 4" + "\n")
        self.commit("Write a component report by hand", "elm", "4-detailed-design")
        chain = self.chain()
        self.assertReason(chain, "4 ELM-06", "its last run cannot be found")

    def test_a_design_that_has_not_started(self):
        shutil.rmtree(self.f.design)
        self.commit("Remove the design", ".")
        project = lib.Project(self.f.design, self.f.quality)
        chain = status.Chain(project, lib.Glossary(), status.Git(self.f.root)).evaluate()
        self.assertEqual([u.key for u in chain.next], ["1"])
        self.assertEqual(self.unit(chain, "1").state, "not run yet")

    def test_runs_rounds_oscillation_and_repeats_since_a_commit(self):
        start = self.git("rev-parse", "HEAD").strip()
        self.write("fnd/FND-02.yaml", finding("FND-02", S2, "critical", lib.REVIEW_SKILL,
                                              "reviews/2-architecture.md", ["DEC-01"]))
        self.write("fnd/FND-03.yaml", finding("FND-03", S2, "major", lib.REVIEW_SKILL, "reviews/2-architecture.md",
                                              ["ELM-01"]))
        self.touch("reviews/2-architecture.md", "a")
        self.commit("design-review: stage 2 again", "fnd", "reviews/2-architecture.md")
        self.write("fnd/FND-02.yaml", finding("FND-02", S2, "critical", lib.REVIEW_SKILL,
                                              "reviews/2-architecture.md", ["DEC-01"], "accepted", "Services"))
        self.write("fnd/FND-03.yaml", finding("FND-03", S2, "major", lib.REVIEW_SKILL, "reviews/2-architecture.md",
                                              ["ELM-01"], "rejected", "It holds"))
        self.f.edit("dec/DEC-01.yaml", "chosen: One application", "chosen: Services")
        self.f.edit("dec/DEC-01.yaml", "debt: null", "debt: {what: X, why_accepted: Y, repay_when: Z}")
        self.touch("2-architecture.md", "b")
        self.commit("architecture-drivers-to-architecture: accept FND-02", "fnd", "dec", "2-architecture.md")
        self.write("fnd/FND-04.yaml", finding("FND-04", S2, "major", lib.REVIEW_SKILL, "reviews/2-architecture.md",
                                              ["ELM-01", "ELM-05"]))
        self.touch("reviews/2-architecture.md", "c")
        self.commit("design-review: stage 2 once more", "fnd", "reviews/2-architecture.md")
        self.f.edit("dec/DEC-01.yaml", "chosen: Services", "chosen: One application")
        self.f.edit("dec/DEC-01.yaml", "debt: {what: X, why_accepted: Y, repay_when: Z}", "debt: null")
        self.touch("2-architecture.md", "d")
        self.commit("architecture-drivers-to-architecture: back to one application", "dec", "2-architecture.md")
        chain = self.chain()
        since = chain.since(status.Git(self.f.design).resolve(start))
        self.assertEqual(dict((k, len(v)) for k, v in since["runs"].items()), {"2": 2, "review 2": 2})
        self.assertEqual(since["critical_rounds"], {"2": 1})
        self.assertEqual([(o["id"], o["field"]) for o in since["oscillation"]], [("DEC-01", "chosen")])
        self.assertEqual([(r["id"], r["like"], r["targets"]) for r in since["repeats"]],
                         [("FND-04", "FND-03", ["ELM-01"])])
        text = status.text_output(chain, since)
        self.assertIn("DEC-01 chosen went back to its value before", text)
        self.assertIn("possible repeat: FND-04", text)

    def test_the_command_line(self):
        out = io.StringIO()
        cwd = os.getcwd()
        os.chdir(self.f.root)
        try:
            with redirect_stdout(out):
                code = status.main(["--summary", "--questions", "--since", "HEAD"])
            with redirect_stdout(io.StringIO()):
                bad = status.main(["--since", "no-such-commit"])
        finally:
            os.chdir(cwd)
        self.assertEqual((code, bad), (0, 2))
        text = out.getvalue()
        for part in ("Next: nothing; every stage and review is up to date", "Open assumptions, highest first:",
                     "DAS-01 (stage 2, judgment; breadth low, severity medium)", "QCR-02 An empty order history",
                     "Questions waiting for answers:\n  none", "runs: 0"):
            self.assertIn(part, text)


class StatusWithoutGitTest(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def tearDown(self):
        self.f.close()

    def test_only_what_the_files_show(self):
        self.f.write(os.path.join(self.f.design, "fnd", "FND-02.yaml"),
                     finding("FND-02", S2, "major", S3, "3-high-level-design.md", ["DEC-01"]))
        project = lib.Project(self.f.design, self.f.quality)
        git = status.Git(self.f.design)
        if git.root:
            self.skipTest("the temporary directory is inside a git repository")
        chain = status.Chain(project, lib.Glossary(), git).evaluate()
        self.assertEqual(self.unit(chain, "1").state, "up to date")
        self.assertEqual(self.unit(chain, "2").state, "stale")
        self.assertIn("not under git", " ".join(self.unit(chain, "2").notes))
        self.assertEqual([u.key for u in chain.next], ["2"])

    def unit(self, chain, key):
        return next(u for u in chain.units if u.key == key)


if __name__ == "__main__":
    unittest.main()
