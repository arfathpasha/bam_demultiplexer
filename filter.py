import pysam
import sys
import csv
import yaml
import logging
import argparse
import collections


def filter_by_sequence_quality_len():
    """
    This method filters out alignment sequence segments whose segment length
    differs from the quality string length.

    This method expects to receive a bam file stream from stdin and streams
    the filtered set of alignments to stdout.

        :param barcodes: list of barcodes to filter by.
        :param tag: tag to filter on.
        :param bam_file: bam file to filter.
        :return:
    """
    logging.info("filtering sequence segments that have sequence-quality len mismatch...")

    infile = pysam.AlignmentFile("-", "rb")  # stream in from stdin

    outfile = pysam.AlignmentFile("-", "wb", template=infile)  # stream out to stdout

    for alignment in infile:
        if alignment.query_alignment_length != len(alignment.query_alignment_qualities):
            logging.warn('seq-qual len mismatch found, dropping sequence ' + alignment.to_string())  # drop alignment sequence
        else:
            outfile.write(alignment)



def filter_by_barcodes(tag, tag_values, filter_undetermined=False):
    """
    This method filters out alignment sequence segments by tag value. If a
    sequence segment with a tag value that is excluded from the specified
    tag_values list is found, then that sequence segment is considered noisy and
    is filtered out.

    If the sequence segment does not contain the specified tag, then that sequence
    segment is considered as undetermined.

    This method expects to receive a bam file stream from stdin and streams
    the filtered set of alignments to stdout.

    :param tag: tag to filter on.
    :param tag_values: list of tag values to filter by.
    :param filter_undetermined: filter out undetermined sequence segment if set to true.
    :param bam_file: bam file to filter.
    :return:
    """
    if tag is None or tag_values is None:
        logging.error('Tag with None type not allowed for filter_by_barcodes method ')
        sys.exit(1)

    logging.info("filtering 'noisy' sequence segments by " + tag + " tag...")

    infile = pysam.AlignmentFile("-", "rb")  # stream in from stdin

    outfile = pysam.AlignmentFile("-", "wb", template=infile)  # stream out to stdout

    for alignment in infile:

        if alignment.has_tag(tag):
            t_val = str(alignment.get_tag(tag))
            if t_val in tag_values:
                outfile.write(alignment)
            else:
                logging.warn('dropping segment with tag_value '+t_val)
        elif filter_undetermined is False:
            outfile.write(alignment)  # treat as undetermined alignment
        else:
            logging.warn('dropping undetermined segment with query_name ' + alignment.query_name)  


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
        filter_by_barcodes(config["tag"], barcodes)
    elif args.by_seq_qual_len_mismatch:
        filter_by_sequence_quality_len()
    else:
        parser.print_help()
        sys.exit(1)



