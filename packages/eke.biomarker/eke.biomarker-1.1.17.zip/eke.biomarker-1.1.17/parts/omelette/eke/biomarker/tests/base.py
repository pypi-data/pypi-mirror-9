# encoding: utf-8
# Copyright 2008–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Testing data.
'''

import eke.knowledge.tests.base as ekeKnowledgeBase
import eke.publications.tests.base as ekePublicationsBase
import eke.study.tests.base as ekeStudyBase
import eke.ecas.tests.base as ekeECASBase

# Traditional Products we have to load manually for test cases:
# (none at this time)

_biomarkerA = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bmdb="http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#">
    <bmdb:Biomarker rdf:about='http://edrn/bmdb/a1'>
        <bmdb:Title>Apogee 1</bmdb:Title>
        <bmdb:HgncName>APG1</bmdb:HgncName>
        <bmdb:ShortName>A1</bmdb:ShortName>
        <bmdb:BiomarkerID>http://edrn/bmdb/a1</bmdb:BiomarkerID>
        <bmdb:URN>urn:edrn:bmdb:bm1</bmdb:URN>
        <bmdb:IsPanel>0</bmdb:IsPanel>
        <bmdb:Description>A sticky bio-marker.</bmdb:Description>
        <bmdb:QAState>Accepted</bmdb:QAState>
        <bmdb:Phase>3</bmdb:Phase>
        <bmdb:Security>Public</bmdb:Security>
        <bmdb:Type>Colloidal</bmdb:Type>
        <bmdb:Alias>Approach</bmdb:Alias>
        <bmdb:Alias>Advent</bmdb:Alias>
        <bmdb:Alias>Bigo</bmdb:Alias>
        <bmdb:memberOfPanel rdf:resource='http://edrn/bmdb/p1'/>
        <bmdb:AccessGrantedTo rdf:resource='ldap://edrn/groups/g1' />
        <bmdb:AssociatedDataset rdf:resource='urn:edrn:top-secret-data'/>
        <bmdb:indicatorForOrgan rdf:resource='http://edrn/bmdb/a1/o1' />
        <bmdb:hasBiomarkerStudyDatas>
            <rdf:Bag>
                <rdf:li>
                    <bmdb:BiomarkerStudyData rdf:about='http://edrn/bmdb/a1/s1'>
                        <bmdb:referencesStudy rdf:resource='http://swa.it/edrn/ps' />
                        <bmdb:SensitivityDatas>
                            <rdf:Bag>
                                <rdf:li>
                                    <bmdb:SensitivityData rdf:about='http://edrn/bmdb/a1/s1/sd-0'>
                                        <bmdb:SensSpecDetail>Full bodied</bmdb:SensSpecDetail>
                                        <bmdb:Sensitivity>97</bmdb:Sensitivity>
                                        <bmdb:Specificity>48</bmdb:Specificity>
                                        <bmdb:Prevalence>43</bmdb:Prevalence>
                                        <bmdb:NPV>12</bmdb:NPV>
                                        <bmdb:PPV>14</bmdb:PPV>
                                    </bmdb:SensitivityData>
                                </rdf:li>
                            </rdf:Bag>
                        </bmdb:SensitivityDatas>
                    </bmdb:BiomarkerStudyData>
                </rdf:li>
                <rdf:li>
                    <bmdb:BiomarkerStudyData rdf:about='http://edrn/bmdb/a1/s1'>
                        <bmdb:referencesStudy rdf:resource='http://swa.it/edrn/so' />
                    </bmdb:BiomarkerStudyData>
                </rdf:li>
            </rdf:Bag>
        </bmdb:hasBiomarkerStudyDatas>
        <bmdb:referencedInPublication rdf:resource='http://is.gd/pVKq' />
        <bmdb:referencesResource rdf:resource='http://yahoo.com/' />
    </bmdb:Biomarker>
    <bmdb:Biomarker rdf:about='http://edrn/bmdb/p1'>
        <bmdb:Title>Panel 1</bmdb:Title>
        <bmdb:ShortName>P1</bmdb:ShortName>
        <bmdb:BiomarkerID>http://edrn/bmdb/p1</bmdb:BiomarkerID>
        <bmdb:URN>urn:edrn:bmdb:p1</bmdb:URN>
        <bmdb:IsPanel>1</bmdb:IsPanel>
        <bmdb:Description>A very sticky panel.</bmdb:Description>
        <bmdb:QAState>Accepted</bmdb:QAState>
        <bmdb:Phase>4</bmdb:Phase>
        <bmdb:Security>Public</bmdb:Security>
        <bmdb:Type>Proteinesque</bmdb:Type>
        <bmdb:Alias>Group 1</bmdb:Alias>
        <bmdb:Alias>Composite 1</bmdb:Alias>
        <bmdb:hasBiomarker rdf:resource='http://edrn/bmdb/a1' />
    </bmdb:Biomarker>
</rdf:RDF>'''

