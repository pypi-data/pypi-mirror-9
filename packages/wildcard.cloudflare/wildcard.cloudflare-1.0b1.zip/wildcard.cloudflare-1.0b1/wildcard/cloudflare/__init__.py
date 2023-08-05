from urllib import urlencode

from zope.component import adapter, queryUtility
from zope.annotation.interfaces import IAnnotations

from plone.registry.interfaces import IRegistry

from plone.cachepurging.interfaces import IPurger
from plone.cachepurging.hooks import KEY
from plone.cachepurging.interfaces import ICachePurgingSettings
from plone.cachepurging.utils import getPathsToPurge

from z3c.caching.interfaces import IPurgeEvent
from zope.globalrequest import getRequest

from ZPublisher.interfaces import IPubSuccess

from wildcard.cloudflare.interfaces import (
    ICloudflareSettings,
    HTTP, HTTPS, BOTH)


cloudflare_endpoint = 'https://www.cloudflare.com/api_json.html'


def getUrlsToPurge(path, key=None, email='', domains=(), scheme=BOTH):
    if key is None:
        return []
    if scheme == BOTH:
        schemes = ('http', 'https')
    elif scheme == HTTP:
        schemes = ('http',)
    elif scheme == HTTPS:
        schemes = ('https',)

    urls = []
    params = {
        'a': 'zone_file_purge',
        'tkn': key,
        'email': email
    }
    for scheme in schemes:
        for domain in domains:
            params.update({
                'z': domain,
                'url': '%s://%s/%s' % (scheme, domain, path.lstrip('/'))
            })
            urls.append('%s?%s' % (cloudflare_endpoint, urlencode(params)))
    return urls


@adapter(IPurgeEvent)
def queuePurge(event):
    """ so this is a little wonky here...
    We need to also purge here because plone.cachepurging will only update
    paths if caching proxies are defined. The deal here is that with
    cloudflare, we do not want to define caching proxies or we may not be """

    request = getRequest()
    if request is None:
        return

    annotations = IAnnotations(request, None)
    if annotations is None:
        return

    registry = queryUtility(IRegistry)
    if registry is None:
        return

    settings = registry.forInterface(ICachePurgingSettings, check=False)
    if not settings.enabled:
        return

    # so we're enabled, BUT we also need to NOT have proxies defined
    # in order to register here
    if bool(settings.cachingProxies):
        return

    paths = annotations.setdefault(KEY, set())
    paths.update(getPathsToPurge(event.object, request))


@adapter(IPubSuccess)
def purge(event):
    """
    Asynchronously send PURGE requests.
    this is mostly copied from plone.cachingpurgin
    """
    request = event.request

    annotations = IAnnotations(request, None)
    if annotations is None:
        return

    paths = annotations.get(KEY, None)
    if paths is None:
        return

    registry = queryUtility(IRegistry)
    if registry is None:
        return

    settings = registry.forInterface(ICachePurgingSettings, check=False)
    if not settings.enabled:
        return

    settings = registry.forInterface(ICloudflareSettings, check=False)
    if not settings.apiKey:
        return

    purger = queryUtility(IPurger)
    if purger is None:
        return

    key = settings.apiKey
    domains = settings.domains
    scheme = settings.scheme
    email = settings.email

    for path in paths:
        for url in getUrlsToPurge(path, key=key, email=email, domains=domains,
                                  scheme=scheme):
            purger.purgeAsync(url, 'GET')
