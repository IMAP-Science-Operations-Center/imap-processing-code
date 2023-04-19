def annotated_direct_events():
    """

    Dependent data from L1A:
        * direct event data
    Outside Data dependent:
        * Space craft spice kernel
        * HAEJ2000 latitude and longitude data
        * list of spin times (spin table from SDC. generated from spice kernel. saves time)

    Each event has this information:
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

    Look at Direct Event plot code for detail explanation of what is in direct
    event packet.

    With every direct events, we annotate it with additional information listed here:
        1. Convert timetag (16-bit value from above) into look direction in the sky.
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
        2. Convert timetag (16-bit value from above) into spin phase and spin angle. TODO: What is spin phase?
            The terms "spin angle" and "spin phase" are related to the rotation of an object and are often used
            interchangeably, but they refer to slightly different things.

            The spin angle is a measure of the rotation of an object around its axis, typically expressed in degrees or radians.
            It refers to the angle between a reference point on the object and a fixed reference direction, such as the direction
            of the sun or a particular star. The spin angle indicates how far the object has rotated from a specific point in time,
            and it can be used to predict the orientation of the object at future times.

            The spin phase, on the other hand, is a measure of the position of an object in its rotation cycle, typically expressed
            in degrees or radians. It refers to the fraction of the rotation cycle that has elapsed since a reference point in time,
            often expressed as a value between 0 and 1. For example, a spin phase of 0.25 would mean that the object has completed one
            quarter of its rotation cycle since the reference point in time. The spin phase is often used to synchronize observations of
            an object with its rotation cycle.

            So in summary, the spin angle describes the orientation of an object in space at a particular time, while the spin phase
            describes the position of the object in its rotation cycle relative to a reference point in time.

            To convert a spin angle into a spin phase, you need to know the period of the rotation cycle of the object,
            which is the time it takes for the object to complete one full rotation around its axis. Once you know the
            rotation period, you can use the following formula to convert a spin angle (in degrees) into a spin phase
            (as a fraction of the rotation cycle):

                Spin Phase(0-1) = Spin Angle(0-360) / 360 degrees
                check for casae if spin phase goes over 1.

            For example, let's say you have an object that rotates with a period of 10 hours, and you observe it at a
            spin angle of 180 degrees. To convert this spin angle into a spin phase, you would use the formula:

                Spin Phase = 180 degrees / 360 degrees = 0.5

            So the object is at a spin phase of 0.5, meaning it has completed half of its rotation cycle since the
            reference point in time.

            Note that if the spin angle is in radians rather than degrees, you should convert it to degrees first by
            multiplying it by 180/π, where π is the mathematical constant pi (approximately equal to 3.14159).

            spin phase (0.0 - 1.0), both according to spacecraft and true (“despun”), as described in Section 2.2.3.
            If you wanted, you could obtain the nominal related histogram bin by multiplying the spin phase by
            90 and truncating to integer. Depending on how the C&DH aligns things you may need to shift the
            spin phase by the clocking angle of the sensor.
        3. Add information about coincidence events, whether it is single, double, triple or quad coincidence.
            Coincidence type: a 4-bit quantity, representable as a hexadecimal digit, made up of the ORed quan-
            tities
            (A hit? 8:0) | (B hit? 4:0) | (C1 hit? 2:0) | (C2 hit? 1 : 0)

            Above means we are storing coincidence type in 4-bits quantity. If A was hit, then 4-bits would
            look like this 0b1000. If B was hit, then 4-bits would look like this 0b0100. If C1 was hit,
            then 4-bits would look like this 0b0010. If C2 was hit, then 4-bits would look like this 0b0001.

            Obtaining the hits from a DE is described previously, but to reiterate: look at the 4-bit triggering-hit
            field. This lets you know if A, B, or C1 was the start of the event. If the first event was [A,B,C1],
            respectively, then [B,A,A] was also hit if the first TOF is not 1023, [C1,C1,B] was also hit if the second
            TOF is not 1023, and C2 was hit if C1 was hit and the third TOF field is not 1023.

            To rephrase above paragraph, if any of TOF is 1023, then it means event didn't happen between two detectors.
            But if any of TOF is not 1023, then it means event happened between two detectors. Knowing this information,
            let's find out if conincidence happened between detectors. Lets create senarios.
                If detector A was hit first:
                    If TOF 1 is not 1023:
                        Then detector B was hit
                    If TOF 2 is not 1023:
                        Then detector C1 was hit
                    If TOF 3 is not 1023:
                        Then detector C2 was hit
                If detector B was hit first:
                    If TOF 1 is not 1023:
                        Then detector A was hit
                    If TOF 2 is not 1023:
                        Then detector C1 was hit
                    If TOF 3 is not 1023:
                        Then detector C2 was hit
                If detector C1 was hit first:
                    If TOF 1 is not 1023:
                        Then detector A was hit
                    If TOF 2 is not 1023:
                        Then detector B was hit
                    If TOF 3 is not 1023:
                        Then detector C2 was hit
            Using this information, we can construct coincidence information. If detector AB was hit, then 4-bit quantity
            will look like this 0b1100. If detector AC1 was hit, then 4-bit quantity will look like this 0b1010. If detector BC1 was
            hit, then 4-bit quantity will look like this 0b0110. If detector ABC1 was hit, then 4-bit quantity will look
            like this 0b1110. If all detector was hit, then 4-bit quantity will look like this 0b1111

            This is not how the DE is transmitted, but it is more useful for ground analysis.

        4. Add information about ESA step information. This is copied from the most recently preceding metaevent.
        5. is_good: 0 or 1
            This will get modified by the good times selection work that’ll happen later, but we might as well
            populate the field a bit now, even though we’re going to do the exact same thing again later with a
            better list.

            For the MET of a DE, figure out which histogram packet it belongs to (likely, the one following, unless
            there was a dropped histogram packet, in which case the DEs are not correlated to histograms and
            thus are definitely in a “bad time”). Convert the DE’s spin phase to a nominal bin, and report the
            value in the appropriate 90-entry array.
        6. Annotate TOFs. ta_b1 - tb_b1. (Page 23)
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