_biomarkerOrganA = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bmdb="http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#">
    <bmdb:BiomarkerOrganData rdf:about="http://edrn/bmdb/a1/o1">
        <bmdb:URN>http://edrn/bmdb/a1/o1</bmdb:URN>
        <bmdb:Biomarker rdf:resource='http://edrn/bmdb/a1'/>
        <bmdb:Description>Action on the rectum is amazing.</bmdb:Description>
        <bmdb:PerformanceComment>The biomarker failed to perform as expected.</bmdb:PerformanceComment>
        <bmdb:Organ>Rectum</bmdb:Organ>
        <bmdb:Phase>1</bmdb:Phase>
        <bmdb:QAState>Accepted</bmdb:QAState>
        <bmdb:AccessGrantedTo rdf:resource='ldap://edrn/groups/g1'/>
        <bmdb:certification rdf:resource='http://www.cms.gov/Regulations-and-Guidance/Legislation/CLIA/index.html'/>
        <bmdb:hasBiomarkerOrganStudyDatas>
            <rdf:Bag>
                <rdf:li rdf:resource='http://edrn/bmdb/a1/o1#s1'/>
            </rdf:Bag>
        </bmdb:hasBiomarkerOrganStudyDatas>
        <bmdb:referencedInPublication rdf:resource='http://is.gd/q6mS'/>
    </bmdb:BiomarkerOrganData>
    <bmdb:BiomarkerOrganStudyData rdf:about='http://edrn/bmdb/a1/o1#s1'>
        <bmdb:referencesStudy rdf:resource='http://swa.it/edrn/ps' />
        <bmdb:DecisionRule>A sample decision rule</bmdb:DecisionRule>
        <bmdb:SensitivityDatas>
            <rdf:Bag>
                <rdf:li rdf:resource='http://tumor.jpl.nasa.gov/bmdb/biomarkers/organs/19/40/sensitivity-data-0' />
                <rdf:li rdf:resource='http://tumor.jpl.nasa.gov/bmdb/biomarkers/organs/19/40/sensitivity-data-1' />
            </rdf:Bag>
        </bmdb:SensitivityDatas>
    </bmdb:BiomarkerOrganStudyData>
    <bmdb:SensitivityData rdf:about='http://tumor.jpl.nasa.gov/bmdb/biomarkers/organs/19/40/sensitivity-data-0'>
        <bmdb:SensSpecDetail>The first one</bmdb:SensSpecDetail>
        <bmdb:Sensitivity>1.0</bmdb:Sensitivity>
        <bmdb:Specificity>2.0</bmdb:Specificity>
        <bmdb:Prevalence>3.0</bmdb:Prevalence>
        <bmdb:NPV>4.0</bmdb:NPV>
        <bmdb:PPV>5.0</bmdb:PPV>
        <bmdb:SpecificAssayType>Sample specific assay type details</bmdb:SpecificAssayType>
    </bmdb:SensitivityData>
    <bmdb:SensitivityData rdf:about='http://tumor.jpl.nasa.gov/bmdb/biomarkers/organs/19/40/sensitivity-data-1'>
        <bmdb:SensSpecDetail>The second two</bmdb:SensSpecDetail>
        <bmdb:Sensitivity>6.0</bmdb:Sensitivity>
        <bmdb:Specificity>7.0</bmdb:Specificity>
        <bmdb:Prevalence>8.0</bmdb:Prevalence>
        <bmdb:NPV>9.0</bmdb:NPV>
        <bmdb:PPV>10.0</bmdb:PPV>
        <bmdb:SpecificAssayType>Sample specific assay type details</bmdb:SpecificAssayType>
    </bmdb:SensitivityData>
