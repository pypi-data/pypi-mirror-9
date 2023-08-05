from Acquisition import aq_inner
from five import grok
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot


class FeedUpdate(grok.View):
    grok.context(IPloneSiteRoot)
    grok.name('update-bise-feeds')
    grok.require('zope2.View')

    def render(self):
        self.update_feeds()
        return 1

    def update_feeds(self):
        with api.env.adopt_roles('Manager'):
            from logging import getLogger
            logger = getLogger('Auto Feed Update')
            logger.info("Beginning feed update process")

            updated = 0
            errors = 0
            context = aq_inner(self.context)

            brains = context.portal_catalog(portal_type="FeedfeederFolder")

            logger.info("Found %d feed folders" % len(list(brains)))

            for brain in brains:
                folder = brain.getObject()
                logger.debug("Updating folder:" + str(folder))
                update_view = folder.unrestrictedTraverse("@@update_feed_items")
                try:
                    update_view.update()
                    updated += 1
                except Exception, e:
                    # Don't allow a single bad feed to crash us.
                    logger.error("Feed raised exception:" + str(folder))
                    logger.exception(e)
                    errors += 1

            msg = "Updated %d feed folders, %d errors" % (updated, errors)
            logger.info(msg)
