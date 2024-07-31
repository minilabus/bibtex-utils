#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Convert a sequence of DOI to a single bib file.
"""

import argparse
import httplib2
import os
from urllib import request, parse

from bs4 import BeautifulSoup
from gscholar import query


def _build_arg_parser():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('in_doi', nargs='+',
                   help='List of input DOI.')
    p.add_argument('out_bib',
                   help='Output bib file.')
    p.add_argument('-f', dest='force_overwrite', action='store_true',
                   help='Overwrite the output files if they exist.')
    return p


class Bibtex(object):
    """ Convert doi number to bibtex entries."""

    def __init__(self, doi=None, title=None):
        """
        Input doi number ou title (actually any text/keyword.)
        Returns doi, encoded doi, and doi url or just the title.
        """
        _base_url = "http://dx.doi.org/"
        self.doi = doi
        self.title = title
        self.bibtex = None
        if doi:
            self._edoi = parse.quote(doi)
            self.url = _base_url + self._edoi  # Encoded doi.
        else:
            self.url = None

    def validate_doi(self):
        """Validate doi number and return the url."""
        h = httplib2.Http()
        h.request(self.url, "GET")
        req = httplib2.Http()
        try:
            self.header, self.html = req.request(self.url, "GET")
            self.paper_url = self.header['content-location']
            return self.paper_url
        except Exception as e:
            print("Could not resolve doi url at: %s \n" % self.url)
            print('Error: %s\n' % str(e))
            return None

    def _soupfy(self, url):
        """Returns a soup object."""
        html = request.urlopen(url).read()
        self.soup = BeautifulSoup(html)
        return self.soup

    def getGScholar(self):
        """If you are feeling lucky."""
        bibtex = query(self.doi, 4)[0]
        self.bibtex = bibtex.encode('utf-8').decode()
        return self.bibtex


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    if os.path.isfile(args.out_bib) and not args.force_overwrite:
        parser.error('{} exists, delete it first.'.format(args.out_bib))

    for filename in args.in_doi:
        # Create the bib object.
        bib = Bibtex(filename)
        bib.getGScholar()

        with open(args.out_bib, "a") as f:
            f.write(bib.bibtex)


if __name__ == '__main__':
    main()
