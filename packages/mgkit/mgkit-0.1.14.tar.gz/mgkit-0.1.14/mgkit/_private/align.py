from ..align import *

def get_regions_count(bam_file, seq_id, regions):
    for start, end in regions:
        norm_start = start - 1
        norm_end = end - 1
        yield bam_file.count(seq_id, norm_start, norm_end)
