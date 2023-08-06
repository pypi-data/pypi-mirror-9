# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EKE Biomarkers: interfaces.
'''

from eke.biomarker import ProjectMessageFactory as _
from eke.knowledge.interfaces import IKnowledgeFolder, IKnowledgeObject, IBodySystem
from eke.publications.interfaces import IPublication
from eke.study.interfaces import IProtocol
from zope import schema
from zope.container.constraints import contains
from zope.interface import Interface

class IBiomarkerFolder(IKnowledgeFolder):
    '''Biomarker folder.'''
    contains(
        'eke.biomarker.interfaces.IBiomarker',
        'eke.biomarker.interfaces.IBiomarkerFolder',
        'eke.biomarker.interfaces.IReviewListing'
    )
    bmoDataSource = schema.TextLine(
        title=_(u'Biomarker-Organ RDF Data Source'),
        description=_(u'URL to a source of RDF data that supplements the RDF data source with biomarker-organ data.'),
        required=True
    )
    disclaimer = schema.Text(
        title=_(u'Disclaimer'),
        description=_(u'Legal disclaimer to display on Biomarker Folder pages.'),
        required=False,
    )


class IQualityAssuredObject(Interface):
    '''An abstract object that undergoes a quality assurance process.'''
    qaState = schema.TextLine(
        title=_(u'QA State'),
        description=_(u'The current status with regard to quality assurance of this object.'),
        required=False,
    )
    
class IPhasedObject(Interface):
    '''An abstract object that undergoes the standard phases of biomarker research.'''
    phase = schema.TextLine(
        title=_(u'Phase'),
        description=_(u"The current phase of the biomarker's development with regard to this organ."),
        required=False,
    )


class IResearchedObject(Interface):
    '''An abstract object that is researched; that is, there are studies,
    publications, datasets, and other resources about it.'''
    protocols = schema.List(
        title=_(u'Protocols & Studies'),
        description=_(u'Protocols and studies that are studying this object.'),
        required=False,
        value_type=schema.Object(
            title=_(u'Study'),
            description=_(u'A study or protocol studying an object.'),
            schema=IProtocol
        )
    )
    publications = schema.List(
        title=_(u'Publications'),
        description=_(u'Publications that have been written talking about this object.'),
        required=False,
        value_type=schema.Object(
            title=_(u'Publication'),
            description=_(u'A publication talking about an object.'),
            schema=IPublication
        )
    )
    resources = schema.List(
        title=_(u'Resources'),
        description=_(u'Additional resources about this object.'),
        required=False,
        value_type=schema.Object(
            title=_(u'Resource'),
            description=_(u'An additional resource about an object.'),
            schema=IKnowledgeObject
        )
    )
    datasets = schema.List(
        title=_(u'Datasets'),
        description=_(u'Datasets providing measured scientific bases for this biomarker.'),
        required=False,
        value_type=schema.TextLine(
            title=_(u'Dataset'),
            description=_(u'Dataset providing a measured scientific basis for this biomarker.'),
        )
    )
    

class IBiomarker(IKnowledgeObject, IResearchedObject, IQualityAssuredObject):
    '''An abstract biomarker.'''
    contains('eke.biomarker.interfaces.IBiomarkerBodySystem')
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'The main name of the biomarker.'),
        required=True
    )
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'A short summary of the biomarker.'),
        required=False
    )
    shortName = schema.TextLine(
        title=_(u'Short Name'),
        description=_(u'A shorter and preferred alias for the biomarker.'),
        required=False
    )
    hgncName = schema.TextLine(
        title=_(u'HGNC Name'),
        description=_(u'The name assigned by the HUGO Gene Nomenclature Committee.'),
        required=False,
    )
    bmAliases = schema.List(
        title=_(u'Aliases'),
        description=_(u'Additional names by which the biomarker is known.'),
        required=False,
        value_type=schema.TextLine(
            title=_(u'Alias'),
            description=_(u'Another name for a biomarker.')
        )
    )
    indicatedBodySystems = schema.List(
        title=_(u'Indicated Organs'),
        description=_(u'Organs for which this biomarker is an indicator.'),
        required=False,
        value_type=schema.TextLine(
            title=_(u'Indicated Organ'),
            description=_(u'Organ for which this biomarker is an indicator.')
        )
    )
    accessGroups = schema.List(
        title=_(u'Access Groups'),
        description=_(u'Groups that are allowed access to this biomarker.'),
        required=False,
        value_type=schema.TextLine(
            title=_(u'Access Group'),
            description=_(u'A single URI identifying a group that may access a biomarker.')
        )
    )
    biomarkerKind = schema.TextLine(
        title=_(u'Kind'),
        description=_(u'What kind of biomarker.'),
        required=False,
    )
    

class IBiomarkerPanel(IBiomarker):
    '''A panel of biomarkers that itself behaves as a single (yet composite) biomarker.'''
    members = schema.List(
        title=_(u'Member Markers'),
        description=_(u'Biomarkers that are a part of this panel'),
        required=False,
        value_type=schema.Object(
            title=_(u'Member Marker'),
            description=_(u"A biomarker that's part of a panel."),
            schema=IBiomarker
        )
    )


class IElementalBiomarker(IBiomarker):
    '''A single, actual biomarker.'''
    biomarkerType = schema.TextLine(
        title=_(u'Biomarker Type'),
        description=_(u'The general category, kind, or class of this biomarker.'),
        required=False
    )


class IBiomarkerBodySystem(IKnowledgeObject, IResearchedObject, IPhasedObject, IQualityAssuredObject):
    '''Research into a biomarker's effects on a single body system.'''
    contains('eke.biomarker.interfaces.IBodySystemStudy')
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'A short summary of the research of a biomarker into a specific organ.'),
        required=False
    )
    performanceComment = schema.Text(
        title=_(u'Performance Comment'),
        description=_(u'A short summary of the biomarker performance with respect to a specific organ'),
        required=False
    )
    bodySystem = schema.Object(
        title=_(u'Organ'),
        description=_(u'The organ for which the biomarker indicates diseases.'),
        required=True,
        schema=IBodySystem
    )
    cliaCertification = schema.Bool(
        title=_(u'CLIA Certification'),
        description=_(u'True if this biomarker has been certified by CLIA for this organ.'),
        required=False,
        default=False,
    )
    fdaCertification = schema.Bool(
        title=_(u'FDA Certification'),
        description=_(u'True if this biomarker has been certified by the FDA for this organ.'),
        required=False,
        default=False,
    )


