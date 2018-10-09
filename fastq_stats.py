import sys
import logging
import argparse
import glob
import os
import yaml
from itertools import izip

def pairwise(iterable):
    "[s0, s1, s2, s3, s4, ...] -> (s0, s1), (s2, s3), (s4, s5), ..."
    aa = iter(iterable)
    return izip(aa, aa)

def quadruple(iterable):
    "[s0, s1, s2, s3, s4, s5, s6, s7, ...] -> (s0, s1, s3, s4), (s5, s6, s7, s8), ..."
    aa = iter(iterable)
    return izip(aa, aa, aa, aa)


errors_found = 0
def validate(fq1_lines, fq2_lines):
    """
    Checks for the following:

    1. mismatched tag lines between the two files
    2. sequence-quality length mismatch for reads in both files
    3. different number of reads in the two files

    :param fq1_lines:  lines from first of the pair of fastq files
    :param fq2_lines:  lines from second of the pair of fastq files
    :return: 0 if pair is valid, else return 1
    """
    global errors_found
    quad1 = quadruple(fq1_lines)  # (tag, sequence, +, quality)
    quad2 = quadruple(fq2_lines)  # (tag, sequence, +, quality)
    l_count = 1

    for quad_pair in zip(quad1, quad2):
        tuple1 = quad_pair[0]
        tuple2 = quad_pair[1]

        # r1, r2 identical tags
        if tuple1[0] != tuple2[0]:
            logging.error("mismatched tags at line "+str(l_count)+": "+str(tuple1[0])+" "+str(tuple2[0]))
            errors_found += 1

        # seq-qual len mismatch
        if len(tuple1[1]) != len(tuple1[3]):
            logging.error("r1 sequence-quality length mismatch at line " + str(l_count) + ": " + str(tuple1))
            errors_found += 1

        if len(tuple2[1]) != len(tuple2[3]):
            logging.error("r2 sequence-quality length mismatch at line  " + str(l_count) + ": " + str(tuple2))
            errors_found += 1

        l_count +=4

    # r1, r2 line count
    len1 = len(fq1_lines)
    len2 = len(fq2_lines)

    if len1 != len2:
        logging.error('different number of reads found: '+str(len1)+', '+str(len2))
        errors_found += 1

    if errors_found > 0:
        print("Errors found! Check log file for list of errors")
    else:
        print("Fastq files are valid!")

    return errors_found


stats = {'num_files': 0, 'total_reads': 0, 'errors': 0}
def summary_stat(fq1_lines, fq2_lines):
    """
       Collects summary stats from the specified file pairs.

       :param fq1_lines:  lines from first of the pair of fastq files
       :param fq2_lines:  lines from second of the pair of fastq files
    """
    global stats
    global errors_found
    stats['num_files'] += 2
    stats['total_reads'] += len(list(quadruple(fq1_lines))) + len(list(quadruple(fq2_lines)))
    stats['errors'] = errors_found


if __name__ == "__main__":
    # defaults
    config_file = "config.yml"
    file_ext = ".fq"

    # args parsing
    parser = argparse.ArgumentParser(description="Validate a list of fastq files in the specified input dir and "
                                                 "and logs summary stats. It is assumed that the fastq file pairs"
                                                 "are named such that an 'ls -l' operation would place the pairs adjecent"
                                                 "to one another in the output list")
    parser.add_argument("-c",
                        "--config",
                        type=str,
                        help="specify config file. Default="+config_file)
    parser.add_argument("-i",
                        "--input_dir",
                        type=str,
                        help="specify input dir where fastq files are stored")

    parser.add_argument("-e",
                        "--file_ext",
                        type=str,
                        help="specify fastq file extensions. Default ="+file_ext)

    args = parser.parse_args()

    if args.input_dir is None:
        parser.print_help()
        sys.exit(1)
    i_dir = args.input_dir


    if args.file_ext is not None:
        file_ext = args.file_ext


    # config
    if args.config is not None:
        config_file = args.config

    with open(config_file, "r") as stream:
        config = yaml.load(stream)

    # logging
    logging.basicConfig(
        filename=config["log_file"],
        level=config["log_level"],
        format="%(levelname)s\t%(asctime)s:\t%(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    # processing
    logging.info('scanning '+i_dir+' for files ending with '+file_ext)

    for fq1, fq2 in pairwise(sorted(glob.glob(os.path.join(i_dir+'/*'+file_ext)))):
        with open(fq1, 'r') as fq1_fh, \
             open(fq2, 'r') as fq2_fh:
            logging.info('validing pair '+fq1+' '+fq2)

            fq1_lines = fq1_fh.readlines()
            fq2_lines = fq2_fh.readlines()

            valid = validate(fq1_lines, fq2_lines)

            summary_stat(fq1_lines, fq2_lines)

    logging.info(" summary stats: " + str(stats))