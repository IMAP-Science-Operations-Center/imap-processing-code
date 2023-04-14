def tof_plot():
    """
    Dependent data from L1B:
        * annotated direct event

    For instrument trending purposes, and for analysis of backgrounds and quality of science data, some addi-
    tional histogrammed plots should be made at this stage. They analyze the time-of-flight performance of the
    detector section.
    Per sensor, and for all direct events that have been annotated as “not bad” to this point:
    • plot histograms of tA − tB in bins of 1 ns, for all DEs with a valid tA − tB, summed over all look
    directions, separately by ESA and summed over all ESAs.
    • plot histograms of tC1 − tA in bins of 1 ns, for all DEs with a valid tC1 − tA, summed over all look
    directions, separately by ESA and summed over all ESAs.
    • plot histograms of tC1 − tB in bins of 1 ns, for all DEs with a valid tC1 − tB, summed over all look
    directions, separately by ESA and summed over all ESAs.
    • plot histograms of tC2 − tC1 in bins of 0.5 ns, for all DEs with a valid tC2 −tC1, summed over all look
    directions, separately by ESA and summed over all ESAs.
    For all four of the plots above, it is diagnostically useful to be able to overplot the histograms not just
    for all DEs with the specific valid TOF, but specifically for double-coincidence DEs that have only
    the one TOF valid and no other hits. Because scientists will debate whether they want the histogram
    scale to be logarithmic or linear, it’s probably best to generate both. If you generate only one, choose
    logarithmic.
    • plot two-dimensional histograms, using a logarithmic rainbow+white colourbar to indicate counts, with
    tA − tB on the horizontal axis and tC1 − tA on the vertical, for all DEs with valid A, B, and C1 hits,
    summed over all look directions separately by ESA and summed over all ESAs. Use 2 ns bins on both
    axes. (Use black to indicate histogram regions with zero counts.)
    • plot a two-dimensional histograms as previously but with tC2 − tC1 on the vertical axis, for all DEs
    with valid A, B, C1, and C2 hits, summed over all look directions and over all ESAs. Use 2 ns bins on
    the horizontal axis and 1 ns bins on the vertical axis. (Again, use black to indicate histogram regions
    with zero counts.)
    The TOF histogram bin sizes listed should be considered subject to change in the future. Further
    two-dimensional histogram plots may be requested in the future.
    """
