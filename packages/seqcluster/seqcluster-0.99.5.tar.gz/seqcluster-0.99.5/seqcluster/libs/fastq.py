import os
from collections import Counter
from classes import quality
from itertools import product


def collapse(in_file):
    """collapse identical sequences and keep Q"""
    keep = Counter()
    with open_fastq(in_file) as handle:
        for line in handle:
            if line.startswith("@"):
                line.strip()
                seq = handle.next().strip()
                handle.next().strip()
                qual = handle.next().strip()
                if seq in keep:
                    keep[seq].update(qual)
                else:
                    keep[seq] = quality(qual)
    return keep


def open_fastq(in_file):
    """ open a fastq file, using gzip if it is gzipped
    from bcbio package
    """
    _, ext = os.path.splitext(in_file)
    if ext == ".gz":
        return gzip.open(in_file, 'rb')
    if ext in [".fastq", ".fq"]:
        return open(in_file, 'r')


def is_fastq(in_file):
    """copy from bcbio package"""
    fastq_ends = [".txt", ".fq", ".fastq"]
    zip_ends = [".gzip", ".gz"]
    base, first_ext = os.path.splitext(in_file)
    second_ext = os.path.splitext(base)[1]
    if first_ext in fastq_ends:
        return True
    elif (second_ext, first_ext) in product(fastq_ends, zip_ends):
        return True
    else:
        return False


def splitext_plus(f):
    """Split on file extensions, allowing for zipped extensions.
    copy from bcbio
    """
    base, ext = os.path.splitext(f)
    if ext in [".gz", ".bz2", ".zip"]:
        base, ext2 = os.path.splitext(base)
        ext = ext2 + ext
    return base, ext
