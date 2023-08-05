#!/bin/bash

export PATH=\
/opt/buildout.python/bin:\
$PATH

virtualenv-2.7 .
bin/python setup.py develop
bin/pp-unoconv samples/doc1.docx -t 12345 -s https://pp-server.zopyx.com -v 
bin/pp-version -s https://pp-server.zopyx.com  
bin/pp-converters -s https://pp-server.zopyx.com 
