# CanMEDS Competency Reflection: Building Finbot

**Document:** Medical School Application Portfolio
**Context:** OMSAS (Ontario Medical School Application Service) — Autobiographical Sketch
**Framework:** CanMEDS 2015 Competency Framework (Royal College of Physicians and Surgeons of Canada)
**Date:** 2026-02-17

---

## Introduction

Over the past three years, I designed and built Finbot — a quantitative analysis platform for financial research that grew to encompass health economics, systematic backtesting, and Monte Carlo simulation. What started as a personal project to answer "should I rebalance my portfolio?" became a rigorous software engineering effort spanning 15,000+ lines of code, 866 automated tests, and a production-ready system documented to academic standards.

This reflection maps that experience to the CanMEDS competency framework, showing how the development of a technical project cultivated physician-ready capacities. My claim is not that building software is equivalent to clinical experience — it clearly is not — but that the systematic, evidence-based thinking required for rigorous quantitative research is the same thinking medicine demands, applied to a different domain.

---

## Medical Expert

*Demonstrating expertise through integration of knowledge, clinical skills, and professional attitudes.*

The "domain expertise" required for Finbot was quantitative finance and health economics — not medicine, but the process of acquiring and applying it was identical to how a physician builds clinical knowledge.

**Systematic literature review**: Before implementing health economics features, I read the primary methodological literature: Drummond et al.'s *Methods for the Economic Evaluation of Health Care Programmes*, NICE's reference case methodology, CADTH's Canadian guidelines, and WHO guidance on willingness-to-pay thresholds. I didn't implement QALY simulation until I understood the underlying methods at a level where I could defend every design decision.

**Evidence-based implementation**: Every major technical decision in Finbot is documented in an Architectural Decision Record (ADR) that states the problem, considered alternatives, and rationale. ADR-001 documents the consolidation of three repositories; ADR-011 documents the decision to adopt NautilusTrader for live trading. This is exactly how clinical practice guidelines are structured — problem, alternatives, evidence, recommendation.

**Recognizing limitations**: The most important section of Finbot's documentation is `docs/limitations.md`, which explicitly lists survivorship bias, look-ahead bias, simulation assumptions, and the risk of overfitting. A physician who doesn't understand the limits of their diagnostic tools is dangerous. A quantitative analyst who doesn't understand the limits of their models is equally so. Both domains demand intellectual honesty about what the evidence can and cannot tell you.

**Health economics as clinical application**: Extending Finbot to health economics was not a tangent — it was the application of quantitative methods to a domain directly relevant to medical practice. The QALY simulator, cost-effectiveness analysis, and treatment optimizer apply methods used daily by health technology assessment bodies like NICE and CADTH. Understanding these tools at an implementation level gives me insight into how healthcare funding decisions are actually made.

---

## Communicator

*Establishing therapeutic relationships and communicating effectively with patients, families, colleagues, and other professionals.*

The physician-patient relationship is fundamentally a communication challenge: how do you convey complex medical information to someone who hasn't spent years learning it? Technical communication faces the same challenge: how do you convey complex quantitative concepts to someone who hasn't built the system?

**Writing for multiple audiences**: Finbot's documentation exists at three levels. The MkDocs-based documentation site targets non-technical users; the API reference targets developers integrating Finbot with their own work; the Jupyter notebooks target researchers who want to understand the methodology before reproducing results. Writing clearly for each audience required understanding what each audience already knows and what they need to learn.

**The blog post series**: Writing "Why I Built Finbot," "Backtesting Engines Compared," and the "Health Economics with Python" three-part tutorial series forced me to distill complex technical topics into accessible narratives. The health economics series in particular required explaining QALY methodology, ICER calculations, and probabilistic sensitivity analysis to readers with programming backgrounds but no health economics training. Explaining something well requires understanding it deeply.

**Visual communication**: Finbot's Streamlit dashboard (7 pages, 12 interactive components) translates quantitative outputs — backtest performance metrics, Monte Carlo distributions, cost-effectiveness planes — into charts and tables that users can interpret without reading code. The design question "what does the user need to see?" is the same question a physician asks when deciding how to present scan results or lab values to a patient.

**Documentation as communication**: 113 markdown files, 8 Jupyter notebooks, and 58%+ docstring coverage represent months of writing. Writing documentation for a project you built requires imagining what a reader knows and doesn't know — the same perspective-taking that makes medical communication effective.

