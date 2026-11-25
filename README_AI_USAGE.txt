AI USAGE: HOW THIS PROJECT WAS PRODUCED AND HOW ITS RELIABILITY IS ENFORCED
============================================================================
The analysis was carried out by CURIOSITY, a set of coordinated Claude agents, run inside Claude Code. 
The main session (orchestrator) ran on Claude Sonnet 5.5. The Executors used Claude Sonnet and their actions were guided by a plan devised ahead of work by Claude Opus. 
I (Mina Khella, designer of CURIOSITY) decided the questions, approved the plan, definitions, assumptions and checks ahead of time; I also approved every replan.
The agents could not approve anything themselves: "hard rules" were enforced through the use of hooks and guards, but more work is necessary to guarantee that the agents cannot work around these hard rules while also having the exact set of tools necessary to accomplish the tasks given to them.


THE AGENTS AND WHAT EACH ONE DOES
---------------------------------
-Orchestrator (main session): the only agent that talked to me. It interviews the human (me), writes the Research Brief (questions, definitions, what counts as "answered"), starts the other agents and reports progress. It never reads data or code.
-Scout: finds free public data, downloads it and seals each file with a fingerprint.
-Planner: turns the Brief into a step-by-step plan with pre-written checks (ranges, row counts, no missing values) and marks which steps are critical. I visioned the plan and approved it before any work was done.
-Executor: carries out exactly one step from a written packet, writes the code and records each result through code.
-Replicator (blind): independently recomputes every critical step with a different method, without seeing the Executor's work, reasoning, results or messages.
-Verifier: reviews each finished step against the plan and Brief and writes PASS or FAIL.


HOW THE SYSTEM ASSURES RELIABILITY
----------------------------------
1. Goalposts first. Questions, definitions, assumptions and checks are fixed before any data was looked at, any subsequent change to them requires human approval.
2. Sealed data. Every raw file is fingerprinted when downloaded and re-checked at every step (37 raw files unchanged at the end).
3. Numbers only from code. A number in the final report must have been recorded by code. Prose with a number that no code produced is rejected, and the report builder refuses to finish if a table or text changed after its step passed.
4. Pre-written checks. Plan checks (ranges, duplicates, missing values) run on every step, and a clean re-run must reproduce identical outputs.
5. Blind replication. All critical steps were recomputed by a second agent using a different method and compared within a tolerance. 
6. Independent review. A Verifier who did not write the code checks each step against the plan.
7. Enforced separation. Hooks block agents from reading what they should not, and the action log is tamper-evident. 


WHAT ACTUALLY HAPPENED
----------------------
Retries were needed at various steps: failed checks forced a retry each time, and the executor and replicator's results disagreed more than once, always revealing a hidden ambiguity in the set of definitions/assumptions. There were several replans and all deviations from the plan were approved by me and subsequently logged. 


WHAT THIS DOES NOT GUARANTEE
----------------------------
- Judgment calls were made by the joined work of the agents and I and are reported with their limits. The checks test the arithmetic and consistency, not whether an assumption is right.
- The blind replica works from the same data and the same written definitions, so a shared misreading of a definition could pass both: I visioned and approved the complete project, definitions and assumptions ahead of work and my judgement is the only guarantee against this potential weak point.
- The result is an academic exercise. It is not investment advice.
