# Requirements

## Functional:

1. Demultiplex one or more bam files based on the optional CB cell identifier tag.

2. Reconstruct the paired reads for each originating cell and output paired reads to _R1 and _R2 FASTQ files.

3. For entries in bam file that do not contain cell identifier, group entries into a cell identifier named 'undetermined' and output into the corresponding FASTQ files.

4. If there is a length mismatch between sequence and quality, fail the processing for the entire cell identifier.

## Non-functional:

1. Stream processing.

2. Use parallelization where possible.

3. Logging.

4. Unit tests.

5. Cleanup any temp files in post processing step.

6. Output stats obtained from processing to log and console out.
