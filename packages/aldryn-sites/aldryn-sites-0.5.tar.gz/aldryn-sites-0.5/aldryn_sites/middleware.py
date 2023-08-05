# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from . import utils


class SiteMiddleware(object):
    """
    redirects any alias domains to the main domain.
    Takes into account if SECURE_SSL_REDIRECT (from django-secure) is set and redirects directly to the
    https version of the main domain if that is true.

    This middleware must be BEFORE djangosecure.middleware.SecurityMiddleware in MIDDLEWARE_CLASSES, so it can
    prevent the redirect from an alias domain to it's https version by djangosecure.middleware.SecurityMiddleware,
    because you might only cover the main domain with the certificate.
    """
    def __init__(self):
        self.domains = settings.ALDRYN_SITES_DOMAINS
        self.secure_redirect = getattr(settings, 'SECURE_SSL_REDIRECT', False)
        self.site_id = getattr(settings, 'SITE_ID', 1)
        utils.set_site_names()

    def process_request(self, request):
        if self.site_id not in self.domains.keys():
            return

        current_url = '{}://{}{}'.format(
            'https' if request.is_secure() else 'http',
            request.get_host(),
            request.get_full_path(),
        )
        site_config = self.domains[self.site_id]
        redirect_url = utils.get_redirect_url(current_url,
                                              config=site_config, https=self.secure_redirect)
        if redirect_url:
            return HttpResponsePermanentRedirect(redirect_url)
