#!/usr/bin/python
#Last-modified: 20 Mar 2015 04:14:12 PM

#         Module/Scripts Description
# 
# Copyright (c) 2008 Yunfei Wang <yfwang0405@gmail.com>
# 
# This code is free software; you can redistribute it and/or modify it
# under the terms of the BSD License (see the file COPYING included with
# the distribution).
# 
# @status:  experimental
# @version: 1.0.0
# @author:  Yunfei Wang
# @contact: yfwang0405@gmail.com

# ------------------------------------
# __import__('pkg_resources').declare_namespace(__name__)
# ------------------------------------
__all__ = ['Bed3','Bed','Peak','Wiggle','BedGraph','GeneBed','Seq','DNA','RNA','Fasta','Fastq','BedList','BedMap','TwoBitFile','BigWigFile','FastaFile','StringFile','mFile','IO','DB','Utils','Pipeline']

# ------------------------------------
# python modules
# ------------------------------------

# built-in libraries
import os
import re
import sys
import copy
import gzip
import time
import types
import random
import cPickle
import cStringIO
import threading
from array import array
from string import maketrans
from bisect import bisect,bisect_left,insort
from itertools import chain
from subprocess import Popen, PIPE, call

# Numeric calculation
import numpy

# SAM/BAM, Fasta and Tabix file manipulation
import pysam

# RNA structure prediction using Vienna RNA package.
#import wRNA

# Wiggle manipulation using Jim Kent's c library.
import wWigIO

# TwoBit file manipulation using Jim Kent's c library.
import wTwoBitIO

# ------------------------------------
# constants
# ------------------------------------

# For debug
debug = False

# $HOME
USERHOME=os.path.expanduser('~')

# Maximum chromosome size bound
MAXCHROMSIZE = 1000000000

# Type of 4 bytes long
LONG = array('L', [0]).itemsize == 4 and 'L' or 'I'

# regular expression for searching in regions like "chr1:100-200+"
regp = re.compile("(\w+):(\d+)-(\d+)([+-\.])")


##############################################################################################
# BIN constants
# This part is from BEDTools. There are something wrong here:
# The code uses a 7 level Bin system but annotation provides a 6 level Bin ragnes.
# It is said the longest chromosome is longer than 512M. 7 level Bin System might be better.
##############################################################################################
# bins
_binLevels = 7

# bins range in size from 16kb to 512Mb 
# Bin  0          spans 512Mbp,   # Level 1
# Bins 1-8        span 64Mbp,     # Level 2
# Bins 9-72       span 8Mbp,      # Level 3
# Bins 73-584     span 1Mbp       # Level 4
# Bins 585-4680   span 128Kbp     # Level 5
# Bins 4681-37449 span 16Kbp      # Level 6
_binOffsetsExtended = [32678+4096+512+64+8+1, 4096+512+64+8+1, 512+64+8+1, 64+8+1, 8+1, 1, 0]
_binFirstShift = 14;      # How much to shift to get to finest bin. 
_binNextShift  = 3;       # How much to shift to get to next larger bin.
##############################################################################################


##############################################################################################
# commonly used genome sizes
##############################################################################################
genome={}
genome['K12']={"K12":4639675}
genome['CFT073']={'CFT073':5231428}
genome['ce6']={'chrI':15072421,'chrII':15279323,'chrIII':13783681,'chrIV':17493785,'chrM':13794,'chrV':20919568,'chrX':17718854}
genome['sc']={'chr01':230218,'chr02':813184,'chr03':316620,'chr04':1531933,'chr05':576874,'chr06':270161,'chr07':1090940,'chr08':562643,'chr09':439888,'chr10':745751,'chr11':666816,'chr12':1078177,'chr13':924431,'chr14':784333,'chr15':1091291,'chr16':948066,'chrM':85779}
genome['hg19']={'chr1':249250621,'chr2':243199373,'chr3':198022430,'chr4':191154276,'chr5':180915260,'chr6':171115067,'chr7':159138663,'chr8':146364022,'chr9':141213431,'chr10':135534747,'chr11':135006516,'chr12':133851895,'chr13':115169878,'chr14':107349540,'chr15':102531392,'chr16':90354753,'chr17':81195210,'chr18':78077248,'chr20':63025520,'chr19':59128983,'chr22':51304566,'chr21':48129895,'chrX':155270560,'chrY':59373566,'chrM':16571}
genome['mm10']={'chrY': 91744698, 'chrX': 171031299, 'chr13': 120421639, 'chr12': 120129022, 'chr11': 122082543, 'chr10': 130694993, 'chr17': 94987271, 'chr16': 98207768, 'chr15': 104043685, 'chr14': 124902244, 'chr19': 61431566, 'chr18': 90702639, 'chrM': 16299, 'chr7': 145441459, 'chr6': 149736546, 'chr5': 151834684, 'chr4': 156508116, 'chr3': 160039680, 'chr2': 182113224, 'chr1': 195471971, 'chr9': 124595110, 'chr8': 129401213}
genome['mm9']={'chrY': '15902555', 'chrX': '166650296', 'chr13': '120284312', 'chr12': '121257530', 'chr11': '121843856', 'chr10': '129993255', 'chr17': '95272651', 'chr16': '98319150', 'chr15': '103494974', 'chr14': '125194864', 'chr19': '61342430', 'chr18': '90772031', 'chrM': '16299', 'chr7': '152524553', 'chr6': '149517037', 'chr5': '152537259', 'chr4': '155630120', 'chr3': '159599783', 'chr2': '181748087', 'chr1': '197195432', 'chr9': '124076172', 'chr8': '131738871'}
##############################################################################################

# ------------------------------------
# Misc functions
# ------------------------------------

# ------------------------------------
# Classes
# ------------------------------------

#########################################################################
# Classes for various biological data format
#########################################################################

class Bed3(object):
    '''
    Simplest Bed format that has only three required fields.
    Example:
        # Create Bed3 instances
            > tbed = Bed3(["chr1", 100, 200])
            > print tbed
            chr1\t100\t200
            > tbed2 = Bed3("chr1\t100\t200\t0.5")
            > print tbed2
            chr1\t100\t200
            > print tbed2.allFields()
            chr1\t100\t200\t0.5
        # Extend Bed3
            > print tbed2.extend(50, 50)
            chr1\t50\t250
            > print tbed2.extend(-20,-20)
            chr1\t120\t180
        # Get sequence from fasta files
            > print Bed3("chr1\t50\t150").getSeq("test/test.fa")
            CAGAAAGCCTTACTGTTGCATTTTGTTAGTTTCTGTTTTCCTCAACAACTAATATGAAGTTCTTTAGCATAACAAGGATCTGCCTTTGTAAAAGAAaaag
    '''
    def __init__(self, x, description=None):
        ''' Initiation. '''
        if isinstance(x, basestring):
            x = x.rstrip().split("\t")
        if isinstance(x[-1], basestring):
            x[-1].rstrip()
        self.chrom = x[0].strip()
        self.start = int(x[1])
        self.stop  = int(x[2])
        self.otherfields = x[3:]
        self.description = description
    def __str__(self):
        ''' Return a string of Bed. '''
        return "{0}\t{1}\t{2}".format(self.chrom, self.start, self.stop)
    def allFields(self):
        ''' Return a string of all the fields in Bed. '''
        return str(self)+"\t"+ "\t".join([str(i) for i in self.otherfields])
    def length(self):
        ''' Length of the Bed. '''
        return self.stop-self.start
    def overlapLength(self, B):
        ''' Overlap length between two Bed. Negative if no overlap. '''
        if B is None or self.chrom != B.chrom:
            return -MAXCHROMSIZE
        return  min(self.stop, B.stop) - max(self.start, B.start)
    def distance(self, B):
        ''' Distance between two Bed. '''
        return -self.overlapLength(B)
    def __add__(self, B):
        '''
        Merge two Beds by coordinates. Return None if no overlap.
        Example: 
            > tbed1 = Bed3(["chr1", 100, 200])
            > tbed2 = Bed3(["chr1", 150, 250])
            > tbed3 = tbed1 + tbed2
            > if tbed3 != None: print tbed3
            chr1\t100\t250
        '''
        if B is None:
            return copy.deepcopy(self)
        if isinstance(B,basestring):
            return str(self)+B
        if issubclass(type(B),Bed3): # tested by user(self.overlapLength(B)>=0):
            tbed = copy.deepcopy(self)
            tbed.start = min(self.start, B.start)
            tbed.stop  = max(self.stop, B.stop)
            return tbed
        raise TypeError("ERROR: object type is not accepted for adding.")
    def __cmp__(self,B):
        ''' Compare two Bed by chrom, start and stop in order. '''
        if isinstance(B,Bed3):
            return cmp(self.chrom,B.chrom) or cmp(self.start,B.start) or cmp(self.stop,B.stop)
        print >>sys.stderr, "# ERROR! Compared with Non-Bed3 objects."
        return 
    def __len__(self):
        ''' Length of Bed. '''
        return self.stop - self.start
    def extend(self,up = 0,down = 0, genome = None):
        '''
        Extend Bed in both direction. Trim Bed if negative values are provided.
        Note: This function will call testBoundary after extension. Check testBoundary function for details.
        Example:
            > tbed = Bed3(["chr1", 100, 200])
            > print tbed.extend(50, 50)    # extend 50bp on both sides
            chr1\t50\t250 
            > print tbed.extend(-50, -30)  # trim 50 and 30 bp on both sides
            chr1\t150\t170
            > print tbed.extend(200, 50)   # set start to 0 if exceed the boundary
            Warning: start is smaller than 0. Set start to 0. 
            chr1\t0\t250
            > print tbed.extend(-100, -50) # exchage start and stop if start > stop
            Warning: start is larger than stop. Exchange start and stop.
            chr1\t150\t200
            > print tbed.extend(0, 100000000000, genome = 'hg19.sizes')
            Warning: stop is larger than chromosome size. Set stop to maximum chromosome size.
            chr1\t150\t249250621
        '''
        tbed = copy.deepcopy(self)
        tbed.start = self.start-up
        tbed.stop  = self.stop+down
        tbed.testBoundary(genome)
        return tbed
    def getBIN(self):
        '''Get the genome BIN.'''
        start=self.start>>_binFirstShift
        stop=(self.stop-1)>>_binFirstShift
        for i in range(_binLevels):
            if start==stop:
                return _binOffsetsExtended[i] + start
            else:
                start >>= _binNextShift
                stop  >>= _binNextShift
        print >>sys.stderr,"Error! Bed range is out of 512M."
        return None
    def swap(self):
        ''' swap the coordinates. '''
        self.start, self.stop = self.stop, self.start
    def testBoundary(self,genomesize=None):
        '''
        Test (1) if start and stop are positive values and start < stop.
             (2) if the Bed boundaries are exceed the limit.
        Example:
            > print Bed3(["chr1", -100, 200])).testBoundary()  # set start to 0 if exceed the boundary
            Warning: start is smaller than 0. Set start to 0. 
            chr1\t0\t200
            > print Bed3(["chr1", 300, 200])).testBoundary()   # exchage start and stop if start > stop
            Warning: start is larger than stop. Exchange start and stop.
            chr1\t200\t300
            > print Bed3(["chr1", 100, 2000000000]), "./hg19.sizes").testBoundary()   # exceed the max chrom size
            Warning: stop is larger than chromosome size. Set stop to maximum chromosome size.
            chr1\t100\t249250621
        '''
        if self.start < 0 :
            print >> sys.stderr, 'WARNING: start {0} is smaller than 0 for {1}. Set start to 0.'.format(self.start,self.id)
            self.start = 0
        if self.start > self.stop:
            print >> sys.stderr, 'WARNING: start {0} is smaller than stop {1} for {2}. Exchange start and stop.'.format(self.start,self.stop,self.id)
            self.start, self.stop = self.stop, self.start
        if genomesize:
            chroms=Utils.genomeSize(genomesize)
            if self.stop > chroms[self.chrom]:
                print >>sys.stderr, "WARNING:: stop {0} is larger than chromosome size for {1}. Set stop to chromosome size.".format(self.stop,self.id)
                self.stop = chroms[self.chrom]
    def fetchDB(self,db):
        '''
        Fetch elements from DB.
        Parameters:
            db: DB object
                ngslib.DB
        Returns:
            A generator if fetching elements in db.
            An object if fetching sequence in db.
        '''
        return db.fetch(self.chrom,self.start,self.stop)
    def pileupDB(self,db,**kwargs):
        '''
        Pileup elements in DB.
        Parameters:
            db: DB ojbect
                ngslib.db
            forcestrand: bool
                pileup elements based on strand information.
            binsize: int
                Rebin the depth in binsize. The region length should be N times of binsize, otherwise the last one will be ommited.
            method: string
                options: min, max, mean, median
        Returns:
            depth: numpy.array
                depth of each bin
        '''
        return db.pileup(self.chrom,self.start,self.stop,**kwargs)

class Wiggle(Bed3):
    '''
    This class is for UCSC Wiggle format. 
    Note: Wiggle coordinates are 1-based. The coordinates are stored in 0-based format.
    Example:
        Wiggle format: chr1\t51\t100\t12 will stored as chr1\t50\t100\12 in Wiggle class.
    '''
    def __init__(self,x, description=None):
        ''' Initiation. '''
        if isinstance(x, basestring):
            x = x.rstrip().split("\t")
        elif isinstance(x[-1], basestring):
            x[-1].rstrip()
        self.chrom = x[0].strip()
        self.start = int(x[1])-1
        self.stop  = int(x[2])
        self.score = float(x[3])
        self.otherfields = x[4:]
        self.description = description
    def __str__(self):
        ''' Return a string of Wiggle. '''
        return "{0}\t{1}\t{2}\t{3}".format(self.chrom, self.start + 1, self.stop, round(self.score,3))
    def span(self):
        ''' Span of Wiggle. '''
        return self.length()
    def bedstr(self):
        ''' Return a string of Wiggle with Bed (0-based) coordinates. '''
        return "{0}\t{1}\t{2}\t{3}".format(self.chrom, self.start, self.stop, self.score)

class BedGraph(Bed3):
    '''
    This class is for UCSC BedGraph format.
    BedGraph format is very similar to Wiggle format except that the coordinates are 0-based.
    Example:
        chr19 49302000 49302300 -1.0
    '''
    def __init__(self,x, description=None):
        ''' Initiation. '''
        if isinstance(x, basestring):
            x = x.rstrip().split("\t")
        elif isinstance(x[-1], basestring):
            x[-1].rstrip()
        self.chrom = x[0].strip()
        self.start = int(x[1])
        self.stop  = int(x[2])
        self.score = float(x[3])
        self.otherfields = x[4:]
        self.description = description
    def __str__(self):
        ''' Return a string of BedGraph. '''
        return "{0}\t{1}\t{2}\t{3}".format(self.chrom, self.start, self.stop, round(self.score,3))
        
class Peak(Bed3):
    '''
    This class is for ChIP-Seq Peaks. 
    It takes peak calling software, MACS (Zhang, Liu et al. 2008), output format as a template.
    Example: 
        (1) test_peaks.xls        
            chr\tstart\tend\tlength\tsummit\ttags\t-10*log10(pvalue)\tfold_enrichment\tFDR(%)
            chr1\t3661094\t3661241\t148\t91\t8\t51.89\t8.20\t1.51
        (2) Read test_peaks.xls
            for tpeak in IO.BioReader("test_peaks.xls",ftype="macs", mask="#", skip = 1)
                print tpeak
    Note: (1) MACS output file is 1-based and will be stored in 0-based in Peak class.
          (2) Peak name is set to "" by default. User can assign a name like this: mypeak.id = "Peak_01"
    '''
    def __init__(self,x, description=None):
        ''' Initiation. '''
        if isinstance(x, basestring):
            x = x.rstrip().split("\t")
        elif isinstance(x[-1], basestring):
            x[-1].rstrip()
        self.chrom = x[0]
        self.start = int(x[1]) - 1
        self.stop = int(x[2])
        self.summit = int(x[4])
        self.tags = int(x[5])
        self.pvalue = float(x[6])
        self.foldchange = float(x[7])
        self.fdr = float(x[8])
        self.id = ""
        self.otherfields = x[9:]
        self.description = description
    def __str__(self):
        ''' Return a string of Peak. '''
        return "\t".join(["{"+str(i)+"}" for i in range(9)]).format(self.chrom, self.start+1, self.stop, self.length(), self.summit, self.tags, self.pvalue, self.foldchange, self.fdr)
    def bedstr(self):
        ''' Return a string of Peak with Bed coordinates. '''
        return "\t".join(["{"+str(i)+"}" for i in range(8)]).format(self.chrom, self.start, self.stop, self.length(), self.summit, self.tags, self.pvalue, self.foldchange, self.fdr)

