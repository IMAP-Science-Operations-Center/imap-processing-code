

class decom_raw_housekeeping():
    """To product L1A raw housekeeping data product, we will use IMAP-Hi packet definition
    submitted on this link: https://lasp.colorado.edu/flares/browse/IMAPCATS-18.
    For IMAP-Hi 45 sensor:
        Packet Name: HI45_APP_NHK
        apIdHex: 2F2
        apId: 754
        maxLengthBits: 1184
        Description: Nominal Housekeeping

    For IMAP-Hi 90 sensor:
        Packet Name: HI90_APP_NHK
        apIdHex: TBD
        apId: TBD
        maxLengthBits: TBD
        Description: Nominal Housekeeping
    """
    
    # Steps:

    # 1. Write XTCE definition for IMAP-Hi 45 and 90 sensor head's Nominal Housekeeping packet
    # 2. For each sensor head, use lasp_packet to parse the CCSDS packet
    # 3. For each sensor head, write unpacked data to CDF file
