#!/usr/bin/env python3
"""Run the top-level script regression suite and reject empty discovery."""
import argparse
from pathlib import Path
import sys
import unittest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default = Path(__file__).resolve().parent.parent / "tests" / "unit" / "scripts"
    parser.add_argument("directory", nargs="?", type=Path, default=default)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.discover(str(args.directory), pattern="test_*.py")
    if suite.countTestCases() == 0:
        print("No tests discovered; refusing to pass.", file=sys.stderr)
        return 1
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
