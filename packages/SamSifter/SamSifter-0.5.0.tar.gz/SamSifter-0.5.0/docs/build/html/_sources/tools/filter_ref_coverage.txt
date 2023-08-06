Filter references by evenness of coverage
-----------------------------------------
This filter analyses the distribution of read bases to reference bases to
calculate the Gini coefficient for each reference, then filters all
references exceeding the given maximimal Gini threshold (default 0.90) to achieve
a higher prevalence of evenly covered references.

The filter can be further restricted to only consider references with average 
coverage falling within a certain range. By default the range is set from 0x
minimal to 9999x maximal coverage, hence the thresholds have no effect. However,
because the Gini coefficient is a measure of *relative* inequality it may have
less significance for references with low minimum coverage, which can be
effectively excluded from filtering by setting a corresponding minimum coverage.

By default all reference bases are considered, but the calculation of coverage
and read length distributions can optionally be restricted to only the covered
bases (coverage >= 1).

What is the Gini coefficient?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The Gini coefficient is often used as a metric for the relative inequality of
income distribution across the population, however it can also be applied to
describe the heterogenity of the distribution of read bases to reference bases
(= the coverage distribution). This makes it a useful tool when dealing with
references that show distinct peaks in their coverage plot due to large clusters
of reads that map to few conserved areas while leaving the larger part of the
reference sequence uncovered.

Given the normed cumulative coverage distribution of all covered reference bases
(= a Lorenz curve) the Gini coefficient describes the ratio of the area A between
the Lorenz curve and the diagonal (describing a perfectly even distribution of
read bases) over the total area B underneath the diagonal. Thus, a completely even
distribution of read bases across the entire reference would have a minimal Gini
coefficient of 0.0 while a completely uneven distribution with all read bases
mapped to just one reference base would have a maximal Gini coefficient of 1.0.

Experimental options
^^^^^^^^^^^^^^^^^^^^
This filter can also be used to analyze the read length distribution per
reference (disabled by default) and to plot coverage and read length
distributions (also disabled by default).

.. warning:: Activating the plotting of these distributions for a large input
             dataset can create I/O problems due to the large amounts of PNG
             files generated. It will also decrease the performance of this
             filter considerably and should only be used to troubleshoot filter
             parameters for small subsets of the data.
