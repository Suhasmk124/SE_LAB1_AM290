# Lab 5: Static Code Analysis - Parking Lot System

Student: Suhas Mohan Kumar | SRN: PES1UG24AM290 | Date: 27 October 2026

## Objective and source

Improve the assigned Python parking manager using Pylint, Bandit and Flake8 while retaining its parking, release, surge-fee, ticket and export workflow.

Source: https://github.com/SETAPESU26/L5_51_parking_lot_system  
Source revision: `f3fba6a9fd742604c8a906662eca8f9115ef976c`. The exact original source is retained as a non-executable text snapshot in `before/`.

## Method and measured results

The original script was run in a temporary working directory and scanned before any edits. Security fixes were made first, then quality/logic fixes, then formatting. All three tools were rerun on the final `parking_lot_system.py`, without disabling checks or using suppression comments.

| Check | Before | After | Requirement |
|---|---|---|---|
| Pylint 4.1.3 | 4.10/10; 36 diagnostics | 10.00/10; 0 diagnostics | Above 9.5 |
| Bandit 1.9.4 | 5 findings: 2 High, 1 Medium, 2 Low | 0 findings | Handle all findings |
| Flake8 7.4.1 | 10 violations | 0 violations | Clear formatting findings |
| Regression tests | Not present in assigned source | 16 passed | Additional verification |

Environment: Python 3.12.14 on Windows in an isolated virtual environment. Raw output is preserved in `before/` and `after/`; `run_metadata.json` records commands and exit codes. An empty `after/flake8_report.txt` is the tool's genuine successful output; its exit code is 0.

## Execution and verification

The final demo reports P02 unavailable, surge fee 45.0 and one vacant slot. Hash output changes to SHA-256 (64 hexadecimal characters), and PIN output varies by design. Gate status is False without PARKING_GATE_KEY and True when configured; the value is never printed. Manifest format remains a Python mapping written as UTF-8 text.

Sixteen tests cover successful bookings and charges, unknown/occupied slots, invalid and fractional hours, blank plates, log isolation, release, vacancy counts, valid fee arithmetic, rejected code expressions, expression size limits, negative/non-finite fees, SHA-256, secure PIN boundaries, literal filenames, import side effects and gate-secret non-disclosure. See `after/test_report.txt`.

## Three fix commits

1. `Lab 5: fix Bandit security findings and preserve baseline reports` (`08a49f6`).
2. `Lab 5: fix Pylint quality issues and validate parking inputs` (`6408246`).
3. `Lab 5: fix Flake8 formatting and complete verified deliverables` (the final submission commit; use `git log -3 --oneline`).

The first two fixes overlap with other tools' findings, as expected. The third commit contains final line wrapping, all after-reports, regression checks and the completed report.

## Behaviour changes and limits

Function names now use snake_case; standalone usage is unchanged, but external Python callers would need to use the new names. release_slot returns a success Boolean. Arbitrary Python surge expressions are intentionally rejected; supported arithmetic is documented in the function. A four-digit random PIN is still small and not guaranteed unique. SHA-256 of a plate is an identifier, not proof of anonymity. The program remains an in-memory teaching example with no database or authentication service.

The upstream README mentions an interactive question, but the actual assigned script has no input prompt; its real execution was used as evidence.

