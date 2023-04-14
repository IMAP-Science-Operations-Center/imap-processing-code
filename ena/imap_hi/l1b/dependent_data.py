def spin_table():
    """
    Two files are mandatory: the spacecraft spin pulse list, and the true spin pulse list.

    Spacecraft spin pulse list: when does the spacecraft think phase 0 of each spin, during or near HVSCI,
    occurred? In other words, when exactly are all the “spin pulses”?

    Format of the spin pulse list file (TODO: does this format apply to true spin pulse list? or is it up to SDC?)

        %.4lf %d %d %.4lf

        * First field: precise MET at phase 0, as was determined by the spacecraft in real time. If
            a fifth decimal place is available and meaningful, it may be included. Note that if MET is
            represented using a double float, and if MET is actually based on GPS Epoch time, the fifth
            decimal is still fairly significant.

            When did phase 0 of each spin, during or near HVSCI, actually occur?
        * Second field: Pointing number
            At any given time, where was the sensor looking?
        * Third field: spin number of current Pointing. This field is expected to increase by one every
            line. At the very least, it must always be increasing, even if there are gaps.
        * Fourth field: spin period
    """


def convert_met_to_utc():
    """What’s the conversion between MET and UTC?
    Processing takes place (nearly) entirely by MET, but to determine 3-month and 6-month boundaries,
    eventually some times will need to be translated to UTC.
    """
