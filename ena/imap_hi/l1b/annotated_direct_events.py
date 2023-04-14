def annotated_direct_events(direct_events):
    """
    Each event has this information:
        * Trigger Id (16-bits timetag): Time it happened in Millie seconds
        * Hit first (2-bits): Which detector trigger first
            * Metadata event captures information about when we step up ESA voltage
                step. Sweep value aka ESA step.
        * TOF 1 (10-bits of nominally 0.5ns)
        * TOF 2 (10-bits of nominally 0.5ns)
        * TOF 3 (10-bits of nominally 0.5ns)
    Look at Direct Event plot for detail explanation of what is in direct
    event packet.

    With every direct events, we annotate it with additional information listed here:
        1. Convert spin angle into look direction in the sky.
        2. Convert spin angle into spin phase
        2. Add information about coincidence events, whether it is single, double, triple or quad coincidence.
        3. Add information about ESA step information

    Parameters
    ----------
    direct_events : _type_
        _description_
    """
