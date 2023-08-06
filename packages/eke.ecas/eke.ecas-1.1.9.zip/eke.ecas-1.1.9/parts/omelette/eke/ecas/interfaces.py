# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EKE ECAS: interfaces.
'''

from zope import schema
from zope.container.constraints import contains
from eke.ecas import ProjectMessageFactory as _
from eke.knowledge.interfaces import IKnowledgeFolder, IKnowledgeObject, IBodySystem
from eke.site.interfaces import ISite
from eke.study.interfaces import IProtocol

class IDatasetFolder(IKnowledgeFolder):
    '''Dataset folder.'''
    contains('eke.ecas.interfaces.IDataset')

class IDataset(IKnowledgeObject):
    '''Dataset.'''
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Name of this science data.'),
        required=True,
    )
    custodian = schema.TextLine(
        title=_(u'Custodian'),
        description=_(u'The caretaker of this science data.'),
        required=False,
    )
    protocol = schema.Object(
        title=_(u'Protocol'),
        description=_(u'The protocol or study that produced this science data.'),
        required=False,
        schema=IProtocol
    )
    sites = schema.List(
        title=_(u'Sites'),
        description=_(u'EDRN sites that contributed to this science data.'),
        required=False,
        value_type=schema.Object(
            title=_(u'EDRN Site'),
            description=_(u'A single EDRN site that contributed to this data.'),
            schema=ISite
        )
    )
    authors = schema.List(
        title=_(u'Authors'),
        description=_(u'People who created this data.'),
        required=False,
        value_type=schema.TextLine(title=_(u'Author'), description=_(u'A single author who helped create this data.'))
    )
    grantSupport = schema.List(
        title=_(u'Grant Support'),
        description=_(u'Grants that are supporting this science data.'),
        required=False,
        value_type=schema.TextLine(title=_(u'Supporting Grant'), description=_(u'A single grant supporting this science data.'))
    )
    researchSupport = schema.List(
        title=_(u'Research Support'),
        description=_(u'Research that supported this science data.'),
        required=False,
        value_type=schema.TextLine(
            title=_(u'Research'),
            description=_(u'A single instance of research that supported this science data.'))
    )
    dataDisclaimer = schema.Text(
        title=_(u'Data Disclaimer'),
        description=_(u'A legal license, warranty, indemnity, and release detailing the acceptable use of this science data.'),
        required=False,
    )
    studyBackground = schema.Text(
        title=_(u'Study Background'),
        description=_(u'Background information that would be useful to know before using this science data.'),
        required=False,
    )
    studyMethods = schema.Text(
        title=_(u'Study Methods'),
        description=_(u'Various methods that may be employed in the study of this science data.'),
        required=False,
    )
    studyResults = schema.Text(
        title=_(u'Study Results'),
        description=_(u'Results that come from studying this science data.'),
        required=False,
    )
    studyConclusion = schema.Text(
        title=_(u'Study Conclusion'),
        description=_(u'The conclusion that may be drawn from analyzing this science data.'),
        required=False,
    )
    dataUpdateDate = schema.Datetime(
        title=_(u'Date'),
        description=_(u'Date this data was last updated.'),
        required=False,
    )
    collaborativeGroup = schema.TextLine(
        title=_(u'Collaborative Group'),
        description=_(u'Which group collaborated to help make this science data.'),
        required=False,
    )
    bodySystem = schema.Object(
        title=_(u'Body System'),
        description=_(u'About what body system (such as an organ) this science data is'),
        required=False,
        schema=IBodySystem
    )
    bodySystemName = schema.TextLine(
        title=_(u'Body System Name'),
        description=_(u'The name of the body system (such as an organ).'),
        required=False,
    )
    protocolName = schema.TextLine(
        title=_(u'Protocol Name'),
        description=_(u'The name of the protocol or study that produced this data.'),
        required=False,
    )
    piUIDs = schema.List(
        title=_(u'PI UIDs'),
        description=_(u'UIDs of the PIs who produced this data.'),
        required=False,
        value_type=schema.TextLine(
            title=_(u'PI UID'),
            description=_(u'UID of a single PI who produced this data.'),
            required=False
        )
    )
    piNames = schema.List(
        title=_(u'PI Names'),
        description=_(u'Names of the PIs who produced this data.'),
        required=False,
        value_type=schema.TextLine(
            title=_(u'PI Name'),
            description=_(u'Name of a single PI who produced this data.'),
            required=False
        )
    )
    collaborativeGroupUID = schema.TextLine(
        title=_(u'Collaborative Group UID'),
        description=_(u'Unique ID of the collaborative group that produced this dataset.'),
        required=False,
    )
