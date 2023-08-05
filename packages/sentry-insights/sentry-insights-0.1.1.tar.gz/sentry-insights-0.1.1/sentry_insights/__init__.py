"""
sentry_insights
~~~~~~~~~~~~~~

:copyright: (c) 2011 by Linovia, see AUTHORS for more details.
:copyright: (c) 2014 by tinyclues, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('sentry_insights').version
except Exception, e:
    VERSION = 'unknown'
