import pysam
import os
import sys
import logging
import yaml
import glob


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
    logging.info('splitting bam files by tag '+tag)
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
        tag_file_name = os.path.join(odir, tag+".bam")
        outfile = pysam.AlignmentFile(tag_file_name, "w", template=alignment_file)

        alignment_objs = tag_to_alignment_map[tag]
        for alignment_segment_obj in alignment_objs:
            outfile.write(alignment_segment_obj)


def collate(idir, odir):
    """
    Collate all bam files in the specified dir

    :param dir: dir of bam files
    :return:
    """
    logging.info('collating bam files ')

    for file in glob.glob(os.path.join(idir, "*")):
        pysam.collate("-o", os.path.join(odir, os.path.basename(file)), file)

# TODO parameterize this func based on samtools.fastq args
def convert_bam_to_fastq(idir, odir):
    '''

    :param idir:
    :param odir:
    :return:
    '''
    logging.info('generating fastq files...')


    for file in glob.glob(os.path.join(idir, "*")):
        pysam.fastq('-1', os.path.join(odir, os.path.basename(file)[:-4]) + '_1.fq',
                    '-2', os.path.join(odir, os.path.basename(file)[:-4]) + '_2.fq',
                    '-0', '/dev/null',
                    '-s', '/dev/null',
                    '-n',
                    '-F', '0x900',
                    file)


    # samtools fastq -1 paired1.fq -2 paired2.fq -0 /dev/null -s /dev/null -n -F 0x900 TTTGTCATCCGCACGA-1_collated.bam



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
    splits_dir = os.path.join(odir, 'splits')
    if not os.path.exists(splits_dir):
        os.mkdir(splits_dir)

    split_by_tag(tag, splits_dir)

    # collate
    collate_dir = os.path.join(odir, 'collate')
    if not os.path.exists(collate_dir):
        os.mkdir(collate_dir)

    collate(splits_dir, collate_dir)

    # convert split and collated bams to fastq
    fastq_dir = os.path.join(odir, 'fastq')
    if not os.path.exists(fastq_dir):
        os.mkdir(fastq_dir)

    convert_bam_to_fastq(collate_dir, fastq_dir)


    # TODO: cleanup temp files
    # TODO: need to fail on reads that have differing seq, qual lengths
    # TODO: think about streaming all the way through to fastq
    # TODO: test with bootstrap
