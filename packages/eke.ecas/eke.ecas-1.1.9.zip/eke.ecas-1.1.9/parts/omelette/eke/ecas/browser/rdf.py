# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EKE ECAS: RDF ingest for Dataset Folders and their Datasets.
'''

from Acquisition import aq_inner
from eke.ecas import ProjectMessageFactory as _
from eke.knowledge.browser.rdf import KnowledgeFolderIngestor, CreatedObject, RDFIngestException
from eke.knowledge.browser.utils import updateObject
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from rdflib import URIRef, ConjunctiveGraph, URLInputSource
from zope.component import queryUtility, getMultiAdapter
from zope.publisher.browser import TestRequest
from Products.CMFCore.WorkflowCore import WorkflowException
from eke.ecas.utils import COLLABORATIVE_GROUP_ECAS_IDS_TO_NAMES

_accessPredicateURI     = URIRef('http://edrn.nci.nih.gov/rdf/schema.rdf#AccessGrantedTo')
_protocolPredicateURI   = URIRef('http://edrn.nci.nih.gov/rdf/schema.rdf#protocol')
_visibilityPredicateURI = URIRef('http://edrn.nci.nih.gov/rdf/schema.rdf#QAState')
_collaborativeGroupURI  = URIRef('urn:edrn:CollaborativeGroup')
# FIXME: this should be dublin core title:
_nonstandardECASTitlePredicateURI = URIRef('urn:edrn:DataSetName')
# Interface identifier for EDRN Collaborative Group, from edrnsite.collaborations
_collabGroup = 'edrnsite.collaborations.interfaces.collaborativegroupindex.ICollaborativeGroupIndex'

class DatasetFolderIngestor(KnowledgeFolderIngestor):
    '''Dataset Folder ingestion.'''
    def _doPublish(self, item, wfTool, action='publish'):
        try:
            wfTool.doActionFor(item, action=action)
            item.reindexObject()
        except WorkflowException:
            pass
        for i in item.objectIds():
            subItem = item[i]
            self._doPublish(subItem, wfTool)
    def _generateID(self, uri, predicates, normalizerFunction):
        if _nonstandardECASTitlePredicateURI in predicates:
            return normalizerFunction(unicode(predicates[_nonstandardECASTitlePredicateURI][0]))
        else:
            return normalizerFunction(unicode(uri))
    def _generateTitle(self, uri, predicates):
        if _nonstandardECASTitlePredicateURI in predicates:
            return unicode(predicates[_nonstandardECASTitlePredicateURI][0])
        else:
            return unicode(uri)
    def publishDataset(self, wfTool, dataset, predicates):
        if _visibilityPredicateURI in predicates:
            visibilty = unicode(predicates[_visibilityPredicateURI][0])
            if visibilty == u'Accepted':
                if wfTool.getInfoFor(dataset, 'review_state') != 'published':
                    self._doPublish(dataset, wfTool)
        else:
            if wfTool.getInfoFor(dataset, 'review_state') != 'private':
                self._doPublish(dataset, wfTool, action='retract')
    def __call__(self):
        '''We have to override this because ECAS datasets come in with unpredictable RDF types.
        '''
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        wfTool = getToolByName(context, 'portal_workflow')
        rdfDataSource = context.rdfDataSource
        if not rdfDataSource:
            raise RDFIngestException(_(u'This folder has no RDF data source URL.'))
        normalizerFunction = queryUtility(IIDNormalizer).normalize
        graph = ConjunctiveGraph()
        graph.parse(URLInputSource(rdfDataSource))
        statements = self._parseRDF(graph)
        createdObjects = []
        for uri, predicates in statements.items():
            objectID = self._generateID(uri, predicates, normalizerFunction)
            title = self._generateTitle(uri, predicates)
            if objectID in context.objectIds():
                dataset = context[objectID]
            else:
                dataset = context[context.invokeFactory('Dataset', objectID)]
            dataset.setTitle(title)
            updateObject(dataset, uri, predicates, context)
            createdObjects.append(CreatedObject(dataset))
            if _collaborativeGroupURI in predicates:
                self.updateCollaborativeGroup(dataset, unicode(predicates[_collaborativeGroupURI][0]), catalog)
            if _protocolPredicateURI in predicates:
                for proto in [i.getObject() for i in catalog(identifier=[unicode(i) for i in predicates[_protocolPredicateURI]])]:
                    uid = dataset.UID()
                    current = [i.UID() for i in proto.datasets]
                    if uid not in current:
                        current.append(uid)
                        proto.setDatasets(current)
                        proto.datasetNames = proto._computeDatasetNames()
                        proto.reindexObject()
            if _accessPredicateURI in predicates:
                groupIDs = [unicode(i) for i in predicates[_accessPredicateURI]]
                dataset.accessGroups = groupIDs
                settings = [dict(type='group', roles=[u'Reader'], id=i) for i in groupIDs]
                sharing = getMultiAdapter((dataset, TestRequest()), name=u'sharing')
                sharing.update_role_settings(settings)
            self.publishDataset(wfTool, dataset, predicates)
            dataset.reindexObject()
        self.objects = createdObjects
        return self.render and self.template() or len(self.objects)
    def updateCollaborativeGroup(self, dataset, groupID, catalog):
        try:
            groupName = COLLABORATIVE_GROUP_ECAS_IDS_TO_NAMES[groupID]
        except KeyError:
            return
        results = [i.getObject() for i in catalog(object_provides=_collabGroup, Title=groupName)]
        for collabGroup in results:
            currentDatasets = collabGroup.getDatasets()
            if dataset not in currentDatasets:
                currentDatasets.append(dataset)
                collabGroup.setDatasets(currentDatasets)
                
        
