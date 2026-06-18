#!/usr/bin/env python
"""Fetch BibTeX entries from DOIs via content negotiation.

Each DOI is resolved through https://doi.org using the standard content
negotiation mechanism (``Accept: application/x-bibtex``).  The resulting
BibTeX records are written to a single output file.
"""

from __future__ import annotations

import argparse
import os
import sys

import requests


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    p.add_argument("in_doi", nargs="+", help="One or more DOIs to resolve.")
    p.add_argument("out_bib", help="Output BibTeX file.")
    p.add_argument(
        "-f",
        dest="force_overwrite",
        action="store_true",
        help="Overwrite the output file if it exists.",
    )
    return p


def fetch_bibtex_from_doi(doi: str, timeout: int = 30) -> str | None:
    """Resolve a DOI to its BibTeX entry via content negotiation.

    Uses the official DOI content negotiation endpoint with the
    ``application/x-bibtex`` media type.

    Parameters
    ----------
    doi : str
        The DOI string (e.g. ``"10.1000/xyz123"``).
    timeout : int
        HTTP request timeout in seconds.

    Returns
    -------
    str | None
        The BibTeX record as a string, or ``None`` on failure.
    """
    url = f"https://doi.org/{doi}"
    headers = {"Accept": "application/x-bibtex"}

    try:
        response = requests.get(
            url, headers=headers, allow_redirects=True, timeout=timeout,
        )
        response.raise_for_status()
        return response.text
    except requests.RequestException as exc:
        print(f"Could not resolve DOI {doi!r}: {exc}", file=sys.stderr)
        return None


def main() -> None:
    """CLI entry point for DOI-to-BibTeX conversion."""
    parser = _build_arg_parser()
    args = parser.parse_args()

    if os.path.isfile(args.out_bib) and not args.force_overwrite:
        parser.error(
            f"{args.out_bib} already exists. Use -f to overwrite."
        )

    records: list[str] = []
    for doi in args.in_doi:
        bibtex = fetch_bibtex_from_doi(doi)
        if bibtex is not None:
            records.append(bibtex)

    with open(args.out_bib, "w", encoding="utf-8") as f:
        f.write("\n".join(records))

    print(f"Wrote {len(records)}/{len(args.in_doi)} entries to {args.out_bib}.")


if __name__ == "__main__":
    main()
