from Acquisition import aq_base
from Products.Five import BrowserView
from Products.CMFPlone.InterfaceTool import getDottedName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.utilities.interfaces import IMarkerInterfaces
from Products.CMFCore.utils import getToolByName

from zope.interface import (providedBy, directlyProvidedBy, alsoProvides,
                            noLongerProvides)
from zope.component.interface import getInterface

from collective.interfaces import _

def formatInfo(ifaces):
    result = []
    for iface in ifaces:
        name = getDottedName(iface)
        info = {'name': name,
                'doc': iface.getDoc()
        }
        result.append((name.lower(), info))

    result.sort()
    return [x[1] for x in result]
    
class InterfacesView(BrowserView):
    """ xxx """
    
    _template = ViewPageTemplateFile('interfaces.pt')
    
    def __call__(self):
        plone_utils = getToolByName(self.context, 'plone_utils')
        
        if self.request.has_key('collective.interfaces.add'):
            add = self.request.get('add')
            if add:
                iface = getInterface(self.context, add)
                alsoProvides(self.context, iface)
                self.context.reindexObject(idxs=["object_provides"])
                plone_utils.addPortalMessage(_("interface_added_msg",
                                                default='Interface ${name} added.',
                                                mapping={'name':add}))
            else:
                plone_utils.addPortalMessage(_('Please select an interface.'))
        
        elif self.request.has_key('collective.interfaces.remove'):
            ifaces = self.request.get('ifaces')
            if ifaces:
                for iface in ifaces:
                    noLongerProvides(self.context, getInterface(self.context, iface))
            
                self.context.reindexObject(idxs=["object_provides"])
                plone_utils.addPortalMessage(_("interfaces_removed_msg",
                                                default='${count} interface(s) removed.',
                                                mapping={'count':len(ifaces)}))
            else:
                plone_utils.addPortalMessage(_('Please select an interface.'))

        return self._template()

    def availableInterfaces(self):
        items = [(x.lower(), x) for x \
            in IMarkerInterfaces(self.context).getAvailableInterfaceNames()]
        items.sort()
        return [x[1] for x in items]

    def directlyProvidedBy(self):
        return formatInfo(directlyProvidedBy(aq_base(self.context)))
    
    def providedBy(self):
        return formatInfo(providedBy(aq_base(self.context)))
    
