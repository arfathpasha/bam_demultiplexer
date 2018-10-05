# bam_demultiplexer

Demultiplexes a merged BAM file by cell identifier. Entries that don't contain cell identifier are grouped together into a new cell identifier CB:undetermined.

# Software Requirements
- virtualenv
- python 3.6+


# Execution

time cat data/bj_mkn45_10pct_possorted_bam_10k_snippet.bam | python filter.py -b | python filter.py -s | python demultiplex.py