class Bed(Bed3):
    ''' 
    This class is used to process Bed6 format files. It has at least three items just like Bed3. The 4-6th fields are optional and will be set to default values if not provided.
    Example:
        > print Bed(["chr1", 100, 200, , , "+"])
        chr1\t100\t200\tNA\t0.00\t+
        > print Bed(["chr1", 100, 200, Peak])
        chr1\t100\t200\tPeak\t0.00\t.
    If the files contains more than 6 fields, the rest will be stored in Bed.otherfields. This will increase the compatibility of Bed class.
    Example:
        > tbed = Bed(["chr1", 100, 200, peak01, 25, "+", 150, 0.001])
        > print tbed.allFields()
        chr1\t100\t200\tpeak01\t25\t+\t150\t0.001
    '''
    def __init__(self,x, description=None):
        ''' Initiate the bed from either line or list. '''
        if isinstance(x,basestring):
            x=x.rstrip().split("\t")
        elif isinstance(x[-1],basestring):
            x[-1].rstrip()
        self.chrom=x[0].strip()
        self.start=int(x[1])
        self.stop=int(x[2])
        try:
            self.id=x[3]
        except:
            self.id="NA"
        try:
            if Utils.is_float(x[4]):
                self.score=float(x[4])
            else:
                self.score=0
        except:
            self.score=0
        try:
            if x[5] in [".","+","-"]:
                self.strand=x[5]
            else:
                self.strand="."
        except:
            self.strand="."
        try:
            self.otherfields=x[6:]
        except:
            self.otherfields=[]
        self.description = description
    def __str__(self):
        '''Return the bed in basestring format.'''
        string=self.chrom+"\t"+str(self.start)+"\t"+str(self.stop)+"\t"+str(self.id)+"\t"+("%-5.2f\t"% self.score)+self.strand        
        return string
    def __add__(self, B):
        ''' Merge two Beds if they are overlapped. Strand information is not considered here. '''
        if B is None:
            return copy.deepcopy(self)
        if isinstance(B,basestring):
            return str(self)+B
        if issubclass(type(B),Bed): # Always test overlap length before adding
            tbed = copy.deepcopy(self)
            tbed.start = min( tbed.start, B.start)
            tbed.stop  = max(tbed.stop, B.stop)
            tbed.id = tbed.id+"_" + B.id
            tbed.strand = tbed.strand == B.strand and tbed.strand or "."
            tbed.score = (self.score*self.length()+B.score*B.length())/tbed.length()
            return tbed
        raise TypeError, "Adding elements of different types."
    def __cmp__(self,other):
        ''' Compare two Beds. '''
        return cmp(self.chrom,other.chrom) or cmp(self.start,other.start) or cmp(self.stop,other.stop) or cmp(other.strand,self.strand) or cmp(self.score,other.score)#'.'<'-'<'+'
    def rc(self):
        ''' Reverse complementary. '''
        if self.strand=="+":
            self.strand="-"
        elif self.strand=="-":
            self.strand="+"
        return
    def getSeq(self,db,forcestrand=True):
        '''
        This is replaced by fetchDB.
        '''
        return self.fetchDB(db,forcestrand=forcestrand)
    def fetchDB(self,db,**kwargs):
        '''
        Fetch elements from DB.
        Parameters:
            db: DB object
                ngslib.DB
            forcestrand: bool
                set it False if strand is not considered.
        Returns:
            A generator if fetching elements in db.
            An object if fetching sequence in db.
        '''
        return db.fetch(chrom=self.chrom,start=self.start,stop=self.stop,strand=self.strand)
    def pileupDB(self,db,**kwargs):
        '''
        Pileup elements in DB.
        Parameters:
            db: DB ojbect
                ngslib.db
            forcestrand: bool
                pileup elements based on strand information.
        Returns:
            depth: numpy.array
                depth of each position.
        '''
        return db.pileup(self.chrom,self.start,self.stop,strand=self.strand,**kwargs)
    def extend(self,up=0,down=0, genome = None):
        ''' Extend or trim the Bed at both ends. See Bed3.extend() in details. '''
        tid = self.id + ("_up"+str(up) if up!=0 else "")+("_down"+str(down) if down!=0 else "")
        if self.strand == "-":
            up, down = down, up
        tbed = super(self.__class__,self).extend( up, down)
        tbed.id = tid
        return tbed
    def cmpStrand(self,bed):
        '''Test if two Beds have the same strand. '''
        if bed.strand == "." or self.strand==".": return "."
        return "+" if self.strand == bed.strand else "-"
    def getTSS(self):
        '''Get TSS of the Bed.'''
        tbed = copy.deepcopy(self)
        tbed.id += "_TSS"
        if self.strand!="-":
            tbed.stop = tbed.start +1
        else:
            tbed.start = tbed.stop -1
        return tbed
    def annoBed(self,annos,annotype='exon'): # to be updated
        '''Return bed overlapped annotations. '''
        annostr=[]
        if annos:
            for i,item in enumerate(annos):
                olen=self.overlapLength(item)
                if olen>0:
                    annostr.append(annotype+"_"+str(i)+":"+str(olen))
        return len(annostr) and ";".join(annostr) or None

class GeneBed(Bed):
    '''UCSC GenePred format.'''
    def __init__(self,x,description=None):
        '''Initiate from GeneBed lines. GeneBed names BioReader are not allowed to be numbers.'''
        if isinstance(x, basestring):
            x = x.rstrip().split('\t')
        try: # sometimes GenePred file has a BIN value in the first column
            self.bin=int(x[0])
            x = x[1:]
        except:
            pass
        self.id=x[0]
        self.chrom=x[1]
        self.strand=x[2]
        self.start=int(x[3])
        self.stop=int(x[4])
        self.txstart=int(x[5])
        self.txstop=int(x[6])
        self.exoncount=int(x[7])
        if isinstance(x[8],basestring):
            self.exonstarts=[int(p) for p in x[8].split(",")[0:-1]]
            self.exonstops=[int(p) for p in x[9].split(",")[0:-1]]
        else:
            self.exonstarts=[int(p) for p in x[8]]
            self.exonstops=[int(p) for p in x[9]]                    
        try:
            self.otherfields = x[10:]
        except:
            self.otherfields = []
        self.score = 0.
        self.proteinid = ""
        if len(self.otherfields)>0:
            try:
                self.score=float(self.otherfields[0])
            except:
                pass
            if len(self.otherfields)>1:
                try:
                    self.proteinid = self.otherfields[1]
                except:
                    pass
        self.description=description
    def __str__(self):
        '''Return GeneBed line.'''
        return "%s\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%s,\t%s,\t%.2f\t%s" % (self.id,self.chrom,self.strand,self.start,self.stop,self.txstart,self.txstop,self.exoncount,",".join([str(p) for p in self.exonstarts]),",".join([str(p) for p in self.exonstops]),self.score,self.proteinid)
    def toBed(self):
        '''Transform to Bed format.'''
        return Bed([self.chrom,self.start,self.stop,self.id,self.score,self.strand])
    def getTSS(self):
        ''' Get TSS as a Bed object. '''
        tbed = self.toBed().getTSS()
        return tbed
    def extend(self,up,down,genome):
        ''' Extend up/downstream. '''
        tgene = copy.deepcopy(self)
        pass # code here
        return tgene
    def getExon(self,i):
        ''' Get the Bed format of ith exon. '''
        if 0<i<=self.exoncount:
            p = self.exoncount-i if self.strand=="-" else i - 1
            return Bed([self.chrom,self.exonstarts[p],self.exonstops[p],self.id+":exon_"+str(i),0,self.strand])
        return None            
    def getIntron(self,i):
        '''Get the Bed format of ith intron.'''
        if i>0 and i<self.exoncount:
            p = self.strand=="-" and self.exoncount-i or i
            return Bed([self.chrom,self.exonstops[p-1],self.exonstarts[p],self.id+":intron_"+str(i),0,self.strand])
        return None
    def _getUTRs(self,end='left'):
        '''Get the UTR.'''
        if end=='left': #Get the UTR located in the left end of chromosome
            if self.start==self.txstart: #No UTR
                return None
            utr=copy.deepcopy(self)
            for i in range(self.exoncount):
                if self.txstart<=self.exonstops[i]: #the txStart site locates in (i+1)th exon.
                    break
            utr.exonstarts=utr.exonstarts[0:i+1]
            utr.exonstops=utr.exonstops[0:i+1]
            utr.stop=utr.txstop=utr.exonstops[i]=self.txstart
            utr.txstart=self.start
            utr.exoncount=i+1
            return utr
        else: #get the UTR located in the right end of chromosome
            if self.stop==self.txstop: #No UTR
                return None
            utr=copy.deepcopy(self)
            for i in range(self.exoncount-1,-1,-1):
                if self.txstop>=self.exonstarts[i]:
                    break
            utr.exonstarts=utr.exonstarts[i:self.exoncount]
            utr.exonstops=utr.exonstops[i:self.exoncount]
            utr.start=utr.txstart=utr.exonstarts[0]=self.txstop
            utr.txstop=self.stop
            utr.exoncount=self.exoncount-i
            return utr
    def getUTR5(self):
        '''Get the 5UTR.'''
        if self.strand=='-':
            utr5=self._getUTRs('right')
        else:
            utr5=self._getUTRs('left')
        if utr5:
            utr5.id+=':UTR5'
        return utr5
    def getUTR3(self):
        '''Get the 3'UTR.'''
        if self.strand=='-':
            utr3=self._getUTRs('left')
        else:
            utr3=self._getUTRs('right')
        if utr3:
            utr3.id+=':UTR3'
        return utr3
    def overlapLength(self,B):
        ''' Return the overlap length between genebed and bed. Only exons are considered. '''
        # check if overlapped with the gene region
        overlen = super(GeneBed, self).overlapLength(B)
        if overlen <=0:
            return overlen
        # check each exons if overlapped with the gene region
        overlen = 0
        idx = bisect_left(self.exonstarts, B.start)
        idx = idx >1 and idx - 1 or 0
        while idx < self.exoncount and self.exonstarts[idx] < B.stop:
            start = max(self.exonstarts[idx], B.start)
            stop  = min(self.exonstops[idx], B.stop)
            overlen += (stop > start) and (stop - start) or 0
            idx += 1
        return overlen
    def exons(self):
        '''Iterate all exons.'''
        for i in range(self.exoncount):
            yield self.getExon(i+1)
        return
    def introns(self):
        '''Iterate all introns.'''
        for i in range(1,self.exoncount):
            yield self.getIntron(i)
        return
    def getCDS(self):
        '''Return GeneBed object.'''
        if self.txstart==self.txstop:
            return None
        cds=copy.deepcopy(self)
        for i in range(self.exoncount-1,-1,-1):
            if cds.txstop<=cds.exonstarts[i] or cds.txstart>=cds.exonstops[i]:
                del cds.exonstarts[i]
                del cds.exonstops[i]
            else:
                if cds.txstop<=cds.exonstops[i]:
                    cds.exonstops[i]=cds.txstop
                if cds.txstart>=cds.exonstarts[i]:
                    cds.exonstarts[i]=cds.txstart
        cds.exoncount=len(cds.exonstarts)
        cds.start = cds.txstart
        cds.stop  = cds.txstop
        return cds
    def getcDNALength(self):
        '''Return cdna length.'''
        l=0
        for exon in self.exons():
            l+=exon.length()
        return l
    def fetchDB(self,db,forcestrand=True):
        '''
        Fetch elements from DB.
        Parameters:
            db: DB object
                ngslib.DB
            forcestrand: bool
                True for force strand fetch.
        Returns:
            A generator if fetching elements in db.
            An object if fetching sequence in db.
        '''
        gts = []
        for i in range(self.exoncount):
            gts.append(self.getExon(i+1).fetchDB(db))
        if isinstance(gts[0],Seq):
            return DNA(''.join([gt.seq for gt in gts]))
        return chain(gts) # a chain of generators.
    def pileupDB(self,db,**kwargs):
        '''
        Pileup elements in DB.
        Parameters:
            db: DB ojbect
                ngslib.db
            forcestrand: bool
                pileup elements based on strand information.
        Returns:
            depth: numpy.array
                depth of each position.
        '''
        depth = numpy.zeros(self.getcDNALength())
        start = 0
        for i in range(self.exoncount):
            exon = self.getExon(i+1)
            depth[start:(start+len(exon))] += exon.pileupDB(db,**kwargs)
            start += len(exon)
        return depth        
    def getSeq(self,fn):
        '''Replaced by fetchDB. Get cDNA Sequence.'''
        seq=""
        if isinstance(fn,str):
            fh = fn.endswith('2bit') and TwoBitFile(fn) or FastaFile(fn)
        else:
            fh = fn
        for i in range(self.exoncount):
            seq+=self.getExon(i+1).getSeq(fh)
        if isinstance(fn,str):
            fh.close()
        return seq
    def getWig(self,fn,method='pileup',forcestrand=True):
        '''
        Replaced by fetchDB or pileupDB.
        Get content from BigWigFile. 
        Parameters:
            fn: string, BigWigFile or DB object
                BigWig file name or pre-opened bigwig file handle by either fn=BigWigFile('*.bw') or DB('*.bw','bigwig')               
            method: string
                'pileup': default, pile up all the items in the Bed region
                'fetch' : iteratively fetch items located in the Bed region
            forcestrand: bool
                Only effective for 'pileup' method. Return the strand specific depth
        Returns:
            wigs: array or list
                arrry of depth at each position
                list of wigs
        '''
        wigs=[]
        exons = list(self.exons())
        if self.strand == '-':
            exons.reverse()
        # get items from BigWig file
        if isinstance(fn,str):
            bwf = BigWigFile(fn)
        else:
            bwf = fn
        for exon in exons:
            if method == 'fetch':
                wigs.extend(bwf.fetch(exon.chrom,exon.start,exon.stop))
            elif method == 'pileup':
                wigs.append(bwf.pileup(exon.chrom,exon.start,exon.stop))
            else:
                raise ValueError("ERROR: method '{0}'is not supported!".format(method))
        if isinstance(fn,str):
            bwf.close()
        wigs = numpy.concatenate(wigs)
        if forcestrand and self.strand == "-":
            wigs = wigs[::-1]
        return wigs

class Seq(object):
    ''' genomic or protein sequences. '''
    def __init__(self,seq = ''):
        ''' Initiation. '''
        self.seq = seq
    def formatSeq(self, length = 100):
        ''' Return sequence with fixed length. length = 0 means no length limit in each line. '''
        # Unlimited line length
        if length == 0:
            return self.seq
        # Fixed line length
        l = len(self.seq)
        n = l/length
        if l%length == 0:
            n = n-1
        lstr=""
        for i in xrange(n):
            lstr+=self.seq[(i*length):(i*length+length)]+"\n"
        lstr+=self.seq[(n*length):]
        return lstr
    def __len__(self):
        ''' Length of sequence. '''
        return len(self.seq)
#    def __getslice__(self, _min, _max = None):
#        ''' Get slice of sequence. '''
#        if _max:
#            return self.seq[_min:_max]
#        else:
#            return self.seq[_min:]
    def length(self):
        ''' Length of sequence. '''
        return len(self.seq)
    def __add__(self,B):
        ''' Concatenate two sequences together. '''
        return self.__class__(self.seq + str(B))
    def __radd__(self,B):
        ''' Concatenate two sequences together. '''
        return self.__class__(str(B)+self.seq)
    def __str__(self):
        ''' Return the sequence. '''
        return self.seq
    def __getitem__(self,n):
        ''' Get the nth item. '''
        return self.__class__(self.seq[n])
    def upper(self):
        ''' Uppercase '''
        return self.__class__(self.seq.upper())
    def lower(self):
        ''' Lowercase '''
        return self.__class__(self.seq.lower())

