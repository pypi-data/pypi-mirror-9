from appeus.content.app import IApp
from plone.indexer import indexer


@indexer(IApp)
def ios_availability(obj):
    return str(bool(obj.ios_availability))

@indexer(IApp)
def android_availability(obj):
    return str(bool(obj.android_availability))