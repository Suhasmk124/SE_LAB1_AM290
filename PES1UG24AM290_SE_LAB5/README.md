# PES1UG24AM290 - SE Lab 5

Static analysis of the [assigned parking lot system](https://github.com/SETAPESU26/L5_51_parking_lot_system), source revision `f3fba6a9fd742604c8a906662eca8f9115ef976c`.

## Deliverables

- `parking_lot_system.py`: cleaned executable source.
- `before/` and `after/`: original and final Pylint, Bandit and Flake8 reports under the exact required names; command exit codes in `run_metadata.json`.
- `before/parking_lot_system.py.original.txt`: untouched original snapshot.
- `report.pdf` and `report.md`: complete report, issue table and reflection.
- `issues.md` and `reflection.md`: separately available tables and reflection responses.
- `test_parking_lot_system.py` and `after/test_report.txt`: 16 regression tests and actual results.

Final results: **Pylint 10.00/10; Bandit 0 findings; Flake8 0 findings; 16 tests passed.** Flake8's successful report is empty; the recorded exit code is 0.

## Reproduce (from this folder)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python parking_lot_system.py
python -m pylint --persistent=n parking_lot_system.py > after/pylint_report.txt
python -m bandit -r parking_lot_system.py > after/bandit_report.txt 2>&1
python -m flake8 parking_lot_system.py > after/flake8_report.txt
python -m unittest -v > after/test_report.txt 2>&1
git log -3 --oneline
```

On Linux/macOS use `source .venv/bin/activate` instead. Run analyzers against the cleaned source file; the tests and original snapshot are separate evidence. Reports included here were captured programmatically as UTF-8 from both output streams without editing tool findings. Re-running may change timestamps and random PINs.

To reproduce the baseline, copy `before/parking_lot_system.py.original.txt` into a separate temporary folder as `parking_lot_system.py`, then run the same three analyzer commands there. The baseline contains intentionally insecure teaching code; its archived findings are already provided.

Three fix commits are recorded in the parent repository history. See `report.md` for their subjects and scope. The final commit hash is available through `git log`, since a commit cannot embed its own hash.

Reflection note: the supplied handout contains no explicit reflection questions. Four relevant reflection prompts are clearly labelled in the report.
