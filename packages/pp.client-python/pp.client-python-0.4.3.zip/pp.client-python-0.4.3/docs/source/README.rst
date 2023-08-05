pp.client-python
================

Produce & Publish bindings for Python.

The ``pp.client-python`` bindings can be used to communicate
with the Produce & Publish server ``pp.server`` for generating
PDF from Python applications or for making document conversions
using the ``unoconv`` (wrapper around LibreOffice or LibreOffice).

Requirements
------------

- Python 2.7
- Python 3.3
- Python 3.4

Source code
-----------

https://bitbucket.org/ajung/pp.client-python

Bug tracker
-----------

https://bitbucket.org/ajung/pp.client-python/issues

Documentation
-------------

https://pythonhosted.org/pp.client-python

API
---

pdf API 
+++++++

The ``pdf`` API supports the conversion of HTML/XML to PDF
through the following PDFconverters:

- PDFreactor 7+ (commercial)
- PrinceXML 9+ (commercial)
- Speedata Publisher (free)
- PhantomJS (free)

The PDF conversion process is based on the "CSS Paged Media" approach
where the input documents (XML or HTML) are styled using CSS only.

The ``pdf`` API of ``pp.client-python`` expects that the input
file and all related assets (images, stylesheets, font files etc.)
are placed within a working directory. The input file must be named 
``index.html``.

Using the commandline frontend::

    $ ../bin/pp-pdf  --help
    usage: pp-pdf [-h] [-f princexml] [-o] [-a] [-s http://localhost:6543]
                  [-t None] [-c] [-v]
                  source_directory [cmd_options]

    positional arguments:
      source_directory      Source directory containing content and assets to be
                            converted
      cmd_options           []

    optional arguments:
      -h, --help            show this help message and exit
      -f princexml, --converter princexml
                            PDF converter to be used (princexml, pdfreactor, publisher)
      -o , --output         Write result ZIP to given .zip filename
      -a, --async           Perform conversion asynchronously)
      -s http://localhost:6543, --server-url http://localhost:6543
                            URL of Produce & Publish server)
      -t None, --authorization-token None
                            Authorization token for P&P server
      -c, --ssl-cert-verification
                            Perform SSL cert validation
      -v, --verbose         Verbose mode


The same functionality is available to any Python application through the 
``pdf()`` API of the ``pp.client-python`` module::


    from pp.client.python.pdf import pdf

    def pdf(source_directory,
            converter='princexml', 
            output='',
            async=False, 
            cmd_options='',
            server_url='http://localhost:6543',
            authorization_token=None,
            ssl_cert_verification=False,
            verbose=False):

unoconv API
+++++++++++

