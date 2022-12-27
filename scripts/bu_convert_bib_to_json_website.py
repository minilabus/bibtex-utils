#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Convert a .bib file to a json format for the MINILABUS website.
"""

import argparse
import json
import os

import bibtexparser


def _build_arg_parser():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('in_bib',
                   help='Input bib file.')
    p.add_argument('out_json',
                   help='Output json file.')
    p.add_argument('-f', dest='force_overwrite', action='store_true',
                   help='Overwrite the output files if they exist.')
    return p


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    if not os.path.isfile(args.in_bib):
        raise IOError('{} does not exist!'.format(args.in_bib))

    if os.path.isfile(args.out_bib) and not args.force_overwrite:
        parser.error('{} exists, delete it first.'.format(args.out_json))

    with open(args.in_bib, 'r') as bibfile:
        ori_bib = bibtexparser.load(bibfile)

    out_dict = []
    for entry in ori_bib.entries:
        curr_dict = {}
        curr_dict['image'] = '{}.png'.format(entry['ID'])
        curr_dict['title'] = entry['title']
        curr_dict['container-title'] = entry['journal']
        curr_dict['abstract'] = ''
        curr_dict['DOI'] = ''
        curr_dict['DOI'] = ''
        curr_dict['issued'] = {"date-parts": [[entry['year'], 2]]}
        authors = []
        for author in entry["author"].split(' and '):
            if not author == 'others':
                last, first = author.split(', ')
                authors.append({'family': last, 'given': first})
        curr_dict['author'] = authors
        out_dict.append(curr_dict)

    with open(args.out_json, 'w') as outfile:
        json.dump(out_dict, outfile,
                  indent=1, sort_keys=True)


if __name__ == '__main__':
    main()
