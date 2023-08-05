from appeus.content import MessageFactory as _
from bs4 import BeautifulSoup
from five import grok
from plone.app.dexterity import PloneMessageFactory as _PMF
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.file import NamedBlobImage as NamedBlobImage_file
from plone.namedfile.interfaces import IImageScaleTraversable
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema

import urllib2
import requests

# Interface class; used to define content-type schema.
class IApp(form.Schema, IImageScaleTraversable):
    """
    App content-type
    """

    author = schema.TextLine(
        title=_(u"Author"),
        required=False,
    )

    form.widget(who=CheckBoxFieldWidget)
    who = schema.List(
        title=_(u"Who"),
        value_type=schema.Choice(
            vocabulary='appeus.content.who',
            required=True,
        ),
        required=True,
        default=['haur', 'nagusi'],
    )

    form.widget(devices=CheckBoxFieldWidget)
    devices = schema.List(
        title=_(u"Devices"),
        value_type=schema.Choice(
            vocabulary='appeus.content.devices',
            required=True,
        ),
        required=True,
        default=['phone', 'tablet'],
    )

    android_availability = schema.Bool(
        title=_(u"Android availability"),
        required=False,
        default=False,
    )

    android_googleplay_url = schema.TextLine(
        title=_(u"URL for Google Play"),
        required=False,
    )

    android_version_number = schema.TextLine(
        title=_(u"App version number for Android"),
        required=False,
    )

    android_min_version = schema.TextLine(
        title=_(u"Min version for Android"),
        required=False,
    )

    android_price = schema.TextLine(
        title=_(u"Price for Android version"),
        required=False,
    )

    ios_availability = schema.Bool(
        title=_(u"IOS availability"),
        required=False,
        default=False,
    )

    ios_itunes_url = schema.TextLine(
        title=_(u"URL for Apple Store"),
        required=False,
    )

    ios_version_number = schema.TextLine(
        title=_(u"App version number for IOS"),
        required=False,
    )

    ios_min_version = schema.TextLine(
        title=_(u"Min version for IOS"),
        required=False,
    )

    ios_price = schema.TextLine(
        title=_(u"Price for IOS version"),
        required=False,
    )

    language = schema.Choice(
        title=_(u"Language"),
        vocabulary='appeus.content.language',
        required=True,
    )

    price = schema.Choice(
        title=_(u"Price"),
        vocabulary='appeus.content.price',
        required=True,
    )

    image = NamedBlobImage(
        title=_(u"Please upload an image"),
        required=False,
    )

    subjects = schema.Tuple(
        title=_PMF(u'label_tags', default=u'Tags'),
        description=_PMF(
            u'help_tags',
            default=u'Tags are commonly used for ad-hoc organization of ' +
                    u'content.'
        ),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
    )


class App(dexterity.Container):
    grok.implements(IApp)
    # Add your class methods and properties here

    def Subject(self):
        return self.subjects

grok.templatedir('templates')


# class AddForm(dexterity.AddForm):
#     grok.name('appeus.content.app')
#     grok.context(IApp)
#     grok.require('appeus.content.AddApp')


# class EditForm(dexterity.EditForm):
#     grok.context(IApp)
#     grok.name('edit')
#     grok.require('cmf.ModifyPortalContent')


class AppView(grok.View):
    grok.context(IApp)
    grok.require('zope2.View')
    grok.name('view')


class GooglePlayImport(grok.View):
    grok.context(IApp)
    grok.require('cmf.ModifyPortalContent')
    grok.name('googleplayimport')

    def render(self):
        sock = requests.get(self.context.android_googleplay_url)
        soup = BeautifulSoup(sock.text)
        title = soup.find('div', {'class': 'document-title'}).text.strip()
        desc = soup.find('div', {'class': 'id-app-orig-desc'}).text.strip()
        author = soup.find('div', itemprop='author').find('a').text.strip()
        version = soup.find('div', itemprop='softwareVersion').text.strip()
        osversion = soup.find('div', itemprop='operatingSystems').text.strip()
        images = soup.find_all('img', {'class': 'screenshot'})
        price = soup.find(itemprop='price')
        if price:
            self.context.android_price = price.get('content')

        if self.context.title:
            self.context.title = self.context.title + ' ' + title
        else:
            self.context.title = title

        if self.context.description:
            self.context.description = self.context.description + ' ' + desc
        else:
            self.context.description = desc

        if self.context.author:
            self.context.author = self.context.author + ' ' + author
        else:
            self.context.author = author

        self.context.android_version_number = version
        self.context.android_min_version = osversion
        for image in images:
            imageurl = image.get('src')
            filename = unicode(imageurl.split('/')[-1], 'utf-8')
            sock = urllib2.urlopen(imageurl)
            imgdata = sock.read()
            try:
                imgobject = imgdata
                self.context.image = NamedBlobImage_file(imgobject,
                    contentType=sock.headers['content-type'],
                    filename=filename)
                break
            except:
                pass
            sock.close()

        messages = IStatusMessage(self.request)
        messages.add(_(u"Information imported from Google Play"), type=u"info")
        return self.request.response.redirect(self.context.absolute_url())


class ItunesImport(grok.View):
    grok.context(IApp)
    grok.require('cmf.ModifyPortalContent')
    grok.name('itunesimport')

    def render(self):
        sock = requests.get(self.context.ios_itunes_url)
        soup = BeautifulSoup(sock.text)
        title = soup.find('h1').text.strip()
        desc = soup.find('div', {'class': 'product-review'}).text.strip()
        author = soup.find('h2').text.strip()
        try:
            version = soup.find('ul', {'class': 'list'}).find_all('li')[3].text.strip()
            self.context.ios_version_number = version
        except:
            pass
        osversion = soup.find('div', {'id': 'left-stack'}).find('p').text.strip()
        images = soup.find('div', {'class': 'screenshots'}).find_all('img')

        if self.context.title:
            self.context.title = self.context.title + ' ' + title
        else:
            self.context.title = title

        if self.context.description:
            self.context.description = self.context.description + ' ' + desc
        else:
            self.context.description = desc

        if self.context.author:
            self.context.author = self.context.author + ' ' + author
        else:
            self.context.author = author


        self.context.ios_min_version = osversion
        for image in images:
            imageurl = image.get('src')
            filename = unicode(imageurl.split('/')[-1], 'utf-8')
            sock = urllib2.urlopen(imageurl)
            imgdata = sock.read()
            try:
                imgobject = imgdata
                self.context.image = NamedBlobImage_file(imgobject,
                    contentType=sock.headers['content-type'],
                    filename=filename)
                break
            except:
                pass
            sock.close()

        messages = IStatusMessage(self.request)
        messages.add(_(u"Information imported from Google Play"), type=u"info")
        return self.request.response.redirect(self.context.absolute_url())


        messages = IStatusMessage(self.request)
        messages.add(_(u"Information imported from Itunes"), type=u"info")
        return self.request.response.redirect(self.context.absolute_url())


class FacetedPreviewItemApp(grok.View):
    grok.context(IApp)
    grok.name('faceted-preview-item')
    grok.require('zope2.View')
