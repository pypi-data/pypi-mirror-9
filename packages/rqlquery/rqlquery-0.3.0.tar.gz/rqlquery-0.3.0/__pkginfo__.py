# pylint: disable=W0622
"""cubicweb-query application packaging information"""

modname = 'rqlquery'
distname = 'rqlquery'

numversion = (0, 3, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'UNLISH S.A.S (Montpellier, FRANCE)'
author_email = 'christophe@unlish.com'
short_desc = 'Experimental ORM Query object'
long_desc = None
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {'cubicweb': '>= 3.17.11', 'iso8601': None}
__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    ]
