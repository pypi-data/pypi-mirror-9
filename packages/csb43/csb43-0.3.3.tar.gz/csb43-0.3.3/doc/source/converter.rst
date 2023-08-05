
Converter
==========

Convert a **CSB/AEB norm 43** file to other file formats.

Supported formats:

- `OFX <http://www.ofx.net/>`_
- `HomeBank CSV <http://homebank.free.fr/help/06csvformat.html>`_
- *HTML* *(python2)*
- *JSON*
- *ODS*: OpenDocument spreadsheet *(python2)*
- *CSV*, *TSV*: comma- or tab- separated values *(python2)*
- *XLS*: Microsoft Excel spreadsheet *(python2)*
- *XLSX*: OOXML spreadsheet *(python2)*
- *YAML*

Options:
-----------

::

    usage: csb2format [-h] [-s] [-df] [-d DECIMAL]
                  [-f {csv,homebank,html,json,ods,ofx,tsv,xls,xlsx,yaml}] [-v]
                  csbFile convertedFile

    Convert a CSB43 file to another format

    positional arguments:
    csbFile               a csb43 file ('-' for stdin)
    convertedFile         destination file ('-' for stdout)

    optional arguments:
    -h, --help            show this help message and exit
    -s, --strict          strict mode
    -df, --dayfirst       use DDMMYY as date format while parsing the csb43 file
                            instead of YYMMDD (default: True)
    -d DECIMAL, --decimal DECIMAL
                            set the number of decimal places for the currency type
                            (default: 2)
    -f {csv,homebank,html,json,ods,ofx,tsv,xls,xlsx,yaml}, --format {csv,homebank,html,json,ods,ofx,tsv,xls,xlsx,yaml}
                            Format of the output file (default: ofx)

Examples
----------

- Converting to OFX format:

    ::

        $ csb2format transactions.csb transactions.ofx

        $ csb2format --format ofx transactions.csb transactions.ofx

    or

    ::

        $ csb2format transactions.csb - > transactions.ofx

    From another app to file

    ::

        $ get_my_CSB_transactions | csb2format - transactions.ofx

- Converting to XLSX spreadsheet format:

    ::

        $ csb2format --format xlsx transactions.csb transactions.xlsx

Spreadsheets
-------------

*ODS* and *XLS* files are generated as books, with the first sheet containing the
accounts information, and the subsequent sheets containing the transactions of
each one of the accounts.

In *XLSX* files all the information is flattened in just one sheet.
