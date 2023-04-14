

class decom_raw_direct_event():
    """To product L1A raw direct event data product, we will use IMAP-Hi packet definition
    submitted on this link: https://lasp.colorado.edu/flares/browse/IMAPCATS-18.
    For IMAP-Hi 45 sensor:
        Packet Name: HI45_SCI_DE
        apIdHex: 302
        apId: 770
        maxLengthBits: 32728
        Description: Science direct events

    For IMAP-Hi 90 sensor:
        Packet Name: HI90_SCI_DE
        apIdHex: TBD
        apId: TBD
        maxLengthBits: TBD
        Description: Science direct events
    """

    # Steps:

    # 1. Write XTCE definition for IMAP-Hi 45 and 90 sensor head's direct event packet
    # 2. For each sensor head, use lasp_packet to parse the CCSDS packet
    # 3. For each sensor head, write unpacked data to CDF file
