# -*- coding: utf-8 -*-
"""Library of standard methods for manipulation of genetic sequences.

.. moduleauthor:: Florian Aldehoff (f.aldehoff@student.uni-tuebingen.de)
"""


def is_iupac(seq):
    """Check nucleotide sequence for invalid (non-IUPAC) codes.

    Parameters
    ----------
    seq : str
        Nucleotide sequence.

    Returns
    -------
    bool
        True if sequence contains only IUPAC ambiguity codes, otherwise False.
    """
    iupac = set(('A', 'T', 'C', 'G',
                 'Y', 'R',
                 'W', 'S',
                 'K', 'M',
                 'B', 'H', 'D', 'V',
                 'X', 'N',
                 '-',
                 'a', 't', 'c', 'g',
                 'y', 'r',
                 'w', 's',
                 'k', 'm',
                 'b', 'h', 'd', 'v',
                 'x', 'n'))
    return set(seq).issubset(iupac)


def opposite(base):
    """Mirror base code into the exact opposite IUPAC ambiguity code.

    'A' becomes 'not A', gap becomes any base, etc.

    Parameters
    ----------
    base : str
        Single one-letter IUPAC nucleotide code.

    Returns
    -------
    str
        Opposite one-letter IUPAC ambiguity code.
    None
        If base is invalid.
    """
    opposites = {'A':    'B',
                 'G':    'H',
                 'C':    'D',
                 'T':    'V',
                 'Y':    'R',    # pyrimidine | purin
                 'R':    'Y',    # purine | pyrimidine
                 'W':    'S',    # weak | strong
                 'S':    'W',    # strong | weak
                 'K':    'M',    # keto | amino
                 'M':    'K',    # amino | keto
                 'B':    'A',
                 'H':    'G',
                 'D':    'C',
                 'V':    'T',
                 'X':    '-',
                 'N':    '-',
                 '-':    'N',    # ____________________
                 'a':    'b',
                 'g':    'h',
                 'c':    'd',
                 't':    'v',
                 'y':    't',    # pyrimidine | purin
                 'r':    'y',    # purine | pyrimidine
                 'w':    's',    # weak | strong
                 's':    'w',    # strong | weak
                 'k':    'm',    # keto | amino
                 'm':    'k',    # amino | keto
                 'b':    'a',
                 'h':    'g',
                 'd':    'c',
                 'v':    't',
                 'x':    '-',
                 'n':    '-'}
    try:
        opposite = opposites[base]
    except KeyError:
        return None
    return opposite


def complement(base):
    """Returns a base's complement according to IUPAC or None.

    Parameters
    ----------
    base : str
        Single one-letter IUPAC nucleotide code.

    Returns
    -------
    str
        Complementary one-letter IUPAC ambiguity code.
    None
        If base is invalid.
    """
    complements = {'A':    'T',
                   'G':    'C',
                   'C':    'A',
                   'T':    'G',
                   'Y':    'R',    # pyrimidine > purin
                   'R':    'Y',    # purine > pyrimidine
                   'W':    'W',    # weak: A or T
                   'S':    'S',    # strong: G or C
                   'K':    'M',    # keto > amino
                   'M':    'K',    # amino > keto
                   'D':    'H',
                   'V':    'B',
                   'H':    'D',
                   'B':    'V',
                   'X':    'X',
                   'N':    'N',
                   '-':    '-',    # ____________________
                   'a':    't',
                   'g':    'c',
                   'c':    'a',
                   't':    'g',
                   'y':    'r',
                   'r':    'y',
                   'w':    'w',
                   's':    's',
                   'k':    'm',
                   'm':    'k',
                   'd':    'h',
                   'v':    'b',
                   'h':    'd',
                   'b':    'v',
                   'x':    'x',
                   'n':    'n'}
    try:
        complement = complements[base]
    except KeyError:
        return None
    return complement


def reverse(seq):
    """Reverses a sequence.

    Parameters
    ----------
    seq : str
        Any sequence.

    Returns
    -------
    str
        Reverse sequence.
    """
    return seq[::1]


def reverse_complement(seq):
    """Reverse complement a nucleotide sequence.

    Parameters
    ----------
    seq : str
        A nucleotide sequence of IUPAC ambuigity codes.
    Returns
    -------
    str
        Reverse complement of the nucleotide sequence.
    """
    rev = seq[::-1]
    revcomp = ''
    for base in rev:
        revcomp += complement(base)
    return revcomp


def transcribe(dna):
    """Transcription of DNA sequence to corresponding RNA sequence.

    Parameters
    ----------
    dna : str
        DNA nucleotide sequence.

    Returns
    -------
    str
        RNA nucleotide sequence.
    """
    return dna.replace('T', 'U').replace('t', 'u')


def reverse_transcribe(rna):
    """Reverse transcription of RNA sequence to corresponding cDNA sequence.

    Parameters
    ----------
    rna : str
        RNA nucleotide sequence.

    Returns
    -------
    str
        DNA nucleotide sequence.
    """
    return rna.replace('U', 'T').replace('u', 't')


