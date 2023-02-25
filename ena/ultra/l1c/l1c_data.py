
def l1c_data_products():
    """
    The IMAP pointing set definition will consist of a frozen IMAP Spin vector, 𝑍 _ and North Polar
    Ecliptic vector, 𝑁 a . Ideally these vectors will be supplied for each repointing interval and will
    define the basis for a common grid in which multiple particle instruments aboard IMAP will use.
    For the duration of valid Pointing Grid(s), SDC will generate IMAP-Ultra Pointing Set: Counts,
    Exposure Times, Background Rates, Sensitivity Factors, Corrected Counts, Ground Processed
    2D Histograms, and Culled Events lists or maps. These L1C products are typically produced on a
    daily basis.

    Inputs (From Processing Pipeline Diagram):
        1. Estimated Background (From instrument team)
        2. Pointing set definition (TODO where? spice kernel?)
        3. Inputs from IMAP and other sources for association with
            inner heliosphere events.(TODO this is still to be determined, right?)
    
    Data Products (From Processing Pipeline Diagram):
        1. Culled Events
            Input:
                Badtimes list

                Other instrument data

                Spin Table (?)

                Images Rate              

            Description:
                Culling is a process of segragating species froma  group according to desired
                or undesired characteristic.

                Culled events are registered, valid events that should not be included in the Pointing Set Counts.
                Direct Events are to be culled when any of the following situations occur:
                    1) Events fall within the Bad Times List
                    2) High background count rates determined by other instrument data
                    3) Foreground obstruction / foreign ENA source has been determined to be present in
                    Ultra’s FOV (ex: Earth / Moon / Magnetosphere in Ultra-45 FOV)
                    4) Solar Energetic Particle event or rapid increase in counts is detected

                Culled Events:
                1. Spin culling
                    For Ultra the process of spin culling consists of determining which spins should be included in
                    the pointing sets.

                    spin culling mask is used here
                2. Spatial culling
                    spin culling mask is used for short duration contamination.
                    spatial mask is used for long duration contamination.
                
                The spatial contamination will be identified by either the Low Res. Rate Images assembled from
                the TOF images accumulated on board OR level 2 data from other IMAP instruments. Each
                contaminated bin, 𝛽Δ, will be accumulated in a table where the spins that are contaminated for
                that bin are listed. Events that fall into 𝛽Δ during these spins will be subsequently removed from
                processing and the exposure time corrected accordingly.
            
            Output:
                culled events list or
                corrected data for subsequence data processing?
                (TODO: what is the output?)


        2. Pointing Set Counts
            Input:
                Annotated Events
                Pointing set definition
                Pointing Grid definition (TODO same as pointing set definition?)

            Description:

                key terms:
                    DPS(Despun Pointing Set) frame
                    Pointing grid

                Bin ENA counts to the Pointing grid. There will be two sets of grids,
                one for items with respect to the spacecraft rest frame Δ and
                another with respect to the heliosphere rest frame D.

                The pointing set counts grid will be 4 dimension where 3rd demension representing
                valid energy range for the given count and 4th dimension representing
                the species type (H, O). TODO what does i, j grid represent? DPS grid?
                


            Output:

        2. Pointing Set Counts (aka  Bin ENA counts to the Pointing grid)
            Input:

            Description:

            Output:
        
        2. Pointing Set Counts (aka  Bin ENA counts to the Pointing grid)
            Input:

            Description:

            Output:

        2. Pointing Set Counts (aka  Bin ENA counts to the Pointing grid)
            Input:

            Description:

            Output:

        2. Pointing Set Counts (aka  Bin ENA counts to the Pointing grid)
            Input:

            Description:

            Output:

    """
