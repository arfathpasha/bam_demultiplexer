# bam_demultiplexer

Demultiplexes a merged BAM file by cell identifier. Entries that don't contain cell identifier are grouped together into a new cell identifier CB:undetermined.

# Software Requirements
- virtualenv
- python 2.7.*


# Execution
$ virtualenv venv
$ source venv/bin/activate

$ time cat <bam_file> | python filter.py -c config.yml -b | python filter.py -c config.yml -s | python demultiplex.py -c config.yml

$ deactivate
