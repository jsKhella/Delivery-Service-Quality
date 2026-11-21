ABOUT ME: I'm Mina Khella, BSc student of statistics and economics at Università degli studi di Milano Bicocca.
CURIOSITY is a research assistant designed by me and built on Claude. AI workers find the data, write the code and draft the text. 
Automatic scripts, which involve no AI, decide whether the work passes: this note explains those checks, and what they do not prove.

1. BEFORE ANY DATA IS LOOKED AT

- The question is written down first, with a short definition of every number that will be reported: what is counted, in which data, and in which unit.
  For a fact-check, the rules for the verdict are fixed at this stage and cannot change later. In a research job, any change of question needs the owner's approval and is listed first in the report's Run record.
- The plan sets out the checks each step must pass (for example "no missing values", "between 0 and 100", "covers 2010 to 2023"). The checks are written before the work starts and are locked once the owner approves the plan.
- Each data file is fingerprinted when it is downloaded (a SHA-256 code that changes if even one byte changes). Every step re-checks those fingerprints, so the source data cannot be quietly edited.


2. AT EVERY STEP OF THE WORK

The work runs one step at a time. A step passes only if all of these pass:

- The plan's own checks. Standard data checks (duplicate rows, empty columns, impossible values such as negative counts) also run on every output; they raise warnings for the reviewer rather than failing the step.
- A re-run test: the step's code is run again from a clean start and must produce byte-identical results.
- Numbers are recorded by the code itself, never typed in by the AI. The text  may only quote numbers that the plan declared in advance.
- A blind redo, for the steps that decide the verdict or the answers: a separate AI worker, who cannot see the first worker's work, recomputes the key numbers by a different method. The two results must agree within a tolerance set in the plan (0.1% unless the plan says otherwise).
- An independent reviewer (a separate AI worker that changes nothing) reads the code, the outputs and the record of errors, and writes PASS or FAIL.
- Every action is written to a tamper-evident log. If a worker changed course without declaring it, that is flagged.

A failed step is retried at most twice and then re-planned. Every retry, workaround and deviation is listed, problems first, in the Run record sheet of the official workbook.


3. THE OFFICIAL REPORT

- A script checks that every reference exists and has the same value in both files, and that no number appears without a recorded source.
- Key numbers and charts must come from trusted (tier 1 or 2) sources unless the owner approved a weaker source.
- Charts are drawn by a script from checked tables, never by the AI.


4. THE RESULTS VAULT, AND POLISHED VERSIONS

- When the report passes, every checked result is sealed in a "results vault": every number by its reference and the full data of every table and chart. It is fingerprinted, and from then on it is the only source for anything made afterwards.
- Better-looking versions (a web page, a PDF, an Excel dashboard) are made "fill-in-the-blanks": the design contains only addresses such as {4.2}, never typed numbers, and a script fills in the exact values from the vault and draws the tables and charts from its data.
- A separate check then re-reads each finished file against the vault. Every number must equal its reference (after rounding, so 41.27% may be shown as 41%), every table cell must match its source row and column, and every chart must show the vault's data (a chart picture must be identical to one re-drawn from the vault). The file must name the Report ID it came from.
- The PDF is printed from the web page after it has passed. It is then read back to confirm that every reference and the Report ID survived printing.
- A file that fails is labelled UNCHECKED_ and is never delivered.



5. WHAT THESE CHECKS DO NOT PROVE

- They prove that the numbers are consistent, traceable and repeatable. They do not prove that the method was the right one for the question, or that the source data is itself correct. The definitions and the plan are in the delivery so that a reader can judge the method.
- The independent reviewer and the blind redo are AI workers. They catch many errors but are not infallible. The blind redo covers the deciding steps only.
- Reproducing needs the same source files. If a publisher removes or changes a file, reproduce.py will say so, but it cannot fetch the old version.
- Files a person edits after delivery are no longer covered by these checks.

