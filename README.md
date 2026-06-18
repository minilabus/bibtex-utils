# bibtex-utils

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: BSD-2](https://img.shields.io/badge/license-BSD--2--Clause-green.svg)](LICENSE)

Tools for BibTeX manipulation at the MINi Lab (Université de Sherbrooke).

## Features

| Command | Description |
|---|---|
| `bu-ieee-case` | Apply IEEE title-case formatting to all entries in a `.bib` file. Keeps neuroimaging acronyms (MRI, DTI, …) fully capitalised. |
| `bu-get-bib-from-doi` | Fetch BibTeX entries from one or more DOIs via content negotiation. |
| `bu-harmonize-tag-zenodo` | Rewrite citation keys to a uniform `authorYEARtitle` pattern. |
| `bu-merge-bib` | Merge multiple `.bib` files into one, removing duplicate entries. |

## Installation

```bash
# Editable (development) install
pip install -e .

# With development tools (ruff, pytest)
pip install -e ".[dev]"
```

## Usage

```bash
# Apply IEEE title case
bu-ieee-case input.bib output.bib

# Fetch BibTeX from DOIs
bu-get-bib-from-doi 10.1016/j.neuroimage.2023.01.001 output.bib

# Harmonize citation keys
bu-harmonize-tag-zenodo input.bib output.bib

# Merge multiple bib files
bu-merge-bib file1.bib file2.bib merged.bib
```

All commands support `-f` to overwrite existing output files.

## Acronyms

The IEEE case formatter loads a curated dictionary of **270+ neuroimaging
acronyms** from [`bibtex_utils/bib_data/acronyms.json`](bibtex_utils/bib_data/acronyms.json).
Contributions to this list are welcome via pull request.

## License

[BSD-2-Clause](LICENSE) — Copyright © 2022 minilabus.
