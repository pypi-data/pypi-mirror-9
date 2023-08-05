#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calculate and filter post-mortem degeneration score for NGS reads in SAM files.

Modified version of PMDtools based on v0.55 by Pontus Skoglund:

> P Skoglund, BH Northoff, MV Shunkov, AP Derevianko, S Paabo, J Krause, M
> Jakobsson (2014) Separating endogenous ancient DNA from modern day
> contamination in a Siberian Neandertal, PNAS, advance online 27 January

Included changes:
- count and show excluded reads due to unsupported CIGAR operations
- count and show excluded reads due to % identity filtering
- port from Python2 to Python3
- bugfix: ambiguous combinations of CIGAR and MD with deletions lead to shifts
          in reconstructed reference sequence
- support for all CIGAR operations except padded references (untested)
- support of IUPAC ambiguity codes
- optional parameters to adapt % identity calculation to MALT defaults
- refactoring into main method
- use of ArgumentParser over deprecated OptionParser
- improved PEP8 and pylint compliance

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

import sys
import argparse
import math
import subprocess
from itertools import repeat

""" custom libraries """
from samsifter.util.sam import reconstruct
from samsifter.util.genetics import reverse_complement, gc, aln_identity


def phred2prob(Q):
    """
    Convert PHRED score to probability of sequencing error.
    """
    return 10.0 ** (-Q / 10.0)


def prob2phred(P):
    """
    Convert probability of sequencing error to PHRED score.
    """
    return -10.0 * math.log(P, 10)


def prob2ascii(P, offset=33):
    """
    Convert probability of sequencing error to ASCII-encoded PHRED score.

    By default uses ASCII offset 33 (Illumina standard).
    """
    return chr(int(prob2phred(P)) + offset)


def prob(pos, model, qual, poly, match=True):
    """
    Calculate probability of either match (default) or mismatch under given
    model.

    Expects distance of base from end of read, a pre-computed distribution of
    damage probabilities, PHRED score of base (probability of sequencing
    error) and probability of true polymorphism.
    """
    p_damage = float(model[pos])
    p_error = phred2prob((ord(qual) - 33)) / 3.0
    p_poly = poly
    p_match = ((1.0 - p_damage) * (1.0 - p_error) * (1.0 - p_poly)
               + (p_damage * p_error * (1.0 - p_poly))
               + (p_error * p_poly * (1.0 - p_damage)))
    p_mismatch = 1.0 - p_match
    if match:
        return p_match
    else:
        return p_mismatch


def L_match(position, model, qual, poly):
    return prob(position, model, qual, poly, True)


def L_mismatch(position, model, qual, poly):
    return prob(position, model, qual, poly, False)


def adjust_quality(position, model, qual):
    """
    Adjust base quality value (sequencing error probability)
    """
    p_damage = float(model[position])
    p_error = phred2prob((ord(qual) - 33)) / 3.0
    adjusted = 1.0 - ((1.0 - p_damage) * (1.0 - p_error))
    return adjusted


def geometric(pval, kval, constant):
    """
    Return probability of deamination based on geometric distribution.
    """
    return ((1.0 - pval) ** (kval - 1)) * pval + constant


def fa_get(ffile, chrom, fstart, fend, samtoolspath, verbose=False):
    """
    unused method stub to get reference sequence from supplied FASTA?
    """
    FNULL = open('/dev/null', 'w')
    chrom = str(chrom)    # 'chr'+str(chrom)
    location = str(chrom) + ':' + str(fstart) + '-' + str(fend)
    cmd_line = [samtoolspath, 'faidx', ffile, location]
    outp_file = subprocess.Popen(cmd_line, stdout=subprocess.PIPE,
                                 stderr=FNULL)
    pileupline = outp_file.stdout.read().split()
    pileupline = ''.join(pileupline[1:])
    if len(pileupline) < 1:
        print('no such reference sequence', cmd_line)
    if verbose:
        print(' '.join(cmd_line))
    return pileupline


def score_pmd(read, ref, quals, ancient_model_deam, modern_model_deam,
              adjustment_model_deam=None,
              polymorphism_contamination=0.001, polymorphism_ancient=0.001,
              adjustbaseq_all=False,
              adjustbaseq=False,
              baseq=0,
              deamination=False,
              cpg=False,
              nocpg=False,
              UDGhalf=False,
              PMDSprim=False):
    """
    Calculate post-mortem degradation score (PMDS).

    Requires full read and reference sequence including clips, skips and gaps
    as recovered from CIGAR and MD to use the correct distance from 5' or 3'
    end in the PMDS calculation. However only the aligned read bases with
    PHRED scores are considered for PMD scoring.

    Optional adjustment of base qualities requires additional adjustment model.
    """
    # this should never happen if reference was correctly reconstructed
    if len(read) != len(ref):
        raise ValueError("Undefined for sequences of unequal length")

    L_D = 1.0    # likelihood of degradation
    L_M = 1.0    # likelihood of mutation