class DNA(Seq):
    ''' DNA sequences. '''
    DNArcTable = maketrans('ACBDGHKMNSRTWVYacbdghkmnsrtwvy',
                           'TGVHCDMKNSYAWBRtgvhcdmknsyawbr')
    mws={'A':313.21,'C':289.19,'G':329.21,'T':304.2,
         'I':314.2,'N':308.95,'R':321.21,'Y':296.69,
         'M':301.2,'K':316.7,'S':309.2,'W':308.71,
         'H':302.2,'B':307.53,'D':315.54,'V':310.53,
         'P':79.98,'X':0,'U':290.17}
    def __init__(self, seq = ''):
        ''' Initiation. '''
        transtab = maketrans('Uu','Tt')
        self.seq = str(seq).translate(transtab)
    def rc(self):
        ''' Return the reverse complementary sequence. '''
        return self.__class__(self.seq.translate(DNA.DNArcTable)[::-1])
    def GCContent(self):
        ''' GC content of the sequeces. '''
        tseq = self.seq.upper()
        try:
            gc = round((tseq.count("G")+tseq.count("C"))/float(len(tseq)-tseq.count("N")),4)
        except:
            gc = 0.
        return gc
    def MW(self):
        ''' Molecular weight. '''
        return round(sum([DNA.mws[x] for x in self.seq.upper()]),3)

class RNA(Seq):
    ''' RNA sequences. '''
    RNArcTable = maketrans('ACBDGHKMNSRUWVYacbdghkmnsruwvy',
                           'UGVHCDMKNSYAWBRugvhcdmknsyawbr')
    def __init__(self, seq = ''):
        ''' Initiation. '''
        self.seq = str(seq).translate(maketrans('Tt','Uu'))
    def rc(self):
        ''' Return the reverse complementary sequence. '''
        return self.__class__(self.seq.makestrans(RNA.RNArcTable)[::-1])
    def GCContent(self):
        ''' GC content of the sequeces. '''
        tseq = self.seq.upper()
        try:
            gc = round((tseq.count("G")+tseq.count("C"))/float(len(tseq)-tseq.count("N")),4)
        except:
            gc = 0.
        return gc

class Fasta(object):
    '''Fasta format.'''
    def __init__(self,name, seq, description=''):
        '''Initiate the fasta record.'''
        self.id=name
        if not isinstance(seq, Seq):
            self.seq = Seq(seq)
        else:
            self.seq = seq
        self.description=description
    def __len__(self):
        '''get the length of sequence.'''
        return len(self.seq)
    def length(self):
        '''get the length of sequence.'''
        return self.seq.length()
    def __str__(self):
        '''String for output of Fasta.'''
        return ">{0}{1}\n{2}".format(self.id,(self.description and ' '+self.description or ''),self.seq)
    
class Fastq(Fasta):
    ''' Fastq format. '''
    def __init__(self, name, seq, qual = '', description = ''):
        ''' Initiation. '''
        Fasta.__init__(self, name, seq, description)
        self.qual = qual
    def __str__(self):
        ''' String for output of Fastq. '''
        return "@{0}\n{1}\n+\n{2}".format(self.id,self.seq, len(self.qual)==self.length() and self.qual or ''.join(['I' for i in xrange(self.length())]))


#########################################################################
# Data structure of biological objects
#########################################################################

class BedMap(dict):
    ''' 
    Store Beds in dictionary with chromsomes and BIN values as keys.
    Usage:
        bedmap = BedMap() # initiate the BedMap
        bedmap.loadBedToMap("mm9_miRNA.bed",'bed') # load Beds into BedMap
        for tbed in bedmap.findOverlap(querybed):  # print all Beds overlapped with query bed.
            print tbed 
    '''
    def __init__(self, genomesize='mm9'):
        ''' Initiation. '''
        dict.__init__(self)
        if isinstance(genomesize, dict):
            chroms = genomesize
        else:
            chroms = Utils.genomeSize(genomesize)
        # Initiation of Bin system
        for chrom in chroms:
            self[chrom]={}
        self.boundary = 0
    def findOverlap(self,bed):
        ''' Find overlaps with bed and put into bedlist. '''
        startBin,stopBin= bed.start >> _binFirstShift, (bed.stop-1) >> _binFirstShift
        for i in range(_binLevels):
            offset = _binOffsetsExtended[i]
            _startBin, _stopBin = offset + startBin, offset + stopBin 
            # startBin
            if self[bed.chrom].has_key(_startBin):
                for item,overlen in self[bed.chrom][_startBin][0].findOverlapInBIN(bed):
                    yield (item,overlen)
                if self.boundary and i <= self.binboundary:
                    for item,overlen in self[bed.chrom][_startBin][1].findOverlapInBIN(bed,self.boundary):
                        yield (item,overlen)
            # the beds in startBin+1 ~ stopBin-1 are sure to overlapped with bed.
            for Bin in xrange(_startBin+1, _stopBin):
                if self[bed.chrom].has_key(Bin):
                    for item in self[bed.chrom][Bin][0]:
                        yield (item, len(item))
                    if self.boundary and i <= self.binboundary:
                        for item in self[bed.chrom][Bin][1]:
                            yield (item, len(item))
            # stopBin
            if _startBin < _stopBin  and self[bed.chrom].has_key(_stopBin):
                for item,overlen in self[bed.chrom][_stopBin][0].findOverlapInBIN(bed):
                    yield (item,overlen)
                if self.boundary and i <= self.binboundary:
                    for item,overlen in self[bed.chrom][_stopBin][1].findOverlapInBIN(bed,self.boundary):
                        yield (item,overlen)
            startBin >>= _binNextShift
            stopBin >>= _binNextShift
        raise StopIteration
    def loadBedToMap(self,bedlist=None,ftype='bed',boundary=0):
        '''Load Bed to BedMap from either Bedlist or bedfile. Load one bedlist once.'''
        bcnt1 = 0
        bcnt2 = 0
        if bedlist:
            # calculate max bin level for a given boundary
            self.boundary = boundary
            self.binboundary = 0 # we at least to check Bin level 7
            # check the Bin level of boundary, usually it is Bin level 7
            tb = boundary
            tb >>= _binFirstShift
            while tb > 0:
                self.binboundary += 1
                tb >>= _binNextShift
            # read BedList into BedMap
            if isinstance(bedlist,str):
                bedlist=IO.BioReader(bedlist,ftype)
            for bed in bedlist:
                _bin=bed.getBIN()
                if not self[bed.chrom].has_key(_bin):
                    self[bed.chrom].setdefault(_bin,[BedList()])
                    self[bed.chrom][_bin][0].sort() # empty and useless if boundary = 0
                    if boundary:
                        self[bed.chrom][_bin].append(BedList())
                        self[bed.chrom][_bin][1].sort()
                # insert in order
                if boundary:
                    if len(bed) >= boundary or _bin < _binOffsetsExtended[self.binboundary]  : # traditional search
                        self[bed.chrom][_bin][0].insort(bed)
                        bcnt1 += 1
                    else:
                        self[bed.chrom][_bin][1].insort(bed)
                        bcnt2 += 1
                else:
                    bcnt1 += 1
                    self[bed.chrom][_bin][0].insort(bed)
            self.ftype = ftype
            # print >> sys.stderr, "Reads number in 0:{0}, 1:{1}".format( bcnt1, bcnt2)
        return
    def close(self):
        ''' Release the memory. '''
        self.clear()

class BedList(list):
    '''List class to hold Bed objects.'''
    def __init__(self,data=[],ftype='bed',description=None):
        '''Initiate data by list class.'''
        list.__init__(self,data)
        self.sorted=0
        self.ftype=ftype
        self.description=description
        self.infile=None
        self.chromsizes=None
    def readfile(self,infile, ftype='bed'):
        '''Read data from file by BioReader.'''
        self.ftype = ftype
        self.infile = infile
        self.sorted = 0
        for item in IO.BioReader(infile,ftype=self.ftype):
            self.append(item)
    def sort(self):
        '''sort BedList.'''
        list.sort(self)
        self.sorted=1
    def bisect(self,item):
        ''' Find the index to place the new item. '''
        if not self.sorted:
            self.sort()
        return bisect_left(self,item)
    def findFirstOverlap(self,item):
        '''
        Find the first overlapped one. This is mainly used to find the overlapped one in a nonoverlapped BedList.
        '''
        if not self.sorted:
            self.sort()
        idx = self.bisect(item)
        if idx == len(self) or  item.stop < self[idx].start:
            idx -= 1
        return idx
    def insort(self, item):
        ''' Insert items into an ordered list. '''
        insort(self, item)
        return
    def findOverlap(self, item):
        '''
        Generate overlapped items one by one. 
        This is a general case that the bed length are variable and may overlapped with each other. There are many ways to expedite this step for special cases.
        '''
        if not self.sorted:
            self.sort()
        tbed = copy.deepcopy(item)
        tbed.start = 0
        idx =  bisect_left(self,tbed) # find the first bed in this chromosome
        while idx < len(self) and item.chrom == self[idx].chrom and item.stop > self[idx].start:
            if self[idx].stop < item.start:
                idx +=1
                continue
            overlen = min(self[idx].stop,  item.stop) - max(self[idx].start, item.start)
            if overlen > 0:
                yield (self[idx], overlen)
            idx +=1
        raise StopIteration
    def findOverlapInBIN(self, item, boundary = 0):
        ''' A special case when the Beds are in BedMap Bins. '''
        idx = 0 # by default, no boundary is set
        if boundary>0:
            item.start -= boundary # negative start won't affect sort.
            idx = bisect_left(self,item)
            item.start += boundary
            idx = idx > 1 and idx -1 or 0
        while idx < len(self) and item.stop > self[idx].start:
            if self[idx].stop < item.start:
                idx += 1
                continue
            overlen = min(self[idx].stop,  item.stop) - max(self[idx].start, item.start)
            if overlen > 0:
                yield (self[idx], overlen)
            idx += 1
        raise StopIteration
    def nearestBed(self, item):
        ''' Find the nearest Bed. '''
        n = self.bisect(item)
        if n == len(self):
            return n-1
        if item.distance(self[n-1])<=item.distance(self[n]):
            return n-1
        else:
            return n
    def clear(self):
        '''Clear List.'''
        del self[:]
        self.sorted=0
    def mergeSort(bedfiles,ftype='bed'): #generator
        '''
        Merge Beds from multiple files. This function is used to merge several huge bed files. 
        The Bed in each file should be sorted before merge.
        '''
        print >>sys.stderr, "Make sure each file input is sorted!"
        if isinstance(bedfiles,str):
            bedfiles=[bedfiles]
        if len(bedfiles)==0:
            print >>sys.stderr, "No bed file names provided...."
        elif len(bedfiles)==1: # for single file
            for tbed in IO.BioReader(bedfiles[0],ftype=ftype):
                yield tbed
        else: #for multiple file
            bediters = [] # Bed iterators
            beds = BedList() # store current Bed item in each file
            for index, bedfile in enumerate(bedfiles):
                bediters.append(IO.BioReader(bedfile,ftype=ftype))
                try:
                    beds.append(bediters[index].next())
                    beds[index].otherfields.append(index)
                except Exception,e:
                    print >>sys.stderr,"Read Bed file error!",e
                    raise
            beds.sort()
            while True:
                if len(beds)>0:    
                    index = beds[0].otherfields[-1]
                    del beds[0].otherfields[-1]
                    yield beds[0] # yield the minimum bed
                    del beds[0]
                    try:
                        tbed=bediters[index].next()
                        tbed.otherfields.append(index)
                        ts=bisect(beds,tbed)
                        beds.insert(ts,tbed) # insert(pos,item) insert tbed in  the right position
                    except StopIteration:
                        print >>sys.stderr,bedfiles[index]+" is finished..."
                else:
                    break
    mergeSort=staticmethod(mergeSort)
    def mergeBeds(bedfiles,ftype = 'bed3', forcestrand=False): #generator
        '''Merge Beds from multiple files. The overlapped beds are combined. The Bed in each file should be sorted.'''
        if forcestrand:
            beds = {".":None, "+":None, "-":None}
            for tbed in BedList.mergeSort(bedfiles,ftype):
                if tbed.overlapLength(beds[tbed.strand]):
                    beds[tbed.strand] = tbed + beds[tbed.strand]
                else:
                    if beds[bedindex[tbed.strand]]:
                        bedcount[bedindex[tbed.strand]]+=1
                        beds[bedindex[tbed.strand]].description=beds[bedindex[tbed.strand]].id
                        beds[bedindex[tbed.strand]].id="Region_"+str(bedcount[bedindex[tbed.strand]])
                        yield beds[bedindex[tbed.strand]]
                    beds[bedindex[tbed.strand]]=tbed
            for tbed in beds:
                if tbed:
                    bedcount[bedindex[tbed.strand]]+=1
                    tbed.description="Region_"+str(bedcount[bedindex[tbed.strand]])
                    tbed.id,tbed.description=tbed.description,tbed.id
                    yield tbed
            assert "Reach this line."
        else:
            bed = None
            bedcount = 0
            for tbed in BedList.mergeSort(bedfiles, ftype):
                if tbed.overlapLength(bed)>0:
                    bed = tbed+bed
                else:
                    if bed is not None:
                        yield bed
                    bed = tbed
            if bed is not None:
                yield bed
            assert "Reach this line."
    mergeBeds=staticmethod(mergeBeds)
    def merge(self):
        ''' Merge beds in BedList. '''
        if not self.sorted():
            self.sort()
        nbeds = BedList()
        nbed = self[0]
        for tbed in self[1:]:
            if nbed.overlapLength(tbed) >0:
                nbed += tbed
            else:
                nbeds.append(nbed)
                nbed = tbed
        nbeds.append(nbed)
        return nbeds


    def pileup(self,chrom,start,stop,byscore = False):
        ''' pile up all beds in a specific regions. '''
        if byscore and len(self) and not Utils.is_set(self[0].score):
            raise ValueError("ERROR: BedList elements have no 'score' vairable.")
        depth = numpy.zeros(stop-start)
        for tbed in self:
            dstart = max(tbed.start,start) - start
            dstop  = min(tbed.stop, stop) - start
            depth[dstart:dstop] += byscore and tbed.score or 1
        return depth

class GeneBedList(BedList): 
    '''A list for Genes.'''
    def __init__(self,data=[],description=None):
        BedList.__init__(self,data,description)
        self.type='gene'


#########################################################################
# Parser of various biological files
#########################################################################

class FastaFile(object):
    ''' 
    Fasta file fast reader. Usually used for huge genome fasta files.
    Usage:
        Open file:
            fio=FastaFile("test.fa")
        Get Sequence:
            fio.getSeq(chrom="test",start=100,stop=200,strand="+")
        Close file:
            fio.close()
    Parameters:
        chrom=None: return empty string.
        start=None: start at first position
        stop=None:  stop at the end of record.
        strand: default "+"
    '''
    def __init__(self,infile):
        ''' Open Fasta file.'''
        self.closed = True
        if not os.path.exists(infile+".fai"): # create index automatically
            print >> sys.stderr, "Creating index for", infile
            pysam.faidx(infile)
        self.infile=infile
        self.fh=pysam.Fastafile(infile)
        self.chroms,self.sizes = self.chromSizes()
        self.closed = False
    def chromSizes(self):
        ''' 
        Get chromosome sizes.
        Returns:
            chromsizes: tuple
                Chromosome sizes in format: ((chr1,chr2,...,chrM),(len1,len2,...,lenM))
        '''
        return self.fh.references,self.fh.lengths
    def getSeq(self,chrom,start=None,stop=None,strand="+"):
        '''
        Obosoleted in the future. use fetch instead. 
        Fetch specific region from Fasta file.
        '''
        return self.fetch(chrom,start,stop,strand)
    def fetch(self,chrom,start=None,stop=None,strand="+",zerobased=True,**kwargs):
        ''' Fetch specific region from Fasta file. 1-based coordiantes. '''
        if kwargs.has_key('forcestrand') and kwargs['forcestrand'] == False:
            strand = '+'
        if not zerobased and start is not None:
            start -= 1
        seq=DNA(self.fh.fetch(reference=chrom,start=start,end=stop))
        if strand=="-":
            seq=seq.rc()
        return seq
    def close(self):
        ''' Close Fasta file. '''
        if not self.closed:
            self.fh.close()
            self.closed = True
    def __enter__(self):
        ''' Enter class. '''
        return self
    def __exit__(self, type, value, traceback):
        ''' Close file. '''
        self.close()
    def __del__(self):
        ''' Close file. Avoid memory leaks.'''
        self.close()
            
