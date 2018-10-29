import pysam
import os
import logging
import glob


"""
Samtools functions required for conversion from bam to fastq. 
"""
def collate(ifile, ofile):
    """
    Collate bam file

    :param ifile: input bam
    :param ofile: output collated bam
    """

    logging.info('collating bam file '+str(ifile))

    pysam.collate("-o", ofile, ifile)


def fastq(ifile, ofile1, ofile2):
    """
    :param ifile: input bam file
    :param ofile1: first file of fastq pair
    :param ofile2: second file of fastq pair
    """

    logging.info('generating fastq file for '+str(ifile))

    pysam.fastq('-1', ofile1,
                '-2', ofile2,
                    '-n',
                    ifile)