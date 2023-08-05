# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EKE Publications: initialization.
'''

from zope.i18nmessageid import MessageFactory
from eke.publications import config
from Products.Archetypes import atapi
import Products.CMFCore

PACKAGE_NAME          = __name__
PROFILE_ID            = 'profile-' + PACKAGE_NAME + ':default'
ENTREZ_TOOL           = 'edrn-portal'
ENTREZ_EMAIL          = 'sean.kelly@nih.gov'
ProjectMessageFactory = MessageFactory(PACKAGE_NAME)

def initialize(context):
    '''Initializer called when used as a Zope 2 product.'''
    from content import publicationfolder, publication
    contentTypes, constructors, ftis = atapi.process_types(atapi.listTypes(config.PROJECTNAME), config.PROJECTNAME)
    for atype, constructor in zip(contentTypes, constructors):
        Products.CMFCore.utils.ContentInit(
            '%s: %s' % (config.PROJECTNAME, atype.portal_type),
            content_types=(atype,),
            permission=config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors=(constructor,)
        ).initialize(context)
    
