#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Jonathan S. Prieto
# @Date:   2015-01-14 22:46:10
# @Last Modified by:   Jonathan Prieto 
# @Last Modified time: 2015-01-15 19:18:06

"""
A friendly Extractor of Text for Data Mining

Usage:
    aTXT
    aTXT -i
    aTXT <file> [-V|--verbose] [-uo] [--to <to>]
    aTXT [--from <from>] [--to <to>] <file>... [-uo] [-V|--verbose]
    aTXT --path <path> --depth <depth> [--to <to>] [-V|--verbose] 
            [-a|--all] [-p|--pdf] [-d|--doc] [-x|--docx] [-t|--dat] [-uo]
    aTXT [-h|--help] 

Arguments:
    <file>            If <from> is none, file should be in current directory.
    --path <path>     Process the folder with path <path> and all files inside.

General Options:
    -i                Launch a Graphical Interface.
    --from <from>     Process files from path <from>. [default: ./]
    --to <to>         Save all (*.txt) files to path <to> if <file> appears. [default: ./]
    --depth <depth>   Depth for trasvering path using depth-first-search
                      for --path option. [default: 1]
    -a, --all         Convert all allowed formats (pdf, docx, doc, dat).
    -p, --pdf         Convert files with extension (*.pdf|*.PDF).
    -x, --docx        Convert files with extension (*.docx|*.DOCX).
    -d, --doc         Convert files with extension (*.doc|*.DOC).
    -t, --dat         Convert files with extension (*.dat|*.DAT).
    -u                Use uppercase for all text processed.
    -o                Overwrite if *.txt file version yet exists.
    -h, --help        Print this help.
    -V, --version         Print current version installed.
    -v, --verbose     Print error messages.
"""

from docopt import docopt

if __name__ == '__main__':
    args = docopt(__doc__)
    print args

