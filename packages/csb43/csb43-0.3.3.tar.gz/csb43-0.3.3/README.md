
# csb43


- *[English](#markdown-header-english)*
    * [csb2format](#markdown-header-csb2format)
    * [using Python](#markdown-header-using-python)
- *[Español](#markdown-header-espanol)*
    * [csb2format](#markdown-header-csb2format_1)
    * [using Python](#markdown-header-en-python)


## English


Tools for converting from the Spanish banks' format **CSB norm 43** (*CSB43*).


### csb2format


Convert a **CSB/AEB norm 43** file to other file formats.

Supported formats:

- [OFX](http://www.ofx.net)
- [HomeBank CSV](http://homebank.free.fr/help/06csvformat.html)
- *HTML* *(python2)*
- *JSON*
- *ODS*: OpenDocument spreadsheet *(python2)*
- *CSV*, *TSV*: comma- or tab- separated values *(python2)*
- *XLS*: Microsoft Excel spreadsheet *(python2)*
- *XLSX*: OOXML spreadsheet *(python2)*
- *YAML*


#### Options:

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


#### Examples


- Converting to OFX format:

        $ csb2format transactions.csb transactions.ofx

        $ csb2format --format ofx transactions.csb transactions.ofx

    or


        $ csb2format transactions.csb - > transactions.ofx

    From another app to file


        $ get_my_CSB_transactions | csb2format - transactions.ofx

- Converting to XLSX spreadsheet format:


        $ csb2format --format xlsx transactions.csb transactions.xlsx


#### Spreadsheets


*ODS* and *XLS* files are generated as books, with the first sheet containing the
accounts information, and the subsequent sheets containing the transactions of
each one of the accounts.

In *XLSX* files all the information is flattened in just one sheet.


### Using Python


Parse a *CSB43* file and print the equivalent *OFX* file

    :::python

    # OFX
    from csb43 import csb_43, ofx

    csbFile = csb_43.File(open("movimientos.csb"), strict=False)

    # print to stdout
    print ofx.convertFromCsb(csbFile)

Parse a *CSB43* file and print the equivalent *HomeBank CSV* file

    :::python

    # OFX
    from csb43 import csb_43, homebank

    csbFile = csb_43.File(open("movimientos.csb"), strict=False)

    # print to stdout
    for line in homebank.convertFromCsb(csbFile):
        print line

Parse a *CSB43* file and print the equivalent in a tabular or dictionary-like file format

    :::python

    # OFX
    from csb43 import csb_43, formats

    csbFile = csb_43.File(open("movimientos.csb"), strict=False)

    # print 'yaml' format to stdout
    o = format.convertFromCsb(csbFile, 'yaml')
    print o.yaml

    # write 'xlsx' format to file
    o = format.convertFromCsb(csbFile, 'xlsx')
    with open("movimientos.xlsx", "wb") as f:
        f.write(o.xlsx)

---


## Español

Herramientas para convertir ficheros en formato usado por múltiples
bancos españoles (**norma 43 del Consejo Superior Bancario** [*CSB43*]
/ **Asociación Española de Banca** [*AEB43*]) a otros formatos.


### csb2format

Conversor de ficheros en **CSB/AEB norma 43** a otros formatos.

Formatos soportados:

- [OFX](http://www.ofx.net)
- [HomeBank CSV](http://homebank.free.fr/help/06csvformat.html)
-  *HTML* *(python2)*
-  *JSON*
-  *ODS*: hoja de cálculo OpenDocument *(python2)*
-  *CSV*, *TSV*: valores separados por coma o tabulador *(python2)*
-  *XLS*: hoja de cálculo de Microsoft Excel *(python2)*
-  *XLSX*: hoja de cálculo OOXML *(python2)*
-  *YAML*


#### Opciones:


    usage: csb2format [-h] [-s] [-df] [-d DECIMAL]
                    [-f {csv,homebank,html,json,ods,ofx,tsv,xls,xlsx,yaml}] [-v]
                    csbFile convertedFile

    Convierte un fichero CSB43 a otro formato

    optional arguments:
    -h, --help            show this help message and exit
    -v, --version         muestra la versión y termina

    conversion arguments:
    csbFile               fichero csb43 ('-' para entrada estándar)
    convertedFile         fichero de destino ('-' para salida estándar)
    -s, --strict          modo estricto (por defecto: False)
    -df, --dayfirst       usa DDMMYY -día, mes, año- como formato de fecha al
                            interpretar los datos del fichero csb43 en lugar de
                            YYMMDD -año, mes, día- (por defecto: True)
    -d DECIMAL, --decimal DECIMAL
                            establece el número de dígitos decimales a considerar
                            en el tipo de divisa (por defecto: 2)
    -f {csv,homebank,html,json,ods,ofx,tsv,xls,xlsx,yaml}, --format {csv,homebank,html,json,ods,ofx,tsv,xls,xlsx,yaml}
                            Formato del fichero de salida (por defecto: ofx)


#### Ejemplos


- Convertir a formato OFX:

        $ csb2format transactions.csb transactions.ofx

        $ csb2format --format ofx transactions.csb transactions.ofx

    o bien

        $ csb2format transactions.csb - > transactions.ofx


    Desde una aplicación de recuperación de datos a otro fichero

        $ get_my_CSB_transactions | csb2format - transactions.ofx


- Convertir a hoja de cálculo XLSX (Excel):

        $ csb2format --format xlsx transactions.csb transactions.xlsx


#### Hojas de cálculo


Los ficheros en *ODS* y *XLS* se generan a modo de libro, conteniendo la primera
hoja la información relativa a las cuentas, y las hojas siguientes conteniendo cada
una los movimientos de cada cuenta.

En los ficheros *XLSX* toda la información está aplanada en una sola hoja.


### En Python


Lee un archivo *CSB43* e imprime el contenido equivalente en *OFX*

    :::python

    # OFX
    from csb43 import csb_43, ofx

    csbFile = csb_43.File(open("movimientos.csb"), strict=False)

    # imprime a stdout
    print ofx.convertFromCsb(csbFile)

Lee un archivo *CSB* e imprime el contenido equivalente a *CSV* de *Homebank*

    :::python

    # OFX
    from csb43 import csb_43, homebank

    csbFile = csb_43.File(open("movimientos.csb"), strict=False)

    # imprime a stdout
    for line in homebank.convertFromCsb(csbFile):
        print line

Lee un archivo *CSB* e imprime el equivalente en un archivo de formato tabular o de diccionario

    :::python

    # OFX
    from csb43 import csb_43, formats

    csbFile = csb_43.File(open("movimientos.csb"), strict=False)

    # imprime formato 'yaml' a stdout
    o = format.convertFromCsb(csbFile, 'yaml')
    print o.yaml

    # escribe a archivo en formato 'xlsx'
    o = format.convertFromCsb(csbFile, 'xlsx')
    with open("movimientos.xlsx", "wb") as f:
        f.write(o.xlsx)