class BigWigFile(object):
    '''
    Fast reader of BigWig format file.
    Usage:
        Open file:
            fh=BigWigFile("test.bw")
        Get chromosome sizes:
            chroms=fh.chromSizes() # (chroms,sizes)
        Fetch regions:
            wigs=fh.fetch(chrom="chr1",start=100,stop=200)
            for wig in wigs:
                #do some thing with wig
                print wig.chrom,wig.start,wig.stop,wig.score
        Close file:
            fh.close()
    
    Parameters:
        chrom=None: return empty list.
        start=None: start at first position.
        stop=None:  stop at the end of chromosome.
    '''
    def __init__(self,infile,chrom_size=None):
        ''' Open BigWig file. '''
        # Check if file exists
        self.closed = True
        if not os.path.exists(infile) and infile != 'stdin':
            raise IOError("ERROR: input file '{0}' dose not exist.".format(infile))
        if infile.endswith('.wig'):
            bwfile = os.path.splitext(infile)[0]+".bw"
            if os.path.exists(bwfile):
                self.infile = bwfile
            else:
                if chrom_size is None:
                    raise IOError("ERROR: 'chrom_size' file is required for wig -> bigwig conversion.")
                BigWigFile.wigToBigWig(infile,chrom_size,bwfile)
            self.infile=bwfile
        else:
            self.infile=infile
        wWigIO.open(self.infile)
        self.closed = False
        self.chroms,self.sizes = self.chromSizes()
        self.closed = False
    def chromSizes(self):
        ''' Get chromosome sizes.'''
        chroms,sizes=wWigIO.getChromSize(self.infile)
        return chroms,sizes
    def fetch(self, chrom,start=None,stop=None,strand="+",zerobased=True,**kwargs):
        '''
        Fetch intervals in a given region. 
        Note: strand is useless here.
        Parameters:
            start: int or None
                start position, None for start=0
            end: int or None
                end position, None for stop = end of chrom
            strand: string
                choice from '+', '-' and '.'
            zerosbased: bool
                indices are zerobased or not. Useless here.
        Dictionary parameters:
            chunksize: int
                chunk size when fetch items from a large region.
        Generates:
            wig: tuple
                (start, stop, value)

        '''
        if chrom is None: raise ValueError("ERROR: chrom name is required.")
        if start is None: start = 0
        if not zerobased: start -= 1
        if start <0:
            raise ValueError('ERROR: start should be >=0 (zerobased=True) or >=1 (zerobased=False).')
        if stop is None: stop = self.sizes[self.chroms.index['chrom']]
        chunksize = kwargs.get('chunksize',10000)
        try:
            for cstart in xrange(start,stop,chunksize):
                cend = cstart + chunksize
                if cend > stop: cend = stop
                for wig in wWigIO.getIntervals(self.infile,chrom,cstart,cend):
                    if wig[0] < cstart: wig[0] = cstart
                    if wig[1] > cend: wig[1] = cend
                    yield wig
        except:
            # check result
            if wigs == 1:
                raise ValueError("ERROR: wWigIO.getIntervals doesn't have correct parameters.")
            if wigs == 2:
                raise ValueError("ERROR: BigWig file cannot be opened.")
    def pileup(self,chrom,start=None,stop=None,strand="+",zerobased=True,**kwargs):
        '''
        Fetch depth for a genomic region.        
        '''
        if chrom is None: raise ValueError("ERROR: chrom name is required.")
        if start is None: start = 0
        if not zerobased: start -= 1
        if stop is None: stop = self.sizes[self.chroms.index(chrom)]
        vals = numpy.zeros(stop-start)
        for wstart,wstop,depth in self.fetch(self.infile,chrom,start,stop,strand,zerobased):
            vals[(wstart-start):(wstop-start)]+=depth
        if strand == "-":
            vals = vals[::-1]
        return vals
    def fetchBed(self,tbed,byPos=False,forcestrand=True):
        '''Fetch intervals for Bed.'''
        wigs=wWigIO.getIntervals(self.infile,tbed.chrom,tbed.start,tbed.stop)
        if not byPos:
            return wigs
        # get depth by position, return a numpy array.
        vals = numpy.zeros(tbed.length())
        for start,stop,depth in wigs:
            start = max(start,tbed.start)
            stop  = min(stop,tbed.stop)
            vals[(start-tbed.start):(stop-tbed.start)]+=depth
        if forcestrand and tbed.strand=="-":
            vals=vals[::-1]
        return vals
    def __enter__(self):
        ''' Enter instance. '''
        return self
    def __exit__(self, type, value, traceback):
        ''' Exit instance. '''
        self.close()
    def close(self):
        ''' Close BigWig file. '''
        if not self.closed:
            wWigIO.close(self.infile)
            self.closed = True
    def __del__(self): 
        ''' Close BigWig file.  Avoid memory leaks.'''
        self.close()
    def wigToBigWig(wigfile, sizefile, bwfile):
        ''' Convert wiggle file to BigWig file. '''
        wWigIO.wigToBigWig(wigfile, sizefile, bwfile)
    wigToBigWig=staticmethod(wigToBigWig)
    def bigWigToWig(bwfile, wigfile):
        ''' Convert BigWig file to Wiggle file. '''
        wWigIO.bigWigToWig(bwfile, wigfile)
    bigWigToWig=staticmethod(bigWigToWig)

class TwoBitFile(dict):
    '''
    This class is used to deal with huge genome files in 2bit format.
    Usage: read twobit file
        from wLib import TwoBitFile
        tbf  = TwoBitFile("test/test.2bit")
        chr1 = tbf['chr1']
        chroms,sizes = tbf.chromSizes()
        seq  = chr1[10:100]
        print chrom
        print seq
    Output:
        {'chr4': 250L, 'chr3': 320L, 'chr2': 240L, 'chr1': 240L}
        AAAGCTTNNNNNNTTTGCGGCCTAAGTTAGCCAAGCCTAGTAGTTTCTAGAGGCAGAAGTTTTTTNNNNNTCACAGACTCTATTGCGAAG
    Usage: create twoBit file
        from wLib import TwoBitFile
        TwoBitFile.faToTwoBit(fafile, twobitfile)
    '''
    bitsToBases = {0:'T', 1:'C', 2:'A', 3:'G'}
    byteTable = {}
    twoBytesTable = {}
    basesToBits = {'T':0, 'C':1, 'A':2, 'G':3}
    fourBasesTable = {}
    #byteTable = numpy.chararray(2**8, itemsize = 4)
    #twoBytesTable = numpy.chararray(2**16, itemsize = 8)
    def __init__(self, infile = None):
        ''' Initiation. '''
        self.fh = None
        if infile:
            self.infile = infile
            self.open(infile)
            self.closed = False
            self.chroms, self.sizes = self.chromSizes()
    def open(self, infile):
        ''' Open TwoBit file. '''
        self.infile = infile
        self.fh = open(self.infile,'rb')
        self.fsize = os.path.getsize(self.infile) # file size
        self.__loadheader()
        self.__loadindex()
        # create byteTable and twoBytesTable
        if len(TwoBitFile.twoBytesTable) == 0: # make sure that we just creat them once.
            TwoBitFile.__createTables()
    def __loadheader(self):
        ''' Load header of 2bit file. '''
        header = array(LONG)
        header.fromfile(self.fh,4)
        self.byteswapped = False
        self.sequencecount = 0
        if not header[0] == 0x1A412743: # check signature
            self.byteswapped = True
            header.byteswap()
            if not header[0] == 0x1A412743:
                raise IOError("File signature Error!")
        self.sequencecount = header[2]
    def __loadindex(self):
        ''' Load index of 2bit file. '''
        self.fh.seek(16) # skip first 4 LONGs
        offsets = []
        for i in range(self.sequencecount):
            namesize = array('B')
            namesize.fromfile(self.fh,1)
            if self.byteswapped:
                namesize.byteswap() 
            name = array('c')
            name.fromfile(self.fh,namesize[0])
            if self.byteswapped:
                name.byteswap()
            offset = array(LONG)
            offset.fromfile(self.fh, 1)
            if self.byteswapped:
                offset.byteswap()
            offsets.append((name.tostring(),offset[0]))
        self.offset_dict = {}
        for chrom, offset in offsets:
            self[chrom] = TwoBitSeq(self.infile, self.fh, offset, self.fsize, self.byteswapped)
            self.offset_dict[chrom] = offset
    def __createTables():
        ''' Create byteTable and twoBytesTables. '''
        for x in xrange(2**8):
            c = (x >> 4) & 0xf
            f = x & 0xf
            cc = (c >> 2) & 0x3
            cf = c & 0x3
            fc = (f >> 2) & 0x3
            ff = f & 0x3
            s = ''.join(map(lambda x:TwoBitFile.bitsToBases[x], (cc, cf, fc, ff)))
            TwoBitFile.byteTable[x] = s
            TwoBitFile.fourBasesTable[s] = x
        for x in xrange(2**16):
            c = (x >> 8) & 0xff
            f = x & 0xff
            TwoBitFile.twoBytesTable[x] = TwoBitFile.byteTable[f] + TwoBitFile.byteTable[c]
        return
    __createTables=staticmethod(__createTables)
    def chromSizes(self):
        ''' Return chroms, sizes for chromosome sizes. '''
        if not self.fh:
            raise IOError("TwoBit file dose not exist.")
        if self.fh.closed:
            raise ValueError("I/O operation on closed file.")
        chroms = []
        sizes  = []
        for chrom, offset in self.offset_dict.iteritems():
            self.fh.seek(offset)
            seqsize = array(LONG)
            seqsize.fromfile(self.fh,1)
            if self.byteswapped:
                seqsize.byteswap()
            chroms.append(chrom)
            sizes.append(seqsize[0])
        return chroms,sizes
    def fetch(self,chrom, start = None,stop = None, strand = "+", zerobased=True,**kwargs):
        '''
        Fetch DNA sequence from 2bit file.
        Parameters:
            chrom: string
                Chromosome name.
            start,stop: int
                Coordinates of a genomic region. Default is begining and end of the chromsome, respectively.
            strand: string, "+", "-" or "."
                Strand
            zerobased: bool
                Start position is zerobased or not. Default is True.
        Returns:
            dna: DNA object.
                A DNA object of given region.        
        '''
        if chrom is None: raise ValueError("ERROR: chrom name is required.")
        if not zerobased and start is not None: start -=1
        if start is None: start = 0
        if stop is None: stop = self.sizes[self.chrom.index(chrom)]
        seq = DNA(self[chrom][start:stop])
        if strand == "-":
            seq = seq.rc()
        return seq
    def close(self):
        ''' Close file. '''
        if not self.fh.closed:
            self.fh.close()
            self.closed = True
    def __enter__(self):
        ''' Enter instance. '''
        return self
    def __exit__(self, type, value, traceback):
        ''' Exit instance. '''
        self.close()
    def __del__(self):
        ''' Close file automatically. '''
        self.close()
    def faToTwoBit(faFile, tbfFile):
        ''' Convert fasta file to 2bit file. '''
        rval = wTwoBitIO.faToTwoBit(faFile, tbfFile)
        assert rval == 0, "faToTwoBit failed for some reason."
        return
    faToTwoBit=staticmethod(faToTwoBit)
    def seqToTwoBit(seq, outfile = 'test.2bitseq'):
        '''
        Convert sequence to TwoBitSeq. 
        This is for testing the compression rate to twobit format for HTS reads.
        '''
        if len(TwoBitFile.fourBasesTable) == 0:
            TwoBitFile.__createTables()
        size = len(seq)
        # record blocks
        re.compile('(N+)')
        blockstarts = array('B')
        blocksizes = array('B')
        bytesarray = array('B')
        for m in re.finditer('N+',seq):
            blockstarts.append(m.start())
            blocksizes.append(m.end()-m.start())
        seq = seq.replace('N','T')
        nbytes = (size+3)/4
        for i in xrange(size/4):
            bytesarray.append( TwoBitFile.fourBasesTable[seq[(i*4):((i+1)*4)]])
        # last byte
        t = size%4
        if t:
            s= seq[-t:]
            s+= 'T'*(4-t)
            bytesarray.append(TwoBitFile.fourBasesTable[s])
        print "Original size:", size
        print "TwoBit size:", 2*blockstarts.itemsize*len(blockstarts)+4+nbytes
        return array('B',[size,len(blockstarts)])+blockstarts+blocksizes+bytesarray
    seqToTwoBit=staticmethod(seqToTwoBit)

class TwoBitSeq(object):
    ''' 
    TwoBit sequence.
    Usage:
        g = TwoBitFile("test/test.2bit")
        chr1 = g['chr1'] # TwoBitSeq object
        seq  = chr1[10:100] # DNA object
    '''
    def __init__(self, infile, fh, offset, fsize, byteswapped = False):
        ''' Initiation. '''
        self.infile = infile
        self.fh = fh
        self.oldoffset = offset
        self.fsize = fsize
        self.byteswapped = byteswapped
        # Read header
        self.fh.seek(offset)
        header = array(LONG)
        header.fromfile(self.fh, 2)
        if byteswapped:
            header.byteswap()
        self.dnasize, self.blockcount = header
        self.nbytes = (self.dnasize + 3) / 4  # number of bytes
        self.packed_dnasize = (self.dnasize + 15) / 16
        # block starts and sizes
        self.blockstarts = array(LONG)
        self.blocksizes = array(LONG)
        self.blockstarts.fromfile(self.fh, self.blockcount)
        self.blocksizes.fromfile(self.fh, self.blockcount)
        if byteswapped:
            self.blockstarts.byteswap()
            self.blocksizes.byteswap()
        mask_rawc = array(LONG)
        mask_rawc.fromfile(self.fh, 1)
        if byteswapped:
            mask_rawc.byteswap()
        self.maskcount = mask_rawc[0]
        self.maskstarts = array(LONG)
        self.masksizes = array(LONG)
        self.maskstarts.fromfile(self.fh, self.maskcount)
        self.masksizes.fromfile(self.fh, self.maskcount)
        if byteswapped:
            self.maskstarts.byteswap()
            self.masksizes.byteswap()
        self.fh.read(4)
        self.offset = self.fh.tell()
    def __len__(self):
        ''' sequence length. '''
        return self.dnasize
    def __del__(self):
        ''' close file. '''
        if not self.fh.closed:
            self.fh.close()
    def __str__(self):
        ''' string of TwoBitSeq. '''
        return str(self[:])
    def __getslice__(self, _min=0, _max = None):
        ''' get subset of sequence. '''
        dsize = self.dnasize
        # Check range
        if _max:
            if _max < 0:
                _max = dsize + 1 + _max
            if _max > dsize:
                _max = dsize
        else:
            _max = dsize
        if _min < -dsize or _min > _max:
            raise IndexError('index out of range')
        if _min < 0 :
            _min = dsize + 1 + _min
        # find block information
        start_byte = _min / 4
        local_offset = self.offset + (start_byte)
        end_byte = (_max + 3) / 4
        bytes_to_read =  end_byte - start_byte # number of bytes to read
        start_offset = _min % 4
        end_offset = _max % 4

        # Read DNA in two bytes
        if self.fh.closed:
            self.fh = open(self.infile)
        self.fh.seek(local_offset)
        twobytesDNA = array('H') # unsigned short, 2 bytes
        twobytesDNA.fromfile(self.fh, bytes_to_read / 2)
        if self.byteswapped:
            twobytesDNA.byteswap()
        
        # Read the last byte if needed
        last_byte = array('B')
        if bytes_to_read % 2 == 1:
            last_byte.fromfile(self.fh, 1)
        
        # adjust sequence by offsets        
        seq =  array('c',"".join([TwoBitFile.twoBytesTable[i] for i in twobytesDNA]) + (len(last_byte) and TwoBitFile.byteTable[last_byte[0]] or ""))
        if end_offset == 0:
            seq =  seq[start_offset:]
        else:
            seq =  seq[start_offset:(end_offset-4)]
        
        # blocks to N
        idx = bisect_left(self.blockstarts, _min) # _min <= self.blockstarts[idx]
        idx = idx >1 and idx -1 or 0 # start from the previous region if available
        while idx < self.blockcount and self.blockstarts[idx] < _max:
            start = max (self.blockstarts[idx], _min) - _min
            end   = min (self.blockstarts[idx] + self.blocksizes[idx], _max) - _min
            seq[start:end] = array('c', 'N' * (end - start))
            idx +=1

        # masks to lower
        idx = bisect_left(self.maskstarts, _min) # _min <= self.maskstarts[idx]
        idx = idx >1 and idx -1 or 0 # start from the previous region if available
        while idx < self.maskcount and self.maskstarts[idx] < _max:
            start = max (self.maskstarts[idx], _min) - _min
            end   = min (self.maskstarts[idx] + self.masksizes[idx], _max) - _min
            seq[start:end] = array('c', seq[start:end].tostring().lower())
            idx +=1
        return DNA(seq.tostring())