class IBodySystemStudy(IKnowledgeObject, IResearchedObject):
    '''Study-specific information on a biomarker's effects on a single organ.'''
    contains('eke.biomarker.interfaces.IStudyStatistics')
    protocol = schema.Object(
        title=_(u'Study'),
        description=_(u'The study or protocol referenced by specific organ with regard to a biomarker.'),
        required=True,
        schema=IProtocol
    )
    decisionRule = schema.Text(
        title=_(u'Decision Rule'),
        description=_(u'Details about the decision rule for this body system study'),
        required=False,
    )
        
    

class IStudyStatistics(IKnowledgeObject):
    '''Statistician-friendly statistics.'''
    sensitivity = schema.Float(
        title=_(u'Sensitivity'),
        description=_(u'Proportion of actual positives that are correctly identified.'),
        required=False
    )
    specificity = schema.Float(
        title=_(u'Specificity'),
        description=_(u'Proportion of actual negatives that are correctly identified.'),
        required=False
    )
    npv = schema.Float(
        title=_(u'NPV'),
        description=_(u'Ratio of true negatives to combined true and false negatives.'),
        required=False
    )
    ppv = schema.Float(
        title=_(u'PPV'),
        description=_(u'Ratio of true positives to combined true and false positives.'),
        required=False
    )
    prevalence = schema.Float(
        title=_(u'Prevalence'),
        description=_(u'A percentage.'),
        required=False
    )
    details = schema.TextLine(
        title=_(u'Details'),
        description=_(u'Detailed notes about this set of statistics.'),
        required=False
    )
    specificAssayType = schema.Text(
        title=_(u'Specific Assay Type'),
        description=_(u'Information about the specific assay type used'),
        required=False
    )


class IReviewListing(Interface):
    '''A selection of biomarkers that are up for review.'''
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Name of this listing.'),
        required=True,
    )
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'A short summary of this review listing.'),
        required=False,
    )
    accessGroup = schema.TextLine(
        title=_(u'Access Group URI'),
        description=_(u'URI of the access group whose biomarkers should appear in the listing.'),
        required=True,
    )
    