---

## Collaborator

*Working effectively with other health care professionals to provide safe, high-quality, patient-centered care.*

Building a solo project might seem to contradict collaboration as a competency. But collaboration isn't only about what you do with others — it's about how you structure your work to enable others to contribute.

**GitHub collaboration infrastructure**: Finbot has complete collaboration infrastructure: CONTRIBUTING.md with development standards, CODE_OF_CONDUCT.md (Contributor Covenant v2.1), CODEOWNERS for automated review requests, issue templates for bugs and features, and pull request templates. These artifacts invite contribution and set clear expectations — they are the systems that make collaboration possible.

**Open source as collaboration**: Publishing Finbot publicly on GitHub is an act of collaboration with the broader developer community. The code, documentation, and notebooks are freely available to anyone who wants to learn from, build on, or critique them. Several design decisions were made specifically to enable reuse: the engine-agnostic contract layer, the typed interfaces, the comprehensive test suite.

**Code review culture**: Pre-commit hooks enforce consistent style (ruff, black) and catch issues before code is committed. CI/CD pipelines run 7 automated checks on every change. This infrastructure creates shared quality standards that make collaboration safe — the same role that protocols and checklists play in clinical settings.

**Interdisciplinary thinking**: Finbot crosses at least three disciplines: financial engineering, software engineering, and health economics. Working effectively across disciplines requires understanding what each brings to the table and where the transfer works. The treatment optimizer works because the mathematical structure of "optimize dose schedule by NMB" is structurally identical to "optimize investment schedule by Sharpe ratio" — recognizing that required thinking across domains.

---

## Leader

*Contributing to the improvement of health care delivery in teams, organizations, and systems.*

Leadership in a solo project is expressed through the choices you make about standards, process, and impact.

**Setting quality standards without an audience**: When I raised the test coverage threshold from 30% to 60%, wrote comprehensive API documentation, and added structured audit logging, there was no one else who would have noticed if I hadn't. Maintaining standards in the absence of external accountability is a form of professional self-leadership that medicine requires constantly — physicians maintain professional standards whether or not they're being observed.

**Process design**: The development of Finbot followed a structured prioritization framework: Priority 0 (bugs), Priority 1 (critical gaps), Priority 2 (high impact), and so on through Priority 7. Each priority had a scope, timeline, and acceptance criteria documented before implementation began. This is program management — designing a process that enables reliable delivery of complex work.

**Automation as organizational infrastructure**: The CI/CD pipeline I built runs 7 automated checks on every code change and flags regressions immediately. The scheduled daily data update workflow keeps data fresh without manual intervention. The performance regression testing prevents performance from silently degrading. These systems embody institutional knowledge — they make the project robust to my own lapses in attention.

**External impact**: The research publications (blog posts, tutorial series, research posters) represent Finbot's contribution beyond its immediate function. A leader doesn't just do good work — they disseminate it so others can benefit. Writing "Health Economics with Python" teaches methods that health economists, medical students, and policy researchers can apply to real clinical questions.

---

## Health Advocate

*Responding to individual patient health needs and issues as part of patient care; responding to the health needs of communities.*

This competency is where Finbot's health economics extension is most directly relevant.

**Understanding population-level health decisions**: The cost-effectiveness analysis module implements exactly the methods health technology assessment bodies use to make coverage decisions. Running these analyses taught me not just the mechanics but the ethical dimensions: willingness-to-pay thresholds encode societal value judgments about how much a year of good health is worth. The CADTH threshold (~$50,000 CAD/QALY) is lower than the US informal benchmark (~$100,000–$150,000 USD), reflecting different societal choices about health spending. Understanding this distinction is prerequisite to contributing to health policy discussions.

**Health advocacy through education**: The health economics tutorial series (Parts 1-3) teaches methods that are often poorly understood even by clinicians. A physician who understands how NICE or CADTH evaluates treatment cost-effectiveness is better positioned to advocate for patients when coverage decisions affect their care, or to contribute to health technology assessment as a physician expert.

**Financial health as determinant of health**: Finbot's primary domain — personal finance — is not separate from health advocacy. Financial stress is a major social determinant of health. The simulation tools I built (Monte Carlo portfolio simulation, backtesting, DCA optimization) help individuals make better long-term financial decisions. Better financial decisions mean less financial stress, better ability to afford healthcare, and improved long-term health outcomes. The connection is indirect but real.

