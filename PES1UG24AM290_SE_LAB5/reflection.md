# Reflection

The supplied three-page handout does not list reflection questions, although the source README refers to four. These are four relevant lab reflection prompts, not quotations of missing questions.

## 1. What did each static analysis tool contribute?

Pylint exposed the shared mutable default, global rebinding, missing documentation and unnecessarily complex logic. Bandit identified five security findings, including shell execution and eval. Flake8 identified ten style or name-use violations. Their overlap helped confirm fixes, while their different scopes found different classes of defects.

## 2. Which issues were prioritized, and why?

The high-severity shell injection and MD5 findings and the medium-severity eval finding were addressed first. The shell call was unnecessary, so printing removed the risk entirely. A small arithmetic interpreter preserved base_rate * 1.50 while rejecting executable Python. Lower-severity exception handling and PIN generation issues were then fixed before the quality and formatting work.

## 3. What required care when applying the fixes?

Replacing eval with a simple numeric parser would have broken the original expression using base_rate. The replacement therefore supports only the arithmetic the program needs, with limits on input size and finite results. Renaming functions required updating all internal calls. Tests checked that collections, vacancy counts and the 45.0 surge-fee example still behaved correctly.

## 4. What are the benefits and limitations of static analysis?

Static analysis provides repeatable feedback without running every path and makes maintenance easier. A clean report does not prove correctness or security: manual inspection found the printed hardcoded gate credential and missing booking validation, neither of which appeared as separate findings here. Sixteen regression tests supplement the scans. In future work the three tools and tests can run on every change.
