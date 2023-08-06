from Products.CMFCore import permissions


PROJECTNAME = 'wildcard.pfg.stripe'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'FormStripeField': permissions.AddPortalContent,
}
