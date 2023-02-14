def l0_decom_packet(xcte_definition, data_file):
    """Level 0 data products are packets downlinked from the spacecraft defined by the CCSDS space
    packet protocol standard.

    Level 0 data is decompressed and properly unpacked into separate CDF files by APID.

    NOTE: At this stage, SDC won't be doing anything besides gather packet defintion.
    SDC writes xcte_defintion in l1a process.

    TODO:
        gather list of packet types and definitions (Decommutation table)
    Types of APID:
        Science APID:
        Event APID: 
    """
