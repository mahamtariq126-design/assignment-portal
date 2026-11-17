"""
scripts/demo_defect.py - introduce or remove ONE deliberate, reversible defect
for the "failing run" demonstration (Demo B / Demo C).

    python scripts/demo_defect.py break    # introduce the bug
    python scripts/demo_defect.py fix      # restore the correct code
    python scripts/demo_defect.py status   # show which version is active

THE DEFECT:
    In validation.py the line that rejects an empty registration number is
    replaced with "pass". After that, the portal wrongly ACCEPTS submissions
    with no registration number. The existing tests (e.g. TEST 2) catch it.

You can also make the same change by hand in VS Code - see DEMO_GUIDE.md.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "validation.py")

CORRECT = 'errors["registration_number"] = "Registration number is required."  # REG-REQUIRED-CHECK'
BROKEN = 'pass  # DEFECT (demo): registration number check disabled  # REG-REQUIRED-CHECK'


def read():
    with open(TARGET, encoding="utf-8") as fh:
        return fh.read()


def write(text):
    with open(TARGET, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def main():
    action = sys.argv[1].lower() if len(sys.argv) > 1 else "status"
    text = read()
    is_broken = BROKEN in text
    is_correct = CORRECT in text

    if not (is_broken or is_correct):
        print("Could not find the marked line in validation.py (REG-REQUIRED-CHECK). "
              "Restore it with:  git checkout -- validation.py")
        return 1

    if action == "status":
        print("validation.py is currently:", "BROKEN (defect active)" if is_broken else "CORRECT")
        return 0
    if action == "break":
        if is_broken:
            print("Defect is already active.")
            return 0
        write(text.replace(CORRECT, BROKEN))
        print("DEFECT INTRODUCED in validation.py:")
        print("   - " + CORRECT)
        print("   + " + BROKEN)
        print("Empty registration numbers are now (wrongly) accepted. Run: python -m pytest")
        return 0
    if action == "fix":
        if is_correct:
            print("Code is already correct.")
            return 0
        write(text.replace(BROKEN, CORRECT))
        print("DEFECT REMOVED - validation.py restored to the correct implementation.")
        return 0

    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
