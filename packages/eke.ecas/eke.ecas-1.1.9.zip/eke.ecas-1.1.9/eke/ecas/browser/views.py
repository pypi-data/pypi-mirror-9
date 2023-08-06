# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EKE ECAS: views for content types.
'''

from Acquisition import aq_inner
from eke.ecas.interfaces import IDataset, IDatasetFolder
from eke.knowledge.browser.views import KnowledgeFolderView, KnowledgeObjectView
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class DatasetFolderView(KnowledgeFolderView):
    '''Default view of a Dataset Folder.'''
    __call__ = ViewPageTemplateFile('templates/datasetfolder.pt')
    def haveDatasets(self):
        return len(self.datasets()) > 0
    def haveSubfolders(self):
        return len(self.subfolders()) > 0
    @memoize
    def datasets(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        uidCatalog = getToolByName(context, 'uid_catalog')
        allDatasets = dict([
            (i.UID, dict(
                title=i.Title, url=i.identifier, bodySystemName=i.bodySystemName, protocolName=i.protocolName,
                collaborativeGroup=i.collaborativeGroup, reviewState='hide',
                protocolURL=self._getProtocolURL(i.getProtocolUID, uidCatalog),
                collaborativeGroupURL=self._getCollaborativeGroupURL(i.collaborativeGroupUID, uidCatalog),
                # I'm not proud of the below expression:
                pis=[dict(name=j[0].Title, url=j[0].getURL(relative=False)) for j in [uidCatalog(UID=k) for k in i.piUIDs]]
            )) for i in catalog.search(
                query_request=dict(
                    object_provides=IDataset.__identifier__,
                    path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
                ),
            )
        ])
        for k, v in allDatasets.items():
            if v['protocolName'] is None:
                del allDatasets[k]
        visibleDatasets = [
            i.UID for i in catalog.searchResults(
                object_provides=IDataset.__identifier__,
                path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            )
        ]
        for i in visibleDatasets:
            if i in allDatasets:
                dataset = allDatasets[i]
                dataset['reviewState'] = 'published'
        results = allDatasets.values()
        results.sort(lambda a, b: cmp(a['title'], b['title']))
        return results
    def _getProtocolURL(self, protocolUID, uidCatalog):
        if protocolUID is None: return None
        results = uidCatalog(UID=protocolUID)
        if len(results) == 0: return None
        return results[0].getURL(relative=False)
    def _getCollaborativeGroupURL(self, collaborativeGroupUID, uidCatalog):
        if collaborativeGroupUID is None: return None
        results = uidCatalog(UID=collaborativeGroupUID)
        if len(results) == 0: return None
        return results[0].getURL(relative=False)
    @memoize
    def subfolders(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            object_provides=IDatasetFolder.__identifier__,
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            sort_on='sortable_title'
        )
        return [dict(title=i.Title, description=i.Description, url=i.getURL()) for i in results]

class DatasetView(KnowledgeObjectView):
    '''Default view of a Dataset.'''
    __call__ = ViewPageTemplateFile('templates/dataset.pt')