#    L_D_max = 1.0
#    L_M_max = 1.0
#
#    L_D_min = 1.0
#    L_M_min = 1.0

    """
    Check for informative sites (does nothing at the moment)
    """
    '''
    #print ref[-1]
    if cpg:
        if 'CG' not in ref:
            #print 'no informative'
            L_D = 1.0
            L_M = 1.0
    elif UDGhalf:
        if 'CG' not in ref and ref[0] != 'C' and ref[-1] != 'G':
            #print 'no informative'
            L_D = 1.0
            L_M = 1.0
    else:
        if 'C' not in ref and 'G' not in ref:
            #print 'no informative'
            L_D = 1.0
            L_M = 1.0
    '''

    newquals = quals

    qual_idx = 0
    for aln_idx, (readbase, refbase) in enumerate(zip(read, ref)):
        # skipped intron
        if readbase == '-' and refbase == 'X':
            continue

        # hard clipping
        if readbase == refbase == 'X':
            continue

        # soft clipping
        if refbase == 'X':
            qual_idx += 1
            continue

        # gaps in read
        if readbase == '-':
            continue

        # gaps in reference
        if refbase == '-':
            qual_idx += 1
            continue

        # ambiguous bases TODO some of these may actually be informative!
        ambiguous = ('N', 'X', 'B', 'D', 'H', 'V', 'Y', 'R', 'W', 'S')
        if (readbase in ambiguous or refbase in ambiguous):
            qual_idx += 1
            continue

        quality = quals[qual_idx]

        """
        At this point we're dealing with a qualified alignment where each
        position has exactly
        - one informative read base:        readbase       read[aln_idx]
        - one informative reference base:   refbase        ref[aln_idx]
        - one quality score:                quality        quals[qual_idx]
        """

        i = qual_idx                    # distance from 5' end of read
        z = len(quals) - 1 - qual_idx    # distance from 3' end of read

        if adjustbaseq_all and adjustment_model_deam is not None:
            newprob = (adjustment_model_deam[i]
                       + adjustment_model_deam[z]
                       + phred2prob(ord(quality) - 33))
#            newprob = min(newprob, 1.0)
            newqual = prob2ascii(newprob)
            newquals = quals[0:i] + newqual + quals[(i + 1):]

        if (ord(quality) - 33) < baseq:
            # make sure that quality is adjusted even if baseq is below
            # threshold
            if adjustbaseq:
                if refbase == 'C' and readbase == 'T':
#                    if cpg:
#                        if i + 1 >= readlen:
#                            break
#                        if ref[i + 1] != 'G':
#                            continue
#                    elif nocpg:
#                        if i + 1 >= readlen:
#                            break
#                        if ref[i + 1] == 'G':
#                            continue
#                    elif UDGhalf:
#                        if i + 1 >= readlen:
#                            break
#                        if ref[i + 1] != 'G' and i != 0:
#                            continue
                    newprob = adjust_quality(i, ancient_model_deam, quality)
                    newqual = prob2ascii(newprob)
                    newquals = quals[0:i] + newqual + quals[(i + 1):]

                if refbase == 'G' and readbase == 'A':
#                    if cpg:
#                        if i - 1 >= readlen:
#                            break
#                        if ref[i - 1] != 'C':
#                            continue
#                    elif nocpg:
#                        if i - 1 >= readlen:
#                            break
#                        if ref[i - 1] == 'C':
#                            continue
#                    elif UDGhalf:
#                        if ref[i - 1] != 'C' and z != 0:
#                            continue
                    newprob = adjust_quality(z, ancient_model_deam, quality)
                    newqual = prob2ascii(newprob)
                    newquals = quals[0:i] + newqual + quals[(i + 1):]
            continue

#        if deamination:
#            if refbase == 'C':
#                if cpg:
#                    if i + 1 >= readlen:
#                        break
#                    if read[i + 1] != 'G':
#                        continue
#                elif nocpg:
#                    if i + 1 >= readlen:
#                        break
#                    if read[i + 1] == 'G':
#                        continue
#                elif UDGhalf:
#                    if i + 1 >= readlen:
#                        break
#                    if ref[i + 1] != 'G' and i != 0:
#                        continue
#
#                thekey = refbase + readbase + str(i)
#                if thekey in mismatch_dict.keys():
#                    addition = mismatch_dict[thekey]
#                    addition += 1
#                    mismatch_dict[thekey] = addition
#                else:
#                    mismatch_dict[thekey] = 1
#
#            if refbase == 'G':
#                if cpg:
#                    if i - 1 >= readlen:
#                        break
#                    if ref[i - 1] != 'C':
#                        continue
#                elif nocpg:
#                    if i - 1 >= readlen:
#                        break
#                    if ref[i - 1] == 'C':
#                        continue
#                elif UDGhalf:
#                    if i - 1 >= readlen:
#                        break
#                    if ref[i - 1] != 'C' and z != 0:
#                        continue
#                thekey = refbase + readbase + str(z)
#                if thekey in mismatch_dict_rev.keys():
#                    addition = mismatch_dict_rev[thekey]
#                    addition += 1
#                    mismatch_dict_rev[thekey] = addition
#                else:
#                    mismatch_dict_rev[thekey] = 1
#            continue

        """
        compute degradation score
        """
#        if i >= readlen:continue
        if refbase == 'C':