class TabixFile(object):
    ''' Tabix file. '''
    def __init__(self,infile,ftype=None,force=False,zerobased=True):
        ''' Initiation. '''
        # Check if gz file
        self.closed = True
        self.ftype = ftype
        # Check if index exists
        self.infile=infile
        if not os.path.exists(infile+".tbi") or force:
            if ftype in ('bed','bed3','bedgraph','peak'):
                self.infile = pysam.tabix_index(infile,force=force,seq_col=0,start_col=1,end_col=2,zerobased=True)
            elif ftype in ('sam','gff','vcf'):
                self.infile = pysam.tabix_index(infile,force=force,preset=ftype,zerobased=True)
            elif ftype in ('genepred','tab','gene'):
                self.infile = pysam.tabix_index(infile, seq_col = 0, start_col = 2, end_col = 3, zerobased = True)
            elif ":" in ftype:
                c, s, e = ftype.split(":")
                if Utils.is_int(c) and Utils.is_int(s) and Utils.is_int(e):
                    self.infile = pysam.tabix_index(infile, seq_col = int(c)-1, start_col = int(s)-1, end_col = int(e)-1, zerobased = zerobased)
        self.fh = pysam.Tabixfile(self.infile)
        self.closed = False
    def __len__(self):
        ''' Length of file. '''
        if self.ftype in ('bed','bed3','bedgraph','peak','genepred','tab','gene','gff'):
            return len(self.fh.contigs)
    def __enter__(self):
        ''' Enter instance. '''
        return self
    def __exit__(self,etype,value,traceback):
        ''' Exit instance. '''
        self.close()
    def __del__(self):
        ''' On deletion. '''
        self.close()
    def close(self):
        ''' close file handle. '''
        if not self.closed:
            self.fh.close()
            self.closed = True
    def fetch(self,chrom=None, start=None, stop=None,strand="+",zerobased=True,**kwargs):
        ''' 
        Fetch items in Tabix file. 
        Allow to use converter to convert the result.
        '''
        # check converter
        converter = kwargs.get('converter')
        if isinstance(converter, basestring) or converter is None:
            if IO.converters.has_key(converter):
                converter = IO.converters[converter]
            elif ":" in converter:
                converter = lambda x:IO.anyToBed(x,converter)
            else:
                raise ValueError("ERROR: converter '{0}' is not valid. It should be either preset types or callable function.".format(converter))
        # fetch items
        if not zerobased: start -= 1
        for item in self.fh.fetch(reference=chrom,start=start,end=stop):
            yield converter(item)
    def pileup(self,chrom=None,start=None,stop=None,strand="+",zerobased=True,**kwargs):
        ''' Pileup items in a given region. '''
        byscore = kwargs.get('byscore',False)
        # check converter
        converter = kwargs.get('converter')
        if isinstance(converter, basestring) or converter is None:
            if IO.converters.has_key(converter):
                converter = IO.converters[converter]
            elif ":" in converter:
                converter = lambda x:IO.anyToBed(x,converter)
            else:
                raise ValueError("ERROR: converter '{0}' is not valid. It should be either preset types or callable function.".format(converter))
        # pileup beds
        if not zerobased: start -= 1
        depth = numpy.zeros(stop-start)
        if byscore:
            for item in self.fh.fetch(reference=chrom,start=start,end=stop):
                tbed = converter(item)
                tstart = max(tbed.start,start) - start
                tstop  = min(tbed.stop,stop) - start
                depth[tstart:tstop] += tbed.score
        else:
            for item in self.fh.fetch(reference=chrom,start=start,end=stop):
                tbed = converter(item)
                tstart = max(tbed.start,start) - start
                tstop  = min(tbed.stop,stop) - start
                depth[tstart:tstop] += 1
        return depth

class BAM(object): # Not finished
    def __init__(self,read):
        ''' Initiation. '''
        if isinstance(read,basestring):
            # LAMARCK:3131:C10NKACXX:8:1216:4799:19543        0       chr10   61155   255     16M     *       0       0       GGTTATATTGTCTAAC        @@=?DBDDF8:CB?EF      XA:i:0  MD:Z:16 NM:i:0
            read = read.split("\t")
            self.id = read[0]
            self.start = read[3]

class BAMFile(pysam.Samfile):
    ''' SAM/BAM file. '''
    def __init__(self,infile,mode='r'):
        ''' Initiation. '''
        self.ftype = 'b' in mode and 'bam' or 'sam'
        self.chroms = self.references
        self.sizes = self.lengths
    def fetch(self,chrom=None,start=None,stop=None,strand="+",zerobased=True, **kwargs):
        ''' Fetch items from BAM file. '''
        if start is not None and not zerobased:
            start -= 1
        for read in super(BAMFile,self).fetch(reference=chrom,start=start,end=stop):
            if strand == ".":
                yield read
            elif strand == "+" and read.is_reverse is not True:
                yield read
            elif strand == "-" and read.is_reverse is True:
                yield read
    def pileup(self,chrom=None,start=None,stop=None,strand=".",zerobased=True, **kwargs):
        ''' Pileup region in BAM file. '''
        if start is not None and not zerobased: start -= 1
        depth = numpy.zeros(stop-start)
        if strand == ".":
            for pc in super(BAMFile,self).pileup(reference=chrom,start=start,end=stop,**kwargs):
                if start <= pc.pos < stop:
                    depth[pc.pos-start] += pc.n
            return depth
        for read in super(BAMFile,self).fetch(reference=chrom,start=start,end=stop):
            if read.is_reverse and strand =="-":
                rstart = read.pos - start
                for mtype,mlen in read.cigar:
                    if mtype==0: # match
                        depth[rstart:rstart+mlen] += 1
                    elif mtype==1: # insertion
                        rstart -= mlen
                    rstart+=mlen
            elif not read.is_reverse and strand == '+':
                rstart = read.pos - start
                for mtype,mlen in read.cigar:
                    if mtype==0: # match
                        depth[rstart:rstart+mlen] += 1
                    elif mtype==1: # insertion
                        rstart -= mlen
                    rstart+=mlen
        if strand == '-': # reverse the genome region
            depth = depth[::-1]
        return depth
    def chromSizes(self):
        ''' chrom sizes. Only work for BAM files'''
        if self.ftype == 'bam':
            return self.references, self.lengths
        raise ValueError("ERROR: SAM file dosen't support chromSize function.")
        return 
    def close(self):
        ''' close file handle. '''
        super(BAMFile,self).close()
    def __enter__(self):
        ''' Enter instance. '''
        return self
    def __exit__(self,etype,value,traceback):
        ''' Exit instance. '''
        self.close()
    def __del__(self):
        ''' On deleteion. '''
        self.close()
    

#########################################################################
# IO: a universal reader for various biological data format.
#########################################################################

class StringFile(object):
    '''
    Make string act as File.
    Example 1: If initiated without string, fh is writable.
        fh = StringFile() 
        fh.write("1\n2\n3\n4")
        ... # write more
        fh.seek(0)
        for line in fh:
            print line.rstrip("\n") # print line
        fh.close()
        
    Example 2: If initiated with string, fh is not writable
        fh = StringFile("1\n2\n3\n4") 
        for line in fh:
            print line.rstrip("\n") # print line
        fh.close()
        
    Example 3: with statement support (recommended)
        with StringFile("1\n2\n3\n4") as fh:
            for line in fh:
                print line.rstrip("\n") # print line        
    '''
    def __init__(self,buffer=None):
        ''' Initiation. '''
        if buffer is None: # write
            self.fh = cStringIO.StringIO()
        else: # read
            self.fh = cStringIO.StringIO(buffer)
        self.closed = False
    def getvalue(self):
        ''' Get value of the content. '''
        return self.fh.getvalue()
    def __str__(self):
        ''' Get value of content. '''
        return self.fh.getvalue()
    def write(self,buf):
        ''' write '''
        if buf is not None:
            self.fh.write(buf)
    def read(self,size=None):
        ''' read '''
        self.fh.read(size)
    def tell(self):
        ''' return current position. '''
        return self.fh.tell()
    def seek(self,offset, whence=0):
        ''' go to offset. '''
        self.fh.seek(offset,whence)
    def readline(self):
        ''' read one line each time. '''
        return self.fh.readline()
    def readlines(self):
        ''' read all lines into string. '''
        return self.fh.readlines()
    def close(self):
        ''' close StringFile. '''
        if not self.fh.closed:
            self.fh.close()
            self.closed=True
    def tofile(self,outfile):
        ''' Write StringFile object into static text file '''
        with IO.mopen(outfile,'w') as ofh:
            ofh.write(str(self))
    def __iter__(self):
        ''' iteration '''
        return self
    def next(self):
        ''' next '''
        try:        
            return self.fh.next()                
        except:
            raise StopIteration
    def __enter__(self):
        ''' Enter instance. '''
        return self
    def __exit__(self, etype, value, traceback):
        ''' Exit instance. '''
        self.close()
    def __del__(self):
        ''' On deletion. '''
        self.close()

class mFile(object):
    ''' Deal with multiple file formats. '''
    def __init__(self,infile=None, mode='r'):
        ''' Initiation. '''
        self.closed = True
        self.infile = infile
        if infile == 'stdin':
            self.fh = sys.stdin
        elif infile == 'stdout':
            self.fh = sys.stdout
        elif infile == 'stderr':
            self.fh = sys.stderr
        elif isinstance(infile,StringFile):
            self.fh = infile.fh
        elif infile.endswith('gz'):
            self.fh = gzip.open(infile, mode)
        else:
            self.fh = open(infile, mode)
        self.closed = False
    def __str__(self):
        ''' Get string if it is a StringFile object. '''
        try:
            return self.fh.getvalue()
        except:
            raise TypeError("ERROR: only StringFile can be converted to string.")
    def seek(self,offset,whence=0):
        ''' Seek '''
        self.fh.seek(offset,whence)
    def tell(self):
        ''' Tell '''
        return self.fh.tell()
    def close(self):
        ''' Close file. '''
        if not self.closed and self.infile not in ['stdin','stdout','stderr']:
            self.fh.close()
        self.closed = True
    def read(self,n=-1):
        ''' read n bytes. '''
        return self.fh.read(n)
    def readline(self):
        ''' read one line. '''
        return self.fh.next()
    def readlines(self):
        ''' read all the lines. '''
        return self.fh.readlines()
    def write(self,lstr):
        ''' write to file. '''
        self.fh.write(lstr)
    def __enter__(self):
        ''' On enter. '''
        return self
    def __exit__(self,etype,value,traceback):
        ''' On exit. '''
        self.close()
    def __del__(self):
        ''' On deletion. '''
        self.close()
    def __iter__(self):
        ''' Iterator. '''
        return self
    def next(self):
        ''' Next '''
        return self.fh.next()

