# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Dataset.'''

from eke.ecas import ProjectMessageFactory as _
from eke.ecas.config import PROJECTNAME
from eke.ecas.interfaces import IDataset
from eke.knowledge.content import knowledgeobject
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName
from zope.interface import implements, directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

ecasURIPrefix = 'urn:edrn:'
edrnURIPrefix = 'http://edrn.nci.nih.gov/rdf/schema.rdf#'

DatasetSchema = knowledgeobject.KnowledgeObjectSchema.copy() + atapi.Schema((
    atapi.StringField(
        'custodian',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Custodian'),
            description=_(u'The caretaker of this science data.'),
        ),
        predicateURI=ecasURIPrefix + 'DataCustodian',
        unmarkedUpRDFLiteral=True,
    ),
    atapi.ReferenceField(
        'protocol',
        required=False,
        enforceVocabulary=True,
        multiValued=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        relationship='protocolProducingThisDataset',
        vocabulary_display_path_bound=-1,
        vocabulary_factory=u'eke.study.ProtocolsVocabulary',
        widget=atapi.ReferenceWidget(
            label=_(u'Protocol'),
            description=_(u'The protocol or study that produced this data.'),
        ),
        predicateURI=edrnURIPrefix + 'protocol',
    ),
    atapi.ReferenceField(
        'sites',
        required=False,
        enforceVocabulary=True,
        multiValued=True,
        storage=atapi.AnnotationStorage(),
        relationship='sitesContributingToThisDataset',
        vocabulary_display_path_bound=-1,
        vocabulary_factory=u'eke.site.Sites',
        widget=atapi.ReferenceWidget(
            label=_(u'Sites'),
            description=_(u'EDRN sites that contributed to this science data.'),
        ),
        predicateURI=edrnURIPrefix + 'site',
    ),
    atapi.LinesField(
        'authors',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u'Authors'),
            description=_(u'People who created this data.'),
        ),
        predicateURI=ecasURIPrefix + 'Author',
        unmarkedUpRDFLiteral=True,
    ),
    atapi.LinesField(
        'grantSupport',
        required=False,
        multiValued=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u'Grant Support'),
            description=_(u'Grants that are supporting this science data.'),
        ),
        predicateURI=ecasURIPrefix + 'GrantSupport',
        unmarkedUpRDFLiteral=True,
    ),
    atapi.LinesField(
        'researchSupport',
        required=False,
        multiValued=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u'Research Support'),
            description=_(u'Research that supported this science data.'),
        ),
        predicateURI=ecasURIPrefix + 'ResearchSupport',
        unmarkedUpRDFLiteral=True,
    ),
    atapi.TextField(
        'dataDisclaimer',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.TextAreaWidget(
            label=_(u'Data Disclaimer'),
            description=_(u'A legal license, warranty, indemnity, and release detailing the acceptable use of this science data.'),
        ),
        predicateURI=ecasURIPrefix + 'DataDisclaimer',
        unmarkedUpRDFLiteral=True,
    ),
    atapi.TextField(
        'studyBackground',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.TextAreaWidget(
            label=_(u'Study Background'),
            description=_(u'Background information that would be useful to know before using this science data.'),
        ),
        predicateURI=ecasURIPrefix + 'StudyBackground',
        unmarkedUpRDFLiteral=True,
    ),
    atapi.TextField(
        'studyMethods',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.TextAreaWidget(
            label=_(u'Study Methods'),
            description=_(u'Various methods that may be employed in the study of this science data.'),
        ),
        predicateURI=ecasURIPrefix + 'StudyMethods',
        unmarkedUpRDFLiteral=True,
    ),
    atapi.TextField(
        'studyResults',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.TextAreaWidget(
            label=_(u'Study Results'),
            description=_(u'Results that come from studying this science data.'),
        ),
        predicateURI=ecasURIPrefix + 'StudyResults',
        unmarkedUpRDFLiteral=True,
    ),
    atapi.TextField(
        'studyConclusion',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.TextAreaWidget(
            label=_(u'Study Conclusion'),
            description=_(u'The conclusion that may be drawn from analyzing this science data.'),
        ),
        predicateURI=ecasURIPrefix + 'StudyConclusion',
        unmarkedUpRDFLiteral=True,
    ),
    atapi.DateTimeField(
        'dataUpdateDate',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.CalendarWidget(
            label=_(u'Date'),
            description=_(u'Date this data was last updated.'),
            show_hm=False,
        ),
        predicateURI=ecasURIPrefix + 'Date',
        unmarkedUpRDFLiteral=False,
    ),
    atapi.StringField(
        'collaborativeGroup',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Collaborative Group'),
            description=_(u'Which group collaborated to help make this science data.'),
        ),
        predicateURI=ecasURIPrefix + 'CollaborativeGroup',
        unmarkedUpRDFLiteral=True,
    ),
    atapi.StringField(
        'collaborativeGroupUID',
        required=False,
        searchable=False,
        storage=atapi.AnnotationStorage(),
        modes=('view',),
        widget=atapi.StringWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
        ),
    ),
    atapi.ReferenceField(
        'bodySystem',
        required=False,
        enforceVocabulary=True,
        multiValued=False,
        storage=atapi.AnnotationStorage(),
        relationship='bodySystemForDataset',
        vocabulary_display_path_bound=-1,
        vocabulary_factory=u'eke.knowledge.BodySystems',
        widget=atapi.ReferenceWidget(
            label=_(u'Body System'),
            description=_(u'About what body system (such as an organ) this science data is'),
        ),
        predicateURI=edrnURIPrefix + 'organ',
    ),
    atapi.ComputedField(
        'bodySystemName',
        required=False,
        searchable=False,
        storage=atapi.AnnotationStorage(),
        expression='context._computeBodySystemName()',
        modes=('view',),
        widget=atapi.ComputedWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
        ),
    ),
    atapi.ComputedField(
        'protocolName',
        required=False,
        searchable=False,
        storage=atapi.AnnotationStorage(),
        expression='context._computeProtocolName()',
        modes=('view',),
        widget=atapi.ComputedWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
        ),
    ),
    atapi.ComputedField(
        'protocolUID',
        required=False,
        searchable=False,
        expression='context._computeMyProtocolUID()',
        modes=('view',),
        widget=atapi.ComputedWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
        ),
    ),
    atapi.ComputedField(
        'piUIDs',
        required=False,
        searchable=False,
        storage=atapi.AnnotationStorage(),
        expression='context._computePIUIDs()',
        multiValued=True,
        modes=('view',),
        widget=atapi.ComputedWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
        ),
    ),
    atapi.ComputedField(
        'piNames',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        expression='context._computePINames()',
        multiValued=True,
        modes=('view',),
        widget=atapi.ComputedWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
        ),
    ),
))

