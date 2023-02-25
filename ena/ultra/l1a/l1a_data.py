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

    L1A data products (From Processing Pipeline Diagram):
        1. Housekeeping
            Inputs:
                Data packets
                XCTE definitions
            Outputs:
                unpacked housekeeping data (TODO: confirm it)

        2. Direct Event
            Inputs:
                Single event packets w/ XCTE definitions
                Auxiliary packets w/ XCTE definitions
                Image Rates
                TOF images
            Description:
                per algorithm document, Direct Events are
                the raw unpacked data from 
                    1. the Image Single Events Packets [1, p. 179-181; Table 54],
                    2. Auxiliary Packet Data [1, p. 186-188; Table 59],
                    3. Image Rates [1, p. 182; Table 55], and 
                    4. TOF Images.
                    TODO: Where are Image Rates and TOF images coming from?
             
            Outputs:
                Raw events Tables (TODO Is this Table 2 from algorithm document? or is
                it constructed using single event packets, auxiliary packets,
                and other packets?)
                
        3. Onboard Processed 2D Histograms
            TODO: How do we make this data product in this step? It's missing from
            the algorithm document.

            Inputs:

            Description:

            Output:

    Args:
        l0_data: raw data packets. How will data packet come?
        xcte_definition: definitios to unpack data
    """

    # TODO: request sample data that matches packet definitions
    # for each packet in data file:
        # unpack data using APID and its packet definition
        # store unpacked data in a CDF variable or array
    
    return "cdf with data unpacked"