class IO(object):
    ''' Universal parser for various biological data fomrat. '''
    converters={ None:lambda x:x,'bed3':Bed3,'macs':Peak,'peak':Peak, 'bed':Bed, 'genepred':GeneBed}
    readers = {}
    # querylst = ['bed','bed3','bedgraph','peak','genepred','bam','any']
    # dblst    = ['bed','bed3','bedgraph','peak','genepred','bam','any','bigwig','fasta']
    def mopen(infile,mode='r'):
        ''' Open file with common or gzip types.'''
        if isinstance(infile,basestring):
            return mFile(infile,mode)
        if isinstance(infile, StringFile):
            infile.seek(0)
            return infile
    mopen=staticmethod(mopen)
    def mclose(fh):
        ''' Close file handle if necessary. '''
        fh.close()
    mclose=staticmethod(mclose)
    def anyToBed(strvec,ftype):
        ''' 
        Any text file with at least chromosome, start and stop BioReaders can be converted to Bed. 
        Indice are provided in this way: 
            If the chrom, start stop, score are in the 2,1,3,4 BioReaders, provide a string like this: "2:1:3:-:4". "-" means missing values.
            The result will be a 6-BioReader Bed with the rest items in Bed.otherfields.
        '''
        idx=[i for i in ftype.split(":")] # index of Bed items
        for i in range(len(idx),6):
            idx.append("-")
        dlst=[] # indice of elements that will be deleted
        # Put Bed items in the beginning of the list
        newvec=[]
        for i in idx:
            if Utils.is_int(i):
                i=int(i)
                dlst.append(i-1)
                newvec.append(strvec[i-1])
            else:
                newvec.append('')
        # delete the used elements
        dlst=list(set(dlst)) # unique
        dlst.sort()
        dlst.reverse()
        for i in dlst: # remove the element from large to small number so that the index won't change
            del strvec[i]
        newvec.extend(strvec)
        return Bed(newvec)
    anyToBed=staticmethod(anyToBed)
    def guess(infile):
        ''' Guess format from file name. '''
        if infile.endswith('.gz'):
            infile = infile[:-3]
        ftype = os.path.splitext(os.path.basename(infile))[1].lower()[1:]
        if ftype == 'bw'or ftype == 'bigwig':
            return 'bigwig'
        if ftype == 'tab' or ftype == 'gpd':
            return 'genepred'
        if ftype == 'fa' or ftype == 'fasta':
            return 'fasta'
        if ftype == 'fq' or ftype == 'fastq':
            return 'fastq'
        return ftype
    guess=staticmethod(guess)
    def bowtieToBed(strvec):
        ''' Bowtie map result to Bed.Bowtie is 0 based. '''
        strvec[3]=int(strvec[3])
        return Bed([strvec[2],strvec[3],strvec[3]+len(strvec[4]),strvec[0],1,strvec[1]])
    bowtieToBed=staticmethod(bowtieToBed)
    def SOAPToBed(x):
        '''SOAP map result to Bed. SOAP is 1 based.'''
        x[8]=int(x[8])-1
        return Bed([x[7],x[8],x[8]+int(x[5]),x[0],1,x[6]])
    SOAPToBed=staticmethod(SOAPToBed)
    def SAMToBed(x):
        ''' SAM format to Bed. '''
        # HWI-ST1113_0169:4:2311:3245:66985#CGATGT/1    16    chr1    3000376    255    36M    *    0    0    CTTCTATTTCCATTTTCAGGTTTTAAACAGTTTCCT    iiihihiiiiihiiiiiiiiiiigggggeeeeebb_    XA:i:0    MD:Z:36    NM:i:0
        if isinstance(x,basestring):
            x = x.split('\t')
        if x[2] == "*": # not mapped
            return None
        return Bed([x[2],x[3],int(x[3])+len(x[9]),x[0],0,int(x[1]) & 16 and "-" or "+"]) 
    SAMToBed=staticmethod(SAMToBed)
    def SAMToBeds(x):
        ''' SAM string to BedList. '''
        if isinstance(x, basestring):
            x = x.split('\t')
        if x[2] == "*":
            return []
        start = int(x[3])
        tbeds = BedList()
        strand = int(x[1]) & 16 and "-" or "+" # 16 means minus strand
        for m in re.finditer('(\d+)(\w)',x[5]):
            mlen,mtype = m.groups()
            mlen = int(mlen)
            if mtype == 'M':
                tbeds.append( Bed([x[2],start,start+mlen,x[0],len(tbeds),strand]))
            elif mtype == 'I':
                continue
            start += mlen
        return tbeds
    SAMToBeds=staticmethod(SAMToBeds)
    def seqReader(infile,ftype='fasta'):
        '''Read sequence files.'''
        ftype=ftype.lower()
        # Read lines
        with IO.mopen(infile) as fh:
            if ftype=='fasta':
                line = fh.next()
                if line[0] != ">":
                    raise ValueError("Records in Fasta files should start with '>' character")
                line = line.lstrip('>').rstrip().replace('\t',' ').split(' ')
                name = line[0]
                desc = ' '.join(line[1:])
                seq = ''
                while True:
                    try:
                        line = fh.next()
                    except:
                        if seq != '':
                            yield Fasta(name, seq, desc)
                        raise StopIteration
                    if line[0] != ">":
                        seq += line.rstrip()
                    else:
                        yield Fasta(name, seq, desc)
                        line = line.lstrip('>').rstrip().replace('\t',' ').split(' ')
                        name = line[0]
                        desc = ' '.join(line[1:])
                        seq = ''
            elif ftype=='fastq':
                while True:
                    try:
                        fid=fh.next().rstrip().lstrip('@')
                        seq=fh.next().rstrip()
                        fh.next()
                        qual = fh.next().rstrip()
                        yield Fastq(fid,seq,qual)
                    except:
                        raise StopIteration
            else:
                raise TypeError(ftype+" format is not supported.")
            assert False, "Do not reach this line."
    seqReader=staticmethod(seqReader)
    def twoBitReader(infile,ftype='2bit'):
        ''' Read large genome file. '''
        ftype=ftype.lower()
        # Read chromosome information
        if ftype=='2bit':
            pass
        else:
            print >>sys.stderr, ftype, "format is not supported."
        raise StopIteration
    def wigReader(infile,ftype='wig'):
        ''' Iteration of Wiggle or BigWig file. '''
        if ftype=='wig':
            with IO.mopen(infile,'r') as fh:
                mode=''
                chrom=''
                start=0
                span=0
                step=0
                for line in fh:
                    if line.startswith( "variableStep" ):
                        header=dict( [ field.split( '=' ) for field in line.split()[1:] ] )
                        chrom=header['chrom']
                        span=int(header.get('span',1))
                        mode="variableStep"
                    elif line.startswith( "fixedStep" ):
                        header= dict( [ field.split( '=' ) for field in line.split()[1:] ] )
                        chrom = header['chrom']
                        start = int( header['start'] ) -1 
                        step  = int( header['step'])
                        span=int(header.get('span',1))
                        mode = "fixedStep"
                    elif mode == "variableStep":
                        fields=line.split()
                        start=int(fields[0]) -1
                        yield Wiggle([chrom,start+1,start+span,float(fields[1])])
                    elif mode == "fixedStep":
                        yield Wiggle([chrom,start+1,start+span,float(line)])
                        start+=step
                    elif line.startswith( "track" ) or line.startswith( "#" ) or line.startswith( "browser" ):
                        continue
                    else:
                        raise "Unexpected input line: %s" % line.strip()
        elif ftype=='bigwig':
            with BigWigFile(infile) as bf:
                chroms = bf.chromSizes()[0]
                for chrom in chroms:
                    for wig in bf.fetch(chrom=chrom):
                        yield wig
    wigReader=staticmethod(wigReader)
    def bamReader(infile, ftype = 'bam'):
        '''
        Iteration of BAM file.
        For 'bam2bed' and 'sam2bed':
            CIGAR information is considered. One mapped reads may cover incontinuous regions in genome. 
            Each of these regions is treated as a single Bed. The number is specified in Bed score.
            For example, a read starts at 1000 and with CIGAR as "10M8D15M" are represented by 2 Beds: 
                chr1    1000    1010    Name    1.00    +
                chr1    1018    1033    Name    2.00    +
        '''
        bypysam = True # file is parsed by pysam
        if ftype == 'sam':
            sam = BAMFile(infile,'r') # pysam.Samfile(infile, 'r')
        elif ftype == 'bam' or ftype == 'bam2bed' or ftype == 'bam2beds':
            sam = BAMFile(infile, 'rb') # pysam.Samfile(infile, 'rb')
        elif ftype == 'sam2bed' or ftype == 'sam2beds':
            try:
                sam = BAMFile(infile,'r') # pysam.Samfile(infile, 'r')
            except:
                sam = IO.mopen(infile)
                bypysam = False
        else:
            raise TypeError("{0} file type is not supported. Please choose from 'sam' or 'bam'.")
        # read file
        with sam as sam:
            if bypysam:
                if ftype == 'bam2beds' or (ftype == 'sam2beds' and bypysam): 
                    for read in sam:
                        if not read.is_unmapped:
                            # processing CIGAR  17M204733N83M=[(0, 17), (3, 204733), (0, 83)]
                            tbeds=BedList()
                            start = read.pos
                            strand = "-" if read.is_reverse else "+"
                            cnt = 1
                            for mtype,mlen in read.cigar:
                                if mtype==0: # match
                                    if len(tbeds)>0 and tbeds[-1].stop == start:
                                        tbeds[-1].stop = start + mlen
                                    else:
                                        tbeds.append(Bed([sam.references[read.tid],start, start+mlen,read.qname,cnt,strand]))
                                        cnt += 1
                                elif mtype==1: # insertion
                                    continue
                                start += mlen
                            yield tbeds
                elif ftype == 'bam2bed' or (ftype == 'sam2bed' and bypysam): # stop = stat + length
                    for read in sam:
                        if not read.is_unmapped:
                            yield Bed([sam.references[read.tid],read.pos,read.pos+read.qlen,read.qname,0,read.is_reverse and "-" or "+"])
                else:
                    for read in sam:
                        yield read        
            else: # not pysam
                if ftype == 'sam2bed':
                    for read in sam:
                        tbed = IO.SAMToBed(read)
                        if tbed is not None: yield tbed # check if mapped
                else:
                    for read in sam:
                        for tbed in IO.SAMToBeds(read):
                            yield tbed
        raise StopIteration
    bamReader=staticmethod(bamReader)
    def BioConverter(ftype=None):
        ''' return converter for ftype. '''
        if ":" in ftype:
            return lambda x:IO.anyToBed(x,ftype)
        return IO.converters.get(ftype, lambda x:x)
    BioConverter=staticmethod(BioConverter)
    def BioReader(infile,ftype=None,**kwargs):
        '''
        Read most of the iterative biological files into Python objects.
        Usage:
            for item in IO.BioReader(filename, sep="\t", skip=10, mask='#'):
                print item
        Parameters:
            ftype: default(None), a string such as Bed, Gene/GeneBed/Tab/GenePred, Bowtie or SOAP. Convert line to specific format.
            sep: character that seperate each BioReader, default("\t"). None means split by whitespaces just like split().
            skip: numeric, default 0. Skip first n lines. Empty lines will be skipped automatically and do not count in here.
            mask: character, default '#'. Mask lines start with '#'.
        Output:
            By default, it returns a vector of strings split by 'sep'.
            For any text file has at least chrom, start and stop, the 'ftype' can be provided as the indices of the Bed elements, such as "2;3;1;-;4;6". "-" indicates missing values.
            Other file types are converted to Python objects such Bed, GeneBed and SAM.
            NOTE: Set 'ftype= None' for any text files if you don't want to convert them to objects, such as SAM, GTF and GFF format.
        '''
        # Parse arguments
        sep=kwargs.get('sep','\t')
        if ftype:
            ftype=ftype.lower()
            if ftype == 'guess':
                ftype = IO.guess(infile)
        skip=int(kwargs.get('skip',0))
        mask=kwargs.get('mask','#')
        if ftype == 'sam2bed' or ftype == 'sam2beds':
            mask = '@'
        # update converters
        IO.converters.update({'sam2bed':IO.SAMToBed,'sam2beds':IO.SAMToBeds})
        # update readers
        IO.readers.update({'fasta':IO.seqReader,'fastq':IO.seqReader,'wig':IO.wigReader,'bigwig':IO.wigReader,'sam':IO.bamReader,'bam':IO.bamReader,'bam2bed':IO.bamReader,'bam2beds':IO.bamReader})
        # for simple files: one object per line such as bed, SAM and GenePred
        if isinstance(infile,basestring) or isinstance(infile, StringFile):
            if  IO.converters.has_key(ftype) or ":" in ftype:
                if IO.converters.has_key(ftype):
                    converter = IO.converters[ftype]
                else:
                    converter = lambda x:IO.anyToBed(x,ftype)
                with IO.mopen(infile) as fh:
                    # Read lines
                    skipped=0
                    for line in fh:
                        if len(line.strip())>0:
                            if line[0]!=mask:
                                if skip==skipped:
                                    x=line.rstrip().split(sep)
                                    yield converter(x) 
                                else:
                                    skipped+=1
            # for complex files: one object in multiple lines such as Fasta, Fastq and GFF; binary files such as BAM, twobit and bigwig
            elif IO.readers.has_key(ftype):
                reader=IO.readers[ftype]
                skipped=0
                for item in reader(infile,ftype):
                    if skip==skipped:
                        yield item
                    else:
                        skipped+=1
        else:
            raise TypeError("ERROR: File type {0} is not supported!".format(ftype))
        return
    BioReader=staticmethod(BioReader)

class DB(object):
    ''' Database for fast search. '''
    def __init__(self,infile,ftype='guess',force=False,zerobased=True,**kwargs):
        ''' Initiate DB for query. '''
        self.infile = infile
        ftype = ftype.lower()
        if ftype == 'guess':
            ftype = IO.guess(infile)
        self.ftype = ftype
        self.force = force
        self.zerobased = zerobased
        self.kwargs = kwargs
        self.db = None
        self.closed = True
        #self.dbtype, self.dbfile = DB.createDB(infile,ftype,force,zerobased,**kwargs)
        #self.db = DB.open(self.dbfile,self.dbtype)
        #self.closed = False
        if isinstance(infile,basestring):
            # tabix index
            if ":" in ftype or ftype in ['bed','bed3','bedgraph','peak', 'genepred','sam','gff','vcf']:
                self.dbtype='tabix'
                self.db = TabixFile(infile,ftype,force,zerobased)
                self.dbfile = self.db.infile
            elif ftype == 'bam':
                self.dbtype='bam'
                self.dbfile = infile
                self.db = BAMFile(infile,'rb')
            elif ftype == 'wig':
                self.dbtype = 'bigwig'
                self.db = BigWigFile(infile,kwargs.get('chrom_size',None)) # need chrom size file to convert wig to bigwig
                self.dbfile = self.db.infile
            elif ftype == 'bigwig':
                self.dbtype='bigwig'
                self.dbfile = infile
                self.db = BigWigFile(infile)
            elif ftype == 'fasta':
                self.dbtype='fasta'
                self.dbfile = infile
                self.db = FastaFile(infile)
            elif ftype == '2bit':
                self.dbtype='2bit'
                self.dbfile=infile
                self.db = TwoBitFile(infile)
        if self.db is None:
            raise TypeError("ERROR: infile or file type is not valid.")
        self.closed = False
    def chromSizes(self):
        ''' Return chroms,sizes of current data. '''
        try:
            return self.db.chromSizes()
        except:
            raise TypeError("ERROR: DB type {0} has no chromSizes function.".format(self.dbtype))
    def fetch(self,chrom=None,start =None ,stop = None,strand = ".",zerobased=True,**kwargs):
        ''' fetch elements from DB. '''
        return self.db.fetch(chrom,start,stop,strand,zerobased,**kwargs)
    def pileup(self,chrom=None,start =None ,stop = None,strand = ".",zerobased=True,**kwargs):
        ''' pileup items from DB. '''
        if self.dbtype in ['bigwig','bam','tabix']:
            return self.db.pileup(chrom,start,stop,strand,zerobased,**kwargs)
        raise ValueError("ERROR: file type '{0} in  DB type '{1}' has no pileup function.".format(self.ftype,self.dbtype))
    def close(self):
        ''' close DB. '''
        if not self.closed:
            self.db.close()
    def __enter__(self):
        ''' Enter instance. '''
        return self
    def __exit__(self,type,value,traceback):
        ''' Exit instance. '''
        self.close()
    def __del__(self):
        ''' On delete. '''
        self.close()


#########################################################################
# Utils: Utilities for biological or computational calculation
#########################################################################
    
class Utils(object):
    '''
    Utilities for biological or computational calculation
    '''
    def is_float(x):
        ''' Check if a variable can be converted to float. '''
        try:
            float(x)
        except:
            return False
        else:
            return True
    is_float=staticmethod(is_float)
    def is_int(x):
        ''' Check if a variable can be converted to int. '''
        try:
            int(x)
        except:
            return False
        else:
            return True
    is_int=staticmethod(is_int)
    def is_set(v):
        ''' Check if a viarable exist or not. '''
        try:
            v
        except:
            return False
        else:
            return True
    is_set=staticmethod(is_set)
    def is_generator(x):
        ''' Check if generator. '''
        return isinstance(x,types.GeneratorType)
    is_generator=staticmethod(is_generator)
    def is_function(x):
        ''' Check if function. '''
        return isinstance(x,types.FunctionType)
    is_function=staticmethod(is_function)
    def rc(seq):
        ''' Reverse complementary sequence. '''
        comps = {'A':"T", 'C':"G", 'G':"C", 'T':"A",
                'B':"V", 'D':"H", 'H':"D", 'K':"M",
                'M':"K", 'R':"Y", 'V':"B", 'Y':"R",
                'W':'W', 'N':'N', 'S':'S'}
        return ''.join([comps[x] for x in seq.upper()[::-1]])
    rc=staticmethod(rc)
    def MW(seq):
        ''' Molecular weight of sequence. '''
        mws={'A':313.21,'C':289.19,'G':329.21,'T':304.2,'I':314.2,'N':308.95,'R':321.21,'Y':296.69,'M':301.2,'K':316.7,'S':309.2,'W':308.71,'H':302.2,'B':307.53,'D':315.54,'V':310.53,'p':79.98,'X':0,'U':290.17}
        return sum([mws[x] for x in seq.upper()])
    MW=staticmethod(MW)
    def TM(seq,Na=100):
        ''' TM value of sequence. '''
        seq=seq.upper()
        if len(seq)<25:
            tm={'A':2,'T':2,'C':4,'G':4}
            return sum([tm[x] for x in seq])
        else:
            N=float(len(seq))
            gc=(seq.count('C')+seq.count('G'))/N
            return 81.5+16.6*numpy.log10(Na/1000.0)+0.41*gc+600.0/N
    TM=staticmethod(TM)
    def GCContent(seq):
        '''Return GC content of sequence.'''
        tseq=seq.upper()
        gc=(tseq.count("G")+tseq.count("C"))/float(len(tseq)-tseq.count("N"))
        return gc 
    GCContent=staticmethod(GCContent)    
    def CpGContent(tbed,genomefile):
        ''' 
        Return the normalized CpG content. 
        Defined in (HG Roider et al., 2009).
        Normalized CpG content = CpG% / ((C%+G%)/2)^2 in the TSS flanking 500bp regions.
        '''
        seq=tbed.updownExtend(500,500).getSeq(genomefile)
        seq=seq.upper()
        CpGs=seq.count("CG")/float(len(seq))
        GCs=(seq.count("C")+seq.count("G"))/2.0/len(seq)
        return CpGs/GCs**2
    CpGContent=staticmethod(CpGContent)
    def toRNA(seq):
        ''' Convert DNA sequences to RNA sequences. '''
        return seq.upper().replace('T','U')
    toRNA=staticmethod(toRNA)
    def toDNA(seq):
        ''' Convert RNA sequences t oDNA sequences. '''
        return seq.upper().replace('U','T')
    toDNA=staticmethod(toDNA)
    def toProtein(seq,table):
        '''Translate DNA or RNA to protein according to standard translation table.'''
        seq=seq.upper().rstrip()
        if "U" in seq:
            seq=Utils.toDNA(seq)
        if len(seq)%3!=0:
            print >>sys.stderr, "Sequcence length should be 3*N."
            return None
        p=""
        for i in xrange(len(seq)/3):
            p+=table[seq[i*3:(i+1)*3]]
        return p
    toProtein=staticmethod(toProtein)
    def formatSeq(seq,length=100):
        ''' print sequence with fixed length.'''
        l=len(seq)
        n=l/length
        lstr=""
        for i in xrange(n):
            lstr+=seq[(i*length):(i*length+length)]+"\n"
        if l%length:
            lstr+=seq[(n*length):]
        return lstr.rstrip()
    formatSeq=staticmethod(formatSeq)
    def fastaToCSFasta(seq,starter='T'):
        trans= [ ['0','1','2','3'], ['1','0','3','2'], ['2','3','0','1'], ['3','2','1','0']]
        bases= {'A':0,'C':1,'G':2,'T':3}
        csf=starter
        seq=seq.upper()
        tseq=starter+seq
        for i in range(len(seq)):
            csf+=trans[bases[tseq[i]]][bases[tseq[i+1]]]
        return csf
    fastaToCSFasta=staticmethod(fastaToCSFasta)
    def csFastaToFasta(seq):
        trans=[ [0,1,2,3], [1,0,3,2], [2,3,0,1], [3,2,1,0]]
        bases={'A':0,'C':1,'G':2,'T':3}
        csbases={0:'A',1:'C',2:'G',3:'T'}
        f=seq[0]
        for i in range(len(seq)-1):
            f+=csbases[trans[bases[f[i]]][int(seq[i+1])]]
        return f[1:]
    csFastaToFasta=staticmethod(csFastaToFasta)
    def genomeSize(gversion):
        '''
        Genome size dictionary. 
        It could be either well known genome names (hg19,ce6,test,sc) or genome size file with each line like this: chrom\tlength.
        '''
        if genome.has_key(gversion):
            return genome[gversion]
        chroms = {}
        try:
            for line in IO.BioReader(gversion):
                chroms[line[0]]=int(line[1])
        except IOError:
            raise IOError('Genome size is not available. Provide a genome size file instead with each line like this: chrom\tlength. ')
        return chroms
    genomeSize=staticmethod(genomeSize)
    def chromConventor(chrom,_from,_to):
        ''' Convent chromosomes from one type to another.\n Types are 'roman':roman numbers, 'num':numbers such as 1,2 ... , 'fnum': formatted numbers such as 01,02   '''
        romans=["chrI","chrII","chrIII","chrIV","chrV","chrVI","chrVII","chrVIII","chrIX","chrX","chrXI","chrXII","chrXIII","chrXIV","chrXV","chrXVI","chrXVII","chrXVIII","chrXIX","chrXX","chrXXI","chrXXII"]
        nums=["chr1","chr2","chr3","chr4","chr5","chr6","chr7","chr8","chr9","chr10","chr11","chr12","chr13","chr14","chr15","chr16","chr17","chr18","chr19","chr20","chr21","chr22"]
        fnums=["chr01","chr02","chr03","chr04","chr05","chr06","chr07","chr08","chr09","chr10","chr11","chr12","chr13","chr14","chr15","chr16","chr17","chr18","chr19","chr20","chr21","chr22"]
        types={'roman':romans,'num':nums,'fnum':fnums}
        chroms={'roman':{},'num':{},'fnum':{}}
        for i in range(len(chrom)):
            chroms['roman'][romans[i]]=i
            chroms['num'][nums[i]]=i
            chroms['fnum'][fnums[i]]=i
        idx=chroms[_from].get(chrom,-1)
        if idx!=-1:
            return types[_to][idx]
        else:
            return chrom
    chromConventor=staticmethod(chromConventor)
    def translateTables(tabletype="standard"):
        '''Translation tables. @ for stop condons.'''
        tables={}
        tables["standard"]={
            'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L', 'TCT': 'S',
            'TCC': 'S', 'TCA': 'S', 'TCG': 'S', 'TAT': 'Y', 'TAC': 'Y',
            'TGT': 'C', 'TGC': 'C', 'TGG': 'W', 'CTT': 'L', 'CTC': 'L',
            'CTA': 'L', 'CTG': 'L', 'CCT': 'P', 'CCC': 'P', 'CCA': 'P',
            'CCG': 'P', 'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
            'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R', 'ATT': 'I',
            'ATC': 'I', 'ATA': 'I', 'ATG': 'M', 'ACT': 'T', 'ACC': 'T',
            'ACA': 'T', 'ACG': 'T', 'AAT': 'N', 'AAC': 'N', 'AAA': 'K',
            'AAG': 'K', 'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
            'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V', 'GCT': 'A',
            'GCC': 'A', 'GCA': 'A', 'GCG': 'A', 'GAT': 'D', 'GAC': 'D',
            'GAA': 'E', 'GAG': 'E', 'GGT': 'G', 'GGC': 'G', 'GGA': 'G',
            'GGG': 'G', 'TAA': '@', 'TAG': '@', 'TGA': '@'}
        return tables[tabletype]
    translateTables=staticmethod(translateTables)
    def RESite(re):
        ''' 
        Return the Restriction Enzyme cutting sequence.
        Usage:
            >print Utils.RESite('HindIII')
            AAGCTT            
        '''
        REs={'HindIII':'AAGCTT','EcoRI':'GAATTC'} # Add more if needed
        return REs.getdefault(re,'')
    RESequence=staticmethod(RESite)
    
    def cmd_exists(cmd):
        ''' Test if commond exists. '''
        return call("type " + cmd, shell=True,  stdout=PIPE, stderr=PIPE) == 0
    cmd_exists=staticmethod(cmd_exists)
    def mustexist(f):
        ''' check if a file exists, or raise an error. '''
        if not os.path.isfile(f):
            raise ValueError('ERROR: {0} does not exist.'.format(f)) 
    mustexist=staticmethod(mustexist)