def gc(seq):
    """Calculate GC content of a nucleotide sequence.

    Considers all IUPAC codes using 6x counts to deal with 1/2 and 1/3
    probabilities from ambiguity codes.

    Parameters
    ----------
    seq : str
        A nucleotide sequence.

    Returns
    -------
    float
        GC content as fraction of 1.
    """
    if len(seq) == 0:
        return 0.0

    gc_at_values = {'A':    (0, 6),
                    'G':    (6, 0),
                    'C':    (6, 0),
                    'T':    (0, 6),
                    'Y':    (3, 3),    # pyrimidine (C or T)
                    'R':    (3, 3),    # purine (A or G)
                    'W':    (0, 6),    # weak (A or T)
                    'S':    (6, 0),    # strong (G or C)
                    'K':    (3, 3),    # keto (T or G)
                    'M':    (3, 3),    # amino (A or C)
                    'B':    (4, 2),    # not A
                    'H':    (2, 4),    # not G
                    'D':    (2, 4),    # not C
                    'V':    (4, 2),    # not T
                    'X':    (3, 3),    # any
                    'N':    (3, 3),    # any
                    '-':    (0, 0),    # ____________________
                    'a':    (0, 6),
                    'g':    (6, 0),
                    'c':    (6, 0),
                    't':    (0, 6),
                    'y':    (3, 3),
                    'r':    (3, 3),
                    'w':    (0, 6),
                    's':    (6, 0),
                    'k':    (3, 3),
                    'm':    (3, 3),
                    'b':    (4, 2),
                    'h':    (2, 4),
                    'd':    (2, 4),
                    'v':    (4, 2),
                    'x':    (3, 3),
                    'n':    (3, 3)}
    gc = 0
    at = 0
    for base in seq:
        gc += gc_at_values[base][0]
        at += gc_at_values[base][1]
    return gc / ((at + gc) * 1.0)


def aln_identity(read, ref, include_indels=False, include_deamination=False,
                 include_unknown=False):
    """Determines identity of two sequences in an alignment.

    Calculates modified Hamming distance of an alignment with gaps with
    optional exclusion of possibly deaminated T>C and A>G as well as indels.

    Enabling all three optional parameters will calculate values identical to
    MALT while the default settings will calculate values identical to
    PMDtools.

    Parameters
    ----------
    read : str
        Full read sequence.
    ref : str
        Corresponding reference sequence (only the aligned part, but including
        any gaps, skips and indels).
    include_indels : bool, optional
        Consider insertions and deletions, defaults to False.
    include_deamination : bool, optional
        Consider any potentially deaminated bases, defaults to False.
    include_unknown : bool, optional
        Consider any unknown bases (N), defaults to False.

    Returns
    -------
    float
        Identity of read and reference as fraction of 1.
    str
        Mismatch string (match = ``|``, mismatch = ``x``, indel = ``-``).

    Example
    -------
    Showing differences between PMDtools and MALT::

        TCCAGCAGGTCGATGACCTTGATGCCGGTCTCGAACATCTTCA
        ||-|||||||||||||||||||||||||||||||||||||-|x
        TC-AGCAGGTCGATGACCTTGATGCCGGTCTCGAACATCT-CG
        ]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]

        43 bases
        2 gaps
        1 total mismatches
            1 G>A mismatches (A in read but G in reference)
            0 C>T mismatches (T in read but C in reference)
            0 other mismatches
        40 matches

        PMD:    40 / 40 = 100%
        identity = 1.0 * matches / (matches + other mismatches)
                 = 1.0 * 40 / (40 + 0)
                 = 1.0

        MALT:   40 / 43 = 93%
        identity = 1.0 * matches / (matches + gaps + total mismatches)
                 = 1.0 * 40 / (40 + 2 + 1)
                 = 0.930232
                 ~ 0.93

    Thus it is required to include indels, potentially deaminated bases and
    unknown bases to produce identity values similar to MALT.
    """
    # this should never happen if reference was correctly reconstructed
    if len(read) != len(ref):
        raise ValueError("Undefined for sequences of unequal length")

    match = 0
    mismatch = 0
    mismatch_string = ''
    for a, b in zip(read, ref):
        thesebases = [a, b]
        if '-' in thesebases:
            mismatch_string += '-'
            # default: exclude indels from mismatches
            if include_indels:
                mismatch += 1
            continue
        if a == 'N':
            if include_unknown:
                mismatch += 1
            else:
                continue
        if b == 'N':
            if include_unknown:
                mismatch += 1
            else:
                continue
        if a == b:
            mismatch_string += '|'
            match += 1
        elif a != b:
            mismatch_string += 'x'
            # default: exclude possible deamination from mismatches
            if not include_deamination:
                if 'C' == b and 'T' == a:
                    continue
                if 'G' == b and 'A' == a:
                    continue
            mismatch += 1

    try:
        perc_identity = 1.0 * match / (match + mismatch)
    except ZeroDivisionError:
        perc_identity = 0.0

    return (perc_identity, mismatch_string)
