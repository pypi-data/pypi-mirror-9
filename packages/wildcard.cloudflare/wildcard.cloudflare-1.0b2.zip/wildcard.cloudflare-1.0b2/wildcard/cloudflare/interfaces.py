from zope.interface import Interface
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


HTTP = u'http'
HTTPS = u'https'
BOTH = u'both'


class ICloudflareSettings(Interface):

    apiKey = schema.TextLine(
        title=u'API Key',
        description=u'Setting an API Key here and enabling cache purging '
                    u'activates purging against Cloudflare.',
        required=False
    )

    email = schema.TextLine(
        title=u'Email',
        description=u'One associated with cloudflare api key',
        required=False
    )

    domains = schema.Tuple(
        title=u'Domains',
        description=u'List of domains to purge for. Example: www.foobar.com',
        value_type=schema.TextLine(),
        default=(),
        required=False
    )

    scheme = schema.Choice(
        title=u'Scheme',
        description=u'What url schemes to purge on cloudflare cache',
        vocabulary=SimpleVocabulary([
            SimpleTerm(value=BOTH, token=BOTH, title='HTTP and HTTPS schemes'),
            SimpleTerm(value=HTTP, token=HTTP, title='HTTP only'),
            SimpleTerm(value=HTTPS, token=HTTPS, title='HTTPS only')
        ]),
        default=BOTH
    )
