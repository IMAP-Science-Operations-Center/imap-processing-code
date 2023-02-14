
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

            Input:
                Events data
                Pointing data from MOC? or IMAP attitude and Ephemeris.

        2. Badtimes List

    L1B data (From Algorithm Documents):
        1. Raw Events Table
            The Raw Events tables contain information about the detected events as seen by Ultra, before
            adding any spacecraft attitude or ephemeris information into the calculations. Table 2 provides
            an overview of the items in the Raw Events table and the following subsections describe the
            items further.

        2. Annotated Events
        3. Bad Times List
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

    Calculate ENA instrument frame:
        Inputs:

    """

    # 3. Bad Times List
    """
    
    """