#            if cpg:
#                if i + 1 >= readlen:
#                    break
#                if ref[i + 1] != 'G':
#                    continue
#            elif cpg:
#                if i + 1 >= readlen:
#                    break
#                if ref[i + 1] == 'G':
#                    continue
#            elif UDGhalf:
#                if i + 1 >= readlen:
#                    break
#                if ref[i + 1] != 'G' and i != 0:
#                    continue

            if readbase == 'T':
                L_D = L_D * L_mismatch(i, ancient_model_deam, quality,
                                       polymorphism_ancient)
                L_M = L_M * L_mismatch(i, modern_model_deam, quality,
                                       polymorphism_contamination)

                if adjustbaseq:
                    newprob = adjust_quality(i, ancient_model_deam, quality)
                    newqual = prob2ascii(newprob)
                    """
                    print phred2prob(ord(quality)),newprob
                    print ord(quality),newphred
                    print quality,newqual
                    print quals[0:i],quality,quals[(i+1):]
                    print quals
                    """
                    quals = quals[0:i] + newqual + quals[(i + 1):]

            elif readbase == 'C':
                L_D = L_D * L_match(i, ancient_model_deam, quality,
                                    polymorphism_ancient)
                L_M = L_M * L_match(i, modern_model_deam, quality,
                                    polymorphism_contamination)

#            if PMDSprim and readbase in ['C', 'T', 'c', 't']:
#                L_D_max = L_D_max * L_mismatch(i, ancient_model_deam, quality,
#                                               polymorphism_ancient)
#                L_M_max = L_M_max * L_mismatch(i, modern_model_deam, quality,
#                                               polymorphism_ancient)
#                L_D_min = L_D_min * L_match(i, ancient_model_deam, quality,
#                                            polymorphism_ancient)
#                L_M_min = L_M_min * L_match(i, modern_model_deam, quality,
#                                            polymorphism_ancient)

        if refbase == 'G':
            if cpg:
                if ref[i - 1] != 'C':
                    continue
            elif nocpg:
                if ref[i - 1] == 'C':
                    continue
            elif UDGhalf:
                if ref[i - 1] != 'C' and z != 0:
                    continue

            if readbase == 'A':
                L_D = L_D * L_mismatch(z, ancient_model_deam, quality,
                                       polymorphism_ancient)
                L_M = L_M * L_mismatch(z, modern_model_deam, quality,
                                       polymorphism_contamination)

                if adjustbaseq:
                    newprob = adjust_quality(z, ancient_model_deam, quality)
                    newqual = prob2ascii(newprob)
                    newquals = quals[0:i] + newqual + quals[(i + 1):]

            elif readbase == 'G':
                L_D = L_D * L_match(z, ancient_model_deam, quality,
                                    polymorphism_ancient)
                L_M = L_M * L_match(z, modern_model_deam, quality,
                                    polymorphism_contamination)

#            if PMDSprim and readbase in ['G', 'A', 'g', 'a']:
#                L_D_max = L_D_max * L_mismatch(z, ancient_model_deam, quality,
#                                               polymorphism_ancient)
#                L_M_max = L_M_max * L_mismatch(z, modern_model_deam, quality,
#                                               polymorphism_ancient)
#                L_D_min = L_D_min * L_match(z, ancient_model_deam, quality,
#                                            polymorphism_ancient)
#                L_M_min = L_M_min * L_match(z, modern_model_deam, quality,
#                                            polymorphism_ancient)

    # calculate log-likelihood ratio as final PMD score
    pmds = math.log(L_D / L_M)

    return (L_D, L_M, pmds, newquals)


