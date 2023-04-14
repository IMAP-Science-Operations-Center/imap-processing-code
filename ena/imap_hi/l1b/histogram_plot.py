def histogram_plot():
    """To generate histogram plot, we need to first understand histogram data.

    Histogram packets (SCI CNT) will include MET of packet creation, ESA stepping number, and
    arrays of 90 12-bit counters:
        – 8 12-bit qualified counters (AB, C1C2, AC1, BC1, ABC1, AC1C2, BC1C2, ABC1C2)
        – 11 12-bit long counters (A, B, C, AB, C1C2, AC1, BC1, ABC1, AC1C2, BC1C2, ABC1C2)
        – 5 12-bit diagnostic counters (totalA, totalB, totalC, FEE DE SENT, FEE DE RECD)

    TODO: What does this counter mean? Is this all types of coincidence types we can have?

    Histogram data is expected on an 8-spin cadence (nominally every two minutes) during HVSCI mode,
    aligned with the stepping of the ESA.
    At present, we are not planning to use a compression scheme on the histogram counters. However,
    if one becomes implemented, this is the step at which uncompression should occur. Any compression
    scheme under consideration would not affect values smaller than 100, and then perform square-root
    compression for larger values.

    Notes from Discussion:
    Every two minutes, we capture data of one ESA step:
    * Every ESA steps ( We have 9 ESA steps)
        * One histogram data packets gets send down
        * For every coincidence types:
            * Coincidence A has 90s element array, AB has 90 elements array and so on.  In other words,
                every coincidence types combination will have 90s element array.
            * It has 90 element array. (90 4 degree bin)
                * It’s integer and it represents counts
                * Each element in the array represents 4 degree bin. 360 degree angle divided by 4 degree
                    gives us 90 bins. And we have counts of every ENA event in their respective bins.

    Every histogram packet tells us which ESA step we were at.

    To create map using a day’s worth of histogram data,
    * sum all the array by angle. This would give us array of counts

    * This data is the idea of spacecraft of what was where. If data is within certain range of TOF,
        then we say it’s a valid event and save it. But it doesn’t keep information about TOFs.
        This can’t be used to identify species.
    * Captures all event data wether it's qualified or not

    """
