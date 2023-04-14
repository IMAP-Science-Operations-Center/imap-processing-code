def annotated_direct_events():
    """

    Dependent data from L1A:
        * direct event data
    Outside Data dependent:
        * Space craft spice kernel
        * HAEJ2000 latitude and longitude data

    Each event has this information:
        * Trigger Id (16-bits timetag): Time it happened in Millie seconds
        * Hit first (2-bits): Which detector trigger first
            * Metadata event captures information about when we step up ESA voltage
                step. Sweep value aka ESA step.
        * TOF 1 (10-bits of nominally 0.5ns)
        * TOF 2 (10-bits of nominally 0.5ns)
        * TOF 3 (10-bits of nominally 0.5ns)

    Look at Direct Event plot code for detail explanation of what is in direct
    event packet.

    With every direct events, we annotate it with additional information listed here:
        1. Convert spin angle into look direction in the sky.
            A few notes on writing the function that will take a MET and return the Hi90 or Hi45 look direction:
                – If nutations are insignificant, then average spin axis and instantaneous phase (determined by
                comparing direct event timetags to the list of phase-0 times) are entirely sufficient to determine
                look direction.

                In simpler terms, When we want to figure out where to point a telescope to observe a specific object
                in space, we need to know the direction in which the telescope should be pointed. There are two main
                things we need to consider:

                    The average spin axis: This refers to the direction in which the Earth is rotating.
                        We can use this information to figure out where the object will be at a certain time.

                    The instantaneous phase: This refers to the position of the object relative to the spin axis at a
                        specific moment in time. We can use this information to determine the exact direction in which
                        the telescope should be pointed to observe the object.

                Sometimes there are small movements in the Earth's rotation, called nutations, that can affect our
                calculations. However, if these movements are not significant, we can ignore them and rely solely on
                the average spin axis and instantaneous phase to determine the look direction for the telescope.
                – If the mission decides to use GPS Epoch time as MET, the mission will start some time around
                1.4e9 seconds, at which point the resolution of a double variable (about 10 μs) is starting to get
                close to the precision of a timetag tick (2 ms). It might be worth considering long doubles, except
                CDF really doesn’t support that (and CDF EPOCH16 is overkill).
                – There has been discussion that this function may also be able to return some sort of indication
                of confidence or uncertainty in the look direction (perhaps from the star tracker’s Kalman filter).
                If so, it would be information useful in the determination of Bad Times as discussed later in this
                document.

            look direction: HAEJ2000 latitude and longitude
            Take the MET, add half a tick, and call whatever routine exists on the spacecraft/SPICE side to find
            out what the look direction of IMAP-Hi was then.
            If for some reason the function can’t provide a legitimate answer, and has a way of letting us know,
            mark the relevant spin angle range (likely all angles) for this time as bad in the 90-element array.
        2. Convert spin angle into spin phase. TODO: What is spin phase?
            spin phase (0.0 - 1.0), both according to spacecraft and true (“despun”), as described in Section 2.2.3.
            If you wanted, you could obtain the nominal related histogram bin by multiplying the spin phase by
            90 and truncating to integer. Depending on how the C&DH aligns things you may need to shift the
            spin phase by the clocking angle of the sensor.
        2. Add information about coincidence events, whether it is single, double, triple or quad coincidence.
            Coincidence type: a 4-bit quantity, representable as a hexadecimal digit, made up of the ORed quan-
            tities
            (A hit? 8:0) | (B hit? 4:0) | (C1 hit? 2:0) | (C2 hit? 1 : 0)
            Obtaining the hits from a DE is described previously, but to reiterate: look at the 4-bit triggering-hit
            field. This lets you know if A, B, or C1 was the start of the event. If the first event was [A,B,C1],
            respectively, then [B,A,A] was also hit if the first TOF is not 1023, [C1,C1,B] was also hit if the second
            TOF is not 1023, and C2 was hit if C1 was hit and the third TOF field is not 1023.
            This is not how the DE is transmitted, but it is more useful for ground analysis.
        3. Add information about ESA step information. This is copied from the most recently preceding metaevent.
        4. is_good: 0 or 1
            This will get modified by the good times selection work that’ll happen later, but we might as well
            populate the field a bit now, even though we’re going to do the exact same thing again later with a
            better list.

            For the MET of a DE, figure out which histogram packet it belongs to (likely, the one following, unless
            there was a dropped histogram packet, in which case the DEs are not correlated to histograms and
            thus are definitely in a “bad time”). Convert the DE’s spin phase to a nominal bin, and report the
            value in the appropriate 90-entry array.
    Annotate every direct event recorded in the Pointing’s telemetry. The point here is to generate a list
    quickly that can be piped into other processes. Actually saving the output to disk is possibly beside the
    point, as long as people can get to it. I suppose saving it to a compressed CDF isn’t too wasteful.
    Note that this step annotates all direct events, not just the “good” ones.

    Final annotated direct event will look like this:
        * MET in seconds reported to 4 decimal places: when it happened
        * Coincidence type
        * Hit First
        * TOF 1
        * TOF 2
        * TOF 3
        * ESA step number
        * Spin phase
        * look direction
        * is_good: 0 or 1

    """