def main():
    parser = argparse.ArgumentParser(
        usage=("python %(prog)s <SAM formatted data with MD field present "
               "from stdin> [options]")
    )

    # options to control PMD score calculation
    pmd_options = parser.add_argument_group(
        title="PMD parameters",
        description=("influence the geometric distribution used for PMD score "
                     "calculation by changing these parameters")
    )
    pmd_options.add_argument("--PMDpparam",
                             action="store",
                             type=float,
                             dest="PMDpparam",
                             help="parameter p in geometric probability \
                             distribution of PMD",
                             default=0.3)
    pmd_options.add_argument("--PMDconstant",
                             action="store",
                             type=float,
                             dest="PMDconstant",
                             help="constant C in geometric probability \
                             distribution of PMD",
                             default=0.01)
    pmd_options.add_argument("--polymorphism_ancient",
                             action="store",
                             type=float,
                             dest="polymorphism_ancient",
                             help="True biological polymorphism between the \
                             ancient individual and the reference sequence",
                             default=0.001)
    pmd_options.add_argument("--polymorphism_contamination",
                             action="store",
                             type=float,
                             dest="polymorphism_contamination",
                             help="True biological polymorphism between the \
                             contaminants and the reference sequence",
                             default=0.001)

    # options to filter SAM file
    filter_options = parser.add_argument_group(
        title="filters",
        description=("restrict analysis to a subset of reads by setting these "
                     "thresholds")
    )
    filter_options.add_argument("--dry",
                                action="store_true",
                                dest="dry",
                                help="print SAM input without any filters",
                                default=False)
    filter_options.add_argument("-n", "--number",
                                action="store",
                                type=int,
                                dest="maxreads",
                                help="stop after these many reads have been \
                                processed",
                                default=(10 ** 20))
    filter_options.add_argument("-c", "--chromosome",
                                action="store",
                                type=str,
                                dest="chromosome",
                                help="only process data from this chromosome",
                                default=False)
    filter_options.add_argument("--perc_identity",
                                type=float,
                                dest="perc_identity",
                                help="only output sequences with percent \
                                identity above this threshold",
                                default=0.0)
    filter_options.add_argument("-m", "--requiremapq",
                                action="store",
                                type=int,
                                dest="mapq",
                                help="only process sequences with mapping \
                                quality at least this great",
                                default=0)
    filter_options.add_argument("--readlength",
                                action="store",
                                type=int,
                                dest="readlength",
                                help="only process sequences with this read \
                                length",
                                default=0)
    filter_options.add_argument("--maxlength",
                                action="store",
                                type=int,
                                dest="maxlength",
                                help="only process sequences with max this \
                                read length",
                                default=300)
    filter_options.add_argument("--minlength",
                                action="store",
                                type=int,
                                dest="minlength",
                                help="only process sequences with min this \
                                read length",
                                default=0)
    filter_options.add_argument("--maxGC",
                                action="store",
                                type=float,
                                dest="maxGC",
                                help="only process sequences with max this \
                                GC content of the aligning reference sequence",
                                default=1.0)
    filter_options.add_argument("--minGC",
                                action="store",
                                type=float,
                                dest="minGC",
                                help="only process sequences with min this GC \
                                content of the aligning reference sequence",
                                default=0.0)
    filter_options.add_argument("-q", "--requirebaseq",
                                action="store",
                                type=int,
                                dest="baseq",
                                help="only process bases with base quality at \
                                least this great",
                                default=0)
    filter_options.add_argument("-t", "--threshold",
                                type=float,
                                dest="threshold",
                                help="only output sequences with PMD score \
                                above this threshold",
                                default=(-20000.0))
    filter_options.add_argument("--upperthreshold",
                                type=float,
                                dest="upperthreshold",
                                help="only output sequences with PMD score \
                                below this threshold",
                                default=(1000000.0))

    # options controlling handling of CpG contexts
    cpg_options = parser.add_argument_group(
        title="CpG context",
        description=("options controlling the handling of deamination in CpG "
                     "contexts")
    )
    # --CpG, --noCpG and --UDGhalf exclude each other
    cpg_excl = cpg_options.add_mutually_exclusive_group(required=False)
    cpg_excl.add_argument("--CpG", "--UDGplus",
                          action="store_true",
                          dest="cpg",
                          help="only use Cs and Gs in CpG context",
                          default=False)
    cpg_excl.add_argument("--noCpG",
                          action="store_true",
                          dest="nocpg",
                          help="dont use Cs and Gs in CpG context",
                          default=False)
    cpg_excl.add_argument("--UDGhalf",
                          action="store_true",
                          dest="UDGhalf",
                          help=("only use Cs and Gs in CpG context, the first "
                                "and last base are used regardless of "
                                "dinucleotide context"),
                          default=False)
