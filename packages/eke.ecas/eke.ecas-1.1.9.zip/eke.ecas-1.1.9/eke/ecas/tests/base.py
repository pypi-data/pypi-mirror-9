# encoding: utf-8
# Copyright 2008 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
Testing base code.
'''

import eke.knowledge.tests.base as ekeKnowledgeBase
import eke.study.tests.base as ekeStudyBase
import eke.site.tests.base as ekeSiteBase

_singleDatasetRDF = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:cas="urn:oodt:" xmlns:ecas="urn:edrn:"
    xmlns:edrn='http://edrn.nci.nih.gov/rdf/schema.rdf#'>
    <ecas:TopSecretData rdf:about='urn:edrn:top-secret-data'>
        <edrn:QAState>Accepted</edrn:QAState>
        <ecas:DataCustodian>Joe McBlow &lt;joe@mcblow.com&gt;</ecas:DataCustodian>
        <ecas:GrantSupport>REDACTED-1</ecas:GrantSupport>
        <ecas:GrantSupport>REDACTED-2</ecas:GrantSupport>
        <edrn:site rdf:resource='http://tongue.com/clinic/3d'/>
        <ecas:Author>Jim Blow</ecas:Author>
        <ecas:ResearchSupport>Blow Me Extramural</ecas:ResearchSupport>
        <ecas:ResearchSupport>Blow You Intramural</ecas:ResearchSupport>
        <edrn:protocol rdf:resource='http://swa.it/edrn/ps'/>
        <ecas:DataSetName>Get Bent</ecas:DataSetName>
        <ecas:DataDisclaimer>If you share this I'll kill you.</ecas:DataDisclaimer>
        <ecas:Date>2009-12-24T18:16:12.129Z</ecas:Date>
        <ecas:StudyMethods>None of your business.</ecas:StudyMethods>
        <ecas:StudyConclusion>Classified.</ecas:StudyConclusion>
        <ecas:StudyResults>Nice try, bub.</ecas:StudyResults>
        <edrn:organ rdf:resource='urn:edrn:organs:anus'/>
        <ecas:StudyBackground>You must have a death wish.</ecas:StudyBackground>
        <ecas:CollaborativeGroup>NSA</ecas:CollaborativeGroup>
    </ecas:TopSecretData>
</rdf:RDF>'''

_dobuleDatasetRDF = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:cas="urn:oodt:" xmlns:ecas="urn:edrn:"
    xmlns:edrn='http://edrn.nci.nih.gov/rdf/schema.rdf#'>
    <ecas:TopSecretData rdf:about='urn:edrn:top-secret-data'>
        <edrn:QAState>Accepted</edrn:QAState>
        <ecas:DataCustodian>Joe McBlow</ecas:DataCustodian>
        <ecas:GrantSupport>1R01 CA098642-01A1/CA/NCI</ecas:GrantSupport>
        <ecas:GrantSupport>R03 CA102888/CA/NCI</ecas:GrantSupport>
        <edrn:site rdf:resource='http://tongue.com/clinic/3d'/>
        <ecas:Author>Jim Blow</ecas:Author>
        <ecas:ResearchSupport>Blow Me Extramural</ecas:ResearchSupport>
        <ecas:ResearchSupport>Blow You Intramural</ecas:ResearchSupport>
        <edrn:protocol rdf:resource='http://swa.it/edrn/ps'/>
        <ecas:DataSetName>Get Bent</ecas:DataSetName>
        <ecas:DataDisclaimer>If you share this I'll kill you.</ecas:DataDisclaimer>
        <ecas:Date>2009-12-24T18:16:12.129Z</ecas:Date>
        <ecas:StudyMethods>None of your business.</ecas:StudyMethods>
        <ecas:StudyConclusion>Classified.</ecas:StudyConclusion>
        <ecas:StudyResults>Nice try, bub.</ecas:StudyResults>
        <edrn:organ rdf:resource='urn:edrn:organs:anus'/>
        <ecas:StudyBackground>You must have a death wish.</ecas:StudyBackground>
        <ecas:CollaborativeGroup>NSA</ecas:CollaborativeGroup>
    </ecas:TopSecretData>
    <ecas:NotAsSecretData rdf:about='urn:edrn:not-as-secret-data'>
        <ecas:DataSetName>Get not as bent</ecas:DataSetName>
        <edrn:protocol rdf:resource='http://swa.it/edrn/ps'/>
        <edrn:QAState>Under Review</edrn:QAState>
        <edrn:AccessGrantedTo rdf:resource='ldap://edrn/groups/silly-group'/>
    </ecas:NotAsSecretData>
    <ecas:TotallySecretData rdf:about='urn:edrn:totally-secret'>
        <ecas:DataSetName>Chad Vader</ecas:DataSetName>
        <edrn:protocol rdf:resource='http://swa.it/edrn/ps'/>
    </ecas:TotallySecretData>
</rdf:RDF>'''

def registerLocalTestData():
    ekeKnowledgeBase.registerLocalTestData()
    ekeStudyBase.registerLocalTestData()
    ekeSiteBase.registerLocalTestData()
    ekeKnowledgeBase.registerTestData('/datasets/a', _singleDatasetRDF)
    ekeKnowledgeBase.registerTestData('/datasets/b', _dobuleDatasetRDF)

