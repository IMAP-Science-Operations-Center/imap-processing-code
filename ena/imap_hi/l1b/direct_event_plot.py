def direct_event_plot():
    """To generate direct event plot, we need to understand direct event data.

    From Document:

    Direct event data (SCI DE) includes MET of packet creation, and some number of coincidence
    events. Each event contains a 16-bit timetag, 2 bits to identify the triggering (initial) hit, and three
    10-bit time-of-flight fields, whose meaning depends on the triggering hit. The units of the 10-bit TOF
    fields are increments of nominally 0.5 ns: the specific increment value will be in the Instrument Status
    Summary.

    Table of DE event information:
    trigger ID |hit first | TOF 1   | TOF 2     | TOF 3
    0          | A        | tB − tA | tC1 − tA  | tC2 − tC1
    1          | B        | tA − tB | tC1 − tB  | tC2 − tC1
    2          | C        | tA − tC1| tB − tC1  | tC2 − tC1
    3          |metaevent | ESA & Time information

    In above table, it maps trigger ID to hit first value. Eg. If we get trigger ID 0 in DE, it means detector A
    was triggered first and so on. Based on who hit first, TOF 1, 2 and 3 correspond to time between detector that
    hit first and other detector. Eg. If dectector A was hit first, then TOF 1 value is the time it took between
    detector A and B, TOF 2 value is the time it took between detector A and C1, and TOF 3 value is the time it
    took between detector A and C2. If the event didn't happen, then the TOF value would default to 1023
    (which is the value of 2^10 -1. This is when TOF's 10-bits is set to all 1s).

    In addition, there is a special case for metaevent:
    If the event is a metaevent, the TOF 1, 2 and 3 fields are filled with ESA step and exact time of the
    step.

    If a hit is not registered, the appropriate field in the DE is set to −1 (i.e., 0x3FF for a 10-bit unsigned
    counter). For a coincidence event, clearly at least one field must not be −1.
    The 16-bit timetag for each direct event is in defined “ticks” (nominally 2 ms) from the time the ESA
    was commanded to step to its current value. It is reset to zero each time the ESA steps.
    To clearly locate in time exactly when the ESA stepped, a “metaevent” is generated containing the
    exact time of the step. 4 bits are reserved to store the ESA stepping number, leaving 42 bits with
    which to note the time. 32 bits are the integer MET, and 10 bits are the integer millisecond of MET.
    The expectation is that if a packet contains a metaevent, it will contain only one, and the metaevent
    will be the first entry in the list of events.
    Under normal operation, direct event recording is throttled not to exceed an average of 10 per second.
    We expect DE packets every 4 spins, aligned with the 8-spin histogram cadence.

    Notes from Discussion:
    Direct Event Data Packet:
        * Direct event recording if event is from ENA using detetor A, B, C1, C2.
        * Only sends down qualified data with its informations.
        * Captures information about exact information when it saw something happened,
            exact TOF between detector A, B, C1 and C2.
            * Each event has this information:
                * Based on which detector trigger first or if it's a metaevent
                    If metaevent:
                        * 48 bits are broken down into this:
                            metaevent(2-bits),
                            ESA step(4-bits),
                            exact time it happened (42-bits). It stores high bits of MET time
                        * Metadata event captures information about when we step up ESA voltage
                            step. Sweep value aka ESA step.
                    else:
                        * 48 bits are broken down into this:
                            * Hit first (2-bits) (Also known as Trigger Id): Which detector trigger first
                            * TOF 1 (10-bits of nominally 0.5ns)
                            * TOF 2 (10-bits of nominally 0.5ns)
                            * TOF 3 (10-bits of nominally 0.5ns)
                            * time ticks(16-bits timetag): Time in ticks. one ticks (2ms or look up from instrument status summary)
        * TOF is used to do species identification. Eg. Hydrogen from helium
            It uses velocity and energy to calculate mass which is then used to do species identification.
        * It is a list of one value after another. Eg.
            * [
                [meta event, ESA step, and exact time it happened],
                [hit first, TOF1, TOF2, TOF3, time_ticks],
                [hit first, TOF1, TOF2, TOF3, time_ticks],
                [hit first, TOF1, TOF2, TOF3, time_ticks]
                .
                .
                [hit first, TOF1, TOF2, TOF3, time_ticks]
            ]
        * Every four spin, we dump direct event data into a packet. There is two direct
        event packets per ESA step because it does 8 spins per ESA.

            * First direct event packet data will look like this
            with metaevent information.
                * [
                    [metaevent(2-bits), ESA step(4-bits), and exact time it happened (42-bits, stores high bits of MET time)],
                    [time_ticks(16-bits), hit first(2-bits), TOF1(10-bits), TOF2(10-bits), TOF3(10-bits), time_ticks],
                    [time_ticks(16-bits), hit first(2-bits), TOF1(10-bits), TOF2(10-bits), TOF3(10-bits), time_ticks],
                    [time_ticks(16-bits), hit first(2-bits), TOF1(10-bits), TOF2(10-bits), TOF3(10-bits), time_ticks],
                    [time_ticks(16-bits), hit first(2-bits), TOF1(10-bits), TOF2(10-bits), TOF3(10-bits), time_ticks],
                    [time_ticks(16-bits), hit first(2-bits), TOF1(10-bits), TOF2(10-bits), TOF3(10-bits), time_ticks],
                    [time_ticks(16-bits), hit first(2-bits), TOF1(10-bits), TOF2(10-bits), TOF3(10-bits), time_ticks],
                    ....
                ]
                Example: TODO: how is 48 bits distributed for the first metaevent.
                * [ [metaevent(2-bits), ESA step(4-bits), and exact time it happened (42-bits, stores high bits of MET time)],
                    [A, 403, 92, 261, time_ticks] (48-bits)
                    [B, 1023, 647, 604, time_ticks]
                    [A, 104, 1023, 1023, time_ticks]
                    [B, 1023, 18, 1023, time_ticks]
                    [A, 83, 1023, 1023, time_ticks]
                    [A, 100, 1023, 1023, time_ticks]
                    [C, 1023, 130, 1023, time_ticks]
                    [C, 1023, 1, 1023, time_ticks]
                    [A, 464, 1023, 1023, time_ticks]
                    [A, 81, 1023, 1023, time_ticks]
                    ...
                ]
            * Second direct event packet will not have metaevent information
                * [
                    [hit first, TOF1, TOF2, TOF3, time_ticks],
                    [hit first, TOF1, TOF2, TOF3, time_ticks],
                    [hit first, TOF1, TOF2, TOF3, time_ticks],
                    ....]
                Example:
                * Example of what data may look like from Paul Janzen. Note from Paul:
                    There are no timetags -- but the DEs themselves in terms of
                    who hit first (A,B,C) and TOF1, TOF2, TOF3 in raw units
                    * [ [A, 403, 92, 261, time_ticks]
                        [B, 1023, 647, 604, time_ticks]
                        [A, 104, 1023, 1023, time_ticks]
                        [B, 1023, 18, 1023, time_ticks]
                        [A, 83, 1023, 1023, time_ticks]
                        [A, 100, 1023, 1023, time_ticks]
                        [C, 1023, 130, 1023, time_ticks]
                        [C, 1023, 1, 1023, time_ticks]
                        [A, 464, 1023, 1023, time_ticks]
                        [A, 81, 1023, 1023, time_ticks]
                        ...
                    ]
        * Every event Data is binned in 4 degree. And therefore every ESA step has 90 elements in array.
            90 * 4 == 360 degree

    Steps to produce Direct Event plots:

    Requirement:
        Time on horizontal axis and spin phase on the vertical, the counts observed in each 4 degree spin bin.
        And use a rainbow + white linear autoscaled colourbar. These plots should be stacked with the first ESA in
        the stepping sequence(nominally ESA 1) at the top and the final ESA (nominally ESA 9 ) at the bottom. The
        ordering is by entry in the stepping sequence table (not by the voltages actually on the electrostatic analyzer).
        The spin phase at the top of each plot should correspond to the 4 degree bin at which Hi45 and Hi90 were looking
        closest to NEP(HAE z^hat). More details in the document.

        We can use histogram packet creation time for horizontal axis. Note that there is different packet creation time for
        each ESA step data. To determine which time to use on horizontal axis, we use the earlist time value of all
        ESA data. This is what was done in the past mission.

        Units of plot is suggested to keep in count. It can be plot in rates if there is requests. This will mean counts
        will be converted to rates using this formula: counts/exposure_time.

        Plots will be done inpendently for Hi45 and Hi90.

    Pre-process to generate data for plot:
        * Use annotated direct events data because it has information about
            1. ESA step
            2. Spin phase
            3. Time of DE
        * Make use of Histogram data to step through DE data and group together because if the telemetry scheme is as expected,
            there should be one or two direct events packets covering exactly the same time as one histogram packet.
        * Group DE per pointing, per sensor. In other word, bin direct event data.
            – When you get to a SCI HIST packet, look at the MET. This time will be shortly after the end of
                the data contained in the packet.3 Also, note the ESA stepping number. Initialize an array of 90
                integers to zero.
            – Step through the SCI DE packets, either from the start of the Pointing or from how far you’ve
                gotten so far, looking for a metaevent with the same ESA stepping number.
            – For every direct event following this metaevent, up until the next metaevent or an event time
                after one second past the SCI HIST MET, determine if the event type is one which you wish to
                histogram. If so, determine the phase angle of the direct event.
                To determine the type of event:
                * if it’s sent as a direct event, it counts as “qualified” as per the sensor qualification scheme.
                * look at the 4-bit triggering-hit field. This lets you know if A, B, or C1 was part of the event.
                * If the first event was [A,B,C1], respectively, then [B,A,A] was also hit if the first TOF is not
                1023, [C1,C1,B] was also hit if the second TOF is not 1023, and C2 was hit if C1 was hit and
                the third TOF field is not 1023.
                To determine the spin phase of the event:
                * Determine the absolute time tDE of the direct event by adding the time of the preceding
                metaevent to the “tick interval” multiplied by the timetag value. Then, add half a tick: on
                average, an event with a time tag of n occurred halfway between n and n + 1.
                * Determine the phase 0 spin times before (tb) and after (ta) the tDE calculated. If you want
                a direct comparison with the histograms, use the spacecraft spin pulse list; if you want a
                comparison with where things ought to be use the true spin pulse list. For this set of plots
                only, use the spacecraft spin pulse list.
                *  phase = tDE − tb / ta − tb
                You may or may not be paranoid enough to make sure this is greater than or equal to zero
                and less than one.
            – Depending on how the C&DH defines spin phase, expect to adjust the spin phase by the clocking
                angle of the sensor.
            – Add one to the integer in the array corresponding to (int)(phase × 360◦/4◦).
            – Once you’ve stepped through all the direct events related to this histogram packet, plot the array
                of histogrammed direct events, which will resemble, in form, the contents from the histogram
                packet. In Section 2.2.2, you would have simply plotted the (sum of various) histograms from the
                histogram packet.
            – Continue on through the Pointing.

            The result here is one plot per sensor per ESA per calibration product4 from binned DEs.
        * Calculate exposure time if plot will be in rate. For this plot, we can use this formula to calculate exposure time.
            (8 spins at 15s/spin, or whatever the average spin value ends up being for
            the Pointing, divided into 90 angle bins is 1.33s per bin; the slight change in exposure time from bin to bin
            over the Pointing is ignorably small for the purposes of this diagnostic plot)
    Once we have binned direct event data, we can plot it.
    """
