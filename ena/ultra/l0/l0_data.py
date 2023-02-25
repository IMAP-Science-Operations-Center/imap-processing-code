def l0_decom_packet(xcte_definition, data_file):
    """
    At this stage, we are getting data packets from MOC or data source.
    It will be placed in SDC data bucket which will trigger rest of the data
    processing pipeline.
    Data Level: L0
        Data product: CCSDS Packets
        Input:
            Data packets.
            Types of data packets received by SDC:
                1. Science packet
                2. Events packets
        Description:
            Level 0 data products are packets downlinked from the spacecraft
            defined by the CCSDS space packet protocol standard
        Output:
            None
    """
