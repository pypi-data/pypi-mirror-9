
``atkit`` provides tools, enabled for all python processes (via ``usercustomize.py``). At the moment, these include:

* A cli tool to completely enable/disable ``atkit``.
* A cli tool to "sandbox" any python module (requires write access), so that edits can be cleanly and safely done, even to standard library modules.
* An exception hook that logs all exceptions and drops you into your preferred debugger (pdb by default).
* A flexible, yet dead-simple logging wrapper that knows about context (filenames, function names, line numbers, etc.)

All of this is highly configurable. Components may be disabled, piece-wise.
