Filter reads by conservation
----------------------------
This filter identifies reads mapping to the references of multiple taxa with similar
alignment scores. It is useful when dealing with reads mapping to highly
conserved or orthologous genes that are shared across multiple taxa. The filter
requires you to specify the permitted deviation from the maximal alignment score
(default is 5) and the maximum number of taxa that a read can be mapped to
within this range of alignment scores before it gets excluded (default is 10).
