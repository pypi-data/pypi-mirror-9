################################################################
# pp.client - Produce & Publish Python Client
# (C) 2013, ZOPYX Ltd, Tuebingen, Germany
################################################################

import os
import plac
import json
import time
import base64
try:
    from urllib2 import URLError
except ImportError:
    from urllib.error import URLError
import requests
import tempfile
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
import zipfile
from pp.client.python.logger import getLogger
from pp.client.python.poll import poll
from pp.client.python.util import mask_url


def makeZipFromDirectory(directory):
    """ Generate a ZIP file from a directory containing all its
        contents. Returns the filename of the generated ZIP file.
    """

    directory = os.path.abspath(directory)
    if not os.path.exists(directory):
        raise IOError('Directory {0:s} does not exist'.format(directory))
    zip_filename = tempfile.mktemp()
    ZF = zipfile.ZipFile(zip_filename, 'w')
    for dirname, dirnames, filenames in os.walk(directory):
        for fname in filenames:
            arcname = os.path.join(dirname, fname).replace(directory + os.path.sep, '')
            fullname = os.path.abspath(os.path.join(dirname, fname))
            ZF.write(fullname, arcname)
    ZF.close()
    return zip_filename

@plac.annotations(
    source_directory=('Source directory containing content and assets to be converted', 'positional'),
    converter=('PDF converter to be used (princexml, pdfreactor, publisher)', 'option', 'f'),
    output=('Write result ZIP to given .zip filename', 'option', 'o'),
    server_url=('URL of Produce & Publish server)', 'option', 's'),
    async=('Perform conversion asynchronously)', 'flag', 'a'),
    authorization_token=('Authorization token for P&P server', 'option', 't'),
    verbose=('Verbose mode', 'flag', 'v'),
    ssl_cert_verification=('Perform SSL cert validation', 'flag', 'c')
)
def pdf(source_directory,
        converter='princexml', 
        output='',
        async=False, 
        cmd_options='',
        server_url='http://localhost:6543',
        authorization_token=None,
        ssl_cert_verification=False,
        verbose=False):

    LOG = getLogger(debug=1 if verbose else 0)
    server_url = server_url.rstrip('/') + '/api/1/pdf'

    zip_filename = makeZipFromDirectory(source_directory)
    params = dict(converter=converter, async=int(async), cmd_options=cmd_options)
    with open(zip_filename, 'rb') as fp:
        files = {'file': fp}
        LOG.debug('Sending data to {0:s} ({1:s}, {2:d} bytes)'.format(mask_url(server_url), 
                                                             converter, 
                                                             os.path.getsize(zip_filename)))
        headers = dict()
        if authorization_token:
            headers['pp-token'] = authorization_token

        result = requests.post(server_url, 
                data=params, 
                files=files, 
                verify=ssl_cert_verification,
                headers=headers)
    if result.status_code != 200:
        raise URLError('Error calling {0:s} (Status: {1:d})'.format(mask_url(server_url), result.status_code))
    result = json.loads(result.text)
    os.unlink(zip_filename)

    if async:
        LOG.debug(result)
        return result
    else:        
        if result['status'] == 'OK':
            if not output:
                base, ext = os.path.splitext(zip_filename)
                if converter == 'calibre':
                    output= base + '.epub'
                else:
                    output= base + '.pdf'
            with open(output, 'wb') as fp:
                fp.write(base64.decodestring(result['data'].encode('ascii')))
            result['output_filename'] = output
            LOG.debug('Output filename: {0:s}'.format(output))
        else:
            LOG.debug('An error occured')
            LOG.debug('Output:')
            LOG.debug(result['output'])
        return result
    
def main():
    plac.call(pdf)

if __name__ == '__main__':
    main()
