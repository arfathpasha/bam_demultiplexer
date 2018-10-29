import os
import argparse
import logging
import pypeliner.workflow
import demultiplex_bam
import samtools_wrapper

from logging.config import fileConfig


def parse_args():
    argparser = argparse.ArgumentParser()
    #pypeliner.app.add_arguments(argparser)  #??

    argparser.add_argument('bam',
                        help='specify the path to the input bam file')

    argparser.add_argument('odir',
                        help='specify path to the output dir')

    argparser.add_argument('--barcode_csv',
                           help='CSV file containing cell identifiers to demultiplex on. ' \
                                'The cell id/barcode must be in the first column of the CSV file')

    args = argparser.parse_args()

    return args



if __name__ == "__main__":

    fileConfig("logging_config.ini")

    logging.info("Starting bam_demultiplexer pipeline...")

    args = vars(parse_args())

    pyp = pypeliner.app.Pypeline([demultiplex_bam], config=args)  #??

    workflow = pypeliner.workflow.Workflow()

    # demultiplex
    workflow.transform(
        name='demultiplex',
        func=demultiplex_bam.demultiplex,
        args=(pypeliner.managed.InputFile(args['bam']),
              pypeliner.managed.TempOutputFile('demux', 'split'),
              args['barcode_csv'])
    )

    # collate demultiplexed bams
    workflow.transform(
        name='collate',
        axes=('split',),
        func=samtools_wrapper.collate,
        args=(pypeliner.managed.TempInputFile('demux', 'split'),
              pypeliner.managed.TempOutputFile('collated', 'split'))
    )

    # convert collated bams to fastq
    workflow.transform(
        name='fastq',
        axes=('split',),
        func=samtools_wrapper.fastq,
        args=(pypeliner.managed.TempInputFile('collated', 'split'),
                    pypeliner.managed.OutputFile(os.path.join(args['odir'], '{split}.fq1'), 'split'),
                    pypeliner.managed.OutputFile(os.path.join(args['odir'], '{split}.fq2'), 'split'))
    )

    logging.info("Ending bam_demultiplexer pipeline...")

    pyp.run(workflow)
