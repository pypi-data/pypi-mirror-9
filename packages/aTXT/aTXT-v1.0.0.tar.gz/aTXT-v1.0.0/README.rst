aTXT.py
=======

A user-friendly tool for extract text data from files of a directory in-depth. 
Files with the extension ``.docx``,\ ``.pdf``,\ ``.doc`` (only *windows*) could be convert a plain
text, file ``.txt``. 

Meta
----

-  Author: Jonathan Prieto
-  Email: prieto.jona@gmail.com
-  Notes: Have feedback? Please send me an email. This project is in development.

Installing
----------

```
    pip install aTXT
```

Usage
-----

```
    aTXT --help 
```
Console shows:

```
A friendly Extractor of Text for Data Mining

Usage:
    aTXT
    aTXT -i
    aTXT <file> [-v|--verbose] [-uo] [--to <to>]
    aTXT [--from <from>] [--to <to>] <file>... [-uo] [-v|--verbose]
    aTXT --path <path> --depth <depth> [--to <to>] [-v|--verbose] 
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
```

