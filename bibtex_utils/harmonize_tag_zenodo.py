#!/usr/bin/env python
"""Harmonize BibTeX citation keys between Google Scholar and Zenodo formats.

Rewrites each entry's citation key to the ``authorYEARtitle`` pattern, where
*author* is the lowercased first surname, *YEAR* is the publication year, and
*title* is the first non-stop-word from the title.
"""

from __future__ import annotations

import argparse
import os
import unicodedata

import bibtexparser
from bibtexparser.model import Entry
import nltk
from nltk.corpus import stopwords


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    p.add_argument("in_bib", help="Input BibTeX file.")
    p.add_argument("out_bib", help="Output BibTeX file.")
    p.add_argument(
        "-f",
        dest="force_overwrite",
        action="store_true",
        help="Overwrite the output file if it exists.",
    )
    return p


def _get_stopwords() -> set[str]:
    """Return NLTK English stop words, downloading them if necessary."""
    try:
        return set(stopwords.words("english"))
    except LookupError:
        nltk.download("stopwords", quiet=True)
        return set(stopwords.words("english"))


def _strip_accents(text: str) -> str:
    """Remove Unicode diacritics (accents) from *text*."""
    nfkd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


def _extract_author(entry: Entry) -> str:
    """Return the lowercased first surname from the entry's author field."""
    author_field = entry.fields_dict.get("author")
    if author_field is None:
        return "unknown"
    surname = author_field.value.split(",")[0].strip().lower()
    if "-" in surname:
        surname = surname.split("-")[0]
    return surname


def _extract_first_content_word(title: str, stop_words: set[str]) -> str:
    """Return the first non-stop-word from *title*, lowercased and cleaned."""
    for word in title.split():
        cleaned = word.lower().replace("{", "").replace("}", "")
        if cleaned and cleaned not in stop_words:
            if "-" in cleaned:
                cleaned = cleaned.split("-")[0]
            return cleaned

    # Fallback: use the first word regardless.
    first = title.split()[0] if title.strip() else "untitled"
    return first.lower().replace("{", "").replace("}", "")


def replace_bib_tags(library: bibtexparser.Library) -> bibtexparser.Library:
    """Rewrite citation keys to the ``authorYEARtitle`` format.

    Entries missing a *year* field are removed with a warning.

    Parameters
    ----------
    library : bibtexparser.Library
        Parsed BibTeX library.

    Returns
    -------
    bibtexparser.Library
        A new library with updated citation keys.
    """
    stop_words = _get_stopwords()
    entries_to_remove: list[Entry] = []

    for entry in library.entries:
        year_field = entry.fields_dict.get("year")
        if year_field is None:
            print(f"Warning: no year for entry {entry.key!r}, skipping.")
            entries_to_remove.append(entry)
            continue

        title_field = entry.fields_dict.get("title")
        title_text = title_field.value if title_field else ""

        author = _extract_author(entry)
        year = year_field.value
        title_word = _extract_first_content_word(title_text, stop_words)

        new_key = _strip_accents(f"{author}{year}{title_word}")
        entry.key = new_key

    for entry in entries_to_remove:
        library.remove(entry)

    return library


def main() -> None:
    """CLI entry point for citation-key harmonization."""
    parser = _build_arg_parser()
    args = parser.parse_args()

    if not os.path.isfile(args.in_bib):
        parser.error(f"{args.in_bib} does not exist.")

    if os.path.isfile(args.out_bib) and not args.force_overwrite:
        parser.error(
            f"{args.out_bib} already exists. Use -f to overwrite."
        )

    library = bibtexparser.parse_file(args.in_bib)

    if library.failed_blocks:
        print(
            f"Warning: {len(library.failed_blocks)} block(s) failed to parse."
        )

    replace_bib_tags(library)

    bibtexparser.write_file(args.out_bib, library)
    print(f"{len(library.entries)} entries in total.")


if __name__ == "__main__":
    main()
