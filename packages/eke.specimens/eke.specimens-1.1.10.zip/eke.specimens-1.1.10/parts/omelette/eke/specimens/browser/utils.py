# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from eke.site.interfaces import ISite
from Products.CMFCore.utils import getToolByName
from zope.interface import directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
import urllib, urllib2, logging

_logger = logging.getLogger(__name__)

_erneWS = 'http://ginger.fhcrc.org/edrn/erneQuery'

_units = {
    '1':  u'mcl',
    '2':  u'ml',
    '3':  u'mcg',
    '4':  u'mg',
    '8':  u'slides',
    '14': u'cells',
    '98': u'',
    '99': u'',
}

_genders = {
    '1': u'Male',
    '2': u'Female',
    '9': u'Refused',
}

_races = {
    '1':	u'White',
    '2':	u'Black/African-American',
    '3':	u'American Indian/Alaska Native',
    '4':	u'Asian',
    '7':	u'Native Hawaiian/Pacific Islander',
    '97':	u'Unspecified',
    '99':	u'Refused/Unknown',
}

_ethnicities = {
    '0':    u'N/A',
    '1':    u'Hispanic/latino',
    '9':    u'Unknown',
}

# Site identifier to ERNE identifier
SITES = {
    'http://edrn.nci.nih.gov/data/sites/167': 'https://telepath-d340.upmc.edu:7576/erne/prod',   # Pittsburgh
    'http://edrn.nci.nih.gov/data/sites/84':  'https://edrn.med.nyu.edu:7576/grid/prod',         # NYU
    'http://edrn.nci.nih.gov/data/sites/189': 'https://ucsf-97-101.ucsf.edu:7576/erne/prod',     # UCSF
    'http://edrn.nci.nih.gov/data/sites/202': 'https://erne.fccc.edu:7576/erne/prod',            # Fox Chase
    'http://edrn.nci.nih.gov/data/sites/203': 'https://profiler.med.cornell.edu:7576/erne/prod', # Beth Israel
    'http://edrn.nci.nih.gov/data/sites/408': 'https://erne.ucsd.edu:7576/erne/prod',            # UCSD
    'http://edrn.nci.nih.gov/data/sites/67':  'https://kepler.dartmouth.edu:7576/erne/prod',     # GLNE Dartmouth
    'http://edrn.nci.nih.gov/data/sites/70':  'https://edrn.partners.org:7576/erne/prod',        # Brigham & Women's
    'http://edrn.nci.nih.gov/data/sites/73':  'https://supergrover.uchsc.edu:7576/erne/prod',    # Colorado
    'http://edrn.nci.nih.gov/data/sites/80':  'https://edrn.creighton.edu:7576/erne/prod',       # Creighton Univ
    'http://edrn.nci.nih.gov/data/sites/81':  'https://surg-oodt.mc.duke.edu:7576/erne/prod',    # Duke Univ
    'http://edrn.nci.nih.gov/data/sites/83':  'https://162.129.227.245:7576/erne/prod',          # Johns Hopkins Urology
    'http://edrn.nci.nih.gov/data/sites/91':  'https://cdc-erne.cdc.gov:7576/erne/prod',         # CDC
    'http://edrn.nci.nih.gov/data/sites/593': 'https://cerc-vm1.fhcrc.org:7576/grid/prod',       # CERC at FHCRC
}


class ERNESpecimenSummary(object):
    def __init__(
        self, storageType, specimenCount, numberCases, numberControls, organ, diagnosis, available, contactEmail,
        protocolID, collectionType
    ):
        self.storageType, self.specimenCount = storageType, specimenCount
        self.numberCases, self.numberControls, self.organ = numberCases, numberControls, organ
        self.diagnosis, self.available, self.contactEmail = diagnosis, available, contactEmail
        self.protocolID = protocolID
        self.collectionType = collectionType
    def __repr__(self):
        return ('%s(storageType=%r,specimenCount=%d,numberCases=%r,numberControls=%r,organ=%r,' +
            'diagnosis=%r,available=%r,contactEmail=%r,protocolID=%r,collectionType=%r)') % (
            self.__class__.__name__, self.storageType, self.specimenCount, self.numberCases, self.numberControls, self.organ,
            self.diagnosis, self.available, self.contactEmail, self.protocolID, self.collectionType
        )
    def __cmp__(self, other):
        for f in (
            'storageType','specimenCount','numberCases','numberControls','organ','diagnosis','available','contactEmail',
            'protocolID', 'collectionType'
        ):
            rc = cmp(getattr(self, f), getattr(other, f))
            if rc < 0:
                return -1
            elif rc > 0:
                return 1
        return 0
    def __hash__(self):
        return self.diagnosis << 31 ^ self.available << 30 ^ hash(self.storageType) << 17 ^ hash(self.specimenCount) << 15 ^ \
            hash(self.numberCases) << 8 ^ hash(self.organ) << 6 ^ hash(self.numberControls) << 3 ^ hash(self.contactEmail) ^ \
            hash(self.protocolID) << 1 ^ hash(self.collectionType) << 7

