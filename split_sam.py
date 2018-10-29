import os
import pysam
import argparse
import warnings
import pandas as pd
import re
import io
import subprocess

class SplitBam(object):
    """
    calculate reads per bin from the input bam file
    """

    def __init__(self, bam, odir, chromosomes, barcode_csv):
        self.bam = bam

        self.odir = odir

        if chromosomes:
            self.chromosomes = chromosomes
        else:
            self.chromosomes = self.__get_chr_names()

        self.bam = self.__get_bam_reader()
        self.chr_lengths = self.__get_chr_lengths()

        # self.mapq_threshold = mapq
        #
        self.barcodes = self.__get_barcodes(barcode_csv)

    def __get_barcodes(self, barcode_file):
        df = pd.read_csv(barcode_file)
        return set(df.barcode.tolist())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # clean up output if there are any exceptions
        # if exc_type and os.path.exists(self.output):
        #     os.remove(self.output)
        pass

    def __get_chr_lengths(self):
        """ returns dict with chromosome names and lengths
        :returns dictionary with chromosome name (str) and lengths(int)
        :rtype dictionary
        """
        names = self.bam.references
        lengths = self.bam.lengths
        return {name: length for name, length in zip(names, lengths)}

    def __get_bam_reader(self):
        """returns pysam bam object
        :returns pysam bam object
        """
        return pysam.AlignmentFile(self.bam, 'rb')

    def __get_chr_names(self):
        """extracts chromosome names from the bam file  CCTACACTCGATCCGG-1_1.fq.gz
        :returns list of chromosome names
        :rtype list
        """
        return self.bam.references

    def __fetch(self, chrom, start, end):
        """returns iterator over reads in the specified region
        :param chrom: chromosome name (str)
        :param start: bin starting pos (int)
        :param end: bin end pos (int)
        :returns iterator over reads
        """
        return self.bam.fetch(chrom, start, end)

        # if not pileupobj.is_duplicate and \
        #         pileupobj.mapping_quality >= self.mapq_threshold:
        #     return False

    def __get_file_for_tag(self, tag_to_file_map, tag_value):
        # TODO make a class for this functionality
        """
        Get a file handle to a file in the specified output dir,
        for writing alignments with the specified tag_value.

        :param tag_to_file_map: map from tag value to file handler
        :param tag_value: tag value
        :param odir: directory where the file should be written
        :param alignment_file: handle to the alignment file
        :return: File handle for the specified tag value.
        """
        if tag_value not in tag_to_file_map.keys():
            tag_file_name = os.path.join(self.odir, tag_value + ".bam")
            file_handle = pysam.AlignmentFile(tag_file_name, "wb", template=self.bam)
            tag_to_file_map[tag_value] = file_handle

        return tag_to_file_map[tag_value]



    def main(self):

        #with pysam.AlignmentFile(self.output, "wb", template=self.bam) as outfile:
        tag_to_file_map = {}
        for chrom in self.chromosomes:
            reflen = self.chr_lengths[chrom]

            for pileupobj in self.__fetch(chrom, 0, reflen):
                if pileupobj.has_tag('CB'):
                    tag_val = pileupobj.get_tag('CB')
                    #if tag_val in self.barcodes:  # filter by barcodes
                    if tag_val in ['AAACGGGTCAAAGTGA-1']:  # filter by barcodes  #>>>>>>
                        outfile = self.__get_file_for_tag(tag_to_file_map, tag_val)
                        outfile.write(pileupobj)
                    else:
                        pass  # discard read
                else:
                    outfile = self.__get_file_for_tag(tag_to_file_map, "undetermined")
                    # outfile.write(pileupobj) #>>>>>>>

        self.bam.close()
        print("closing files: ")
        for file in tag_to_file_map.values():
            try:
                file.close()
            except:
                warnings('error closing file ' + file)


# num lines in downsampled bam/sam =  12563361  => no data loss
# TODO prepare file with header before writing to it
def split_sam(self):
    barcode_pattern = re.compile(r'CB:[A-Z]:[AGCT]*-[0-9]')
    tag_to_file_map = {}
    count = 0;

    with open(self.samfile) as sf:
        for line in sf:
            match = re.search(barcode_pattern, line)
            if match:
                barcode = match.group(0)
                if barcode in self.barcodes:  # filter by barcodes
                    outfile = self.__get_file_for_tag(tag_to_file_map, barcode)
                    outfile.write(line)
                else:
                    pass # discard read

            else:
                outfile = self.__get_file_for_tag(tag_to_file_map, "undetermined")
                outfile.write(line)

    print("closing split files: ")
    for file in tag_to_file_map.values():
        try:
            file.close()
        except:
            warnings('error occurred while closing file ' + file)

def split_bam(bamfile):
    '''
    This function runs about 200 times slower than the split_sam function.

    :param bamfile:
    :return:
    '''
    count = 0
    proc = subprocess.Popen(["samtools", "view", bamfile], stdout=subprocess.PIPE)

    while True:
        line = proc.stdout.readline()
        if line is not None and line.strip() != '':
            count += 1
        else:
            break

    return count

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('bam',
                        help='specify the path to the input bam file')

    parser.add_argument('odir',
                        help='specify path to the output dir')

    parser.add_argument('--chromosomes',
                        nargs='*',
                        default=map(str, range(1, 23)) + ['X', 'Y', 'hs37d5'],
                        help='specify target chromosomes'
                        )

    # parser.add_argument('-m', '--mapping_quality_threshold',
    #                     type=int,
    #                     default=0,
    #                     help='threshold for the mapping quality, reads ' \
    #                          'with quality lower than threshold will be ignored')

    parser.add_argument('--barcode_csv',
                        help='threshold for the mapping quality, reads ' \
                             'with quality lower than threshold will be ignored')


    args = parser.parse_args()

    return args


if __name__ == "__main__":
    # args = parse_args()
    # with SplitBam(args.bam, args.odir, args.chromosomes,
    #                args.barcode_csv) as splitbam:
    #     splitbam.main()


    count = split_sam("data/downsampled/bj_mkn45_10pct_possorted_bam.sam")
    print("count = "+str(count))

    # count = split_bam("data/downsampled/bj_mkn45_10pct_possorted_bam.bam")
    # count = split_bam("data/bj_mkn45_10pct_possorted_bam_10k_snippet.bam")
    # print("count = " + str(count))