# FIXME: ECAS RDF uses some bizarre nonstandard title predicate. It should probably be dublin core.
DatasetSchema['title'].predicateURI = ecasURIPrefix + 'Title'

finalizeATCTSchema(DatasetSchema, folderish=False, moveDiscussion=False)

class Dataset(knowledgeobject.KnowledgeObject):
    '''Dataset.'''
    implements(IDataset)
    schema                = DatasetSchema
    portal_type           = 'Dataset'
    title                 = atapi.ATFieldProperty('title')
    custodian             = atapi.ATFieldProperty('custodian')
    protocol              = atapi.ATReferenceFieldProperty('protocol')
    sites                 = atapi.ATReferenceFieldProperty('sites')
    authors               = atapi.ATFieldProperty('authors')
    grantSupport          = atapi.ATFieldProperty('grantSupport')
    researchSupport       = atapi.ATFieldProperty('researchSupport')
    dataDisclaimer        = atapi.ATFieldProperty('dataDisclaimer')
    studyBackground       = atapi.ATFieldProperty('studyBackground')
    studyMethods          = atapi.ATFieldProperty('studyMethods')
    studyResults          = atapi.ATFieldProperty('studyResults')
    studyConclusion       = atapi.ATFieldProperty('studyConclusion')
    dataUpdateDate        = atapi.ATDateTimeFieldProperty('dataUpdateDate')
    collaborativeGroup    = atapi.ATFieldProperty('collaborativeGroup')
    collaborativeGroupUID = atapi.ATFieldProperty('collaborativeGroupUID')
    bodySystem            = atapi.ATReferenceFieldProperty('bodySystem')
    bodySystemName        = atapi.ATFieldProperty('bodySystemName')
    protocolName          = atapi.ATFieldProperty('protocolName')
    piUIDs                = atapi.ATFieldProperty('piUIDs')
    piNames               = atapi.ATFieldProperty('piNames')
    def _computeBodySystemName(self):
        return self.bodySystem is not None and self.bodySystem.title or None
    def _computeProtocolName(self):
        return self.protocol is not None and self.protocol.title or None
    def _computeMyProtocolUID(self):
        uid = self.protocol.UID() if self.protocol is not None else None
        return uid
    def _computePIUIDs(self):
        if self.protocol and self.protocol.leadInvestigatorSite and self.protocol.leadInvestigatorSite.principalInvestigator:
            return [self.protocol.leadInvestigatorSite.principalInvestigator.UID()]
        return []
    def _computePINames(self):
        if self.protocol and self.protocol.leadInvestigatorSite and self.protocol.leadInvestigatorSite.principalInvestigator:
            return [self.protocol.leadInvestigatorSite.principalInvestigator.Title()]
        return []

atapi.registerType(Dataset, PROJECTNAME)

def DatasetVocabularyFactory(context):
    '''Yield a vocabulary for datasets.'''
    catalog = getToolByName(context, 'portal_catalog')
    # TODO: filter by review_state?
    results = catalog(object_provides=IDataset.__identifier__, sort_on='sortable_title')
    terms = [SimpleVocabulary.createTerm(i.UID, i.UID, i.Title.decode('utf-8')) for i in results]
    return SimpleVocabulary(terms)
directlyProvides(DatasetVocabularyFactory, IVocabularyFactory)

def DatasetUpdater(context, event):
    context.bodySystemName = context._computeBodySystemName()
    context.protocolName   = context._computeProtocolName()
    context.piUIDs         = context._computePIUIDs()
    context.reindexObject(idxs=['bodySystemName', 'protocolName', 'piUIDs'])