</rdf:RDF>'''

_biomarkerB = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bmdb="http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#">
    <bmdb:Biomarker rdf:about='http://edrn/bmdb/b1'>
        <bmdb:Title>Bile 1</bmdb:Title>
        <bmdb:ShortName>B1</bmdb:ShortName>
        <bmdb:HgncName> BB </bmdb:HgncName>
        <bmdb:BiomarkerID>http://edrn/bmdb/b1</bmdb:BiomarkerID>
        <bmdb:URN>urn:edrn:bmdb:bm2</bmdb:URN>
        <bmdb:IsPanel>0</bmdb:IsPanel>
        <bmdb:Description>A brown bio-marker.</bmdb:Description>
        <bmdb:QAState>Under Review</bmdb:QAState>
        <bmdb:Phase>3</bmdb:Phase>
        <bmdb:Security>Public</bmdb:Security>
        <bmdb:Alias>Ooze</bmdb:Alias>
        <bmdb:Type>Colloidal</bmdb:Type>
        <bmdb:AccessGrantedTo rdf:resource='ldap://edrn/groups/g1' />
        <bmdb:indicatorForOrgan rdf:resource='http://edrn/bmdb/a1/o1' />
        <bmdb:hasBiomarkerStudyDatas>
            <rdf:Bag>
                <rdf:li>
                    <bmdb:BiomarkerStudyData rdf:about='http://edrn/bmdb/a1/s1'>
                        <bmdb:referencesStudy rdf:resource='http://swa.it/edrn/ps' />
                        <bmdb:DecisionRule>A sample decision rule</bmdb:DecisionRule>
                    </bmdb:BiomarkerStudyData>
                </rdf:li>
            </rdf:Bag>
        </bmdb:hasBiomarkerStudyDatas>
        <bmdb:referencedInPublication rdf:resource='http://is.gd/pVKq' />
        <bmdb:referencesResource rdf:resource='http://yahoo.com/' />
    </bmdb:Biomarker>
</rdf:RDF>'''

_biomarkerOrganB = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bmdb="http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#">
    <bmdb:BiomarkerOrganData rdf:about="http://edrn/bmdb/b1/o1">
        <bmdb:URN>http://edrn/bmdb/b1/o1</bmdb:URN>
        <bmdb:Biomarker rdf:resource='http://edrn/bmdb/b1'/>
        <bmdb:Description>Action on the anus is amazing.</bmdb:Description>
        <bmdb:PerformanceComment>The biomarker failed to perform as expected.</bmdb:PerformanceComment>
        <bmdb:Organ>Anus</bmdb:Organ>
        <bmdb:Phase>2</bmdb:Phase>
        <bmdb:QAState>Under Review</bmdb:QAState>
        <bmdb:certification rdf:resource='http://www.fda.gov/regulatoryinformation/guidances/ucm125335.htm'/>
        <bmdb:AccessGrantedTo rdf:resource='ldap://edrn/groups/g1'/>
        <bmdb:hasBiomarkerOrganStudyDatas/>
    </bmdb:BiomarkerOrganData>
