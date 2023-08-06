# encoding: utf-8
# Copyright 2008–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment: Testing base code.
'''

import eke.knowledge.tests.base as ekeKnowledgeBase
import eke.site.tests.base as ekeSiteBase
import eke.study.tests.base as ekeStudyBase

_siteProtocolRDF = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF
    xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    xmlns:edrn='http://edrn.nci.nih.gov/rdf/schema.rdf#'>
	<edrn:Site rdf:about='http://tongue.com/clinic/3d'>
        <edrn:hasSpecimensForProtocols>
		    <edrn:Protocol rdf:about='http://swa.it/edrn/ps' specimenCount='123'/>
		    <edrn:Protocol rdf:about='http://swa.it/edrn/so' specimenCount='456'/>
		</edrn:hasSpecimensForProtocols>
	</edrn:Site>
	<edrn:Site rdf:about='http://plain.com/2d'>
		<edrn:hasSpecimensForProtocols>
			<edrn:Protocol rdf:about='http://swa.it/edrn/ps' specimenCount='789'/>
		</edrn:hasSpecimensForProtocols>
	</edrn:Site>
</rdf:RDF>'''

_protocolSpecimensRDF = ''''''

_erneResponse = '''0\t5\t1\tx@y.com\t1\t16\t116\t15$1\t5\t2\tx@y.com\t1\t16\t116\t15$1\t6\t3\tz@y.com\t1\t16\t116\t15$'''

def registerLocalTestData():
    ekeSiteBase.registerLocalTestData()
    ekeStudyBase.registerLocalTestData()
    ekeKnowledgeBase.registerTestData('/erne/a/siteProto', _siteProtocolRDF)
    ekeKnowledgeBase.registerTestData('/erne/a/protoSpec', _protocolSpecimensRDF)
    ekeKnowledgeBase.registerTestData('/erne/erneQuery', _erneResponse)
