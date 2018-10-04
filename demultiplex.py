import pysam
import os
import sys
import logging
import yaml
import glob


def get_file_for_tag(tag_to_file_map, tag_value, odir, alignment_file):
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
        tag_file_name = os.path.join(odir, tag_value + ".bam")
        file_handle = pysam.AlignmentFile(tag_file_name, "w", template=alignment_file)
        tag_to_file_map[tag_value] = file_handle

    return tag_to_file_map[tag_value]


def split_by_tag(tag_key, odir):
    """
    Split input sam file by specified tag and write one file per tag to the specified
    output dir.
    :param tag_key
    :param bam_file:
    :param odir
    """
    logging.info('splitting bam files by tag ' + tag_key)
    alignment_file = pysam.AlignmentFile("-", "rb")  # stream in from stdin

    # split file by tag
    print("writing bam files, one per "+ tag_key +" tag value ...")
    tag_to_file_map = {}
    read_count = 0
    for aligned_segment_obj in alignment_file:
        read_count += 1
        sys.stdout.write("# alignments processed: %d%%   \r" % (read_count))
        sys.stdout.flush()

        if aligned_segment_obj.has_tag(tag_key):
            tag_value_obj = aligned_segment_obj.get_tag(tag_key)
            file_handle = get_file_for_tag(tag_to_file_map, str(tag_value_obj), odir, alignment_file)
            file_handle.write(aligned_segment_obj)
        else:
            file_handle = get_file_for_tag(tag_to_file_map, 'undetermined', odir, alignment_file)
            file_handle.write(aligned_segment_obj)


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

    # reset system ulimit
    #reset_ulimit()


    # TODO: cleanup temp files
    # TODO: need to fail on reads that have differing seq, qual lengths
    # TODO: test with bootstrap
    # TODO: filter out sequences that have seq-qual len mismatch