#    cpg_options.add_argument("--UDGplus",
#                             action="store_true",
#                             dest="UDGplus",
#                             help="only use Cs and Gs in CpG context \
#                             (synonymous with option --CpG)",
#                             default=False)
    cpg_options.add_argument("--UDGminus",
                             action="store_true",
                             dest="UDGminus",
                             help="use all bases (placeholder)",
                             default=False)

    # options controlling output
    output_options = parser.add_argument_group(
        title="output",
        description="control type and detail of output"
    )
    output_options.add_argument("--verbose",
                                action="store_true",
                                dest="verbose",
                                help="verbose",
                                default=False)
    output_options.add_argument("--header",
                                action="store_true",
                                dest="header",
                                help="output the SAM header",
                                default=False)
    output_options.add_argument("--writesamfield",
                                action="store_true",
                                dest="writesamfield",
                                help="add 'DS:Z:<PMDS>' field to SAM output, \
                                will overwrite if already present",
                                default=False)
    output_options.add_argument("--stats",
                                action="store_true",
                                dest="stats",
                                help="output summarizing statistics to stderr",
                                default=False)
    output_options.add_argument("--debug",
                                action="store_true",
                                dest="debug",
                                help="show additional information for \
                                debugging",
                                default=False)
    output_options.add_argument("-p", "--printDS",
                                action="store_true",
                                dest="printDS",
                                help="print PMD scores",
                                default=False)
    output_options.add_argument("--printalignments",
                                action="store_true",
                                dest="printalignments",
                                help="print human readable alignments",
                                default=False)
    output_options.add_argument("--platypus",
                                action="store_true",
                                dest="platypus",
                                help="output big list of base frequencies for \
                                platypus",
                                default=False)
    output_options.add_argument("-d", "--deamination",
                                action="store_true",
                                dest="deamination",
                                help="output base frequencies in the read at \
                                positions where there are C or G in the \
                                reference",
                                default=False)

    # options to modify calculation of percent identity
    perc_id_options = parser.add_argument_group(
        title="percent identity",
        description="options to modify calculation of percent identity"
    )
    perc_id_options.add_argument("--include_deamination",
                                 action="store_true",
                                 dest="include_deamination",
                                 help="treat possibly deaminated T>C and A>G \
                                 pairs as mismatches in calculation of \
                                 percent identity",
                                 default=False)
    perc_id_options.add_argument("--include_indels",
                                 action="store_true",
                                 dest="include_indels",
                                 help="treat insertions and deletions as \
                                 mismatches in calculation of percent \
                                 identity",
                                 default=False)
    perc_id_options.add_argument("--include_unknown",
                                 action="store_true",
                                 dest="include_unknown",
                                 help="treat Ns in either read or reference \
                                 as mismatch in calculation of percent \
                                 identity",
                                 default=False)

    # remaining options
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s v0.55 (modified)')
    parser.add_argument("--PMDSprim",
                        action="store_true",
                        dest="PMDSprim",
                        help="PMDSprim",
                        default=False)
    parser.add_argument("--PMDSprimthreshold",
                        action="store",
                        type=float,
                        dest="PMDSprimthreshold",
                        help="PMDSprimthreshold",
                        default=False)
    parser.add_argument("--first",
                        action="store_true",
                        dest="first",
                        help="outputs the deamination rate at the first \
                        position only, but with a standard error",
                        default=False)
    parser.add_argument("--range",
                        action="store",
                        type=int,
                        dest="range",
                        help="output deamination patterns for this many \
                        positions from the sequence terminus (default=30)",
                        default=30)
    parser.add_argument("--noclips",
                        action="store_true",
                        dest="noclips",
                        help="no clips",
                        default=False)
    parser.add_argument("--noindels",
                        action="store_true",
                        dest="noindels",
                        help="no indels",
                        default=False)
    parser.add_argument("--onlyclips",
                        action="store_true",
                        dest="onlyclips",
                        help="only clips",
                        default=False)
    parser.add_argument("--onlydeletions",
                        action="store_true",
                        dest="onlydeletions",
                        help="only deletions",
                        default=False)
    parser.add_argument("--onlyinsertions",
                        action="store_true",
                        dest="onlyinsertions",
                        help="only insertions",
                        default=False)
    parser.add_argument("--nodeletions",
                        action="store_true",
                        dest="nodeletions",
                        help="no deletions",
                        default=False)
    parser.add_argument("--noinsertions",
                        action="store_true",
                        dest="noinsertions",
                        help="no insertions",
                        default=False)
    parser.add_argument("--notreverse",
                        action="store_true",
                        dest="notreverse",
                        help="no reverse complement alignments",
                        default=False)
    parser.add_argument("-a", "--adjustbaseq",
                        action="store_true",
                        dest="adjustbaseq",
                        help="apply PMD-aware adjustment of base quality \
                        scores specific to C>T and G>A mismatches to the \
                        reference",
                        default=False)
    parser.add_argument("--adjustbaseq_all",
                        action="store_true",
                        dest="adjustbaseq_all",
                        help="apply PMD-aware adjustment of base quality \
                        scores regardless of observed bases",
                        default=False)
    parser.add_argument("--samtoolspath",
                        action="store",
                        dest="samtoolspath",
                        help="full path to samtools",
                        default='samtools')
    parser.add_argument("--basecomposition",
                        action="store_true",
                        dest="basecomposition",
                        help="basecomposition",
                        default=False)
    parser.add_argument("-r", "--refseq",
                        action="store",
                        dest="refseq",
                        help="refseq",
                        default=False)
    parser.add_argument("--estimate",
                        action="store_true",
                        dest="estimate",
                        help="two-terminus estimate of contamination",
                        default=False)
    parser.add_argument("--estimatebase",
                        action="store",
                        type=int,
                        dest="estimatebase",
                        help="position of base used fortwo-terminus estimate \
                        of contamination",
                        default=0)
    parser.add_argument("-b", "--basic",
                        action="store",
                        type=int,
                        dest="basic",
                        help="only output reads with a C>T mismatch this \
                        many basepairs from the 5' end",
                        default=0)

    (options, args) = parser.parse_known_args()

#    if options.UDGplus:
#        options.CpG = True

#    maxlen = options.maxlength

    # pre-compute probabilities of deamination for 1000 bases under modern and
    # ancient models
    modern_model_deam = [i for i in repeat(0.001, 1000)]
    ancient_model_deam = [geometric(options.PMDpparam, i, options.PMDconstant)
                          for i in range(1, 1000)]
    adjustment_model_deam = None
    if options.adjustbaseq_all:
        # constant is 0.0 here in contrast to model used to compute PMD scores
        adjustment_model_deam = [geometric(options.PMDpparam, i, 0.0)
                                 for i in range(1, 1000)]

    # base composition
#    start_count = 0
#    rev_start_count = 0
#    not_counted = 0
#    imperfect = 0

#    start_dict= {}
#    start_dict_rev = {}
    mismatch_dict = {}
    mismatch_dict_rev = {}
#    mismatch_dict_CpG = {}
#    mismatch_dict_CpG_rev = {}

    firstC = 0
    firstT = 0

    clipexcluded = 0
    indelexcluded = 0
    cigarextexcluded = 0  # reads excluded for extended CIGAR (N, H, P, not S)
    identityexcluded = 0  # reads excluded due to percent identity filter
    noMD = 0
    noGCexcluded = 0
    excluded_threshold = 0
    passed = 0
    noquals = 0
#    maskings = 0
#
#    CCandCC = 0
#    CTandCC = 0
#    CCandCT = 0
#    CTandCT = 0
#
#    estimator_list = []

    composition_dict = {}
    composition_dict_rev = {}

    line_counter = 0
    for line in sys.stdin:
        if '@' in line[0]:
            if options.header:
                print(line.rstrip('\n'))
            continue
        line_counter += 1
        line = line.rstrip('\n')
        col = line.split('\t')

        if options.debug:
            print(col)