The ``unoconv`` API provides a generic conversion API
for various formats (supported by the underlaying LibreOffice
background service)::

    The following list of document formats are currently available:

      bib      - BibTeX [.bib]
      doc      - Microsoft Word 97/2000/XP [.doc]
      doc6     - Microsoft Word 6.0 [.doc]
      doc95    - Microsoft Word 95 [.doc]
      docbook  - DocBook [.xml]
      docx     - Microsoft Office Open XML [.docx]
      docx7    - Microsoft Office Open XML [.docx]
      fodt     - OpenDocument Text (Flat XML) [.fodt]
      html     - HTML Document (OpenOffice.org Writer) [.html]
      latex    - LaTeX 2e [.ltx]
      mediawiki - MediaWiki [.txt]
      odt      - ODF Text Document [.odt]
      ooxml    - Microsoft Office Open XML [.xml]
      ott      - Open Document Text [.ott]
      pdb      - AportisDoc (Palm) [.pdb]
      pdf      - Portable Document Format [.pdf]
      psw      - Pocket Word [.psw]
      rtf      - Rich Text Format [.rtf]
      sdw      - StarWriter 5.0 [.sdw]
      sdw4     - StarWriter 4.0 [.sdw]
      sdw3     - StarWriter 3.0 [.sdw]
      stw      - Open Office.org 1.0 Text Document Template [.stw]
      sxw      - Open Office.org 1.0 Text Document [.sxw]
      text     - Text Encoded [.txt]
      txt      - Text [.txt]
      uot      - Unified Office Format text [.uot]
      vor      - StarWriter 5.0 Template [.vor]
      vor4     - StarWriter 4.0 Template [.vor]
      vor3     - StarWriter 3.0 Template [.vor]
      xhtml    - XHTML Document [.html]

    The following list of graphics formats are currently available:

      bmp      - Windows Bitmap [.bmp]
      emf      - Enhanced Metafile [.emf]
      eps      - Encapsulated PostScript [.eps]
      fodg     - OpenDocument Drawing (Flat XML) [.fodg]
      gif      - Graphics Interchange Format [.gif]
      html     - HTML Document (OpenOffice.org Draw) [.html]
      jpg      - Joint Photographic Experts Group [.jpg]
      met      - OS/2 Metafile [.met]
      odd      - OpenDocument Drawing [.odd]
      otg      - OpenDocument Drawing Template [.otg]
      pbm      - Portable Bitmap [.pbm]
      pct      - Mac Pict [.pct]
      pdf      - Portable Document Format [.pdf]
      pgm      - Portable Graymap [.pgm]
      png      - Portable Network Graphic [.png]
      ppm      - Portable Pixelmap [.ppm]
      ras      - Sun Raster Image [.ras]
      std      - OpenOffice.org 1.0 Drawing Template [.std]
      svg      - Scalable Vector Graphics [.svg]
      svm      - StarView Metafile [.svm]
      swf      - Macromedia Flash (SWF) [.swf]
      sxd      - OpenOffice.org 1.0 Drawing [.sxd]
      sxd3     - StarDraw 3.0 [.sxd]
      sxd5     - StarDraw 5.0 [.sxd]
      sxw      - StarOffice XML (Draw) [.sxw]
      tiff     - Tagged Image File Format [.tiff]
      vor      - StarDraw 5.0 Template [.vor]
      vor3     - StarDraw 3.0 Template [.vor]
      wmf      - Windows Metafile [.wmf]
      xhtml    - XHTML [.xhtml]
      xpm      - X PixMap [.xpm]

    The following list of presentation formats are currently available:

      bmp      - Windows Bitmap [.bmp]
      emf      - Enhanced Metafile [.emf]
      eps      - Encapsulated PostScript [.eps]
      fodp     - OpenDocument Presentation (Flat XML) [.fodp]
      gif      - Graphics Interchange Format [.gif]
      html     - HTML Document (OpenOffice.org Impress) [.html]
      jpg      - Joint Photographic Experts Group [.jpg]
      met      - OS/2 Metafile [.met]
      odg      - ODF Drawing (Impress) [.odg]
      odp      - ODF Presentation [.odp]
      otp      - ODF Presentation Template [.otp]
      pbm      - Portable Bitmap [.pbm]
      pct      - Mac Pict [.pct]
      pdf      - Portable Document Format [.pdf]
      pgm      - Portable Graymap [.pgm]
      png      - Portable Network Graphic [.png]
      potm     - Microsoft PowerPoint 2007/2010 XML Template [.potm]
      pot      - Microsoft PowerPoint 97/2000/XP Template [.pot]
      ppm      - Portable Pixelmap [.ppm]
      pptx     - Microsoft PowerPoint 2007/2010 XML [.pptx]
      pps      - Microsoft PowerPoint 97/2000/XP (Autoplay) [.pps]
      ppt      - Microsoft PowerPoint 97/2000/XP [.ppt]
      pwp      - PlaceWare [.pwp]
      ras      - Sun Raster Image [.ras]
      sda      - StarDraw 5.0 (OpenOffice.org Impress) [.sda]
      sdd      - StarImpress 5.0 [.sdd]
      sdd3     - StarDraw 3.0 (OpenOffice.org Impress) [.sdd]
      sdd4     - StarImpress 4.0 [.sdd]
      sxd      - OpenOffice.org 1.0 Drawing (OpenOffice.org Impress) [.sxd]
      sti      - OpenOffice.org 1.0 Presentation Template [.sti]
      svg      - Scalable Vector Graphics [.svg]
      svm      - StarView Metafile [.svm]
      swf      - Macromedia Flash (SWF) [.swf]
      sxi      - OpenOffice.org 1.0 Presentation [.sxi]
      tiff     - Tagged Image File Format [.tiff]
      uop      - Unified Office Format presentation [.uop]
      vor      - StarImpress 5.0 Template [.vor]
      vor3     - StarDraw 3.0 Template (OpenOffice.org Impress) [.vor]
      vor4     - StarImpress 4.0 Template [.vor]
      vor5     - StarDraw 5.0 Template (OpenOffice.org Impress) [.vor]
      wmf      - Windows Metafile [.wmf]
      xhtml    - XHTML [.xml]
      xpm      - X PixMap [.xpm]

    The following list of spreadsheet formats are currently available:

      csv      - Text CSV [.csv]
      dbf      - dBASE [.dbf]
      dif      - Data Interchange Format [.dif]
      fods     - OpenDocument Spreadsheet (Flat XML) [.fods]
      html     - HTML Document (OpenOffice.org Calc) [.html]
      ods      - ODF Spreadsheet [.ods]
      ooxml    - Microsoft Excel 2003 XML [.xml]
      ots      - ODF Spreadsheet Template [.ots]
      pdf      - Portable Document Format [.pdf]
      pxl      - Pocket Excel [.pxl]
      sdc      - StarCalc 5.0 [.sdc]
      sdc4     - StarCalc 4.0 [.sdc]
      sdc3     - StarCalc 3.0 [.sdc]
      slk      - SYLK [.slk]
      stc      - OpenOffice.org 1.0 Spreadsheet Template [.stc]
      sxc      - OpenOffice.org 1.0 Spreadsheet [.sxc]
      uos      - Unified Office Format spreadsheet [.uos]
      vor3     - StarCalc 3.0 Template [.vor]
      vor4     - StarCalc 4.0 Template [.vor]
      vor      - StarCalc 5.0 Template [.vor]
      xhtml    - XHTML [.xhtml]
      xls      - Microsoft Excel 97/2000/XP [.xls]
      xls5     - Microsoft Excel 5.0 [.xls]
      xls95    - Microsoft Excel 95 [.xls]
      xlt      - Microsoft Excel 97/2000/XP Template [.xlt]
      xlt5     - Microsoft Excel 5.0 Template [.xlt]
      xlt95    - Microsoft Excel 95 Template [.xlt]
      xlsx     - Microsoft Excel 2007/2010 XML [.xlsx]