## Issue table

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Shell command injection | Bandit B605 / High | 64 | A filename was concatenated into os.system, allowing shell metacharacters to become commands. | Remove the shell call; print the export message directly. |
| Weak vehicle hash | Bandit B324 / High | 53 | MD5 is unsuitable for security-sensitive identifiers. | Use hashlib.sha256. A plate hash alone does not guarantee anonymity. |
| Arbitrary expression execution | Bandit B307 / Medium; Pylint W0123 | 46-49 | eval accepts executable Python rather than just a surge calculation. | Parse a restricted AST: numbers, base_rate, +, -, *, / and unary signs only. Bound expression length and nodes; reject non-finite or negative results. |
| Suppressed failures | Bandit B110 / Low; Pylint W0702; Flake8 E722 | 27-33 | A bare except silently discarded every error. | Catch KeyError only; return False for unknown slots and True on success. |
| Predictable ticket PIN | Bandit B311 / Low | 56-57 | The standard random generator is unsuitable for security tokens. | Use 1000 + secrets.randbelow(9000), retaining four-digit PINs. |
| Shared mutable default | Pylint W0102 | 15 | entry_logs=[] persists across calls and retains unrelated entries. | Use None and create a fresh list when the caller does not supply logs. |
| Global scalar mutation | Pylint W0603, C0103 | 12,16,22 | A global statement updates total_collections inside a function. | Keep the running amount in COLLECTIONS['total']; remove global rebinding. |
| Resource handling | Pylint R1732, W1514 | 60-63 | Manual close is skipped if writing fails; encoding is implicit. | Use a with block with encoding='utf-8'. |
| Redundant availability logic | Pylint C0121, R1703, R1705; Flake8 E711 | 36-43 | Equality against None and a redundant if/else obscure a simple check. | Return slot is not None and not slot['is_occupied']. |
| Unused and shadowed names | Pylint W0611, W0612, W0621; Flake8 F401, F841 | 4,37,47,67-71 | Unused math, overtime_fee and loop keys; a parameter shadows parking_slots. Tools could not see base_rate usage inside eval. | Use math for finite checks, remove dead locals, rename the parameter to slots, count values directly, and reference base_rate explicitly in the AST interpreter. |
| Missing documentation and naming | Pylint C0114, C0116, C0103 | 1,15-75 | Functions lack docstrings and use mixed-case names. | Add module/function docstrings and snake_case function names; update all internal callers. |
| Formatting and string style | Pylint C0301, C0304, C0209; Flake8 E501, W292 | 7-9,23,88 | Long lines, percent-style interpolation and a missing final newline reduce consistency. | Wrap lines to 79 columns, use f-strings, and end the file with a newline. |
| Secret embedded and printed | Manual review / additional fix | 76,85 | The demo stored a gate credential in source and printed its value. This was not flagged by this Bandit run. | Read PARKING_GATE_KEY from the environment and print only whether it is configured. |
| Import side effects and invalid bookings | Manual review / additional fix | 15-24,88 | Import runs the demo; nonpositive or invalid booking hours can corrupt collections. | Add a __main__ guard and reject invalid hours and blank plates before state changes. |

## Reflection

The supplied three-page handout does not list reflection questions, although the source README refers to four. These are four relevant lab reflection prompts, not quotations of missing questions.

## 1. What did each static analysis tool contribute?

Pylint exposed the shared mutable default, global rebinding, missing documentation and unnecessarily complex logic. Bandit identified five security findings, including shell execution and eval. Flake8 identified ten style or name-use violations. Their overlap helped confirm fixes, while their different scopes found different classes of defects.

## 2. Which issues were prioritized, and why?

The high-severity shell injection and MD5 findings and the medium-severity eval finding were addressed first. The shell call was unnecessary, so printing removed the risk entirely. A small arithmetic interpreter preserved base_rate * 1.50 while rejecting executable Python. Lower-severity exception handling and PIN generation issues were then fixed before the quality and formatting work.

## 3. What required care when applying the fixes?

Replacing eval with a simple numeric parser would have broken the original expression using base_rate. The replacement therefore supports only the arithmetic the program needs, with limits on input size and finite results. Renaming functions required updating all internal calls. Tests checked that collections, vacancy counts and the 45.0 surge-fee example still behaved correctly.

## 4. What are the benefits and limitations of static analysis?

Static analysis provides repeatable feedback without running every path and makes maintenance easier. A clean report does not prove correctness or security: manual inspection found the printed hardcoded gate credential and missing booking validation, neither of which appeared as separate findings here. Sixteen regression tests supplement the scans. In future work the three tools and tests can run on every change.