#        readname = col[0]
        position = int(col[3])
        chromosome = col[2]

        if options.chromosome:
            if chromosome != options.chromosome:
                continue
        MAPQ = int(col[4])
        read = col[9]
        readlen = len(read)
        quals = col[10]
        flag = col[1]
        position = int(col[3])
        cigar = col[5]

        if len(quals) < 2:
            noquals += 1
            continue

        if options.noinsertions:
            if 'I' in cigar:
                continue
        if options.nodeletions:
            if 'D' in cigar:
                continue
        if options.onlyinsertions:
            if 'I' not in cigar:
                continue
        if options.onlydeletions:
            if 'D' not in cigar:
                continue
        if options.noindels:
            if 'I' in cigar or 'D' in cigar:
                indelexcluded += 1
                continue
        if options.noclips:
            if 'S' in cigar or 'H' in cigar or 'N' in cigar or 'P' in cigar:
                clipexcluded += 1
                continue
        if options.onlyclips:
            if 'S' not in cigar:
                continue
        if 'H' in cigar or 'P' in cigar or 'N' in cigar:
            print("cigar found: %s" % (cigar,),
                  "PMDtools only supports cigar operations M, I, S and D,",
                  "the alignment has been excluded",
                  file=sys.stderr)
            cigarextexcluded += 1
            continue
        if MAPQ < options.mapq:
            continue

        # read length filter
        # TODO check for default values unnecessary, just remove defaults and
        # check for args directly
        if options.readlength > 0:
            if options.readlength != len(read):
                continue
        if options.minlength > 0:
            if options.minlength > len(read):
                continue
        if options.maxlength != 300:
            if options.maxlength < len(read):
                continue

        # chromosome filter
        if options.chromosome:
            if chromosome != options.chromosome:
                continue

        # check orientation of read
        if flag.isdigit():
            if int(flag) & 16:
                reverse = True
            else:
                reverse = False
        else:
            if 'r' in flag:
                reverse = True
            else:
                reverse = False

        # filter reverse reads
        if options.notreverse:
            if reverse:
                continue

        # check for previously calculated PMD score
        DSfield = False
        if 'DS:Z:' in line:
            DSfield = True
            PMDS = float(line.split('DS:Z:')[1].rstrip('\n').split()[0])
            LR = PMDS
#            print PMDS

        """
        Recreate reference sequence from MD field
        """
        if (DSfield is False
           or options.writesamfield
           or options.basic > 0
           or options.perc_identity > 0.01
           or options.printalignments
           or options.adjustbaseq
           or options.adjustbaseq_all
           or options.deamination
           or options.dry
           or options.estimate
           or options.first):
            read = col[9]
            try:
                MD = line.split('MD:Z:')[1].split()[0].rstrip('\n')
            except IndexError:
                noMD += 1
                continue

            # using external library to reconstruct reference from CIGAR and MD
            rec = reconstruct(read, cigar, MD)
            (rec_ref_full, rec_read_full, rec_ref_aln, rec_read_aln) = rec

            if reverse:
                read = reverse_complement(read)
                # don't use raw read beyond here...
                rec_ref_full = reverse_complement(rec_ref_full)
                rec_read_full = reverse_complement(rec_read_full)
                rec_ref_aln = reverse_complement(rec_ref_aln)
                rec_read_aln = reverse_complement(rec_read_aln)
                quals = quals[::-1]

            # this assumption previously lead to trouble because of missing
            # gaps in aligned read!
            real_read = read
            real_ref_seq = rec_ref_aln

        # debugging the reference sequence reconstruction
        if options.debug:
            print("%s\tread\n%s\tref" % (real_read, real_ref_seq))
            print("CIGAR:\t%s" % (cigar,))
            print("MD:\t%s" % (MD,))

        # GC content filter
        # FA: Read and aligned reference can have different lengths!
        # See genetics.gc() for a faster, case-unaware alternative considering
        # all ambiguity codes.
#        GCcontent = (1.0 * (real_ref_seq.count('G') + real_ref_seq.count('C'))
#                     / readlen)
        GCcontent = gc(real_ref_seq)
        if GCcontent > options.maxGC:
            continue
        elif GCcontent < options.minGC:
            continue

        # test for empty reference sequence TODO include in reconstruction
        # method and throw exception?
        if ('G' not in real_ref_seq
           and 'C' not in real_ref_seq
           and 'T' not in real_ref_seq
           and 'A' not in real_ref_seq):
            print('bad reference sequence reconstruction: %s' % real_ref_seq,
                  file=sys.stderr)
            print('SAM line: %s' % (line,))
            exit(1)

        if options.basecomposition:
            backoffset = 10
            if reverse:
                endpos = position
                startpos = position + len(real_read)
            else:
                startpos = position
                endpos = position + len(real_read)

            """
            5' end
            """
            largerefseq = fa_get(options.refseq,
                                 chromosome,
                                 startpos - backoffset,
                                 startpos + options.range)
            if len(largerefseq) < 1:
                continue
#            print largerefseq
            if reverse:
                largerefseq = reverse_complement(largerefseq)
#            print(largerefseq, real_read)
            for i in range(-backoffset, options.range):
