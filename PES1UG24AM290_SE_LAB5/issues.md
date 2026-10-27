# Identified issues and fixes

Line numbers refer to the untouched assigned source in `before/parking_lot_system.py.original.txt`. Bandit severity labels are the tool's actual output; manual findings are identified separately.

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
