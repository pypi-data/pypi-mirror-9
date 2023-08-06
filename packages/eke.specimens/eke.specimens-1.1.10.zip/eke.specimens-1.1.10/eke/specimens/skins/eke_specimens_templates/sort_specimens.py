## Script (Python) "sort_specimens"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=folderContents=None
##title=Find out if the object is expired
##

# This entire crappy hack is all for CA-926's #3 item.  Fsck'n P.O.S. requirement.

if folderContents is None:
    folderContents = []
else:
    folderContents = list(folderContents)

stupidLungOrdering = (
    'LUNG REF Set A Rapid Set',
    'LUNG REF Set A Panel Pre-validation',
    'LUNG REF Set A Phase II Validation',
)

def safeIndex(l, i):
    try:
        return l.index(i)
    except ValueError:
        return None

def specialOrdering(a, b):
    a, b = a.Title, b.Title
    if a.startswith('LUNG REF Set A') and b.startswith('LUNG REF Set A'):
        alpha, beta = safeIndex(stupidLungOrdering, a), safeIndex(stupidLungOrdering, b)
        if alpha is not None and beta is not None:
            return cmp(alpha, beta)
    return cmp(a, b)

folderContents.sort(specialOrdering)
return folderContents
