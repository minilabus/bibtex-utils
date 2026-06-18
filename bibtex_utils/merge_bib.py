#!/usr/bin/env python
"""Merge a list of BibTeX files into one, removing duplicate entries.

Duplicates are identified by their citation key. When duplicates are found,
the first occurrence is kept.
"""

from __future__ import annotations

import argparse
import os

import bibtexparser
from bibtexparser.model import Entry


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    p.add_argument("in_bib", nargs="+", help="Input BibTeX files to merge.")
    p.add_argument("out_bib", help="Output BibTeX file.")
    p.add_argument(
        "-f",
        dest="force_overwrite",
        action="store_true",
        help="Overwrite the output file if it exists.",
    )
    return p


def remove_duplicates(entries: list[Entry]) -> list[Entry]:
    """Remove duplicate entries based on their citation key.

    Parameters
    ----------
    entries : list[Entry]
        List of BibTeX entries (bibtexparser v2 Entry objects).

    Returns
    -------
    list[Entry]
        De-duplicated list, preserving first-seen order.
    """
    seen: dict[str, Entry] = {}
    for entry in entries:
        if entry.key not in seen:
            seen[entry.key] = entry

    n_duplicates = len(entries) - len(seen)
    if n_duplicates:
        print(f"\t{n_duplicates} duplicate(s) removed.")

    return list(seen.values())


def main() -> None:
    """CLI entry point for BibTeX file merging."""
    parser = _build_arg_parser()
    args = parser.parse_args()

    for in_bib in args.in_bib:
        if not os.path.isfile(in_bib):
            parser.error(f"{in_bib} does not exist.")

    if os.path.isfile(args.out_bib) and not args.force_overwrite:
        parser.error(
            f"{args.out_bib} already exists. Use -f to overwrite."
        )

    all_entries: list[Entry] = []
    for i, filename in enumerate(args.in_bib):
        library = bibtexparser.parse_file(filename)

        if library.failed_blocks:
            print(
                f"Warning: {len(library.failed_blocks)} block(s) failed to "
                f"parse in {filename}."
            )

        print(f"{len(library.entries)} entries in file #{i + 1}")
        deduped = remove_duplicates(library.entries)
        all_entries.extend(deduped)

    print(f"{len(all_entries)} entries in merged file (before global dedup).")
    unique_entries = remove_duplicates(all_entries)

    out_library = bibtexparser.Library()
    for entry in unique_entries:
        out_library.add(entry)

    bibtexparser.write_file(args.out_bib, out_library)
    print(f"{len(unique_entries)} entries in total.")


if __name__ == "__main__":
    main()