#########################################################################
# Software: Commonly used software for NGS data analysis
#########################################################################

class Pipeline(object):
    Path = {}
    Path['aspera'] = os.path.expanduser("~/.aspera/connect/bin/ascp") 
    def init(paths):
        '''
        Initiation of Pipeline environment.
        Parameters:
            env: dict or string
                Provide a dictionary of file for the tool paths.
        Example 1:
            paths = {}
            paths['apsera'] = "~/.aspera/connect/bin/ascp"
            ...
            Pipeline.init(paths)
            Pipeline.aspera(...,...)
        Example 2:
            tools.cfg:
            ==============================
            aspera    $HOME/.aspera/connect/bin/ascp
            bowtie    ~/bin/bowtie
            ==============================
            Pipeline.init('tools.cfg')
            Pipeline.aspera(...,...)
        '''
        if isinstance(paths,str):
            for line in IO.BioReader(paths,sep=None):
                path = os.path.expandvars(os.path.expanduser(line[1]))
                Utils.mustexist(path)
                Pipeline.Path[line[0]] = line[1]
        else:
            for key,value in paths.iteritems():
                path = os.path.expandvars(os.path.expanduser(value))
                Utils.mustexist(path)
                Pipeline.Path[key] = path
    init=staticmethod(init)
    def aspera(link,outputdir="."):
        '''
        aspera is a High-speed file transfer software. It is used to download sequencing data from NCBI SRA database.
        Parameters:
            link: string
                sra link starts from "/sra"
            outputdir: string:
                output directory
        
        Usage:
            Pipeline.aspera('/sra/sra-instant/reads/ByExp/sra/SRX/SRX100/SRX100293/SRR351390/','.')
        
        Corresponding Shell example:
            ~/.aspera/connect/bin/ascp -i ~/.aspera/connect/etc/asperaweb_id_dsa.putty -k1 -QTr -l200m anonftp@ftp-private.ncbi.nlm.nih.gov:/sra/sra-instant/reads/ByExp/sra/SRX/SRX100/SRX100292/SRR351389/ ./
        '''
        if len(link) == 0: # sra link, skip
            sys.stderr.write('No sra link. Skipped.\n')
            return
        if not link.startswith("/sra"):
            link = link[link.find("/sra"):]

        outputdir = os.path.expanduser(outputdir)
        if not Pipeline.Path.has_key('aspera'):
            raise OSError('ERROR: aspera path is not provided!')
        aspera = Pipeline.Path['aspera']
        putty = aspera[:aspera.find('/bin')] + "/etc/asperaweb_id_dsa.putty"

        sys.stderr.write('Starting apsera ...\n')             
        cmd = " ".join([aspera,'-i', putty, '-k1', '-QTr', '-l200m', 'anonftp@ftp-private.ncbi.nlm.nih.gov:'+link, outputdir])
        
        sys.stderr.write("Running command: {0}\n".format(cmd))
        p = Popen( cmd.split(), stdin=None,stdout=None,stderr=sys.stderr)
        p.communicate()
    aspera=staticmethod(aspera)
    def fastq_dump(srafile, prefix= None, paired = False, overwrite=False,clean=False):
        '''
        Dump reads from SRA compressed file.
        Parameters:
            srafile: string
                srafile such as SRRXXXX.sra
            prefix: string
                prefix of output file(s)
            paired: bool
                paired end sequencing or not
            overwrite: bool
                overwrite old files or not
            clean: bool
                clean sra file to save space or not. 

        Shell example: 1 single end reads
            fastq-dump SRR351390/SRR351390.sra
        Shell example: 2 paired end reads
            fastq-dump --split-3 SRR351390/SRR351390.sra
        Usage:
            Pipeline.fastq_dump('SRR351390/SRR351390.sra',"HDAC3_ChIP_ZT22-2")
            Pipeline.fastq_dump('SRR351390/SRR351390.sra',"HDAC3_ChIP_ZT22-2",False)
        '''
        if len(srafile) == 0:
            sys.stderr.write("No input sra file. Skipped.\n")
            return
        
        sys.stderr.write("Starting fastq-dump ...\n")
        fastq_dump = Pipeline.Path.get('fastq-dump','fastq-dump')
        if not Utils.cmd_exists('fastq-dump'):
            raise ValueError('ERROR: fastq-dump cannot be found.')

        srafile = os.path.expanduser(srafile)

        # check if output files are existed.
        outprefix = prefix and prefix or os.path.splitext(os.path.basename(srafile))[0]
        if paired and os.path.isfile(outprefix+"_1.fastq") and os.path.isfile(outprefix+"_2.fastq"):
            if overwrite:
                os.remove(outprefix+"_1.fastq")
                os.remove(outprefix+"_2.fastq")
            else:
                sys.stderr.write("Skipped: output files {0} {1} exist.\n".format(outprefix+"_1.fastq",outprefix+"_2.fastq"))
                return
        elif not paired and os.path.isfile(outprefix+".fastq"):
            if overwrite:
                os.remove(outprefix+".fastq")
            else:
                sys.stderr.write("Skipped: output file {0} exists.\n".format(outprefix+".fastq"))
                return
            
        print "paired",paired
        if paired:
            sys.stderr.write("Running command: fastq-dump --split-3 {0}\n".format(srafile))
            p = call('fastq-dump --split-3 '+ srafile, shell=True)
        else:
            sys.stderr.write("Running command: fastq-dump {0}\n".format(srafile))
            p = call('fastq-dump '+srafile, shell=True)
        # Rename file
        if prefix is not None:
            fn = os.path.basename(srafile).replace('sra','fastq')
            os.rename(fn,prefix+".fastq")
        # clean sra file
        if clean:
            os.remove(srafile)
            sys.stderr.write("Clean SRA file: {0}\n".format(srafile))
    fastq_dump=staticmethod(fastq_dump)
    def bowtie(genome, fqfile,fqfile2=None, samfile=None, paras="-m 1 -v 2 -p 6",overwrite=False):
        ''' 
        Bowtie aligner.
        Shell example:
            bowtie ~/Data/mm9/mm9 -m 1 -v 2 -p 6 -S input.fastq output.sam
        Usage:
            Pipeline.bowtie("~/Data/mm9/mm9","input.fastq", None, "output.sam")
        '''
        sys.stderr.write("Starting bowtie ...\n")
        if not Utils.cmd_exists('bowtie'):
            raise ValueError('ERROR: bowtie cannot be found.')

        genome = os.path.expanduser(genome)
        if samfile is None:
            samfile = os.path.splitext(fqfile)[0]+".sam"
        else:
            samfile = os.path.expanduser(samfile)
        # check if samfile exists
        if os.path.isfile(samfile):
            if overwrite:
                os.remove(samfile)
            else:
                sys.stderr.write("Skipped: output file: {0} exists.\n".format(samfile))
                return 

        # check if fastq file exists
        fqfile = os.path.expanduser(fqfile)
        Utils.mustexist(fqfile)
        if fqfile2 is not None: 
            fqfile2 = os.path.expanduser(fqfile2)
            Utils.mustexist(fqfile2)
        # check if genome exists
        Utils.mustexist(genome+".1.ebwt")
        
        # run bowtie
        if fqfile2:
            cmd = "bowtie {0} {1} -1 {2} -2 {3} -S {4}".format(genome, paras, fqfile, fqfile2, samfile)
        else:
            cmd = "bowtie {0} {1} {2} -S {3}".format(genome, paras, fqfile,samfile)
        sys.stderr.write("Running command: {0}\n".format(cmd))
        p = Popen(cmd.split(), stdin=None, stdout=PIPE, stderr=PIPE)
        pstdout, pstderr = p.communicate()
        # check return code
        rc = p.returncode
        if rc < 0:
            os.remove(samfile)

        # Writing log file
        logfile = os.path.splitext(fqfile)[0]+"_bowtie.log"
        sys.stderr.write("Writing log information into {0}.\n".format(logfile))
        with open(logfile,'w') as ofh:
            print >> ofh, pstderr
    bowtie=staticmethod(bowtie)
    def bowtie2(genome, fqfile,fqfile2=None, samfile=None, paras="--fast -k 1",overwrite=False):
        ''' 
        Bowtie version 2
        bowtie2 [options]* -x <bt2-idx> {-1 <m1> -2 <m2> | -U <r>} [-S <sam>]
        '''
        sys.stderr.write("Starting bowtie2 ...\n")
        if not Utils.cmd_exists('bowtie2'):
            raise ValueError('ERROR: bowtie2 cannot be found.')

        genome = os.path.expanduser(genome)
        if samfile is None:
            samfile = os.path.splitext(fqfile)[0]+".sam"
        else:
            samfile = os.path.expanduser(samfile)
        # check if samfile exists
        if os.path.isfile(samfile):
            if overwrite:
                os.remove(samfile)
            else:
                sys.stderr.write("Skipped: output file: {0} exists.\n".format(samfile))
                return 

        # check if fastq file exists
        fqfile = os.path.expanduser(fqfile)
        Utils.mustexist(fqfile)
        if fqfile2 is not None: 
            fqfile2 = os.path.expanduser(fqfile2)
            Utils.mustexist(fqfile2)
        # check if genome exists
        Utils.mustexist(genome+".1.bt2")
        
        # run bowtie
        if fqfile2:
            cmd = "bowtie2 {0} -x {1} -1 {2} -2 {3} -S {4}".format(genome, paras, fqfile, fqfile2, samfile)
        else:
            cmd = "bowtie2 {0} -x {1} -U {2} -S {3}".format(genome, paras, fqfile,samfile)
        sys.stderr.write("Running command: {0}\n".format(cmd))
        p = Popen(cmd.split(), stdin=None, stdout=PIPE, stderr=PIPE)
        pstdout, pstderr = p.communicate()
        rc = p.returncode
        if rc < 0:
            os.remove(samfile)

        # Writing log file
        logfile = os.path.splitext(fqfile)[0]+"_bowtie.log"
        sys.stderr.write("Writing log information into {0}.\n".format(logfile))
        with open(logfile,'w') as ofh:
            print >> ofh, pstderr
    bowtie2=staticmethod(bowtie2)
    def bam_index(samfile,bamfile= None,overwrite=False):
        '''
        convert samfile to indexed bamfile.
        Shell example:
            samtools view test.sam |samtools sort - test
            samtools index test.bam
        Usage:
            Pipeline.bam_index('test.sam','test.bam')
        '''
        sys.stderr.write("Starting samtools index ...\n")
        if not Utils.cmd_exists('samtools'):
            raise ValueError('ERROR: samtools cannot be found.')
        samfile = os.path.expanduser(samfile)
        Utils.mustexist(samfile)
        if bamfile is None:
            bamfile = os.path.splitext(samfile)[0]+".bam"
        bamfile = os.path.expanduser(bamfile)

        # check if bamfile exists
        if os.path.isfile(bamfile) and os.path.isfile(bamfile+".bai"):
            if overwrite:
                os.remove(bamfile)
                os.remove(bamfile+".bai")
            else:
                sys.stderr.write("Skipped: outfile {0} exists.\n".format(bamfile))
                return 
        prefix = os.path.splitext(bamfile)[0]
        logfh  = open(prefix+".log",'w')
        
        # sam to unsorted bam
        cmd = 'samtools view -Sub {0} | samtools sort - {1}'.format(samfile,prefix)
        sys.stderr.write("Running command: {0}\n".format(cmd))
        p = Popen(['samtools', 'view', '-Sb', samfile],stdin=None, stdout=PIPE, stderr=logfh)
        p2 = Popen(['samtools', 'sort', '-', prefix], stdin=p.stdout,stdout= None, stderr=logfh)
        p.stdout.close()
        p2.communicate()

        
        # index bam
        cmd = "samtools index {0}".format(bamfile)
        sys.stderr.write("Running command: {0}\n".format(cmd))
        p = Popen(cmd.split(), stdin = None, stdout=None,stderr=logfh)
        pstderr = p.communicate()[1]
        logfh.close()
    bam_index=staticmethod(bam_index)
    def macs14(treatment, control, prefix, paras='-f BAM -g mm',overwrite=False):
        '''
        MACS version 1.4
        Shell example:
            macs14 -t HDAC3_ChIP_ZT10-1.bam -c Liver_input_ZT10.bam -f BAM -g hs -n HDAC3_ChIP_ZT10-1
        Usage:
            Pipeline.macs14('HDAC3_ChIP_ZT10-1.bam', 'Liver_input_ZT10.bam', 'HDAC3_ChIP_ZT10-1', '-f BAM -g hs)
        '''
        sys.stderr.write("Starting macs14 ...\n")
        if not Utils.cmd_exists('macs14'):
            raise ValueError('ERROR: macs14 cannot be found.')
        treatment = os.path.expanduser(treatment)
        control = os.path.expanduser(control)
        
        # check if output file exists
        if os.path.isfile(prefix+"_peaks.bed"):
            if overwrite:
                os.remove(prefix+"_peaks.bed")
            else:
                sys.stderr.write("Skipped: output file {0}_peaks.bed exists.\n".format(prefix))
                return

        logfile = os.path.splitext(treatment)[0]+"_macs14.log"
        cmd = 'macs14 -t {0} -c {1}  -n {2} {3}'.format(treatment,control, prefix, paras)
        
        # run MACS
        sys.stderr.write("Running command: {0}\n".format(cmd))
        p = Popen(cmd.split(),stdin= None, stdout=PIPE,stderr=PIPE)
        pstdout, pstderr = p.communicate()
        if pstderr is not None:
            with open(logfile,'w') as ofh:
                print >>ofh, pstderr
            sys.stderr.write("Writing log information into {0}.\n".format(logfile))
            
        # create pdf file is _model.r exists
        if os.path.isfile(prefix+"_model.r"):
            sys.stderr.write("Draw pdf for {0}.\n".format( prefix+"_model.r"))
            p = Popen(['Rscript', prefix+"_model.r"],stdin=None, stdout=PIPE,stderr=PIPE)
            pstdout, pstderr = p.communicate()
        else:
            sys.stderr.write("MACS14: No model is built for {0}.\n".format(prefix))
    macs14=staticmethod(macs14)
    def macs2(treatment, control, prefix, paras='-f BAM -g mm'):
        '''
        MACS version 2
        Shell example:
            macs2 callpeak -t HDAC3_ChIP_ZT10-1.bam -c Liver_input_ZT10.bam -f BAM -g hs -n HDAC3_ChIP_ZT10-1
        Usage:
            Pipeline.macs2('HDAC3_ChIP_ZT10-1.bam', 'Liver_input_ZT10.bam','HDAC3_ChIP_ZT10-1','-f BAM -g hs')
        '''
        sys.stderr.write("Starting macs2 ...\n")
        if not Utils.cmd_exists('macs2'):
            raise ValueError('ERROR: macs2 cannot be found.')

        treatment = os.path.expanduser(treatment)
        control = os.path.expanduser(control)
        
        # check if output file exists
        if os.path.isfile(prefix+"_peaks.bed"):
            if overwrite:
                os.remove(prefix+"_peaks.bed")
            else:
                sys.stderr.write("Skipped: output file {0}_peaks.bed exists.\n".format(prefix))
                return
        
        logfile = os.path.splitext(treatment)[0]+".log"
        cmd = 'macs2 callpeak -t {0} -c {1} -n {2} {3}'.format(treatment,control,prefix,paras)
        
        # run MACS
        sys.stderr.write("Running command: {0}\n".format(cmd))
        p = Popen(cmd.split(),stdin= None, stdout=PIPE,stderr=PIPE)
        pstdout, pstderr = p.communicate()
        if pstderr is not None:
            with open(logfile,'w') as ofh:
                print >>ofh, pstderr
            sys.stderr.write("Writing log information into {0}.".format(logfile))
        # create pdf file is _model.r exists
        if os.path.isfile(prefix+"_model.r"):
            sys.stderr.write("Draw pdf for {0}_model.r.\n".format( prefix))
            p = Popen(['Rscript', prefix+"_model.r"],stdin=None, stdout=PIPE,stderr=PIPE)
            pstdout, pstderr = p.communicate()
        else:
            sys.stderr.write("MACS2: No model is built for {0}.\n".format(prefix))
    macs2=staticmethod(macs2)
    def bam2wig(treatment,Control,gsize='~/Data/mm9/mm9.sizes',paras="-n 10 -e 200",overwrite=False):
        '''
        Covert bam file to bigwig file.
        '''
        sys.stderr.write("Starting bam to bigwig conversion ...\n")
        # check if output file exists
        if not overwrite:
            existed = []
            for t in treatment:
                wigfile = os.path.splitext(os.path.basename(t))[0]+("_"+os.path.splitext(os.path.basename(Control))[0] if Control else "")+".wig"
                bwfile = os.path.splitext(wigfile)[0]+".bw"
                # Do not conver t if t.wig or t.bw exists
                if os.path.isfile(wigfile) or os.path.isfile(bwfile):
                    existed.append(t)
            for t in existed:
                treatment.remove(t)
                sys.stderr.write("Skipped: output file {0} or {1} exists.\n".format(wigfile,bwfile))

        # check bam files
        if len(treatment) == 0: return
        for i in range(len(treatment)):
            treatment[i] = os.path.expanduser(treatment[i])
            Utils.mustexist(treatment[i])
        Control = os.path.expanduser(Control)
        gsize = os.path.expanduser(gsize)
        Utils.mustexist(Control)
        Utils.mustexist(gsize)
        
        # run wBamToWig.py
        logfile = os.path.splitext(os.path.basename(Control))[0]+"_bam2wig.log"
        cmd = 'wBamToWig.py -t {0} -c {1} {2}'.format(" ".join(treatment),Control,paras)
        sys.stderr.write('Running command: {0}\n'.format(cmd))
        p = Popen(cmd.split(),stdin=None,stdout=PIPE,stderr=PIPE)
        pstdout, pstderr = p.communicate()
        with open(logfile,'w') as ofh:
            print >>ofh, pstderr
        
        # wig to bigwig
        sys.stderr.write('Coverting wiggle files to bigwig files.\n')
        for t in treatment:
            prefix = os.path.splitext(os.path.basename(t))[0]
            if Control:
                prefix += "_"+os.path.splitext(os.path.basename(Control))[0]
            if os.path.isfile(prefix+".bw"):
                sys.stderr.write("Skipped: {0}.bw exists.\n".format(prefix))
            else:
                sys.stderr.write(prefix+".wig " + "->" + prefix+".bw\n")
                BigWigFile.wigToBigWig(prefix+".wig",gsize,prefix+".bw")
    bam2wig=staticmethod(bam2wig)  
    def Mapping_thread(samples,paras):
        '''
        Download reads from GEO and do mapping and indexing.
        '''
        # Parse parameters
        genome      = paras.get('genome','~/Data/mm9/mm9') # for bowtie
        gsize       = paras.get('gsize','~/Data/mm9/mm9.sizes') # for bam2wig
        paired      = eval(paras.get('paired','False'))
        aligner     = paras.get('aligner',['bowtie','-m 1 -v 2 -p 6'])

        # check if sra link, download files if true
        threads = []
        for prefix in samples:
            srafile = samples[prefix]
            if srafile.startswith('/sra') and srafile.endswith('.sra'): # make sure it is a full link
                t = threading.Thread(target = Pipeline.aspera, args = (srafile,))
                t.start()
                threads.append(t)
                samples[prefix] = os.path.basename(srafile)
        for t in threads:
            t.join()     
        
        # fastq-dump
        threads = []
        for prefix in samples:
            srafile = samples[prefix]
            t = threading.Thread(target = Pipeline.fastq_dump, args=(srafile,paired,prefix))
            t.start()
            threads.append(t)        
        for t in threads:
            t.join()
            
        # bowtie
        # bowtie(genome, fqfile,fqfile2=None, samfile=None, paras="-m 1 -v 2 -p 6",overwrite=False):
        threads = []
        if aligner[0] == 'bowtie':
            target = Pipeline.bowtie
        elif aligner[0] == 'bowtie2':
            target = Pipeline.bowtie2
        else:
            raise ValueError("ERROR: Aligner {0} cannot be found.".format(aligner[0]))
        for prefix in samples:
            t = threading.Thread(target = target, args=(genome, prefix+".fastq",None, None,aligner[1]))
            t.start()
            threads.append(t)        
        for t in threads:
            t.join()

        # bam_index
        threads = []
        for prefix in samples:
            t = threading.Thread(target = Pipeline.bam_index, args=(prefix+".sam",))
            t.start()
            threads.append(t)        
        for t in threads:
            t.join()
    Mapping_thread=staticmethod(Mapping_thread)
    def ChIP_thread(samples,Control,paras): # macs='macs14',effectsize='mm',gsize='~/Data/mm9/mm9.sizes',normedto=10,fraglen=200):
        '''
        Given a list of samples and their pair information, run ChIPSeq pipeline.
        Parameters:
            samples: {prefix:srafile}
                SRA link: {'HDAC3_Liver': '/sra/sra-instant/reads/ByExp/sra/SRX/SRX100/SRX100300/SRR351397/SRR351397/SRR351397.sra'}            
                SRA file: {'HDAC3_Liver': 'SRR351397.sra'}
                Fastq file: {'HDAC3_Liver': ''}        
            Control: prefix
            paras:
                genome: bowtie indexed genome (~/Data/mm9/mm9)
                macs: macs version
                gsize: genome size for macs.
                normedto: number of reads normalized to for wBamToWig.py
                fraglen: fragment length for wBamToWig.py
        '''
        # Parse parameters
        genome      = paras.get('genome','~/Data/mm9/mm9') # for bowtie
        gsize       = paras.get('gsize','~/Data/mm9/mm9.sizes') # for bam2wig
        paired      = eval(paras.get('paired','False'))
        aligner     = paras.get('aligner',['bowtie','-m 1 -v 2 -p 6'])
        bamtowig     = paras.get('bam2wig','-n 10 -e 200')
        peakcalling = paras.get('peakcalling',['macs14','-f BAM -g mm'])

        # check if sra link, download files if true
        threads = []
        for prefix in samples:
            srafile = samples[prefix]
            if srafile.startswith('/sra') and srafile.endswith('.sra'): # make sure it is a full link
                t = threading.Thread(target = Pipeline.aspera, args = (srafile,))
                t.start()
                threads.append(t)
                samples[prefix] = os.path.basename(srafile)
        for t in threads:
            t.join()     
        
        # fastq-dump
        threads = []
        for prefix in samples:
            srafile = samples[prefix]
            t = threading.Thread(target = Pipeline.fastq_dump, args=(srafile,prefix,paired))
            t.start()
            threads.append(t)        
        for t in threads:
            t.join()
            
        # bowtie
        # bowtie(genome, fqfile,fqfile2=None, samfile=None, paras="-m 1 -v 2 -p 6",overwrite=False):
        threads = []
        if aligner[0] == 'bowtie':
            target = Pipeline.bowtie
        elif aligner[0] == 'bowtie2':
            target = Pipeline.bowtie2
        else:
            raise ValueError("ERROR: Aligner {0} cannot be found.".format(aligner[0]))
        for prefix in samples:
            t = threading.Thread(target = target, args=(genome, prefix+".fastq",None, None,aligner[1]))
            t.start()
            threads.append(t)        
        for t in threads:
            t.join()

        # bam_index
        threads = []
        for prefix in samples:
            t = threading.Thread(target = Pipeline.bam_index, args=(prefix+".sam",))
            t.start()
            threads.append(t)        
        for t in threads:
            t.join()
        
        # run macs and wBamTowig.py
        threads = []
        treatment = samples.keys()
        treatment.remove(Control)
        t = threading.Thread(target = Pipeline.bam2wig, args=([p+".bam" for p in treatment],Control+".bam", gsize, bamtowig))
        t.start()
        threads.append(t)
        if peakcalling[0] == 'macs14':
            target = Pipeline.macs14
        elif peakcalling[0] == 'macs2':
            target = Pipeline.macs2
        else:
            raise ValueError("ERROR: Peakcalling software {0} cannot be found.".format(peakcalling[0]))
        for p in treatment:
            t = threading.Thread(target = target, args=(p+".bam",Control+".bam",p,peakcalling[1]))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        
        sys.stderr.write("ChIP pipeline for {0} is finished.\n".format(Control))
    ChIP_thread=staticmethod(ChIP_thread)
    def ChIP_Project(cfgfile, clean= False):
        '''
        Read config file and run ChIP pipeline accordingly.
        Example config file: HDAC.cfg
            ###################################################
            # bowtie index genome prefix
            @genome ~/Data/mm9
            # genome size file in format: chrN\tlength
            @gsize  ~/Data/mm9/mm9.sizes
            
            # paired end or not
            @paired False

            # Aligner: bowtie (default) or bowtie2
            # When paired end: @fastq-dump  paired
            # example parameter for bowtie: -m 1 -v 2 -p 6
            # example parameter for bwotie2: --fast -k 1
            @aligner    bowtie  -m 1 -v 2 -p 6
            
            # macs version: macs14 (default) or macs2
            # example parameter -f BAM -g mm
            @peakcalling    macs14 -f BAM -g mm
            
            # bam2wig parameter: default is "-n 10 -e 200"
            @bam2wig    -n 10 -e 200
            
            # data
            SRR351397.sra    HDAC1_ChIP_ZT22    Control_ChIP_ZT22
            SRR351398.sra    HDAC2_ChIP_ZT22    Control_ChIP_ZT22
            SRR351399.sra    HDAC3_ChIP_ZT22    Control_ChIP_ZT22    IgG_ChIP_ZT22
            SRR351400.sra    Control_ChIP_ZT22
            SRR351401.sra    IgG_ChIP_ZT22
            ###################################################
        Usage:
            Pipeline.ChIP_Project('HDAC.cfg')
        '''
        pairs = {}
        samples = {}
        paras = {'genome':'~/Data/mm9/mm9','gsize':'~/Data/mm9/mm9.sizes', 'paired':'False','aligner':['bowtie','-m 1 -v 2 -p 6'],'peakcalling':['macs14','-f BAM -g mm'],'bam2wig':'-n 10 -e 200'}

        # read samples
        for i,line in enumerate(IO.BioReader(cfgfile)):
            if line[0].startswith('@'): # software and parameters
                print line
                if len(line) == 2:
                    paras[line[0].lstrip('@')] = line[1]
                else:
                    paras[line[0].lstrip('@')] = line[1:] 
            elif len(line) == 2: # Control
                samples[line[1]] = line[0]
            elif len(line) > 2: # treatment
                samples[line[1]] = line[0]
                for control in line[2:]:
                    pairs.setdefault(control,[])
                    pairs[control].append(line[1])
            else:
                if len(line)>0:
                    raise ValueError("ERROR: Cannot parse config file {0} at line:\n '{1}'.".format(cfgfile,i),"\t".join(line))

        # run pipeline for each pairs
        threads = []
        for Control in pairs:
            subsamples = {Control:samples[Control]}
            for p in pairs[Control]:
                subsamples[p] = samples[p]
            t = threading.Thread(target = Pipeline.ChIP_thread, args=(subsamples,Control,paras)) 
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        # finish
        print >> sys.stderr, "ChIPSeq project from {0} is finished.".format(cfgfile) 
    ChIP_Project=staticmethod(ChIP_Project)       
    def Mapping_Project(cfgfile, clean= False):
        samples = {}
        paras = {'genome':'~/Data/mm9/mm9','gsize':'~/Data/mm9/mm9.sizes', 'paired':'False','aligner':['bowtie','-m 1 -v 2 -p 6']}

        # read samples
        for line in IO.BioReader(cfgfile):
            if line[0].startswith('@'): # software and parameters
                print line
                if len(line) == 2:
                    paras[line[0].lstrip('@')] = line[1]
                else:
                    paras[line[0].lstrip('@')] = line[1:] 
            elif len(line) == 2: # Control
                samples[line[1]] = line[0]
            else:
                if len(line)>0:
                    raise ValueError("ERROR: Cannot parse config file {0} at line:\n '{1}'.".format(ctgfile),"\t".join(line))

        # run pipeline for each pairs
        for s in samples:
            print s+":\t"+samples[s]
        threads = []
        t = threading.Thread(target = Pipeline.Mapping_thread, args=(samples,paras)) 
        t.start()
        threads.append(t)
        for t in threads:
            t.join()

        # finish
        print >> sys.stderr, "Mapping project from {0} is finished.".format(cfgfile) 
    Mapping_Project=staticmethod(Mapping_Project)

# ------------------------------------
# Main
# ------------------------------------

if __name__=="__main__":
    if len(sys.argv)==1:
        sys.exit("Example:"+sys.argv[0]+" file1 file2... ")
    for item in IO.BioReader(sys.argv[1],ftype='bed'):
        print item

