"""Separating ancient DNA from modern contamination.

This package includes a modified version of PMDtools. The original software
developed by Pontus Skoglund is available at
https://code.google.com/p/pmdtools/.

PMDtools implements a likelihood framework incorporating postmortem damage
(PMD), base quality scores and biological polymorphism to identify degraded DNA
sequences that are unlikely to originate from modern contamination. Using the
model, each sequence is assigned a PMD score, for which positive values
indicate support for the sequence being genuinely ancient. For details of the
method, please see the main paper in PNAS:
http://www.pnas.org/content/111/6/2229.abstract

In addition, PMDtools also offers PMD-aware base quality score adjustment and
investigation of damage patterns.

PMDtools takes SAM-formatted input, and requires an MD tag with alignment
information. The MD tag is featured in the output of many aligners but can
otherwise be added e.g. using the SAMtools fillmd/calmd tool
(Li, Handsaker et al. 2009).
"""
