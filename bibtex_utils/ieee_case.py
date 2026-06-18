#!/usr/bin/env python
"""Format BibTeX entry titles to conform with IEEE citation standards.

This script parses an input BibTeX database and applies IEEE title case rules
to the title fields. It dynamically loads a domain-specific dictionary of
neuroimaging acronyms to ensure recognized abbreviations remain fully
capitalized.

Standard English stop words are converted to lowercase using the
Natural Language Toolkit (NLTK).
"""

from __future__ import annotations

import argparse
import json
import os
import re
from importlib.resources import files

import bibtexparser
from bibtexparser.model import Field
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


def get_acronyms() -> set[str]:
    """Load the acronyms dictionary from the package data directory.

    Returns
    -------
    set[str]
        Upper-case acronym strings (e.g. ``{"MRI", "DTI", ...}``).
    """
    json_path = files("bibtex_utils").joinpath("bib_data", "acronyms.json")
    acronyms_dict = json.loads(json_path.read_text(encoding="utf-8"))
    return set(acronyms_dict.keys())


def _get_stopwords() -> set[str]:
    """Return NLTK English stop words, downloading them if necessary."""
    try:
        return set(stopwords.words("english"))
    except LookupError:
        nltk.download("stopwords", quiet=True)
        return set(stopwords.words("english"))


def convert_to_ieee_case(title: str, acronym_set: set[str]) -> str:
    """Apply IEEE title case to *title* while keeping known acronyms uppercase
    and respecting BibTeX brace protection (e.g., {FreeSurfer}).

    Parameters
    ----------
    title : str
        The raw title string.
    acronym_set : set[str]
        Set of known acronyms in upper case.

    Returns
    -------
    str
        The title reformatted according to IEEE rules.
    """
    # Explicit list of words IEEE lowercases (articles, conjunctions, short prepositions)
    ieee_lowercase = {
        "a", "an", "the", 
        "and", "but", "or", "nor", "for", "yet", "so",
        "as", "at", "by", "in", "of", "on", "to", "up", "off", "out"
    }

    # Split by braced groups OR alphabetical runs to retain all punctuation and whitespace
    tokens = re.split(r"(\{[^}]+\}|[a-zA-Z]+)", title)
    
    # Identify indices of tokens that are either pure alphabetic or braced groups
    word_indices = []
    for i, tok in enumerate(tokens):
        if tok.isalpha() or (tok.startswith('{') and tok.endswith('}')):
            word_indices.append(i)

    if not word_indices:
        return title

    for idx, i in enumerate(word_indices):
        word = tokens[i]

        # If the word is protected by BibTeX braces, leave it completely untouched
        if word.startswith('{') and word.endswith('}'):
            continue

        if word.upper() in acronym_set:
            tokens[i] = word.upper()
            continue

        # Check if the text between the previous word and this word contains a colon
        after_colon = False
        if idx > 0:
            prev_word_idx = word_indices[idx - 1]
            intervening_punctuation = "".join(tokens[prev_word_idx + 1 : i])
            if ":" in intervening_punctuation:
                after_colon = True

        # First word, last word, and words following a colon are always capitalized
        if idx == 0 or idx == len(word_indices) - 1 or after_colon:
            tokens[i] = word.capitalize()
            continue

        # IEEE keeps specific short prepositions, conjunctions, and articles lowercase
        if word.lower() in ieee_lowercase:
            tokens[i] = word.lower()
        else:
            tokens[i] = word.capitalize()

    return "".join(tokens)


def process_bibtex(input_file: str) -> bibtexparser.Library:
    """Parse a BibTeX file and apply IEEE title case to every entry.

    Parameters
    ----------
    input_file : str
        Path to the input ``.bib`` file.

    Returns
    -------
    bibtexparser.Library
        The modified library ready to be written.
    """
    acronyms = get_acronyms()
    library = bibtexparser.parse_file(input_file)

    if library.failed_blocks:
        print(
            f"Warning: {len(library.failed_blocks)} block(s) failed to parse."
        )

    for entry in library.entries:
        title_field = entry.fields_dict.get("title")
        if title_field is not None:
            original_title = title_field.value.strip("{}")
            new_title = convert_to_ieee_case(original_title, acronyms)
            entry.set_field(Field("title", f"{{{new_title}}}"))

    return library


def main() -> None:
    """CLI entry point for IEEE title-case formatting."""
    parser = _build_arg_parser()
    args = parser.parse_args()

    if not os.path.isfile(args.in_bib):
        parser.error(f"{args.in_bib} does not exist.")

    if os.path.isfile(args.out_bib) and not args.force_overwrite:
        parser.error(
            f"{args.out_bib} already exists. Use -f to overwrite."
        )

    library = process_bibtex(args.in_bib)
    bibtexparser.write_file(args.out_bib, library)


if __name__ == "__main__":
    main()
