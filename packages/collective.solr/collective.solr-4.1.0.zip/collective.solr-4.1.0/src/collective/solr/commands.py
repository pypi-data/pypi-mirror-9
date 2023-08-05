# -*- coding: utf-8 -*-
from collective.solr.interfaces import ISolrConnectionManager
from zope.component import queryUtility
from zope.site.hooks import setHooks
from zope.site.hooks import setSite

import logging
import sys

logger = logging.getLogger()


def _get_site(app, args):
    name = None
    if len(args) > 0:
        name = args[0]
        if name not in app:
            logger.error("Specified site '%s' not found in database." % name)
            sys.exit(1)
    else:
        from Products.CMFPlone.Portal import PloneSite
        for k, v in app.items():
            if isinstance(v, PloneSite):
                name = k
                break
    if not name:
        logger.error("No Plone site found in database root.")
        sys.exit(1)
    site = getattr(app, name)
    setHooks()
    setSite(site)
    return site


def _solr_connection():
    manager = queryUtility(ISolrConnectionManager)
    conn = manager.getConnection()
    logger.info('Opened Solr connection to %s' % conn.host)
    return conn


def solr_clear_index(app, args):
    """Removes all data from a Solr index. Equivalent to removing the
    `data/index` directory while Solr is stopped. You can optionally specify
    the id of the Plone site as the first command line argument.
    """
    _get_site(app, args)  # calls setSite so queryUtility works
    conn = _solr_connection()
    conn.deleteByQuery('[* TO *]')
    conn.commit(optimize=True)
    conn.close()
