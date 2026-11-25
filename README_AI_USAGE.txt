AI USAGE: HOW THIS PROJECT WAS PRODUCED AND HOW ITS RELIABILITY IS ENFORCED
============================================================================

The analysis was carried out by CURIOSITY, a set of cooperating Claude agents (run inside Claude Code). In this job the main session ran on Claude Sonnet 5.5. The Executors used Claude Sonnet and their actions were guided by a plan devised ahead of work by Claude Opus. I (Mina Khella, designer of CURIOSITY) decided the questions, approved the plan and every change of meaning, and typed every approval. The agents did not choose the questions and could not approve anything themselves.


THE AGENTS AND WHAT EACH ONE DOES
---------------------------------
-Orchestrator (main session): the only agent that talked to me. It interviews the owner, writes the Research Brief (questions, definitions, what counts as "answered"), starts the other agents and reports progress. It never reads data or code: the system blocks it.
-Scout: finds free public data, downloads it and seals each file with a fingerprint.
-Planner: turns the Brief into a step-by-step plan with pre-written checks (ranges, row counts, no missing values) and marks which steps are critical. I visioned the plan and approved it before any work was done.
-Executor: carries out exactly one step from a written packet, writes the code and records each result through code.
-Replicator (blind): independently recomputes every critical step with a different method, without seeing the Executor's results or messages.
-Verifier: reviews each finished step against the plan and Brief and writes PASS or FAIL.


HOW THE SYSTEM ASSURES RELIABILITY
----------------------------------
1. Goalposts first. Questions, definitions and assumptions were fixed before any data was looked at. In this job they could only change with the owner's approval.
2. Sealed data. Every raw file is fingerprinted when downloaded and re-checked at every step (37 raw files unchanged at the end).
3. Numbers only from code. A number in the report must have been recorded by code. Prose with a number that no code produced is rejected, and the report builder refuses to finish if a table or text changed after its step passed.
4. Pre-written checks. Plan checks (ranges, duplicates, missing values) run on every step, and a clean re-run must reproduce identical outputs.
5. Blind replication. All 12 critical steps were recomputed by a second agent using a different method and compared within a tolerance (0.1% to 3%, the widest for the Monte Carlo since different seeds inevitably lead to different simulation results). They agreed.
6. Independent review. A Verifier who did not write the code checks each step against the plan.
7. Enforced separation. Hooks block agents from reading what they should not (35 actions were blocked in this job), and the action log is tamper-evident (chain intact, 4970 entries). 


WHAT ACTUALLY HAPPENED
----------------------
11 retries were needed and 9 deviations from the plan were logged (1 was undeclared). A failed check forced a retry each time. There were several replans. The replan after the Monte Carlo step changed one check (a strict check written ahead of work would always fail the Executor and Replicator's result comparison of the monte carlo simulation). 


WHAT THIS DOES NOT GUARANTEE
----------------------------
- Judgment calls (choice of peers, industry beta, scenario and simulation ranges) were made by the joined work of the agents and I and are reported with their limits. The checks test the arithmetic and consistency, not whether an assumption is right.
- The blind replica works from the same data and the same written definitions, so a shared misreading of a definition could pass both: I visioned and approved the complete project, definitions and assumptions ahead of work and my judgement is the only guarantee against this potential weak point
- The result is an academic exercise. It is not investment advice.
