#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reconstruction of reference sequences from CIGAR and MD tags in SAM files.

Includes tests for various scenarios of clipping, insertion and deletion.
Padding remains untested!

@author:    Florian Aldehoff (f.aldehoff@student.uni-tuebingen.de)
"""

import sys
import re


def decompress_cigar(cigar):
    """
    Decompress CIGAR string.
    """
    cigar_ext = ""
    cigar_ops = re.findall('(\d+)(\D)', cigar)
    for (count, op) in cigar_ops:
        cigar_ext += op * int(count)
    return cigar_ext


def decompress_md(md):
    """
    Decompress MD string.

    Parameters
    ----------
    md : string
      MD string from SAM file without MD:Z: prefix

    Returns
    -------
    md_ext : string
      extended MD string without MD:Z: prefix

    """
    md_ext = ""
    md_ops = re.findall('(\d*)(\D*)', md)
    for (match, mismatch) in md_ops:
        try:
            md_ext += '=' * int(match)
        except ValueError:
            # regex also catches empty string, can be safely ignored
            pass
        md_ext += mismatch.lstrip('^')
    return md_ext


def reconstruct(read, cigar, md, verbose=False):
    """
    Reconstruct the full reference sequence and the aligned reference sequence.

    Parameters
    ----------
    read : string
        Raw read sequence without gaps, can be clipped.
    cigar : string
        CIGAR string from SAM file
    md : string
        matching MD string from SAM file without MD:Z: prefix

    Returns
    -------
    ref_full : string
        full reference sequence including indels, clipped and skipped parts
    read_full : string
        full read sequence including indels, clipped and skipped parts
    ref_aln : string
        aligned part of reference sequence (can include gaps)
    read_aln : string
        aligned part of read sequence (clipped, can include gaps)
    """
    ref_full = ""    # full reference sequence
    read_full = ""   # full read sequence
    ref_aln = ""     # aligned reference sequence (can include gaps)
    read_aln = ""    # aligned read sequence (clipped, can include gaps)

    cigar_ext = decompress_cigar(cigar)
    md_ext = decompress_md(md)

    # reconstruct reference by CIGAR and MD
    read_idx = 0
    md_idx = 0
    for (idx, op) in enumerate(cigar_ext):
        if op in ('M', 'X'):          # alignment match|mismatch -> consult MD
            if md_ext[md_idx] == '=':
                ref_full += read[read_idx]
                ref_aln += read[read_idx]
            else:
                ref_full += md_ext[md_idx]
                ref_aln += md_ext[md_idx]
            read_full += read[read_idx]
            read_aln += read[read_idx]
            read_idx += 1
            md_idx += 1
        elif op == '=':                # certain match
            ref_full += read[read_idx]
            ref_aln += read[read_idx]
            read_full += read[read_idx]
            read_aln += read[read_idx]
            read_idx += 1
            md_idx += 1
        elif op == 'D':                # deletion from reference -> consult MD
            ref_full += md_ext[md_idx]
            ref_aln += md_ext[md_idx]
            read_full += '-'
            read_aln += '-'
            md_idx += 1
        elif op == 'I':                # insertion to reference
            ref_full += '-'
            ref_aln += '-'
            read_full += read[read_idx]
            read_aln += read[read_idx]
            read_idx += 1
        elif op == 'N':                # skipped region in reference (intron?)
            ref_full += 'X'
#            ref_aln += 'N'
            read_full += '-'
#            read_aln += 'N'
        elif op == 'H':                # hard clipping (5' or 3' only)
            ref_full += 'X'
#            ref_aln += 'N'
            read_full += 'X'
#            read_aln += 'N'
        elif op == 'S':                # soft clipping (5' or 3' only)
            ref_full += 'X'
#            ref_aln += 'N'
            read_full += read[read_idx]
#            read_aln += 'N'
            read_idx += 1
        elif op == 'P':                # ignore padding, aligning single reads
            pass
    return (ref_full, read_full, ref_aln, read_aln)


"""
tests for reference reconstruction method
"""


def test_deletion_snp_no_delim(verbose=False):
    """
    test reference reconstruction despite missing 0 delimiter after deletion \
    in MD
    """
    read = "CTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    cigar = "37M4D8M"
    md = "G36^CCTTTC6"
    """
    CTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA    AAAAAAAA    read
    |||||||||||||||||||||||||||||||||||||----||||||||    extended CIGAR
    G||||||||||||||||||||||||||||||||||||CCTTTC||||||    extended MD
    GTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACCTTTCAAAAAA    full reference
    CTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA----AAAAAAAA    full read
    GTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACCTTTCAAAAAA    aligned reference
    CTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA----AAAAAAAA    aligned read
    """
    ref_full = "GTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACCTTTCAAAAAA"
    read_full = "CTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA----AAAAAAAA"
    ref_aln = "GTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACCTTTCAAAAAA"
    read_aln = "CTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA----AAAAAAAA"

    (rec_ref_full, rec_read_full, rec_ref_aln, rec_read_aln) = reconstruct(read, cigar, md, verbose)
    if verbose:
        print(rec_ref_full + "\treconstructed reference")
        print(ref_full + "\tactual reference")
        print(rec_read_full + "\treconstructed read")
        print(read_full + "\tactual read")
        print(rec_ref_aln + "\treconstructed aligned reference")
        print(ref_aln + "\tactual aligned reference")
        print(rec_read_aln + "\treconstructed aligned read")
        print(read_aln + "\tactual aligned read")
    print("%s\tSNP after deletion without 0 delimiter"
          % (rec_ref_full == ref_full
             and rec_read_full == read_full
             and rec_ref_aln == ref_aln
             and rec_read_aln == read_aln,))
    return (rec_ref_full == ref_full
            and rec_read_full == read_full
            and rec_ref_aln == ref_aln and
            rec_read_aln == read_aln)


def test_deletion_snp_0_delim(verbose=False):
    """
    test reference reconstruction with 0 delimiter after deletion in MD
    """
    read = "CTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    cigar = "37M4D8M"
    md = "G36^CCTT0TC6"
    """
    CTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA    AAAAAAAA    read
    |||||||||||||||||||||||||||||||||||||----||||||||    extended CIGAR
    G||||||||||||||||||||||||||||||||||||CCTTTC||||||    extended MD
    GTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACCTTTCAAAAAA    full reference
    CTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA----AAAAAAAA    full read
    GTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACCTTTCAAAAAA    aligned reference
    CTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA----AAAAAAAA    aligned read
    """
    ref_full  = "GTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACCTTTCAAAAAA"
    read_full = "CTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA----AAAAAAAA"
    ref_aln   = "GTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACCTTTCAAAAAA"
    read_aln  = "CTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA----AAAAAAAA"

    (rec_ref_full, rec_read_full, rec_ref_aln, rec_read_aln) = reconstruct(read, cigar, md, verbose)
    if verbose:
        print(rec_ref_full + "\treconstructed reference")
        print(ref_full + "\tactual reference")
        print(rec_read_full + "\treconstructed read")
        print(read_full + "\tactual read")
        print(rec_ref_aln + "\treconstructed aligned reference")
        print(ref_aln + "\tactual aligned reference")
        print(rec_read_aln + "\treconstructed aligned read")
        print(read_aln + "\tactual aligned read")
    print("%s\tSNP after deletion with 0 delimiter"
          % (rec_ref_full == ref_full
             and rec_read_full == read_full
             and rec_ref_aln == ref_aln
             and rec_read_aln == read_aln,))
    return (rec_ref_full == ref_full
            and rec_read_full == read_full
            and rec_ref_aln == ref_aln
            and rec_read_aln == read_aln)


def test_insertion(verbose=False):
    """
    test reference reconstruction with insertion to reference
    """
    read = "GCCTTCCGCGTCGGCGAGGACGGCCCCACCCACCAGCCCAT"
    cigar = "1M1I39M"
    md = "2A2G2C31"
    """
    GCCTTCCGCGTCGGCGAGGACGGCCCCACCCACCAGCCCAT    read (41bp)
    MIMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM    extended CIGAR (41bp)
    = =A==G==C===============================    extended MD (40bp) ! shift by del
    G-CATCGGCCTCGGCGAGGACGGCCCCACCCACCAGCCCAT    full reference
    GCCTTCCGCGTCGGCGAGGACGGCCCCACCCACCAGCCCAT    full read
    G-CATCGGCCTCGGCGAGGACGGCCCCACCCACCAGCCCAT    aligned reference
    GCCTTCCGCGTCGGCGAGGACGGCCCCACCCACCAGCCCAT    aligned read
    """
    ref_full  = "G-CATCGGCCTCGGCGAGGACGGCCCCACCCACCAGCCCAT"
    read_full = "GCCTTCCGCGTCGGCGAGGACGGCCCCACCCACCAGCCCAT"
    ref_aln   = "G-CATCGGCCTCGGCGAGGACGGCCCCACCCACCAGCCCAT"
    read_aln  = "GCCTTCCGCGTCGGCGAGGACGGCCCCACCCACCAGCCCAT"

    (rec_ref_full, rec_read_full, rec_ref_aln, rec_read_aln) = reconstruct(read, cigar, md, verbose)
    if verbose:
        print(rec_ref_full + "\treconstructed reference")
        print(ref_full + "\tactual reference")
        print(rec_read_full + "\treconstructed read")
        print(read_full + "\tactual read")
        print(rec_ref_aln + "\treconstructed aligned reference")
        print(ref_aln + "\tactual aligned reference")
        print(rec_read_aln + "\treconstructed aligned read")
        print(read_aln + "\tactual aligned read")
    print("%s\tinsertion into reference" % (rec_ref_full == ref_full
                                            and rec_read_full == read_full
                                            and rec_ref_aln == ref_aln
                                            and rec_read_aln == read_aln,))
    return (rec_ref_full == ref_full
            and rec_read_full == read_full
            and rec_ref_aln == ref_aln
            and rec_read_aln == read_aln)


def test_skipped_intron(verbose=False):
    """
    test reference reconstruction with skipped intron
    """
    read = "GTGTAACCCTCAGAATA"
    cigar = "9M32N8M"
    md = "17"
    """
    GTGTAACCC                                TCAGAATA    read (17bp)
    MMMMMMMMMNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNMMMMMMMM    extended CIGAR (49bp)
    =========                                ========    extended MD (17bp)
    GTGTAACCCNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNTCAGAATA    full reference
    GTGTAACCC--------------------------------TCAGAATA    full read
    GTGTAACCC                                TCAGAATA    aligned reference
    GTGTAACCC                                TCAGAATA    aligned read
    """
    ref_full  = "GTGTAACCCXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXTCAGAATA"
    read_full = "GTGTAACCC--------------------------------TCAGAATA"
    ref_aln   = "GTGTAACCCTCAGAATA"
    read_aln  = "GTGTAACCCTCAGAATA"

    (rec_ref_full, rec_read_full, rec_ref_aln, rec_read_aln) = reconstruct(read, cigar, md, verbose)
    if verbose:
        print(rec_ref_full + "\treconstructed reference")
        print(ref_full + "\tactual reference")
        print(rec_read_full + "\treconstructed read")
        print(read_full + "\tactual read")
        print(rec_ref_aln + "\treconstructed aligned reference")
        print(ref_aln + "\tactual aligned reference")
        print(rec_read_aln + "\treconstructed aligned read")
        print(read_aln + "\tactual aligned read")
    print("%s\tskipped intron" % (rec_ref_full == ref_full
                                  and rec_read_full == read_full
                                  and rec_ref_aln == ref_aln
                                  and rec_read_aln == read_aln,))
    return (rec_ref_full == ref_full
            and rec_read_full == read_full
            and rec_ref_aln == ref_aln
            and rec_read_aln == read_aln)


def test_hard_clipping_front(verbose=False):
    """
    test reference reconstruction with hard clipped 5' read
    """
    read = "ATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCA"
    cigar = "23H37M"
    md = "36G"
    """
                           ATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCA    read (37bp)
    HHHHHHHHHHHHHHHHHHHHHHHMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM    extended CIGAR (50bp)
                           ====================================G    extended MD (37bp)
    NNNNNNNNNNNNNNNNNNNNNNNATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCG    full reference
    NNNNNNNNNNNNNNNNNNNNNNNATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCA    full read
                           ATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCG    aligned reference
                           ATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCA    aligned read
    """
    ref_full  = "XXXXXXXXXXXXXXXXXXXXXXXATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCG"
    read_full = "XXXXXXXXXXXXXXXXXXXXXXXATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCA"
    ref_aln   = "ATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCG"
    read_aln  = "ATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCA"

    (rec_ref_full, rec_read_full, rec_ref_aln, rec_read_aln) = reconstruct(read, cigar, md, verbose)
    if verbose:
        print(rec_ref_full + "\treconstructed reference")
        print(ref_full + "\tactual reference")
        print(rec_read_full + "\treconstructed read")
        print(read_full + "\tactual read")
        print(rec_ref_aln + "\treconstructed aligned reference")
        print(ref_aln + "\tactual aligned reference")
        print(rec_read_aln + "\treconstructed aligned read")
        print(read_aln + "\tactual aligned read")
    print("%s\t5' hard clipping" % (rec_ref_full == ref_full
                                    and rec_read_full == read_full
                                    and rec_ref_aln == ref_aln
                                    and rec_read_aln == read_aln,))
    return (rec_ref_full == ref_full
            and rec_read_full == read_full
            and rec_ref_aln == ref_aln
            and rec_read_aln == read_aln)


def test_hard_clipping_end(verbose=False):
    """
    test reference reconstruction with hard clipped 3' read
    """
    read = "GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    cigar = "44M6H"
    md = "44"
    """
    GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA        read (44bp)
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMHHHHHH  extended CIGAR (50bp)
    ============================================        extended MD (44bp)
    GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANNNNNN  full reference
    GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANNNNNN  full read
    GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA        aligned reference
    GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA        aligned read
    """
    ref_full  = "GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAXXXXXX"
    read_full = "GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAXXXXXX"
    ref_aln   = "GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    read_aln  = "GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

    (rec_ref_full, rec_read_full, rec_ref_aln, rec_read_aln) = reconstruct(read, cigar, md, verbose)
    if verbose:
        print(rec_ref_full + "\treconstructed reference")
        print(ref_full + "\tactual reference")
        print(rec_read_full + "\treconstructed read")
        print(read_full + "\tactual read")
        print(rec_ref_aln + "\treconstructed aligned reference")
        print(ref_aln + "\tactual aligned reference")
        print(rec_read_aln + "\treconstructed aligned read")
        print(read_aln + "\tactual aligned read")
    print("%s\t3' hard clipping" % (rec_ref_full == ref_full
                                    and rec_read_full == read_full
                                    and rec_ref_aln == ref_aln
                                    and rec_read_aln == read_aln,))
    return (rec_ref_full == ref_full
            and rec_read_full == read_full
            and rec_ref_aln == ref_aln
            and rec_read_aln == read_aln)


def test_soft_clipping_front(verbose=False):
    """
    test reference reconstruction with soft clipped 5' read
    """
    read = "GGGGGGGGGGGGGGGGGGGGGGGATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCA"
    cigar = "23S37M"
    md = "36G"
    """
    GGGGGGGGGGGGGGGGGGGGGGGATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCA    read (50bp)
    SSSSSSSSSSSSSSSSSSSSSSSMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM    extended CIGAR (50bp)
                           ====================================G    extended MD (37bp)
    NNNNNNNNNNNNNNNNNNNNNNNATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCG    full reference
    NNNNNNNNNNNNNNNNNNNNNNNATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCA    full read
                           ATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCG    aligned reference
                           ATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCA    aligned read
    """
    ref_full  = "XXXXXXXXXXXXXXXXXXXXXXXATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCG"
    read_full = "GGGGGGGGGGGGGGGGGGGGGGGATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCA"
    ref_aln   = "ATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCG"
    read_aln  = "ATGAGAGTTTGATCCTGGCTCAGGACGAACGCTGGCA"

    (rec_ref_full, rec_read_full, rec_ref_aln, rec_read_aln) = reconstruct(read, cigar, md, verbose)
    if verbose:
        print(rec_ref_full + "\treconstructed reference")
        print(ref_full + "\tactual reference")
        print(rec_read_full + "\treconstructed read")
        print(read_full + "\tactual read")
        print(rec_ref_aln + "\treconstructed aligned reference")
        print(ref_aln + "\tactual aligned reference")
        print(rec_read_aln + "\treconstructed aligned read")
        print(read_aln + "\tactual aligned read")
    print("%s\t5' soft clipping" % (rec_ref_full == ref_full
                                    and rec_read_full == read_full
                                    and rec_ref_aln == ref_aln
                                    and rec_read_aln == read_aln,))
    return (rec_ref_full == ref_full
            and rec_read_full == read_full
            and rec_ref_aln == ref_aln
            and rec_read_aln == read_aln)


def test_soft_clipping_end(verbose=False):
    """
    test reference reconstruction with soft clipped 3' read
    """
    read = "GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGGGGGG"
    cigar = "44M6S"
    md = "44"
    """
    GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGGGGGG    read (44bp)
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMSSSSSS    extended CIGAR (50bp)
    ============================================          extended MD (44bp)
    GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANNNNNN    full reference
    GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANNNNNN    full read
    GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA          aligned reference
    GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA          aligned read
    """
    ref_full  = "GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAXXXXXX"
    read_full = "GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGGGGGG"
    ref_aln   = "GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    read_aln  = "GTTTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

    (rec_ref_full, rec_read_full, rec_ref_aln, rec_read_aln) = reconstruct(read, cigar, md, verbose)
    if verbose:
        print(rec_ref_full + "\treconstructed reference")
        print(ref_full + "\tactual reference")
        print(rec_read_full + "\treconstructed read")
        print(read_full + "\tactual read")
        print(rec_ref_aln + "\treconstructed aligned reference")
        print(ref_aln + "\tactual aligned reference")
        print(rec_read_aln + "\treconstructed aligned read")
        print(read_aln + "\tactual aligned read")
    print("%s\t3' soft clipping" % (rec_ref_full == ref_full
                                    and rec_read_full == read_full
                                    and rec_ref_aln == ref_aln
                                    and rec_read_aln == read_aln,))
    return (rec_ref_full == ref_full
            and rec_read_full == read_full
            and rec_ref_aln == ref_aln
            and rec_read_aln == read_aln)


def main(argv):
    # test the reconstruction method
    tests = [test_deletion_snp_no_delim(verbose=False),
             test_deletion_snp_0_delim(verbose=False),
             test_insertion(verbose=False),
             test_skipped_intron(verbose=False),
             test_hard_clipping_front(verbose=False),
             test_hard_clipping_end(verbose=False),
             test_soft_clipping_front(verbose=False),
             test_soft_clipping_end(verbose=False)]
    print("passed %i out of %i tests"
          % (tests.count(True), len(tests)))

    # process command line arguments
    if len(argv) == 4:
        print()
        (rec_ref_full, rec_read_full, rec_ref_aln, rec_read_aln) = reconstruct(argv[1], argv[2], argv[3], verbose=True)
        print(rec_ref_full + "\treconstructed reference")
        print(rec_ref_aln + "\treconstructed aligned reference")
        print(rec_read_aln + "\treconstructed aligned read")

    exit()


if __name__ == "__main__":
    main(sys.argv)