**Evidence-based advocacy**: The project's core methodology — backtesting investment strategies against historical data, validating QALY models against published estimates, documenting limitations — models the same evidence standards medicine uses. Health advocacy grounded in evidence is more effective than advocacy grounded in anecdote. Building tools that enforce evidence standards (validation tests, limitations documentation) cultivated that habit.

---

## Scholar

*Engaging in a lifelong commitment to excellence in practice through continuous learning.*

Scholarship is the competency I have most deliberately cultivated, and the one most visibly embodied in Finbot.

**Self-directed learning**: Everything I know about quantitative finance, health economics, and the software engineering practices embedded in Finbot was self-taught. No course taught me how to build a QALY simulator or implement probabilistic sensitivity analysis — I identified the need, found the primary sources, and implemented from first principles. This is exactly the self-directed learning medicine demands.

**Primary source engagement**: I read the papers before I wrote the code. The health economics module is grounded in Drummond et al., NICE methodology, and CADTH guidelines. The backtesting module is grounded in academic literature on momentum strategies, risk parity, and market regime detection. The limitations document is grounded in the academic literature on backtesting pitfalls.

**Rigor and reproducibility**: 866 automated tests, 61.63% test coverage, versioned data contracts, snapshot-based reproducibility, and experiment tracking are all tools for making work reproducible and reviewable. Science that can't be replicated isn't science. I built infrastructure that makes every backtest result reproducible from the same data snapshot.

**Teaching as scholarship**: Writing the three-part health economics tutorial series required me to understand the material well enough to explain it clearly to someone who didn't know it — the best test of understanding. Preparing the "Backtesting Engines Compared" technical article required reviewing the primary documentation of both Backtrader and NautilusTrader, running comparative benchmarks, and synthesizing the results into actionable guidance.

**Continuous improvement**: Finbot has gone through 7 priority tiers of systematic improvement since its origin as three separate, messy projects. The willingness to look critically at your own work — to document your mistakes (the three-repo fragmentation, the numba dependency, the pickle serialization), extract lessons, and correct course — is the same growth mindset medicine demands.

---

## Professional

*Commitment to the health and well-being of individual patients and society through ethical practice.*

Professionalism in a software project manifests as the standards you maintain even when no one is watching.

**Ethical transparency**: Finbot includes a DISCLAIMER.md that explicitly states it is not financial advice, the SECURITY.md that documents how to report vulnerabilities, and the limitations documentation that details what the system cannot do. These are not legally required. I included them because they are the right thing to do.

**Security standards**: The security posture of Finbot includes: bandit static analysis (SAST) for Python security vulnerabilities, pip-audit for dependency vulnerability scanning, trivy for container scanning, all GitHub Actions pinned to SHA hashes to prevent supply chain attacks, and structured audit logging for all significant operations. The CLAUDE.md file documents a commit authorship policy that ensures transparent attribution. These choices reflect professional accountability.

**Long-term thinking**: Choosing parquet over pickle for data serialization meant current storage files weren't readable without migration — but pickle's fragility across Python versions made it a liability for a long-lived project. Choosing to write 866 tests when 0 would have been "faster" meant slower initial development but dramatically faster subsequent iteration. Professional judgment is the willingness to accept short-term costs for long-term reliability.

**Intellectual honesty**: The project documents that Priority 5 is 93.3% complete, not 100%. It documents that the walk-forward analysis pilot ran against only 3 strategies, not the full suite. It documents that the NautilusTrader migration took 15 hours and produced unexpected typing challenges. This is how honest reporting looks — not "everything went perfectly" but "here's what happened, here's what I learned."

---

## Conclusion

Building Finbot was not a clinical experience. But it was a scholarly, systematic, ethically grounded, collaborative, communicative project that required exactly the competencies CanMEDS identifies as essential to excellent medical practice.

The clearest evidence of this isn't in any single feature — it's in the overall character of the project: rigorous where rigor matters, transparent about limitations, continuously improved through structured reflection, and designed to benefit others beyond its immediate context.

I am applying to medicine because the domain of health — its science, its economics, its human dimensions — is where I want to apply these capacities for the next forty years. The systematic thinking I developed building Finbot is the same thinking clinical medicine demands. What changes is the subject matter, the stakes, and the privilege of working directly with patients.

---

*This document is part of a medical school application portfolio. For technical documentation, see the [Finbot repository](https://github.com/jerdaw/finbot).*