class SpecimenInventory(object):
    def __init__(self, contact, specimens, count, limit):
        self.contact, self.specimens, self.count, self.limit = contact, specimens, count, limit
        # Show specimen collected, storage, cancer diagnosis
        # Then break down # samples # participants by gender, race, smoking history
    def __repr__(self):
        return '%s(contact=%s,# specimens=%d)' % (self.__class__.__name__, self.contact, len(self.specimens))
    def __iter__(self):
        return iter(self.specimens)

class Quantity(object):
    def __init__(self, value, units):
        self.value, self.units = value, units
    def __unicode__(self):
        if self.value in ('unknown', '9999.0', 'blank'): return u'–'
        return u'%s %s' % (self.value, _units.get(self.units, u''))
    
class Specimen(object):
    def __init__(self, pptID, gender, race, ethnicity, icd9, ageAtCollection, ageAtDX, isAvailable, final, collected, remaining):
        self.pptID, self._gender, self._race, self._ethnicity = pptID, gender, race, ethnicity
        self.icd9, self._ageAtCollection, self._ageAtDX, self.isAvailable = icd9, ageAtCollection, ageAtDX, isAvailable
        self.final, self.collected, self.remaining = final, collected, remaining
    @property
    def gender(self):
        return _genders.get(self._gender, u'Unknown') # FIXME: Not i18n
    @property
    def race(self):
        return _races.get(self._race, u'Unknown') # FIXME: Not i18n
    @property
    def ethnicity(self):
        return _ethnicities.get(self._ethnicity, u'Unknown') # FIXME: Not i18n
    @property
    def ageAtCollection(self):
        return self._ageAtCollection in ('999', 'unknown', 'blank') and u'–' or self._ageAtCollection
    @property
    def ageAtDX(self):
        return self._ageAtDX in ('999' or 'unknown') and u'–' or self._ageAtDX
    def __repr__(self):
        return '%s(pptID=%s,gender=%s,race=%s,ethnicity=%s,...)' % (
            self.__class__.__name__, self.pptID, self.gender, self.race, self.ethnicity
        )

def getSpecimens(erneID, erneWS=_erneWS):
    cdes = (
        'BASELINE_CANCER-CONFIRMATION_CODE', 'SPECIMEN_STORED_CODE', 'STUDY_PARTICIPANT_ID',
        'SPECIMEN_CONTACT-EMAIL_TEXT', 'SPECIMEN_AVAILABLE_CODE', 'SPECIMEN_TISSUE_ORGAN-SITE_CODE', 'STUDY_PROTOCOL_ID',
        'SPECIMEN_COLLECTED_CODE'
    )
    numCDES = len(cdes)
    queryStr = ' AND '.join(['RETURN = %s' % cde for cde in cdes])
    params = {'q': queryStr, 'url': erneID}
    con = None
    records, available, email = [], None, None
    try:
        con = urllib2.urlopen(erneWS, urllib.urlencode(params))
        stats = {}
        for erneRecord in con.read().split('$'):
            fields = erneRecord.split('\t')
            if len(fields) != numCDES: continue # Avoid partial responses
            for i in xrange(0, numCDES):
                fields[i] = fields[i].strip()
            cancerDiag, storage, ppt, email, available, organ, protocolID, collection = fields
            available = available == '1'
            # Avoid garbled responses
            if not cancerDiag or cancerDiag in ('9', 'unknown', 'blank') or not storage or storage in ('unknown', 'blank') \
                or not ppt or ppt in ('unknown', 'blank') or not collection or collection in ('unknown', 'blank'):
                continue
            # Group by {diagnosis: {collection: {storage type: {organ: {participant ID: specimen count}}}}}
            diagnoses = stats.get(cancerDiag, {})
            collectionTypes = diagnoses.get(collection, {})
            storageTypes = collectionTypes.get(storage, {})
            organs = storageTypes.get(organ, {})
            specimenCount = organs.get(ppt, 0)
            specimenCount += 1
            organs[ppt] = specimenCount
            storageTypes[organ] = organs
            collectionTypes[storage] = storageTypes
            diagnoses[collection] = collectionTypes
            stats[cancerDiag] = diagnoses
        for cancerDiag, collectionTypes in stats.iteritems():
            withCancer = cancerDiag == '1'
            for collection, storageTypes in collectionTypes.iteritems():
                for storage, organs in storageTypes.iteritems():
                    for organ, pptIDs in organs.iteritems():
                        totalSpecimens = sum(pptIDs.values())
                        totalPpts = len(pptIDs)
                        cases, controls = totalPpts, 0 # FIXME: but how? No idea how to compute # cases or # controls from ERNE data
                        records.append(ERNESpecimenSummary(
                            storage, totalSpecimens,cases,controls,organ,withCancer,available,email,protocolID,collection
                        ))
        return records
    except urllib2.HTTPError, ex:
        _logger.info('Ignoring failed attempt to get specimens from %s via %s: %r', erneID, erneWS, ex)
    try:
        con.close()
    except (IOError, AttributeError):
        pass
    return records

