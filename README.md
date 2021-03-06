# bam_demultiplexer

Demultiplexes a BAM file by cell identifier and converts the demultiplexed bam files to paired fastq files. Read alignments that don't contain a cell identifier tag are assigned the cell identifier CB:Z:undetermined.

# Software Requirements
- virtualenv
- python 2.7.*
- Ensure that the user ulimit for open files is larger than the number of expected demultiplexed bam files `$ ulimit -n 4000` for example. 


# Execution
```bash
$ virtualenv -p /usr/bin/python2.7 venv
$ source venv/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements.txt

$ time python bam_demultiplexer/pypeline.py \
--barcode_csv test/data/bj_mkn45_10pct_per_cell_summary_metrics.csv  \
test/data/bj_mkn45_10pct_possorted_bam_10k_snippet.bam \
test/data/output

$ deactivate
```
