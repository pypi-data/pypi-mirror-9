#!/usr/bin/python

import time,csv,re,sys
import numpy as np
from DatabaseTools import populate_gene_table
from htsint.database import  get_file_sizes, db_connect

session,engine = db_connect()
timeStart = time.time()
idmapCount,geneInfoCount = get_file_sizes()

#timeStr,addedStr = populate_gene_table(geneInfoCount,session,engine)
#push_out(timeStr)
#push_out(addedStr)


sys.exit()

uniprotIdMap = uniprot_mapper(session)

uniprotQuery = session.query(Uniprot).all()#filter_by(uniprot_id='P07663').first()
#self.assertEqual(uniprotQuery.uniprot_entry,"PER_DROME")
#geneQuery = self.session.query(Gene).filter_by(id=uniprotQuery.gene_id).first(
#elf.assertEqual(geneQuery.ncbi_id,'31251')

for uq in uniprotQuery:
    print 'id',uq.id
    print 'ac',uq.uniprot_ac


print len(uniprotQuery)

#print uniprotIdMap.keys()
sys.exit()


annotationFile = get_annotation_file()
annotationFid = open(annotationFile,'rU')
#gene2goFile = get_gene2go_file()
#gene2goFid = open(gene2goFile,'rU')
annotationCount = 0


print("...loading mappers")

noTaxon = 0
total = 0

print("...getting annotations from gene_association (uniprot)")
for record in annotationFid:
    record = record[:-1].split("\t")

    ## check that it is a uniprot entry 
    if record[0][0] == "!":
        continue
    if record[0] != 'UniProtKB':
        continue

    uniprotId = record[1]
    dbObjectSymbol = record[2]
    goId = record[4]
    pubmedRefs = record[5]
    evidenceCode = record[6]
    aspect = record[8]
    goTermName = record[11]
    taxon = re.sub("taxon:","",record[12])
    date = record[13]
    assignedBy = record[14]

    if re.search("\|",taxon):
        continue

    if taxon == None:
        noTaxon += 1

    total += 1

    print 'goid', goId
    print 'evidence code', evidenceCode
    print 'pubmedrefs', pubmedRefs
    print 'uniprotid', uniprotId
    print 'taxon', taxon

    if total > 25:
        sys.exit()


print 'annotation fid'
print 'total', total
print 'no taxon', noTaxon


#termIdMap = goterm_mapper(session)
#taxaIdMap = taxa_mapper(session)
#uniprotIdMap = uniprot_mapper(session)
#print("...populating rows")





"""
print("...getting gene info")
#geneIdMap = gene_mapper(session)
timeStart = time.time()
toAdd = []
totalRecords = 0
idmappingFile = "/usr/local/share/htsint/idmapping.dat.db"
idmappingFid = open(idmappingFile,'rb')
reader = csv.reader(idmappingFid,delimiter="\t")

print("...populating rows")
bad = 0
current = None



uniprotKbEntry,ncbiId,refseq,ncbiTaxaId = None,None,None,None

noTaxa = 0
noNcbi = 0
total = 0
noTaxaYesNcbi = 0

for record in reader:

    if len(record) != 3:
        continue

    uniprotKbAc = record[0]

    if current == None:
        current = uniprotKbAc

    if record[1] == 'NCBI_TaxID':
        ncbiTaxaId = record[2]
    if record[1] == 'GeneID':
        ncbiId = record[2]
    if record[1] == 'UniProtKB-ID':
        uniprotKbEntry = record[2]
    if record[1] == 'RefSeq':
        refseq = record[2]

    ## check to see if entry is finished
    if current != uniprotKbAc:
        current = uniprotKbAc
        total += 1

        if ncbiTaxaId == None:
            noTaxa += 1
        if ncbiId == None:
            noNcbi += 1
        if ncbiId and ncbiTaxaId == None:
            noTaxaYesNcbi += 1





        #if None in [uniprotKbEntry,ncbiId,refseq,ncbiTaxaId]:
        #    print "\nuniprotid:%s\nncbiid%s\nrefseq:%s\ntaxaid:%s"%(uniprotKbEntry,ncbiId,refseq,ncbiTaxaId)
        #else:
        #    print "...", uniprotKbEntry
        #sys.exit()

        uniprotKbEntry,ncbiId,refseq,ncbiTaxaId = None,None,None,None


print "......"
print "total%s"%total
print "noTaxa%s"%noTaxa
print "noNcbi%s"%noNcbi
print "noTaxaYesNcbi%s"%noTaxaYesNcbi
"""
