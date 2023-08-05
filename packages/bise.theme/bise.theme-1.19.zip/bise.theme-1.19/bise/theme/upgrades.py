from logging import getLogger
from Products.CMFCore.utils import getToolByName

PROFILE_ID = 'profile-bise.theme:default'


def ploneglossary_1001(context, logger=None):
    if logger is None:
        logger = getLogger('ploneglossary_1001')

    js_registry = getToolByName(context, 'portal_javascripts')
    resource = js_registry.getResource('ploneglossary_definitions.js')
    resource.setInline(False)
    logger.info('Upgraded')


def reload_css_1001(context, logger=None):
    if logger is None:
        logger = getLogger('reload_css_1001')

    default_profile = 'profile-bise.biodiversityfactsheet:default'
    context.runImportStepFromProfile(default_profile, 'jsregistry')
    logger.info('Upgraded')


def upgrade_to_1002(context, logger=None):
    if logger is None:
        logger = getLogger('reload_css_1002')

    setup = getToolByName(context, 'portal_setup')

    setup.runAllImportStepsFromProfile('profile-plone.app.versioningbehavior:default')
    setup.runAllImportStepsFromProfile('profile-plone.app.iterate:plone.app.iterate')

    setup.runImportStepFromProfile(PROFILE_ID, 'typeinfo')
    setup.runImportStepFromProfile(PROFILE_ID, 'repositorytool')
    setup.runImportStepFromProfile(PROFILE_ID, 'plone-difftool')
    logger.info('Upgrade steps executed')


def upgrade_to_1003(context, logger=None):
    if logger is None:
        logger = getLogger('upgrade_to_1003')

    setup = getToolByName(context, 'portal_setup')
    wtool = getToolByName(context, 'portal_workflow')
    wtool.manage_delObjects([
        'simple_publication_workflow',
        ])
    setup.runImportStepFromProfile(PROFILE_ID, 'actions')
    setup.runImportStepFromProfile(PROFILE_ID, 'workflow')
    wtool.updateRoleMappings()
    logger.info('Upgrade steps executed')


def upgrade_to_1004(context, logger=None):
    if logger is None:
        logger = getLogger('upgrade_to_1004')

    setup = getToolByName(context, 'portal_setup')

    wtool = getToolByName(context, 'portal_workflow')
    wtool.manage_delObjects([
        'simple_publication_workflow',
        ])
    setup.runImportStepFromProfile(PROFILE_ID, 'propertiestool')
    setup.runImportStepFromProfile(PROFILE_ID, 'actions')
    setup.runImportStepFromProfile(PROFILE_ID, 'placeful_workflow')
    setup.runImportStepFromProfile(PROFILE_ID, 'workflow')
    wtool.updateRoleMappings()
    logger.info('Upgrade steps executed')


def upgrade_to_1005(context, logger=None):
    if logger is None:
        logger = getLogger('upgrade_to_1005')

    js_registry = getToolByName(context, 'portal_javascripts')
    resource = js_registry.getResource('jquery.bugme.js')
    resource.setEnabled(False)
    logger.info('Upgraded')


def upgrade_to_1006(context, logger=None):
    if logger is None:
        logger = getLogger('upgrade_to_1006')

    js_registry = getToolByName(context, 'portal_javascripts')
    resource = js_registry.getResource('jquery.bugme.js')
    resource.setEnabled(True)
    logger.info('Upgraded')


def upgrade_to_1007(context, logger=None):
    if logger is None:
        logger = getLogger('upgrade_to_1007')

    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'typeinfo')
    logger.info('Upgraded')