def getInventory(erneID, withCancer, collection, storage, limit=100, erneWS=_erneWS):
    cdes = (
    	'BASELINE_CANCER-AGE-DIAGNOSIS_VALUE',
    	'BASELINE_CANCER-ICD9-CODE',
    	'BASELINE_DEMOGRAPHICS-ETHNIC_CODE',
    	'BASELINE_DEMOGRAPHICS-GENDER_CODE',
    	'BASELINE_DEMOGRAPHICS_RACE_CODE',
    	'BASELINE_SMOKE-REGULAR_1YEAR_CODE',
    	'SPECIMEN_AGE-COLLECTED_VALUE',
    	'SPECIMEN_AMOUNT-STORED_UNIT_CODE',
    	'SPECIMEN_AMOUNT-STORED_VALUE',
    	'SPECIMEN_AMOUNT_REMAINING_UNIT_CODE',
    	'SPECIMEN_AMOUNT_REMAINING_VALUE',
    	'SPECIMEN_AVAILABLE_CODE',
    	'SPECIMEN_CONTACT-EMAIL_TEXT',
    	'SPECIMEN_FINAL-STORE_CODE',
    	'SPECIMEN_TISSUE_ORGAN-SITE_CODE',
    	'STUDY_PARTICIPANT_ID',
    )
    queryStr = 'BASELINE_CANCER-CONFIRMATION_CODE = %(withCancer)d AND ' + \
        'SPECIMEN_COLLECTED_CODE = %(collection)s AND ' + \
        'SPECIMEN_STORED_CODE = %(storage)s AND %(selection)s'
    queryStr = queryStr % {
        'withCancer': withCancer and 1 or 0,
        'collection': collection,
        'storage':    storage,
        'selection':  ' AND '.join(['RETURN = %s' % cde for cde in cdes])
    }
    params = {'q': queryStr, 'url': erneID}
    con = None
    try:
        con = urllib2.urlopen(erneWS, urllib.urlencode(params))
        contactEmailAddr, specimens = None, []
        count = 0
        for erneRecord in con.read().split('$'):
            fields = erneRecord.split('\t')
            if len(fields) != 16: continue
            count += 1
            if count < limit:
                ageAtDX,icd9,ethnicity,gender,race,smoke,ageAtCol,su,sv,ru,rv,isAvailable,email,final,organ,ppt = fields
                if not contactEmailAddr: contactEmailAddr = email
                collected, remaining = Quantity(sv, su), Quantity(rv, ru)
                s = Specimen(ppt, gender, race, ethnicity, icd9, ageAtCol, ageAtDX, isAvailable, final, collected, remaining)
                specimens.append(s)
        return SpecimenInventory(contactEmailAddr, specimens, count, limit)
    finally:
        try:
            con.close()
        except (IOError, AttributeError):
            pass

def ERNESitesVocabulary(context):
    catalog = getToolByName(context, 'portal_catalog')
    # TODO: filter by review_state?
    results = catalog(object_provides=ISite.__identifier__, identifier=SITES.keys())
    siteNames = frozenset([(i.Title, i.Title) for i in results])
    siteNames = list(siteNames)
    siteNames.sort()
    return SimpleVocabulary.fromItems(siteNames)
directlyProvides(ERNESitesVocabulary, IVocabularyFactory)


if __name__ == '__main__':
    import sys
    for i in getSpecimens(sys.argv[1]):
        print i
    # details = getInventory(sys.argv[1], bool(sys.argv[2]), sys.argv[3], sys.argv[4])
    # print details
    # for i in details:
    #     print i
     
    
