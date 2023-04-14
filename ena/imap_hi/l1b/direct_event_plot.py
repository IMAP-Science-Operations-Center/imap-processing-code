def direct_event_plot():
    """To generate direct event plot, we need to understand direct event data.

    From Section 2.1.1

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
        * Direct event has 4 coincidences that identify if event is from ENA - A, B, C1, C2
        * Only sends down qualified data with its informations.
        * Captures information about exact information when it saw something happened,
            exact TOF between detector A, B, C1 and C2.
            * Each event has this information:
                * Trigger Id (16-bits timetag): Time it happened in Millie seconds
                * Hit first (2-bits): Which detector trigger first
                    * Metadata event captures information about when we step up ESA voltage
                        step. Sweep value aka ESA step.
                * TOF 1 (10-bits of nominally 0.5ns)
                * TOF 2 (10-bits of nominally 0.5ns)
                * TOF 3 (10-bits of nominally 0.5ns)
        * TOF is used to do species identification. Eg. Hydrogen from helium
            It uses velocity and energy to calculate mass which is then used to do species identification.
        * It is a list of one value after another. Eg.
            * [
                [trigger id, hit first (meta event), ESA step, and exact time it happened],
                [trigger id, hit first, TOF1, TOF2, TOF3],
                [trigger id, hit first, TOF1, TOF2, TOF3],
                [trigger id, hit first, TOF1, TOF2, TOF3]
                .
                .
                [trigger id, hit first, TOF1, TOF2, TOF3]
            ]
        * Every four spin, we dump direct event data into a packet. There is two direct
        event packets per ESA step because 8 spins per ESA.

            * First direct event packet data will look like this
            with metaevent information.
                * [
                    [ metaevent, ESA step, and exact time it happened (stores high bits of MET time)],
                    [trigger id, hit first, TOF1, TOF2, TOF3],
                    [trigger id, hit first, TOF1, TOF2, TOF3],
                    [trigger id, hit first, TOF1, TOF2, TOF3],
                    ....
                ]
                Example:
                * [ [2-bits for metaevent, 4 bits for ESA step, 32-bits for integer MET, 10-bits for integer millisecond of MET]
                    [trigger_id, A, 403, 92, 261]
                    [trigger_id, B, 1023, 647, 604]
                    [trigger_id, A, 104, 1023, 1023]
                    [trigger_id, B, 1023, 18, 1023]
                    [trigger_id, A, 83, 1023, 1023]
                    [trigger_id, A, 100, 1023, 1023]
                    [trigger_id, C, 1023, 130, 1023]
                    [trigger_id, C, 1023, 1, 1023]
                    [trigger_id, A, 464, 1023, 1023]
                    [trigger_id, A, 81, 1023, 1023]
                    ...
                ]
            * Second direct event packet will not have metaevent information
                * [
                    [trigger id, hit first, TOF1, TOF2, TOF3],
                    [trigger id, hit first, TOF1, TOF2, TOF3],
                    [trigger id, hit first, TOF1, TOF2, TOF3],
                    ....]
                Example:
                * Example of what data may look like from Paul Janzen. Note from Paul:
                    There are no timetags -- but the DEs themselves in terms of
                    who hit first (A,B,C) and TOF1, TOF2, TOF3 in raw units
                    * [ [trigger_id, A, 403, 92, 261]
                        [trigger_id, B, 1023, 647, 604]
                        [trigger_id, A, 104, 1023, 1023]
                        [trigger_id, B, 1023, 18, 1023]
                        [trigger_id, A, 83, 1023, 1023]
                        [trigger_id, A, 100, 1023, 1023]
                        [trigger_id, C, 1023, 130, 1023]
                        [trigger_id, C, 1023, 1, 1023]
                        [trigger_id, A, 464, 1023, 1023]
                        [trigger_id, A, 81, 1023, 1023]
                        ...
                    ]
        * Every event Data is binned in 4 degree. And therefore every ESA step has 90 elements in array.
            90 * 4 == 360 degree
    """
