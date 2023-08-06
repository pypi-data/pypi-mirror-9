"""Make sure we're getting correct transcritp sequence from Ensembl and that
it's a sequence type which correctly implements `complement`
and `reverse_complement`
"""

from __future__ import absolute_import
from nose.tools import eq_
from pyensembl import EnsemblRelease


ensembl54 = EnsemblRelease(54, auto_download=True)

def test_transcript_sequence_ensembl54():

    seq = ensembl54.transcript_sequence("ENST00000321606")
    assert len(seq) == 414, \
        "Expected transcript ENST00000321606 to have 414nt, got %s : %d" % (
            seq, len(seq))
    nucleotide_lines = [
        "CATGTCACCCACCTTCAGGCGGCCCAAGACACTGCGACTCCGGAGGCAGCCCAGATATCCTCGGAAGAG",
        "CACCCCCAGGAGAAACAAGCTTGGCCACTATGCTATCATCAAGTTTCCGCTGACCACTGAGTCGGCCGT",
        "GAAGAAGATAGAAGAAAACAACACGCTTGTGTTCACTGTGGATGTTAAAGCCAACAAGCACCAGATCAG",
        "ACAGGCTGTGAAGAAGCTCTATGACAGTGATGTGGCCAAGGTCACCACCCTGATTTGTCCTGATAAAGA",
        "GAACAAGGCATATGTTCGACTTGCTCCTGATTATGATGCTTTCGATGTTGTAACAAAATTGGGATCACC",
        "TAAACTGAGTCCAGCTGGCTAACTCTAAATATATGTGTATCTTTTCAGCATAAAAAAATAATGTTTTTC"
    ]
    full_transcript_sequence = "".join(nucleotide_lines)
    eq_(str(seq), full_transcript_sequence)

    # make sure the Sequence object's reverse and complement properties work
    reverse_complement = seq.complement()
    reverse_complement_lines = [
        "GAAAAACATTATTTTTTTATGCTGAAAAGATACACATATATTTAGAGTTAGCCAGCTGGACTCAGTTTA",
        "GGTGATCCCAATTTTGTTACAACATCGAAAGCATCATAATCAGGAGCAAGTCGAACATATGCCTTGTTC",
        "TCTTTATCAGGACAAATCAGGGTGGTGACCTTGGCCACATCACTGTCATAGAGCTTCTTCACAGCCTGT",
        "CTGATCTGGTGCTTGTTGGCTTTAACATCCACAGTGAACACAAGCGTGTTGTTTTCTTCTATCTTCTTC",
        "ACGGCCGACTCAGTGGTCAGCGGAAACTTGATGATAGCATAGTGGCCAAGCTTGTTTCTCCTGGGGGTG",
        "CTCTTCCGAGGATATCTGGGCTGCCTCCGGAGTCGCAGTGTCTTGGGCCGCCTGAAGGTGGGTGACATG"
    ]
    reverse_complement = "".join(reverse_complement_lines)
    eq_(len(seq.reverse_complement()), 414)
    eq_(str(seq.reverse_complement()), reverse_complement)
