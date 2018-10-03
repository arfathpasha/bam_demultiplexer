# bam_demultiplexer

Demultiplexes a merged BAM file by cell identifier. Entries that don't contain cell identifier are grouped together into a new cell identifier CB:undetermined.

# Execution

cat data/bj_mkn45_10pct_possorted_bam_10k_snippet.bam | python filter.py | python demultiplex.py 



