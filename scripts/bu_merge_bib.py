#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Merge a list of input bib file to a single one. Attemps to remove duplicated
entries.
"""

import argparse
from math import isnan
import os

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import pandas as pd


def _build_arg_parser():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('in_bib', nargs='+',
                   help='List of input bib file.')
    p.add_argument('out_bib',
                   help='Output bib file.')
    p.add_argument('-f', dest='force_overwrite', action='store_true',
                   help='Overwrite the output files if they exist.')
    return p


def remove_duplicates(ori_bib):
    if isinstance(ori_bib, list):
        entries = ori_bib
    else:
        entries = ori_bib.entries

    entry_0_keys_id = set([entry['ID'] for entry in entries])

    df = pd.DataFrame(entries)
    entries_list = []
    for ID in entry_0_keys_id:
        elem = df[df['ID'] == ID].iloc[0].to_dict()
        clean_dict = {k: elem[k] for k in elem if isinstance(elem[k], str) or
                      not isnan(elem[k])}
        entries_list.append(clean_dict)

    db = BibDatabase()
    db.entries = entries_list
    print('\t{} duplicates in this file.'.format(
        len(entries) - len(db.entries)))

    return db


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    if not os.path.isfile(args.in_bib):
        raise IOError('{} does not exist!'.format(args.in_bib))

    if os.path.isfile(args.out_bib) and not args.force_overwrite:
        parser.error('{} exists, delete it first.'.format(args.out_bib))

    entries_list = []
    for i, filename in enumerate(args.in_bib):
        with open(filename, 'r') as bibfile:
            ori_bib = bibtexparser.load(bibfile)

        print('{} entries in file #{}'.format(len(ori_bib.entries), i))

        out_bib = remove_duplicates(ori_bib)
        entries_list.extend(out_bib.entries)

    print('\nFinal file has {} entries.'.format(len(entries_list)))
    out_bib = remove_duplicates(entries_list)
    writer = BibTexWriter()
    with open(args.out_bib, 'w') as bibfile:
        bibfile.write(writer.write(out_bib))


if __name__ == '__main__':
    main()
