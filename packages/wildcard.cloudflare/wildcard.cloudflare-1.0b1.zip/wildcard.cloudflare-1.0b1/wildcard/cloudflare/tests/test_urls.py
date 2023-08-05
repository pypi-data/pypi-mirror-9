import unittest
import zope.component.testing

from zope.interface import implements
from zope.interface import alsoProvides

from zope.component import provideUtility
from zope.component import provideAdapter
from zope.component import provideHandler

from zope.event import notify

from zope.annotation.attribute import AttributeAnnotations
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable

from plone.registry.interfaces import IRegistry
from plone.registry import Registry

from plone.registry.fieldfactory import persistentFieldAdapter

from plone.cachepurging.interfaces import IPurger
from plone.cachepurging.interfaces import ICachePurgingSettings

from ZPublisher.pubevents import PubSuccess
from wildcard.cloudflare.interfaces import (
    ICloudflareSettings)
from wildcard.cloudflare import purge


class FauxContext(dict):
    pass


class FauxRequest(dict):
    pass


class TestPurgeHandler(unittest.TestCase):

    def setUp(self):
        provideAdapter(AttributeAnnotations)
        provideAdapter(persistentFieldAdapter)
        provideHandler(purge)

        class FauxPurger(object):
            implements(IPurger)

            def __init__(self):
                self.purged = []

            def purgeAsync(self, url, httpVerb='PURGE'):
                self.purged.append(url)

        self.purger = FauxPurger()
        provideUtility(self.purger)

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_no_paths(self):
        request = FauxRequest()
        alsoProvides(request, IAttributeAnnotatable)

        IAnnotations(request)['plone.cachepurging.urls'] = set()

        registry = Registry()
        registry.registerInterface(ICachePurgingSettings)
        provideUtility(registry, IRegistry)

        settings = registry.forInterface(ICachePurgingSettings)
        settings.enabled = True
        settings.cachingProxies = ('http://localhost:1234',)

        notify(PubSuccess(request))

        self.assertEquals([], self.purger.purged)

    def test_no_registry(self):
        request = FauxRequest()
        alsoProvides(request, IAttributeAnnotatable)

        IAnnotations(request)['plone.cachepurging.urls'] = set(['/foo',
                                                                '/bar'])
        notify(PubSuccess(request))
        self.assertEquals([], self.purger.purged)

    def test_caching_disabled(self):
        request = FauxRequest()
        alsoProvides(request, IAttributeAnnotatable)

        IAnnotations(request)['plone.cachepurging.urls'] = set(['/foo',
                                                                '/bar'])

        registry = Registry()
        registry.registerInterface(ICachePurgingSettings)
        registry.registerInterface(ICloudflareSettings)
        provideUtility(registry, IRegistry)

        settings = registry.forInterface(ICachePurgingSettings)
        settings.enabled = False

        settings = registry.forInterface(ICloudflareSettings)
        settings.apiKey = u'foobar'
        settings.domains = (u'www.foobar.com',)
        notify(PubSuccess(request))

        self.assertEquals([], self.purger.purged)

    def test_purge(self):
        request = FauxRequest()
        alsoProvides(request, IAttributeAnnotatable)

        IAnnotations(request)['plone.cachepurging.urls'] = set(['/foo',
                                                                '/bar'])

        registry = Registry()
        registry.registerInterface(ICloudflareSettings)
        registry.registerInterface(ICachePurgingSettings)
        provideUtility(registry, IRegistry)

        settings = registry.forInterface(ICachePurgingSettings)
        settings.enabled = True

        settings = registry.forInterface(ICloudflareSettings)
        settings.apiKey = u'foobar'
        settings.domains = (u'www.foobar.com',)
        settings.email = u'foo@bar.com'

        notify(PubSuccess(request))

        self.assertEquals(len(self.purger.purged), 4)
        self.assertEquals(
            self.purger.purged[0],
            ('https://www.cloudflare.com/api_json.html?a=zone_file_purge&'
             'tkn=foobar&url=http%2Fwww.foobar.com%2F%2Ffoo&'
             'email=foo%40bar.com&z=www.foobar.com'))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