#                print(i+backoffset, len(largerefseq))
                base = largerefseq[min([i + backoffset, len(largerefseq)])]
                thekey = '5' + base + str(i)
                if thekey in composition_dict.keys():
                    addition = composition_dict[thekey]
                    addition += 1
                    composition_dict[thekey] = addition
                else:
                    composition_dict[thekey] = 1

            """
            3' end
            """
            largerefseq = fa_get(options.refseq,
                                 chromosome,
                                 endpos - options.range,
                                 endpos + backoffset)
            if len(largerefseq) < 1:
                continue
            if reverse:
                largerefseq = reverse_complement(largerefseq)

            for i in range(-backoffset, options.range):
                base = largerefseq[min([i + backoffset, len(largerefseq)])]
                thekey = '3' + base + str(i)
                if thekey in composition_dict_rev.keys():
                    addition = composition_dict_rev[thekey]
                    addition += 1
                    composition_dict_rev[thekey] = addition
                else:
                    composition_dict_rev[thekey] = 1
            continue    # useless?

        """
        basic filter
        prints the SAM line if a C>T mismatch with sufficient base quality is
        observed in the first n bases, where n is specified
        """
        if options.basic > 0:
#            start_position = len(real_read) - len(real_read.lstrip('-'))
            for a, b, x in zip(real_read, real_ref_seq,
                               range(0, len(real_ref_seq))):
                if a == 'N':
                    break
                elif b == 'N':
                    break
                elif a == '-':
                    break
                elif b == '-':
                    break
                i = x                       # - start_position
                if i >= readlen:            # 20
                    break
                if i >= options.basic:
                    break
#                print(a, b, i)
                if options.cpg:
                    if (b == 'C' and a == 'T'
                       and ord(quals[i] - 33) > options.baseq
                       and real_ref_seq[i + 1] == 'G'):
                        print(line.rstrip('\n'))
                        break

                elif (b == 'C' and a == 'T'
                      and ord(quals[i]) - 33 > options.baseq):
                    print(line.rstrip('\n'))
                    break

        """
        first base
        prints the deamination rate at the first base and a standard error
        computed by jackknife over reads
        """
        if options.first:
            b = real_ref_seq[0]
            a = real_read[0]
            if options.cpg:
                if (b == 'C' and a == 'T'
                   and ((ord(quals[0])-33) > options.baseq)
                        and (real_ref_seq[1] == 'G')):
                    firstT += 1
                if (b == 'C' and a == 'C'
                   and ((ord(quals[0])-33) > options.baseq)
                        and (real_ref_seq[1] == 'G')):
                    firstC += 1
            else:
                if (b == 'C' and a == 'T'
                   and ord(quals[0]) - 33 > options.baseq):
                    firstT += 1
                if (b == 'C' and a == 'C'
                   and ord(quals[0]) - 33 > options.baseq):
                    firstC += 1

        if options.perc_identity > 0.01 or options.printalignments:
            """
            divergence filter
            """
            (perc_identity, mismatch_string) = aln_identity(
                rec_read_aln,
                rec_ref_aln,
                options.include_indels,
                options.include_deamination,
                options.include_unknown
            )
            if perc_identity < options.perc_identity:
                identityexcluded += 1
                continue

        """
        start PMD score computations
        """
        if (DSfield is False
           or (DSfield is True and options.writesamfield is True)
           or options.basic > 0
           or options.adjustbaseq
           or options.adjustbaseq_all
           or options.deamination
           or options.dry):

            (L_D, L_M, LR, newquals) = score_pmd(
                rec_read_full,  # was: real_read
                rec_ref_full,   # was: real_ref_seq
                quals,
                ancient_model_deam,
                modern_model_deam,
                adjustment_model_deam,
                options.polymorphism_contamination,
                options.polymorphism_ancient,
                options.adjustbaseq_all,
                options.adjustbaseq,
                options.baseq
            )
            # TODO re-enable these options step by step...
#                options.deamination,
#                options.cpg,
#                options.nocpg,
#                options.UDGhalf,
#                options.PMDSprim)

#            if options.PMDSprim:
#                maxPMDSval = math.log(L_D_max / L_M_max)
#                maxPMDSval = maxPMDSval / readlen
#                if LR > 0.0:
#                    LRnumerator = math.log(L_D_max / L_M_max)
#                elif LR < 0.0:
#                    LRnumerator = math.log(L_D_max / L_M_max)
#                if options.PMDSprimthreshold:
#                    if maxPMDSval < options.PMDSprimthreshold:
#                        continue
#
#                if options.printDS:
#                    print(LR, maxPMDSval, maxPMDSval, maxPMDSval * readlen,
#                          readlen)
##                LR = LR / LRnumerator
#            quals = newquals

        if options.adjustbaseq:
            if reverse:
                qualsp = quals[::-1]
            else:
                qualsp = quals
            line = ('\t'.join(col[0:10]) + '\t'
                    + qualsp + '\t'
                    + '\t'.join(col[11:]))

        """
        add PMDS tag
        """
        if options.writesamfield is True:
            # remove DS field if present
            if DSfield is True:
                newline = ''
                for col in line.split('\t'):
                    if 'DS:Z:' in col:
                        continue
                    else:
                        newline += col + '\t'
                line = newline.rstrip('\t')

            line = line.rstrip('\n') + '\t' + 'DS:Z:' + str(round(LR, 3))

        if options.printDS:
            print(L_D, '\t', L_M, '\t', L_D / L_M, '\t', LR)
