[BetterRMDup] Remove duplicates
-------------------------------
This wrapper for Alexander Peltzer's `BetterRMDup` removes duplicate reads from
BAM files and improves upon the SAMtools `rmdup` tool by considering both the
start *and* the stop coordinates. It runs the command ::

	betterrmdup -

which itself is a wrapper for ::

	java -jar BetterRMDup.jar -

The tool currently provides no further options.

.. seealso:: :ref:`remove_duplicates` for the original SAMtools `rmdup`
