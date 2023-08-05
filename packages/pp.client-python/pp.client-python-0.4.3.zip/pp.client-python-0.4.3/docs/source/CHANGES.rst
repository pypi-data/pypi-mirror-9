CHANGES
=======

0.4.2 (2015-02-02)
------------------
- support for /api/available-converters (requires pp.server>=0.6.1)

0.4.1 (2014-11-19)
------------------
- experimental support for Speedata Publisher

0.4.0 (2014-10-13)
------------------
- compatiblity with Python 3.3 and 3.4
- dropped Python 2.6 support

0.3.6 (24-01-2014)
------------------
- added option '-c' to most commandline script in order
  for explicit SSL cert validation 

0.3.5 (24-01-2014)
------------------
- disabled SSL cert validation since Python/requests module
  can not deal properly with the StartCOM SSL cert of
  https://pp-server.zopyx.com

0.3.4 (21-01-2014)
------------------
- updated unoconv API documentation

0.3.3 (13-01-2014)
------------------
- support for server side token-based authorization

0.3.2 (13-01-2014)
------------------
- import fix

0.3.1 (21-10-2013)
------------------
- fixed an open file issue on Windows
  https://bitbucket.org/ajung/pp.client-python/issue/1/

0.3.0 (17-10-2013)
------------------
- Python 3.3 compatibility

0.2.9 (06-10-2013)
------------------
- added API methods for ``version`` and ``converters`` API
  of pp.server webservice

0.2.8 (05-10-2013)
------------------
- added support for ``cmd_options`` parameter
  for pp.server==0.3.5

0.2.7 (03-10-2013)
------------------
- documentation update

0.2.6 (14-07-2013)
------------------
- better error handling
- fixed issues with format() calls under Python 2.6

0.2.0 (06-07-2013)
------------------
- minor fixes
- moved documentation to Sphinx

0.1.5 (04-07-2013)
------------------
- implemented poll support
- fixes

0.1.4 (04-07-2013)
------------------
- added async support to pp-pdf commandline frontend

0.1.3 (03-07-2013)
------------------
- pdf converter parameter not properly propagated

0.1.2 (03-07-2013)
------------------
- logger fixes/changes

0.1.0 (03-07-2013)
------------------

- initial release
