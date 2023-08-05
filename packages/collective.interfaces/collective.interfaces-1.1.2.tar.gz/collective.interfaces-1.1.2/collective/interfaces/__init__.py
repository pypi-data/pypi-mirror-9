from plone.theme.interfaces import IDefaultPloneLayer
from zope.i18nmessageid import MessageFactory

_ = MessageFactory("collective.interfaces")

class IInterfacesSpecific(IDefaultPloneLayer):
    """ A marker interface that defines a Zope 3 browser layer. """