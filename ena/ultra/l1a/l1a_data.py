def l1a_data_products(l0_data, xcte_definition):
    """

    Level 0 data is decompressed and properly unpacked into separate CDF files by APID. This
    cumulative data set is referred to as Level 1A data. Level 1A consists of Direct Events which are
    the raw unpacked data from the Image Single Events Packets [1, p. 179-181; Table 54],
    Auxiliary Packet Data [1, p. 186-188; Table 59], Image Rates [1, p. 182; Table 55], and TOF
    Images. Algorithm relevant information is summarized in Table 1 and includes information
    from both Single Event packets and Auxiliary packets. Image Rates and TOF images will be
    used for diagnostic purposes such as estimating backgrounds, creating a “bad times” list, and for
    culling. Further details are described in [2] and [3].

    Inputs (From Processing Pipeline Diagram):
        1. Calibration Table 1 (From instrument team). 
            TODO: requests details of what is in this file and what parts we use at this
            step. For which data product, is this for?
        2. Timing, Attitude, Ephemerids (From MOC?)
            TODO: What specific data are we getting here and what information is used
            at this step. Or is information extracted here and stored to be used later?

    L1A data consist of (From algorithm document):
        Types of Packets:
            1. Science data packets - contains science data
            2. Event packets - raw unpacked data from the Image single Events
            3. Auxiliary Packet data
        Where are these two data coming from?
            4. Image Rates - Used for diagnostic data products.
            5. TOF Images - Used for dianostic data products.

    L1A data products (From Processing Pipeline Diagram):
        1. Housekeeping
            Inputs:
                Data packets
                XCTE definitions
            Outputs:
                unpacked housekeeping data

        2. Direct Event
            Inputs:
                Single event packets w/ XCTE definitions
                Auxiliary packets w/ XCTE definitions
            Outputs:
                Table 1 from algorithm documents
                Table 1 list Direct Event items needed for algorithms
                NOTE: This table is created using Single event packets and
                    Auxiliary packets. Do we only stored item listed in
                    Table 1? or Do we store all items from Single Event
                    packets and Auxiliary packets?
        3. Onboard Processed 2D Histograms
            NOTE: How do we make this data product in this step?
    Args:
        l0_data: raw data packets. How will data packet come?
        xcte_definition: definitios to unpack data
    """

    # Processing Algorithm:
    # TODO: get science data packet definition or any other packets defintions
    #       we will be getting
    #
    # TODO: get sample data that matches packet definitions
    # for each packet in data file:
        # unpack data using APID and its packet definition
        # store unpacked data in a CDF variable or array
    
    # NOTE:
    # How do we get packets from MOC? One day's worth of data in one zip file?
    # Does it contain many packets with different APID?
    
    return "cdf with data unpacked"