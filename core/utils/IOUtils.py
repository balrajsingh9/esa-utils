# THE PARSER
# reads and returns the seq as string from the FASTA/FASTQ file
import random

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord


def get_seqs_from_file(file_path, fmt="fasta") -> list[SeqRecord]:
    return list(SeqIO.parse(file_path, fmt))
