
def l1b_data_products():
    """
    Level 1B data uses the information from level 1A to begin the construction of Raw Events
    Tables and Annotated Events, as well as a Bad Times list.

    Inputs (From Processing Pipeline Diagram):
        1. Calibration Table 1 (From instrument team). 
            TODO: requests details of what is in this file and what parts we use at this
            step. For which data product, is this for?
        2. Timing, Attitude, Ephemerids (From MOC?)
            TODO: What specific data are we getting here and what information is used
            at this step. Or is information extracted here and stored to be used later?
    
    Data Products (From Processing Pipeline Diagram):
        1. Annotated Events
            Input:
                Raw Events Tables - Contains information about the detected events as
                    seen by Ultra. TODO: This is outcome from L1A, right?
                
                Pointing data from MOC? or IMAP attitude and Ephemeris.

            Description:
                The Annotated Events table is an extension of the Raw Events table with more geometric
                information from the events calculated using the IMAP attitude and ephemeris. This table will
                be carried through at various processing stages from Level 1B – Level 2 (with more information
                appended to it in other data levels). The Annotated Events table will initially include particle
                trajectory information (ENA velocity vectors) in various frames, spacecraft attitude information,
                species type, and energy estimates.

                Table 3 in the algorithm document describes the initial items that should be included in the
                Annotated Events.

                Events of particle trajectory in various:
                    * frames
                    * spacecraft attitude information
                    * species type
                    * energy estimates
                    TODO: Do we have all the data we need to calculate these various from using
                    input listed below?

            Output:
                Annotated events table. TODO Is that Table 3 from algorithm document?

        2. Badtimes List
            Input:

            Description:

            Output:

    """

    # Processing Algorithms:
    
    # 1. Event Time Calculatioin Algorithm
    """
    Inputs:
        1. Single event packets
            theta_event - Phase angle. Interger value from 0 - 719
        2. Auxiliary packets:
            t_spin_duration - Spin duration. The measured spin period in milliseconds
            t_spin_start - Spin start time in seconds
            t_start_sub - Spin Start subseconds. in milliseconds

    Formula to calculate event time:
        t_event = t_spin_start + (t_start_sub / 1000) + ((t_spin_duration/ 1000) * (theta_event / 720))
    
    This event time will later be used for grouping events into the appropriate pointing sets, can aid
    in the determination of spatiotemporal noise and the creation of a bad times list. Event time can
    also be used to determine which events belong to a given Pointing.
    """

    # 2. ENA Instrument Frame Trajectories, Energy, and Species Determination
    """
    Inputs:
        1. Direct events information. (TODO: is this in the Single event packets?)
        2. Calibration Table (Instruments will provide the table)
        3. Calibration lookup table. (TODO: is it same has Calibration Table?)
        4. Image Params
        5. Another lookup table was mentioned before calculating species determination.
            TODO What is that and where is it coming from?

    Description:
        Details in the algorithm document, section 1.2.3.2
        In the algorithm, it performs various pre calculations to construct inputs
        for three main calculations.
        1. Particle's Trajectories
            formula (2) and (3)
        2. Parlicles's Energy
            psuedocode between formula (6) and (7)
        3. Corrected TOF
            formula (7)
        4. Particle's species determination
            formula (8)

    Output:

    """

    # 3. Bad Times List
    """
    Input:
        Spin Table - The Spin Table is a proposed, projectmaintained
            data set which represents binary filters, on/off, switches that represent the nonnominal
            / nominal conditions that warrant a bad spin. Look at Table 4 from algorithm document
        
        image rate packets

    Description:
        the Bad Times list should mostly contain time periods when attitude
        information is poor, or when an unexpectedly high number of non-Triple / low confidence events
        occur.

        image rate packet is used to calculate Rates p_i and may be useful for background calculations.

        Bad times list is determined using these conditions:
            • Ultra in a state not suitable for ENA imaging (e.g., voltages not appropriate)
            • Ultra telemetry errors (e.g., checksum failures, bad packets)
            • Ultra event rates beyond threshold
            • Attitude system not suitable for Ultra processing (e.g., spin rates out of bounds,
            repointing in progress)
            • Excessive solar wind near Ultra’s FOV
            • Abundant Energetic ion / electron flux

    Output:

    """