#!/usr/bin/env python3
"""rename — bulk file rename utility.

Rename files using patterns (prefix, suffix, replace, regex).
Supports dry-run mode. Zero external dependencies.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys

__version__ = "1.0.0"
__prog__ = "rename"


def resolve_files(patterns: list[str]) -> list[str]:
    """Expand glob patterns into a sorted list of existing files (no dirs)."""
    seen: set[str] = set()
    result: list[str] = []
    for pat in patterns:
        for path in sorted(glob.glob(pat)):
            if os.path.isfile(path) and path not in seen:
                seen.add(path)
                result.append(path)
    return result


def apply_rename(
    src: str,
    *,
    prefix: str | None = None,
    suffix: str | None = None,
    replace: tuple[str, str] | None = None,
    regex: tuple[str, str] | None = None,
) -> str | None:
    """Compute the new name for *src* given the requested transforms.

    Returns the new basename (not full path), or *None* if the name
    would not change.
    """
    base = os.path.basename(src)
    name, ext = os.path.splitext(base)

    if prefix is not None:
        name = prefix + name

    if suffix is not None:
        name = name + suffix

    if replace is not None:
        old, new = replace
        name = name.replace(old, new)

    if regex is not None:
        pattern, repl = regex
        name = re.sub(pattern, repl, name)

    new_base = name + ext
    return new_base if new_base != base else None


def run(args: argparse.Namespace) -> int:
    """Execute the rename operation.  Returns an exit code."""
    files = resolve_files(args.patterns)

    if not files:
        print(f"{__prog__}: no files matched the given pattern(s)", file=sys.stderr)
        return 1

    if args.verbose:
        print(f"{__prog__}: {len(files)} file(s) matched")

    renamed_count = 0
    for src in files:
        new_base = apply_rename(
            src,
            prefix=args.prefix,
            suffix=args.suffix,
            replace=(args.replace[0], args.replace[1]) if args.replace else None,
            regex=(args.regex[0], args.regex[1]) if args.regex else None,
        )
        if new_base is None:
            if args.verbose:
                print(f"  = {os.path.basename(src)}  (unchanged)")
            continue

        dirname = os.path.dirname(src) or "."
        dst = os.path.join(dirname, new_base)

        if os.path.exists(dst):
            print(
                f"{__prog__}: cannot rename {os.path.basename(src)!r} -> {new_base!r}: "
                f"destination already exists",
                file=sys.stderr,
            )
            return 1

        if args.dry_run:
            print(f"  ~ {os.path.basename(src)} -> {new_base}")
        else:
            os.rename(src, dst)
            print(f"  + {os.path.basename(src)} -> {new_base}")

        renamed_count += 1

    if renamed_count == 0:
        if not args.verbose:
            print(f"{__prog__}: no files were renamed (use --verbose to see why)", file=sys.stderr)
        return 1

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=__prog__,
        description="Bulk file rename utility.",
        epilog=(
            "Examples:\n"
            f"  {__prog__} --prefix 'draft_' *.md\n"
            f"  {__prog__} --suffix '_backup' *.txt\n"
            f"  {__prog__} --replace 'old' 'new' *.jpg\n"
            f"  {__prog__} --regex 's/\\d+//' *.log\n"
            f"  {__prog__} --dry-run --prefix 'v2_' *\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "patterns",
        nargs="+",
        help="One or more glob patterns to match files (e.g. *.txt, data/*.csv)",
    )

    parser.add_argument(
        "--prefix",
        help="Prepend text to each filename (before the extension)",
    )
    parser.add_argument(
        "--suffix",
        help="Append text to each filename (before the extension)",
    )
    parser.add_argument(
        "--replace",
        nargs=2,
        metavar=("OLD", "NEW"),
        dest="replace",
        help="Replace all occurrences of OLD with NEW in filenames",
    )
    parser.add_argument(
        "--regex",
        nargs=2,
        metavar=("PATTERN", "REPLACEMENT"),
        dest="regex",
        help="Apply a regex substitution (re.sub) to filenames",
    )

    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Show what would be renamed without actually renaming",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show matched files even when unchanged",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Validate that at least one transform was given
    transforms = [args.prefix, args.suffix, args.replace, args.regex]
    if all(t is None for t in transforms):
        parser.error("at least one of --prefix, --suffix, --replace, or --regex is required")

    return run(args)


if __name__ == "__main__":
    sys.exit(main())