</rdf:RDF>'''

_biomarkerC = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bmdb="http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#">
    <bmdb:Biomarker rdf:about='http://edrn/bmdb/msb'>
        <bmdb:Title>My Single Biomarker</bmdb:Title>
        <bmdb:HgncName></bmdb:HgncName>
        <bmdb:ShortName>MSB</bmdb:ShortName>
        <bmdb:BiomarkerID>http://edrn/bmdb/msb</bmdb:BiomarkerID>
        <bmdb:URN>urn:edrn:bmdb:msb</bmdb:URN>
        <bmdb:IsPanel>0</bmdb:IsPanel>
        <bmdb:Description>A cloyingly sweet biomarker.</bmdb:Description>
        <bmdb:QAState>Accepted</bmdb:QAState>
        <bmdb:Phase>3</bmdb:Phase>
        <bmdb:Security>Public</bmdb:Security>
        <bmdb:Type>Colloidal</bmdb:Type>
        <bmdb:memberOfPanel rdf:resource='http://edrn/bmdb/mbp'/>
        <bmdb:AccessGrantedTo rdf:resource='ldap://edrn/groups/g1' />
    </bmdb:Biomarker>
    <bmdb:Biomarker rdf:about='http://edrn/bmdb/mbp'>
        <bmdb:Title>My Biomarker P[anel]</bmdb:Title>
        <bmdb:ShortName>MBP</bmdb:ShortName>
        <bmdb:BiomarkerID>http://edrn/bmdb/mbp</bmdb:BiomarkerID>
        <bmdb:URN>urn:edrn:bmdb:mbp</bmdb:URN>
        <bmdb:IsPanel>1</bmdb:IsPanel>
        <bmdb:Description>A wood panel, very retro-chic.</bmdb:Description>
        <bmdb:QAState>Accepted</bmdb:QAState>
        <bmdb:Phase>4</bmdb:Phase>
        <bmdb:Security>Public</bmdb:Security>
        <bmdb:Type>Proteinesque</bmdb:Type>
        <bmdb:hasBiomarker rdf:resource='http://edrn/bmdb/msb' />
    </bmdb:Biomarker>
</rdf:RDF>'''

_biomarkerOrganC = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"/>'''

_badStudyBiomarker = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bmdb="http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#">
    <bmdb:Biomarker rdf:about='http://edrn/bmdb/bad-study'>
        <bmdb:Title>Bad Study</bmdb:Title>
        <bmdb:ShortName>BS</bmdb:ShortName>
        <bmdb:BiomarkerID>http://edrn/bmdb/bad-study</bmdb:BiomarkerID>
        <bmdb:URN>urn:edrn:bmdb:bs</bmdb:URN>
        <bmdb:IsPanel>0</bmdb:IsPanel>
        <bmdb:QAState>Accepted</bmdb:QAState>
        <bmdb:indicatorForOrgan rdf:resource='http://edrn/bmdb/bad-study/bad-organ' />
    </bmdb:Biomarker>
</rdf:RDF>'''

_badStudyBiomarkerOrgan = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bmdb="http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#">
  <bmdb:BiomarkerOrganData rdf:about="http://edrn/bmdb/bad-study/bad-organ">
    <bmdb:URN>urn:edrn:bmdb:biomarkerorgan:120</bmdb:URN>
    <bmdb:Biomarker rdf:resource="http://edrn/bmdb/bad-study"/>
    <bmdb:Description></bmdb:Description>
    <bmdb:PerformanceComment>testing everything in bmdb.....
</bmdb:PerformanceComment>
    <bmdb:Organ>Rectum</bmdb:Organ>
    <bmdb:Phase>Three</bmdb:Phase>
    <bmdb:QAState>Under Review</bmdb:QAState>
    <bmdb:hasBiomarkerOrganStudyDatas>
      <rdf:Bag>
        <rdf:li rdf:resource="http://edrn/bmdb/bad-study/bad-organ#bad-protocol"/>
      </rdf:Bag>
    </bmdb:hasBiomarkerOrganStudyDatas>
  </bmdb:BiomarkerOrganData>
  <bmdb:BiomarkerOrganStudyData rdf:about="http://edrn/bmdb/bad-study/bad-organ#bad-protocol">
    <bmdb:referencesStudy rdf:resource="http://edrn.nci.nih.gov/data/protocols/non-existent-protocol"/>
    <bmdb:DecisionRule></bmdb:DecisionRule>
  </bmdb:BiomarkerOrganStudyData>
</rdf:RDF>'''