Using the commandline frontend::

    $ bin/pp-unoconv --help
    usage: pp-unoconv [-h] [-f pdf] [-o] [-a] [-s http://localhost:6543] [-t None]
                      [-v]
                      input_filename

    positional arguments:
      input_filename        Source file to be converted

    optional arguments:
      -h, --help            show this help message and exit
      -f pdf, --format pdf  Output format (default=pdf)
      -o , --output         Write converted file to custom filename
      -s http://localhost:6543, --server-url http://localhost:6543
                            URL of Produce & Publish server)
      -t None, --authorization-token None
                            Authorization token for P&P server
      -v, --verbose         Verbose mode)

For example you can use the following commandline call for converting your 
``my.docx`` document to HTML. The conversion result will be returned always
as a ZIP file containing the converted data (in this case the ZIP file
will contain the converted HTML and extracted graphic files if applicable).
A dedicated ``token`` is necessary if you want to access the hosted conversion
service provided by ZOPYX Limited (contact us)::

    bin/pp-unoconv -f html -s https://pp-server.zopyx.com -v -o out.zip -t <token> my.docx

The same functionality is available to any Python application through the 
``unoconv()`` API of the ``pp.client-python`` module::


    from pp.client.python.unoconv import unoconv

    def unoconv(input_filename, 
               format='pdf', 
               output='',
               server_url=None,
               authorization_token=None,
               verbose=False):
                                                    

Support
-------

Support for Produce & Publish Server and components is currently only available
on a project basis.

License
-------
``pp.client-python`` is published under the GNU Public License V2 (GPL 2).

Contact
-------

| Andreas Jung/ZOPYX 
| Hundskapfklinge 33
| D-72074 Tuebingen, Germany
| info@zopyx.com
| www.zopyx.com