#            print(L_D, '\t', L_M, '\t', L_D / L_M, '\t', LR, '\t',
#                  readlen, '\t',
#                  perc_identity, '\t',
#                  perc_identity * math.log(L_D / L_M))

        if options.dry:
            if len(line) < 1:
                continue
            print(line.rstrip('\n'))
            continue

        if options.threshold > (-10000) or options.upperthreshold < (1000000):
            if LR >= options.threshold and LR < options.upperthreshold:
                print(line.rstrip('\n'))
            else:
                excluded_threshold += 1

        if options.printalignments:
            if (options.threshold > -10000
               or options.upperthreshold < 1000000):
                try:
                    LR = math.log(L_D / L_M)
                except:
                    continue
                if (LR < options.threshold
                   or LR > options.upperthreshold < 1000000):
                    continue

            quals1 = ''
            quals2 = ''
            for q in quals:
                qnum = ord(q) - 33
                if qnum < 10:
                    quals1 += '0'
                    quals2 += str(qnum)
                else:
                    quals1 += str(qnum)[0]
                    quals2 += str(qnum)[1]
#            print(MD, cigar, reverse)
#            print(col[9])
            print(real_read)
            print(mismatch_string)
            print(real_ref_seq)
            print(quals)
#            print(quals1)
#            print(quals2)
#            print(col[10])
            print('')
        passed += 1
        if passed >= options.maxreads:
            break

    if options.first:
        n = firstC + firstT
        freq = 1.0 * firstT / n
        SE = math.sqrt((freq * (1.0 - freq)) / n)
        if freq == 0.0:
            SE = 'NA'
        print('C>T at first position and SE:', freq, '\t', SE)
#        print('C>T at first position and SE:', freq, '\t', SE, '\t',
#              n, firstC, firstT)

    if options.stats:
        print('""""""""""""""""""""""""""""""""', file=sys.stderr)

        # added stats
        print("excluded due to extended CIGAR (H, N, P):\t%i"
              % (cigarextexcluded,), file=sys.stderr)
        print("excluded due percent identity filter:\t%i"
              % (identityexcluded,), file=sys.stderr)

        print("excluded due to clipping:\t%i" % (clipexcluded,),
              file=sys.stderr)
        print("excluded due to indels:\t%i" % (indelexcluded,),
              file=sys.stderr)
        print("no MD field:\t%i" % (noMD,), file=sys.stderr)
        print("no G or C in ref:\t%i" % (noGCexcluded,), file=sys.stderr)
        print("total seqs:\t%i" % (passed,), file=sys.stderr)
        print("excluded due to PMD score < %i:\t%i"
              % (int(options.threshold), excluded_threshold), file=sys.stderr)
        print("passed seqs:\t%i" % (passed - excluded_threshold,),
              file=sys.stderr)

        print('""""""""""""""""""""""""""""""""', file=sys.stderr)

    if options.deamination:
        if True:
            pairs = ['CT', 'CA', 'CG', 'CC', 'GA', 'GT', 'GC', 'GG']
            itotaldict = {}
            ztotaldict = {}
            for i in range(0, options.range):
                itotal = 0
                ztotal = 0
                for p in pairs:
                    thekey = p + str(i)
                    try:
                        itotal += mismatch_dict[thekey]
                    except KeyError:
                        pass
                    try:
                        ztotal += mismatch_dict_rev[thekey]
                    except KeyError:
                        pass
                itotaldict[i] = itotal
                ztotaldict[i] = ztotal

            print('z\t', '\t'.join(pairs))

            for i in range(0, options.range):
                print(str(i) + '\t')
                for p in pairs:
                    thekey = p + str(i)
                    if 'C' in p[0]:
                        try:
                            thecount = mismatch_dict[thekey]
                        except KeyError:
                            print('0.00000\t')
                            continue
                        thetotal = itotaldict[i]
                        frac = 1.0 * thecount / thetotal
                    if 'G' in p[0]:
                        try:
                            thecount = mismatch_dict_rev[thekey]
                        except KeyError:
                            print('0.00000\t')
                            continue
                        thetotal = ztotaldict[i]
                        frac = 1.0 * thecount / thetotal
                    print(str(round(frac, 5)) + '\t')
                print('')

    if options.basecomposition:
        print(composition_dict)
        print(composition_dict_rev)
        if True:
            pairs = ['5T', '5A', '5G', '5C', '3T', '3A', '3G', '3C']
            itotaldict = {}
            ztotaldict = {}
            for i in range(-backoffset, options.range):
                itotal = 0
                ztotal = 0
                for p in pairs:
                    thekey = p + str(i)
                    try:
                        itotal += composition_dict[thekey]
                    except KeyError:
                        pass
                    try:
                        ztotal += composition_dict_rev[thekey]
                    except KeyError:
                        pass
                itotaldict[i] = itotal
                ztotaldict[i] = ztotal

            print('z\t', '\t'.join(pairs))

            for i in range(-backoffset, options.range):
                print(str(i) + '\t')
                for p in pairs:
                    thekey = p + str(i)
                    if '5' in p[0]:
                        try:
                            thecount = composition_dict[thekey]
                        except KeyError:
                            print('0.00000\t')
                            continue
                        thetotal = itotaldict[i]
                        frac = 1.0 * thecount / thetotal
                    if '3' in p[0]:
                        try:
                            thecount = composition_dict_rev[thekey]
                        except KeyError:
                            print('0.00000\t')
                            continue
                        thetotal = ztotaldict[i]
                        frac = 1.0 * thecount / thetotal
                    print(str(round(frac, 5)) + '\t')
                print('')

    exit()

if __name__ == "__main__":
    main()
