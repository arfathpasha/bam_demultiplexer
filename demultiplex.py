import pysam
import re
import glob
import os
import sys
import logging
import yaml


def get_tag_list(cb_map, tag):
    """
    Get list that is mapped to specified tag in cb_map.

    :param cb_map:
    :param tag:
    :return:
    """
    if tag not in cb_map.keys():
        cb_map[tag] = []

    return cb_map[tag]


def split_by_tag(tag, odir):
    """
    Split input sam file by specified tag and write one file per tag to the specified
    output dir.
    :param tag
    :param bam_file:
    :param odir
    """
    alignment_file = pysam.AlignmentFile("-", "rb")  # stream in from stdin

    # split file by tag
    print("reading " + tag + " tags...")
    tag_to_alignment_map = {}
    read_count = 0
    for aligned_segment_obj in alignment_file:
        read_count += 1
        sys.stdout.write("# reads: %d%%   \r" % (read_count))
        sys.stdout.flush()

        if aligned_segment_obj.has_tag(tag):
            tag_file_obj = aligned_segment_obj.get_tag(tag)
            tag_list = get_tag_list(tag_to_alignment_map, str(tag_file_obj))
            tag_list.append(aligned_segment_obj)
        else:
            tag_list = get_tag_list(tag_to_alignment_map, "undetermined")
            tag_list.append(aligned_segment_obj)

    # write reads by CB to files
    print("writing bam files, one per cell...")
    for tag in tag_to_alignment_map.keys():
        tag_file_name = os.path.join(config['out_dir'], tag+".bam")
        outfile = pysam.AlignmentFile(tag_file_name, "w", template=alignment_file)

        alignment_objs = tag_to_alignment_map[tag]
        for alignment_segment_obj in alignment_objs:
            outfile.write(alignment_segment_obj)


def collate(dir):
    """
    Collate all bam files in the specified dir

    :param dir: dir of bam files
    :return:
    """
    logging.info('collating bam files ')

    for file in glob.glob(os.path.join(dir, "*")):
        pysam.collate("-o", file[:-4] + "_collated.bam", file)



if __name__ == "__main__":

    with open("config.yml", "r") as stream:
        config = yaml.load(stream)

    logging.basicConfig(
        filename=config["log_file"],
        level=config["level"],
        format="%(asctime)s: %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    odir = config['out_dir']
    tag = config['tag']

    # split file by tag
    split_by_tag(tag, odir)

    # collate
    collate(odir)

    # pull out paired reads and split into fastq files

    # TODO: then split into fastq files (look into using samtools for this too)
    # TODO: cleanup temp files
