# coding:utf-8

"""
    Dynamic SITE ID
    ~~~~~~~~~~~~~~~
    
    Set the SITE_ID dynamic by the current Domain Name.
    
    More info: read .../django_tools/dynamic_site/README.creole
    
    :copyleft: 2011-2015 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function



import os
import sys
import warnings

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

from django.conf import settings
from django.contrib.sites import models as sites_models
from django.core.exceptions import MiddlewareNotUsed, ImproperlyConfigured
from django.utils import log

from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache


USE_DYNAMIC_SITE_MIDDLEWARE = getattr(settings, "USE_DYNAMIC_SITE_MIDDLEWARE", False)

logger = log.getLogger("django_tools.DynamicSite")


Site = sites_models.Site  # Shortcut


class DynamicSiteId(object):
    def __getattribute__(self, name):
#        print "DynamicSiteId __getattribute__", name
        return getattr(SITE_THREAD_LOCAL.SITE_ID, name)
    def __int__(self):
#        print "DynamicSiteId __int__"
        return SITE_THREAD_LOCAL.SITE_ID
    def __hash__(self):
#        print "DynamicSiteId __hash__"
        return hash(SITE_THREAD_LOCAL.SITE_ID)
    def __repr__(self):
#        print "DynamicSiteId __repr__"
        return repr(SITE_THREAD_LOCAL.SITE_ID)
    def __str__(self):
#        print "DynamicSiteId __str__"
        return str(SITE_THREAD_LOCAL.SITE_ID)
    def __unicode__(self):
#        print "DynamicSiteId __unicode__"
        return str(SITE_THREAD_LOCAL.SITE_ID)


def _clear_cache(self):
    logger.debug("Clear SITE_CACHE (The django-tools LocalSyncCache() dict)")
    SITE_CACHE.clear()


if USE_DYNAMIC_SITE_MIDDLEWARE == True:
    # Use the same SITE_CACHE for getting site object by host [1] and get current site by SITE_ID [2]
    # [1] here in DynamicSiteMiddleware._get_site_id_from_host()
    # [2] in django.contrib.sites.models.SiteManager.get_current()
    SITE_CACHE = LocalSyncCache(id="DynamicSiteMiddlewareCache")
    sites_models.SITE_CACHE = SITE_CACHE

    SITE_THREAD_LOCAL = local()

    # Use Fallback ID if host not exist in Site table. We use int() here, because
    # os environment variables are always strings.
    FALLBACK_SITE_ID = int(getattr(os.environ, "SITE_ID", settings.SITE_ID))
    logger.debug("Fallback SITE_ID: %r" % FALLBACK_SITE_ID)

    # Use Fallback ID at startup before process_request(), e.g. in unittests
    SITE_THREAD_LOCAL.SITE_ID = FALLBACK_SITE_ID

    try:
        FALLBACK_SITE = Site.objects.get(id=FALLBACK_SITE_ID)
    except Site.DoesNotExist as e:
        all_sites = Site.objects.all()
        msg = "Fallback SITE_ID %i doesn't exist: %s (Existing sites: %s)" % (
            FALLBACK_SITE_ID, e, repr(all_sites.values_list("id", "domain").order_by('id'))
        )
        logger.critical(msg)
        raise ImproperlyConfigured(msg)
#        site = Site(id=FALLBACK_SITE_ID, domain="example.tld", name="Auto Created!")
#        site.save()

    settings.SITE_ID = DynamicSiteId()

    # Use the same cache for Site.objects.get_current():
    sites_models.SITE_CACHE = SITE_CACHE

    # monkey patch for django.contrib.sites.models.SiteManager.clear_cache
    sites_models.SiteManager.clear_cache = _clear_cache


class DynamicSiteMiddleware(object):
    """ Set settings.SITE_ID based on request's domain. """

    def __init__(self):
        # User must add "USE_DYNAMIC_SITE_MIDDLEWARE = True" in his local_settings.py
        # to activate this middleware
        if USE_DYNAMIC_SITE_MIDDLEWARE != True:
            logger.info("DynamicSiteMiddleware is deactivated.")
            raise MiddlewareNotUsed()
        else:
            logger.info("DynamicSiteMiddleware is active.")

    def process_request(self, request):
        # Get django.contrib.sites.models.Site instance by the current domain name:
        site = self._get_site_id_from_host(request)

        # Save the current site
        SITE_THREAD_LOCAL.SITE_ID = site.pk

        # Put site in cache for django.contrib.sites.models.SiteManager.get_current():
        SITE_CACHE[SITE_THREAD_LOCAL.SITE_ID] = site

#        def test():
#            from django.contrib.sites.models import Site, SITE_CACHE
#            from django.conf import settings
#            print id(SITE_CACHE), SITE_CACHE
#            print "-"*79
#            for k, v in SITE_CACHE.items():
#                print k, type(k), id(k), hash(k), v
#            print "-"*79
#            print id(settings.SITE_ID), settings.SITE_ID
#            print "TEST:", Site.objects.get_current()
#        test()

    def _get_site_id_from_host(self, request):
        host = request.get_host().lower()
        try:
            return SITE_CACHE[host]
        except KeyError:
            site = self._get_site_from_host(host)
            if site is None:
                # Fallback:
                logger.critical("Use FALLBACK_SITE !")
                site = FALLBACK_SITE
            else:
                logger.debug("Set site to %r for %r" % (site, host))
                SITE_CACHE[host] = site
            return site

    def _get_site_from_host(self, host):
        site = None
        try:
            site = Site.objects.get(domain__iexact=host)
        except Site.DoesNotExist:
            # Look if there is a alias
            from django_tools.dynamic_site.models import SiteAlias # against import loops ;(
            try:
                site = SiteAlias.objects.get_from_host(host)
            except SiteAlias.DoesNotExist:
                # FIXME: How can we give better feedback?
                all_sites = Site.objects.all()
                msg = "Error: There exist no SITE entry for domain %r! (Existing domains: %s)" % (
                    host, repr(all_sites.values_list("id", "domain").order_by('id'))
                )
                logger.critical(msg)
#                if settings.DEBUG:
#                    raise RuntimeError(msg)
#                else:
                warnings.warn(msg)
        return site