_privateBiomarker = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bmdb="http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#">
    <bmdb:Biomarker rdf:about='http://edrn/bmdb/secret1'>
        <bmdb:Title>Secret 1</bmdb:Title>
        <bmdb:ShortName>S1</bmdb:ShortName>
        <bmdb:BiomarkerID>http://edrn/bmdb/secret1</bmdb:BiomarkerID>
        <bmdb:URN>urn:edrn:bmdb:secret1</bmdb:URN>
        <bmdb:IsPanel>0</bmdb:IsPanel>
        <bmdb:Description>A secret biomarker.</bmdb:Description>
        <bmdb:QAState>Private</bmdb:QAState>
        <bmdb:Phase>3</bmdb:Phase>
        <bmdb:Security>Public</bmdb:Security>
        <bmdb:Alias>Hush-hush</bmdb:Alias>
        <bmdb:Type>Colloidal</bmdb:Type>
        <bmdb:AccessGrantedTo rdf:resource='ldap://edrn/groups/g1' />
        <bmdb:indicatorForOrgan rdf:resource='http://edrn/bmdb/secret1/secretOrgan1' />
    </bmdb:Biomarker>
</rdf:RDF>'''

_privateBiomarkerOrgan = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bmdb="http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#">
    <bmdb:BiomarkerOrganData rdf:about="http://edrn/bmdb/secret1/secretOrgan1">
        <bmdb:URN>http://edrn/bmdb/secret1/secretOran1</bmdb:URN>
        <bmdb:Biomarker rdf:resource='http://edrn/bmdb/secret1'/>
        <bmdb:Description>Shhh, it's secret!</bmdb:Description>
        <bmdb:PerformanceComment>The biomarker's performance is secret.</bmdb:PerformanceComment>
        <bmdb:Organ>Secret</bmdb:Organ>
        <bmdb:Phase>2</bmdb:Phase>
        <bmdb:QAState>Private</bmdb:QAState>
        <bmdb:AccessGrantedTo rdf:resource='ldap://edrn/groups/g1'/>
        <bmdb:hasBiomarkerOrganStudyDatas/>
    </bmdb:BiomarkerOrganData>
</rdf:RDF>'''


# BiomarkerIngestException: Study "http://edrn.nci.nih.gov/data/protocols/" not found for biomarker body system "'http://tumor.jpl.nasa.gov/bmdb/biomarkers/organs/100/120'"

def registerLocalTestData():
    ekeKnowledgeBase.registerLocalTestData()
    ekePublicationsBase.registerLocalTestData()
    ekeStudyBase.registerLocalTestData()
    ekeECASBase.registerLocalTestData()
    ekeKnowledgeBase.registerTestData('/biomarkers/a', _biomarkerA)
    ekeKnowledgeBase.registerTestData('/biomarkerorgans/a', _biomarkerOrganA)
    ekeKnowledgeBase.registerTestData('/biomarkers/b', _biomarkerB)
    ekeKnowledgeBase.registerTestData('/biomarkerorgans/b', _biomarkerOrganB)
    ekeKnowledgeBase.registerTestData('/biomarkers/c', _biomarkerC)
    ekeKnowledgeBase.registerTestData('/biomarkerorgans/c', _biomarkerOrganC)
    ekeKnowledgeBase.registerTestData('/biomarkers/bad-study', _badStudyBiomarker)
    ekeKnowledgeBase.registerTestData('/biomarkerorgans/bad-study', _badStudyBiomarkerOrgan)
    ekeKnowledgeBase.registerTestData('/biomarkers/private', _privateBiomarker)
    ekeKnowledgeBase.registerTestData('/biomarkerorgans/private', _privateBiomarkerOrgan)

