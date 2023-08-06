## Script (Python) "compute_participants"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=item=None
##title=Find out if the object is expired
##

if item is None:
    return 0

value = item.getNumParticipants
if not value:
    specimenSet = item.getObject()
    return specimenSet.getNumParticipants()
return value
