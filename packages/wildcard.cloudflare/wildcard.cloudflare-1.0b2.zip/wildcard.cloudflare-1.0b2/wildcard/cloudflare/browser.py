from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from plone.app.registry.browser import controlpanel
from wildcard.cloudflare.interfaces import ICloudflareSettings
from zope.component import getMultiAdapter
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from wildcard.cloudflare import getUrlsToPurge, queuePurge
from plone.cachepurging.interfaces import IPurger


class CloudflareSettingsEditForm(controlpanel.RegistryEditForm):

    schema = ICloudflareSettings
    label = u"Cloudflare Settings"
    description = u""""""


class CloudflareSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    index = ViewPageTemplateFile('controlpanel_layout.pt')

    form = CloudflareSettingsEditForm


class FakeEvent(object):

    def __init__(self, object):
        self.object = object


class Purge(BrowserView):

    def purge(self, paths):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(ICloudflareSettings, check=False)
        key = settings.apiKey
        domains = settings.domains
        scheme = settings.scheme
        email = settings.email

        purger = queryUtility(IPurger)

        request_urls = []
        for path in paths:
            for url in getUrlsToPurge(path, key=key, email=email,
                                      domains=domains, scheme=scheme):
                purger.purgeAsync(url, 'GET')
                request_urls.append(url)
        return request_urls

    def __call__(self):
        authenticator = getMultiAdapter((self.context, self.request),
                                        name=u"authenticator")
        if authenticator.verify():
            self.paths = self.request.get('paths', '').splitlines()
            if self.paths:
                self.purged = self.purge(self.paths)
            else:
                self.purged = []
        return self.index()


class PurgePage(BrowserView):

    def __call__(self):
        queuePurge(FakeEvent(self.context))
        self.request.response.redirect(self.context.absolute_url() + '/view')
