# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Dataset folder.'''

from eke.ecas.config import PROJECTNAME
from eke.ecas.interfaces import IDatasetFolder
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements
from eke.knowledge.content import knowledgefolder

DatasetFolderSchema = knowledgefolder.KnowledgeFolderSchema.copy() + atapi.Schema((
    # No other fields
))

finalizeATCTSchema(DatasetFolderSchema, folderish=True, moveDiscussion=False)

class DatasetFolder(knowledgefolder.KnowledgeFolder):
    '''Dataset Folder which contains Datasets.'''
    implements(IDatasetFolder)
    portal_type               = 'Dataset Folder'
    _at_rename_after_creation = True
    schema                    = DatasetFolderSchema

atapi.registerType(DatasetFolder, PROJECTNAME)
