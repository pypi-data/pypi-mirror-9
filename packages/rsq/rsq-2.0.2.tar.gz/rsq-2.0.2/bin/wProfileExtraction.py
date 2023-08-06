#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Last-modified: 19 Mar 2015 03:17:48 PM
#
#         Module/Scripts Description
# 
# Copyright (c) 2014 Yunfei Wang <yfwang0405@gmail.com>
#
#   __     __           __     _  __          __               
#   \ \   / /          / _|   (_) \ \        / /               
#    \ \_/ /   _ _ __ | |_ ___ _   \ \  /\  / /_ _ _ __   __ _ 
#     \   / | | | '_ \|  _/ _ \ |   \ \/  \/ / _` | '_ \ / _` |
#      | || |_| | | | | ||  __/ |    \  /\  / (_| | | | | (_| |
#      |_| \__,_|_| |_|_| \___|_|     \/  \/ \__,_|_| |_|\__, |
#                                                         __/ |
#                                                        |___/
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
# python modules
# ------------------------------------

import os
import sys
import numpy
import pysam
import argparse
import itertools
from bisect import bisect_left,bisect_right
from ngslib import IO,BigWigFile

# ------------------------------------
# constants
# ------------------------------------

# ------------------------------------
# Misc functions
# ------------------------------------

def argParser():
    ''' Parse arguments. '''
    p=argparse.ArgumentParser(description='Convert BAM file to Wiggle file. This is for PARS data analysis. The BAM file is sorted and indexed. See http://rsqwiki.appspot.com/mapping for details. Contact Yunfei Wang to report any bugs (yfwang0405@gmail.com).',epilog='dependency ngslib')
    p._optionals.title = "Options"
    p.add_argument("-i","--input",dest="input",type=str,metavar="GM12878_S1.bam", required=True, nargs='+',help="Sorted and indexed BAM file(s).")
    p.add_argument("-a","--anno",dest="anno",type=str,metavar="hg19_RefSeq.genepred",required=True,help="Gene annotation file in genepred format.")
    p.add_argument("-s","--shift",dest="shift",type=int,metavar='-1',default=-1,help="Read shift to enzyme recognition site. [default=-1 for PARS technology]")
    p.add_argument("-o",dest="outdir",type=str,metavar="ourputdir",default=".",help="Directory to put wiggle file(s). [default= \".\"].")
    if len(sys.argv)==1:
        sys.exit(p.print_help())
    args = p.parse_args()
    return args

def BAMToWig(bfile,outdir):
    sname=os.path.basename(bfile)
    sname=os.path.splitext(sname)[0]
    sam = pysam.Samfile(bfile,'rb')
    bwfs = {'+':open(outdir+"/"+sname+"_plus.wig",'w'),'-':open(outdir+"/"+sname+"_minus.wig",'w')}
    for strand in bwfs:
        bwfs[strand].write("track type=wiggle_0 name={0}_{1}\n".format(sname,strand))
    chroms = {}
    shift = args.shift
    for chrom in sorted(gene_in_chroms):
        chrlen = sam.lengths[bisect_left(sam.references,chrom)]
        chroms[chrom] = chrlen
        depth = {'+':numpy.zeros(chrlen),'-':numpy.zeros(chrlen)}
        # fetch reads mapped to chrom
        for gid in itertools.chain([chrom],gene_in_chroms[chrom]):
            offsets,starts,strand = genes[gid]
            for read in sam.fetch(gid):
                idx = bisect_right(offsets,read.pos)-1
                pos = starts[idx]+read.pos-offsets[idx]
                gstrand = (strand == '+')^read.is_reverse and '+' or '-'# gstrand = '+' if strand == read.strand else '-'
                pos += gstrand=='+' and shift or -shift # plus strand -1 , minus strand +1
                depth[gstrand][pos] += 1
        # report wig file
        for strand,bwf in bwfs.iteritems():
            bwf.write("variableStep chrom={0}\n".format(chrom))
            for i in numpy.nonzero(depth[strand])[0]:
                bwf.write("{0}\t{1}\n".format(i,depth[strand][i]))
    sam.close()
    for bwf in bwfs.values():
        bwf.close()

# ------------------------------------
# Classes
# ------------------------------------

# ------------------------------------
# Main
# ------------------------------------

if __name__=="__main__":
    args=argParser()

    # Read gene annotation
    print >>sys.stderr, "Reading gene annotation file:", args.anno
    timestart = time.time()
    genes = {}
    gene_in_chroms = {}
    for gene in IO.BioReader(args.anno,ftype='genepred'):
        offsets = [0]
        starts = []
        for exon in gene.exons():
            starts.append(exon.start)
            offsets.append(offsets[-1]+exon.length())
        genes[gene.id] = (offsets,starts,gene.strand)
        gene_in_chroms.setdefault(gene.chrom,[])
        gene_in_chroms[gene.chrom].append(gene.id)
    print >>sys.stderr, "Finished in {0}s.\n".format(time.time()-timestart)
        
    # read BAM file
    print >>sys.stderr, "BAM->Wiggle conversion ..."
    for bfile in args.input:
        print >> sys.stderr, "Processing BAM file: {0}".format(bfile),
        timestart = time.time()
        BAMToWig(bfile,args.outdir)
        print >> sys.stderr, "Finished in {0}s.".format(time.time()-timestart)
    
    # Wiggle to BigWig conversion
    print >>sys.stderr, "Covert Wiggle files to BigWig files ..."
    timestart = time.time()
    with open(outdir+"/chrom.sizes",'w') as fh:
        for chrom,chrlen in chroms.iteritems():
            fh.write("{0}\t{1}\n".format(chrom,chrlen))
    for fname in os.listdir(outdir):
        bwfname = fname[:-3]+'.bw'
        if fname.endswith('wig') and not os.path.isfile(bwfname):
            BigWigFile.wigToBigWig(fname,outdir+"/chrom.sizes",bwfname)
            print >>sys.stderr, "Finished {0} -> {1}.".format(fname,bwfname)
    print >> sys.stderr, "Finished in {0}s.".format(time.time()-timestart)
    
    
