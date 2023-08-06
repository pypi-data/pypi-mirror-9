# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''ERNE Specimen system: content implementation.'''

from eke.specimens.config import PROJECTNAME
from eke.specimens.interfaces import IERNESpecimenSystem
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from specimensystem import SpecimenSystemSchema, SpecimenSystem
from zope.interface import implements

ERNESpecimenSystemSchema = SpecimenSystemSchema.copy() + atapi.Schema((
    # No other fields needed
))

finalizeATCTSchema(ERNESpecimenSystemSchema, folderish=True, moveDiscussion=True)

class ERNESpecimenSystem(SpecimenSystem):
    '''ERNE Specimen system which contains sets of ERNE specimens.'''
    implements(IERNESpecimenSystem)
    portal_type       = 'ERNE Specimen System'
    schema            = ERNESpecimenSystemSchema

atapi.registerType(ERNESpecimenSystem, PROJECTNAME)
