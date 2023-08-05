from Acquisition import aq_inner
from five import grok
from Products.CMFPlone.interfaces import IPloneSiteRoot

import urllib2


class GetCreatorsFromNaaya(grok.View):
    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')

    def render(self):
        context = aq_inner(self.context)
        sock = urllib2.urlopen('http://biodiversity.europa.eu/AAAAAA-Owners')
        data = sock.read()
        from logging import getLogger
        log = getLogger(__name__)
        for item in eval(data):
            try:
                content = context.restrictedTraverse(item['path'][1:])
                content.setCreators(item['owner'])
                #changeOwnership(content, user, recursive=0)
                content.reindexObject()
                log.info('%s modified' % item['path'])
            except:
                log.info('ERROR: %s' % item['path'])

        return 1
