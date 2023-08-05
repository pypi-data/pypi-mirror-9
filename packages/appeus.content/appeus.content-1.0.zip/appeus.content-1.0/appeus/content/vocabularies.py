from plone import api
from five import grok
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from appeus.content import MessageFactory as _


class WhoVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        terms.append(SimpleVocabulary.createTerm('haur', 'haur', _('Haur')))
        terms.append(SimpleVocabulary.createTerm('nagusi', 'nagusi', _('Nagusi')))

        return SimpleVocabulary(terms)

grok.global_utility(WhoVocabulary, name=u"appeus.content.who")


class PriceVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        terms.append(SimpleVocabulary.createTerm('free', 'free', _('Free')))
        terms.append(SimpleVocabulary.createTerm('nonfree', 'nonfree', _('Non free')))

        return SimpleVocabulary(terms)

grok.global_utility(PriceVocabulary, name=u"appeus.content.price")


class LanguageVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        terms.append(SimpleVocabulary.createTerm('eu', 'eu', _('Only basque')))
        terms.append(SimpleVocabulary.createTerm('multilingual', 'multilingual', _('Multilingual')))

        return SimpleVocabulary(terms)

grok.global_utility(LanguageVocabulary, name=u"appeus.content.language")


class DevicesVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        terms.append(SimpleVocabulary.createTerm('phone', 'phone', _('Phone')))
        terms.append(SimpleVocabulary.createTerm('tablet', 'tablet', _('Tablet')))

        return SimpleVocabulary(terms)

grok.global_utility(DevicesVocabulary, name=u"appeus.content.devices")


class AppVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        catalog = api.portal.get_tool('portal_catalog')
        apps = catalog(portal_type='App')
        for app in apps:
            term = SimpleVocabulary.createTerm(app.UID, app.UID, app.Title)
            terms.append(term)

        terms.sort(lambda x, y: cmp(x.title.lower(), y.title.lower()))

        return SimpleVocabulary(terms)

grok.global_utility(AppVocabulary, name=u"appeus.content.apps")
