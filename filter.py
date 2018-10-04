import pysam
import re
import glob
import os
import sys
import csv
import yaml
import logging
import argparse


def filter_by_sequence_quality_len():
    pass

def filter_by_barcodes(barcodes, tag):
    """
    This method expects to receive a bam file stream from stdin and streams
    the filtered set of alignments to stdout.

    :param barcodes: list of barcodes to filter by.
    :param tag: tag to filter on.
    :param bam_file: bam file to filter.
    :return:
    """
    logging.info("filtering bam alignments by barcodes and tag=" + tag + " ...")

    in_file = pysam.AlignmentFile("-", "rb")  # stream in from stdin

    outfile = pysam.AlignmentFile("-", "wb", template=in_file)  # stream out to stdout

    for alignment in in_file:

        if alignment.has_tag(tag):
            barcode = str(alignment.get_tag(tag))
            if barcode in barcodes:
                outfile.write(alignment)
            else:
                logging.debug('dropping barcode '+barcode)  # drop alignment
        else:
            outfile.write(alignment)  # treat as undetermined alignment


def get_barcodes_from_summary_metrics(metrics_csv_file):
    """

    :param metrics_csv_file: file name
    :return:
    """
    summary_list = []
    barcodes = []

    with open(metrics_csv_file, "rb") as ff:
        reader = csv.reader(ff, delimiter=",")
        summary_list = list(reader)

    for cell in summary_list:
        barcodes.append(cell[0])

    return barcodes


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b",
                        "--by_barcodes",
                        help="Filter bam file by barcodes. The module expects to find "
                                              "a metrics_file in config.yml where the first column in the csv"
                                              "file is the list of barcodes to filter by. i.e. sequences with"
                                              "barcodes not in this list will be filtered out.",
                        action="store_true")

    parser.add_argument("-s",
                        "--by_seq_qual_len_mismatch",
                        help="Filter bam file to remove all alignment sequences in which"
                              "the segment sequence (SEQ) length is different from"
                              "the QUALity string length",
                        action="store_true")

    args = parser.parse_args()

    with open("config.yml", "r") as stream:
        config = yaml.load(stream)

    logging.basicConfig(
        filename=config["log_file"],
        level=config["level"],
        format="%(asctime)s: %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    if args.by_barcodes:
        barcodes = get_barcodes_from_summary_metrics(config["metrics_file"])
        filter_by_barcodes(barcodes, config["tag"])
    elif args.by_seq_qual_len_mismatch:
        filter_by_sequence_quality_len()
    else:
        parser.print_help()
        sys.exit(1)




