################################################################
# pp.client - Produce & Publish Python Client
# (C) 2013, ZOPYX Ltd, Tuebingen, Germany
################################################################

from __future__ import print_function

import plac
import base64
import json
import time
import requests
from pp.client.python.logger import getLogger

@plac.annotations(
    server_url=('URL of Produce & Publish API)', 'option', 's'),
)
def converter_versions(server_url='http://localhost:6543'):
    if server_url.endswith('/'):
        server_url = server_url[:-1]
    return requests.get(server_url + '/api/converter-versions', verify=False)


def main():
    print(plac.call(converter_versions))

if __name__ == '__main__':
    main()
