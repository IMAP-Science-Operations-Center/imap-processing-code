def imap_hi_bad_times():
    """
    Dependend data from L1A:
        * Direct event
        * histogram
        * housekeeping

    Dependent data from L1B:
        * Annotated Direct Event
        * Processed housekeeping


    What follows
    here is necessary to establish the Bad Times list. These checks are more complex than the basic plots that
    the housekeeping team is capable of: in particular, they require mode-based limits checking, correlation of
    housekeeping in time-wise relation to science data, and “housekeeping” checks on direct events in relation
    to histogrammed data.

    Step through the SCI DE packets, the histogram packets, and the housekeeping packets for each sensor
    head, in timewise order.
        • Store, in arrays, the times of creation of each histogram packet, along with the ESA stepping number
            (histogram packets are created at the end of each ESA step). Also, for each histogram packet creation
            time, initialize one array of 90 integers (or bits), all to 1. This is the start of the “good times”.
        • From the meta-events in the SCI DE packets and/or from the “spare field meta-DE” space, determine
            exactly when the sensor changed the ESA step. Store these times and ESA steps in arrays as well.
        • If you find histogram packets without corresponding DE packets, or vice versa, log a warning. There
            needs to be histogram data for an interval to be a “good time”, but there doesn’t absolutely need to
            be DE data, because of how we calculate DE exposure time (Section 2.3.5). Even so, consider it a
            bad time if the packets didn’t both come down. So, if there are no (or insufficient) corresponding DE
            packets for a histogram packet, change all 90 entries in the array for that histogram’s MET to 0.
        • IMAP-Hi may possibly run in HVSCI mode through repoints. Data taken during a repoint is not good
            because the look direction has changed. Examine the METs of the first SCI HIST packets, subtract
            8 times the average spin period for the Pointing, and, for any resulting MET that is less than 240
            seconds after the start of the Pointing, set all 90 entries in the array for that histogram’s MET to 0.
            Similarly, zero out the array for any SCI HIST packet created within 240 seconds of the end of the
            Pointing.
        • Confirm from the histogram packets, using the MET of packet creation and the ESA stepping field,
            that the histogram and DE packets agree as to the value of this ESA step. If they do not, log a warning
            and set all 90 entries in the array for that histogram’s MET to 0.
        • From the housekeeping telemetry in the time range of each ESA step, read the measured voltages for
            CEM front, CEM A rear, CEM B rear, MCP front, MCP rear, U-Can, positive deflector, and negative
            deflector. Confirm that each is within the expected range for HVSCI (these tolerances will be supplied
            following calibration). These will be considerably tighter ranges than the red and yellow limits that
            housekeeping is nominally checked against, for they apply solely to successful science operation and,
            for example, would not allow zero volts on the U-Can, which is otherwise perfectly acceptable during
            LVENG, for example. If any of these voltages are outside the allowed range, log a warning and set all
            90 entries in the array for the relevant histogram’s MET to 0. [Note: during gain tests, there will be
            numerous “errors” generated here. This is as it should be: gain test intervals during HVSCI should
            not be part of the standard science “good times”!]

            From the housekeeping telemetry reported during the time range of each ESA step,
                – increment a counter of housekeeping packets seen during HVSCI for this Pointing.
                – read the Inner and Outer ESA voltages. By comparison to a lookup table for ESA steps that will
                be supplied after calibration, determine if the voltages are within i and o (to be supplied after
                calibration) of one of the settings.
                    * If the settings match any of the Background Test ranges, accept them and move on.
                    * If the settings match the ESA step reported by the histogram and DE packets, move on.
                    * If the settings match an ESA step but not the ESA step reported by the histogram and DE
                    packets, log a warning and remember this time.
                    * If the settings do not match an ESA step but are within the expected range of voltages,
                    increment a counter of “missed ESA steps”. These typically happen during flyback.
                    * Otherwise, log a warning and note the time.
                Note that if a fully valid Instrument Status Summary has been constructed already, some of this
                testing may become simpler, and fewer log messages may ensue.
        • log, at a warning level, the percentage of times that the ESA was not found to be at a valid setting
        during HVSCI, using the counters from the previous step. This is a useful value to trend over the
        mission.
        • check to see that each ESA stepping interval contains eight spins. How:
            – Find the meta-event from the SCI DE packets for this ESA step (it’s in an array created already).
            – Take the time difference between this meta-event and the MET creation time of the histogram
            packet.
            – Divide this difference by the average spin period this Pointing (excluding, as usual, the first few
            and last few spins).
            – Add 0.25 and truncate to integer.
            – This should be 8. If it’s greater than 8, log a warning (probably, it’s due to an interval out of
            HVSCI). If it’s less than 8, set all 90 entries in the array corresponding to this histogram packet’s
            MET to zero.
        • if some foreground object hoves into view that we wish to exclude, such as, I don’t know, a comet, and
            we have a SPICE kernel for it, I guess we could mask out any of the 90 angle bins that end up seeing
            it. I probably wouldn’t code that up just now, though.
    Anything that’s not zero at this point is not a “bad time”. But we’re not done yet. The bad times list
    isn’t finished until after the Annotated Direct Events are created, because annotating direct events might
    find more issues.

    towards_bad_times_list = [
        {
            "packet_creation_time(get it from histogram packet.)": [1, 1, 1, ...., 1] (90 element),
            "ESA step x": "time of when the sensor changed the ESA step (from meta-event in DE packet)",
            "Warning Message": ""
        }
        ,
        ....
    ]

    bad_times_list = filter out towards_bad_times_list by going through annotated direct event.
    """
