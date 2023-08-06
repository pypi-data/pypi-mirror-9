from Products.CMFCore.utils import getToolByName

PRODUCT_DEPENDENCIES = (
    'PloneFormGen',
)

EXTENSION_PROFILES = (
    'wildcard.pfg.stripe:default',
)

UNINSTALL_PROFILES = (
    'wildcard.pfg.stripe:uninstall',
)


def uninstall(self):
    portal_setup = getToolByName(self, 'portal_setup')
    for extension_id in UNINSTALL_PROFILES:
        portal_setup.runAllImportStepsFromProfile(
            'profile-%s' % extension_id, purge_old=False)
