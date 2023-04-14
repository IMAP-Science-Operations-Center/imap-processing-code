def processed_housekeeping(raw_housekeeping_data):
    """Housekeeping packets will include MET of packet creation, commanded and monitored voltages of
    the inner ESA, outer ESA, inner deflector, outer deflector, U-Can, CEM Fronts, CEMs A & B Rears,
    MCP Front, and MCP Rear. Translation from engineering units for some high voltages may require
    additional status bits (e.g., HI or LO mode). Additionally, there will be current monitors on several
    of the HVPSs. Low-voltage power supplies will also have voltage and current monitors. There will be
    several temperature monitors and a CPU percent-idle monitor. The mode of the sensor (e.g., HVSCI)
    is also reported. Finally, an instrument-specific area may include periodic additional information, such
    as front-end electronics (FEE) settings and TOF qualification ranges.
    Housekeeping not mentioned in this list is not directly relevant to science data processing.
    Housekeeping is expected at a cadence of 30 s, subject to change. (From section 2.1.1)

    How to process housekeeping?
    Steps to:
        1. Translation from engineering units for some high voltages may require
            additional status bits (e.g., HI or LO mode).
        2. Housekeeping not mentioned in this list is not directly relevant to science data processing.
            Does this mean we should filter housekeeping information based on the list?
        3. How to convert to physical unit? And how do we know which ones need convertion or not?
    """
