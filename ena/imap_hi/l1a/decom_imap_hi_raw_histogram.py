

class decom_raw_histogram():
    """To product L1A raw histogram data product, we will use IMAP-Hi packet definition
    submitted on this link: https://lasp.colorado.edu/flares/browse/IMAPCATS-18.
    For IMAP-Hi 45 sensor:
        Packet Name: HI45_SCI_CNT
        apIdHex: 301
        apId: 769
        maxLengthBits: 832
        Description: Science count

    For IMAP-Hi 90 sensor:
        Packet Name: HI90_SCI_CNT
        apIdHex: TBD
        apId: TBD
        maxLengthBits: TBD
        Description: Science count
    """

    # Steps:

    # 1. Write XTCE definition for IMAP-Hi 45 and 90 sensor head's histogram (AKA Science count) packet
    # 2. For each sensor head, use lasp_packet to parse the CCSDS packet
    # 3. For each sensor head, write unpacked data to CDF file
    # 4. Add paddings to the CDF file to make the file size a multiple of 8 bytes.
    #    Eg. Hit first value is 2-bit but when we store it in CDF file, it will be stored
    #    in 8 or 16 or 32 or 64 bits.
