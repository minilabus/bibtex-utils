#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Merge a list of input bib files to a single one. Attempts to remove duplicated
entries and adjust citation keys according to a specific format.
"""

import argparse
import os

import nltk
from nltk.corpus import stopwords
import unicodedata
nltk.download('stopwords')

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

def _build_arg_parser():
    # Create an argument parser to handle command line arguments
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter)
    # Add argument for input BibTeX file
    p.add_argument('in_bib',
                   help='List of input bib file.')
    # Add argument for output BibTeX file
    p.add_argument('out_bib',
                   help='Output bib file.')
    # Add optional flag to force overwrite of the output file if it already exists
    p.add_argument('-f', dest='force_overwrite', action='store_true',
                   help='Overwrite the output files if they exist.')
    return p

def _replace_bib_tags(bib_db):
    """
    Replace bibtex entry keys to match the format: authorYEARtitle.
    E.g. "rheault_influence_2022" -> "rheault2022influence"
    """
    stop_words = set(stopwords.words('english'))
    for entry in bib_db.entries:
        original_key = entry['ID']

        # Regex to match the typical pattern in the original keys.
        # The pattern expects 'author_title_year' format with alphabets and hyphens allowed in author/title.

        # Extract author, year, and title from the matched groups
        author = entry['author'].split(', ')[0].lower()  # Use the first part of the author name if hyphenated
        if '-' in author:
            author = author.split('-')[0]
        
        if 'year' not in entry:
            print(f'Year not found for entry: {entry}')
            del entry
            continue
        year = entry['year']
        # Find the first non-stop word in the title
        title_parts = entry['title'].split(' ')
        title = None
        for word in title_parts:
            if word.lower() not in stop_words:
                title = word
                break
        if title is None:
            title = title_parts[0]  # Fallback to the first part if no non-stop word is found
        if '-' in title:
            title = title.split('-')[0]
        title = title.lower().replace('{', '').replace('}', '')

        # Construct the new key as 'authorYEARtitle'
        new_key = f"{author}{year}{title}"
        # Update the entry ID with the new key
        new_key = ''.join(
            (c for c in unicodedata.normalize('NFD', new_key) if unicodedata.category(c) != 'Mn')
        )
        entry['ID'] = new_key

    return bib_db

def main():
    # Build the argument parser and parse the command line arguments
    parser = _build_arg_parser()
    args = parser.parse_args()

    # Check if the input BibTeX file exists
    if not os.path.isfile(args.in_bib):
        raise IOError(f'{args.in_bib} does not exist!')

    # If the output file already exists and overwrite is not allowed, raise an error
    if os.path.isfile(args.out_bib) and not args.force_overwrite:
        parser.error(f'{args.out_bib} exists, delete it first or use -f to overwrite.')

    # Load the original BibTeX file
    with open(args.in_bib, 'r') as bibfile:
        ori_bib = bibtexparser.load(bibfile)
    
    # Replace bibtex entry keys with the desired format
    modified_bib = _replace_bib_tags(ori_bib)

    # Write the modified BibTeX entries to the output file
    writer = BibTexWriter()
    with open(args.out_bib, 'w') as bibfile:
        bibfile.write(writer.write(modified_bib))
    
    # Print the total number of entries in the output file
    print(f'{len(modified_bib.entries)} entries in total.')

if __name__ == '__main__':
    main()
