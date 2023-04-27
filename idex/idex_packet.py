#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A Python object to store IDEX packets.
__author__      = Ethan Ayari & Gavin Medley, 
Institute for Modeling Plasmas, Atmospheres and Cosmic Dust

Works with Python 3.8.10

TODO:
    * Continue conversations with SPDF about CDF file structure
        * TT2000 is placeholder for now
        * Some of the attributes are incorrect
        * We may get rid of DEPEND_1 altogether and simply use a single DEPEND_0
    * Add checks for array sizes and/or missing data
    * Change name of the output files
"""

import bitstring
import h5py
import matplotlib.pyplot as plt
plt.style.use("seaborn-poster")
import numpy as np

from lasp_packets import xtcedef  # Gavin Medley's xtce UML implementation
from lasp_packets import parser  # Gavin Medley's constant bitstream implementation
import cdflib.cdfwrite as cdfwrite
import cdflib.cdfread as cdfread
import cdflib
# ||
# ||
# || Generator object from LASP packets
# || to read in the data
class IDEXPacket:
    def __init__(self, filename: str):
        """Test parsing a real XTCE document"""
        idex_xtce = 'idex_combined_science_definition.xml'
        idex_definition = xtcedef.XtcePacketDefinition(xtce_document=idex_xtce)
        assert isinstance(idex_definition, xtcedef.XtcePacketDefinition)


        idex_packet_file = filename
        print(f"Reading in data file {idex_packet_file}")
        idex_binary_data = bitstring.ConstBitStream(filename=idex_packet_file)
        print("Data import completed, writing packet structures.")

        idex_parser = parser.PacketParser(idex_definition)
        idex_packet_generator = idex_parser.generator(idex_binary_data,
                                                    # skip_header_bits=32,
                                                    show_progress=True,
                                                    yield_unrecognized_packet_errors=True)
    

        print("Packet structures written.")
        idex_binary_data.pos = 0
        self.epoch = []
        self.data = {}
        self.header={}
        evtnum = 0

        for pkt in idex_packet_generator:
            if 'IDX__SCI0TYPE' in pkt.data:
                scitype = pkt.data['IDX__SCI0TYPE'].raw_value
                if scitype == 1:
                    evtnum += 1
                    # print(pkt.data)
                    print(f"^*****Event header {evtnum}******^")
                    print(f"AID = {pkt.data['IDX__SCI0AID'].derived_value}")  # Instrument event number
                    print(f"Event number = {pkt.data['IDX__SCI0EVTNUM'].raw_value}")  # Event number out of how many events constitute the file
                    # print(f"Time = {pkt.data['IDX__SCI0TIME32'].derived_value}")  # Time in 20 ns intervals
                    print(f"Rice compression enabled = {bool(pkt.data['IDX__SCI0COMP'].raw_value)}")   # TODO: Use this to determine if we should rice_decompress the data {0,1}
                    # self.header[evtnum][f"TimeIntervals"] = pkt.data['IDX__SCI0TIME32'].derived_value  # Store the number of 20 ns intervals in the respective CDF "Time" variables
                    self.header[(evtnum, 'Timestamp')] = pkt.data['SHCOARSE'].derived_value + 20*(10**(-6))*pkt.data['SHFINE'].derived_value  # Use this as the CDF epoch
                    self.epoch.append(pkt.data['SHCOARSE'].derived_value + 20 * (10 ** (-6)) * pkt.data['SHFINE'].derived_value)
                    print(f"Timestamp = {self.header[(evtnum, 'Timestamp')]} seconds since epoch (Midnight January 1st, 2012)")


                if scitype in [2, 4, 8, 16, 32, 64]:
                    if scitype not in self.data:
                        self.data.update({scitype : {}})
                    if evtnum not in self.data[scitype]:
                        self.data[scitype][evtnum] = pkt.data['IDX__SCI0RAW'].raw_value
                    else:
                        self.data[scitype][evtnum] += pkt.data['IDX__SCI0RAW'].raw_value

        # Parse the waveforms according to the scitype present (high gain and low gain channels encode waveform data differently).
        names = {2: "TOF High Gain [dN]", 4: "TOF Low Gain [dN]", 8: "TOF Mid Gain [dN]", 16: "Target Low CSA [dN]",
                 32: "Target High CSA [dN]", 64: "Ion Grid CSA [dN]"}
        datastore = {}
        for scitype in self.data:
            datastore[names[scitype]] = []
            for evt in self.data[scitype]:
                datastore[names[scitype]].append(self.parse_waveform_data(self.data[scitype][evt], scitype))

        self.data = datastore
        self.epoch = (np.array(self.epoch)*1000).astype(int)
        self.numevents = evtnum

    # ||
    # || Parse the high sampling rate data, this
    # || should be 10-bit blocks
    def parse_hs_waveform(self, waveform_raw: str):
        """Parse a binary string representing a high gain waveform"""
        w = bitstring.ConstBitStream(bin=waveform_raw)
        ints = []
        while w.pos < len(w):
            w.read('pad:2')  # skip 2
            ints += w.readlist(['uint:10']*3)
        return ints

    # ||
    # || Parse the low sampling rate data, this
    # || should be 12-bit blocks
    def parse_ls_waveform(self, waveform_raw: str):
        """Parse a binary string representing a low gain waveform"""
        w = bitstring.ConstBitStream(bin=waveform_raw)
        ints = []
        while w.pos < len(w):
            w.read('pad:8')  # skip 2
            ints += w.readlist(['uint:12']*2)
        return ints

    # ||
    # || Use the SciType flag to determine the sampling rate of
    # || the data we are trying to parse
    def parse_waveform_data(self, waveform: str, scitype: int):
        """Parse the binary string that represents a waveform"""
        print(f'Parsing waveform for scitype={scitype}')
        if scitype in (2, 4, 8):
            return self.parse_hs_waveform(waveform)
        else:
            return self.parse_ls_waveform(waveform)

    # ||
    # ||
    # || Write the waveform data
    # || to CDF files
    def write_to_cdf(self):

        cdf_master = cdfread.CDF('imap_idex_l0-raw_0000000_v01.cdf')
        if (cdf_master.file != None):
            # Get the cdf's specification
            info = cdf_master.cdf_info()
            cdf_file = cdfwrite.CDF('./IDEX_Sawtooth.cdf', cdf_spec=info, delete=True)
        else:
            raise OSError('Problem reading master file.... Stop')

        # Get the global attributes
        globalaAttrs = cdf_master.globalattsget(expand=True)
        # Write the global attributes
        cdf_file.write_globalattrs(globalaAttrs)
        zvars = info['zVariables']
        print('no of zvars=', len(zvars))
        # Loop thru all the zVariables --> What are zvars vs rvars?
        for x in range(0, len(zvars)):
            # Get the variable's specification
            varinfo = cdf_master.varinq(zvars[x])
            print('Z =============>', x, ': ', varinfo['Variable'])

            if (varinfo['Variable'] == "Epoch"):
                # NOTE: This is not actually a time variable! We need to figure out how to convert to TT2000!
                vardata = self.epoch
            if (varinfo['Variable'] == "IDEX_Trigger"):
                vardata = self.header[(1, "Timestamp")]
            if (varinfo['Variable'] == "TOF_Low"):
                print(len(np.array(self.data["TOF Low Gain [dN]"])))
                vardata = np.array(self.data["TOF Low Gain [dN]"], float)
            if (varinfo['Variable'] == "TOF_Mid"):
                vardata = np.array(self.data["TOF Mid Gain [dN]"])
            if (varinfo['Variable'] == "TOF_High"):
                vardata = np.array(self.data["TOF High Gain [dN]"])
            if (varinfo['Variable'] == "Time_Low_SR"):
                vardata = np.linspace(0, len(self.data["Target Low CSA [dN]"][0]) - 1,
                                      len(self.data["Target Low CSA [dN]"][0]))
            if (varinfo['Variable'] == "Time_High_SR"):
                vardata = np.linspace(0, len(self.data["TOF Low Gain [dN]"][0]) - 1,
                                      len(self.data["TOF Low Gain [dN]"][0]))
            if (varinfo['Variable'] == "Target_Low"):
                vardata = np.array(self.data["Target Low CSA [dN]"])
            if (varinfo['Variable'] == "Target_High"):
                vardata = np.array(self.data["Target High CSA [dN]"])
            if (varinfo['Variable'] == "Ion_Grid"):
                vardata = np.array(self.data["Ion Grid CSA [dN]"])

            # Get the variable's attributes
            varattrs = cdf_master.varattsget(zvars[x], expand=True)
            cdf_file.write_var(varinfo, var_attrs=varattrs, var_data=vardata)

        cdf_master.close()
        cdf_file.close()
    
# ||
# ||
# || Gather all of the events 
# || and plot them
def plot_full_event(packets):
    fix, ax = plt.subplots(nrows=6)
    for i, (k, v) in enumerate(packets.items()):
        if(k[0] == 1):
            x = np.linspace(0, len(v), len(v))
            ax[i].plot(v)
            ax[i].fill_between(x, v, color='r')
            ax[i].set_ylabel(k, font="Times New Roman", fontsize=12, fontweight='bold')
            ax[i].set_xlabel("Bit number", font="Times New Roman", fontsize=30, fontweight='bold')
    plt.suptitle(f"IDEX FM Sawtooth Test All Events", font="Times New Roman", fontsize=30, fontweight='bold')
    plt.show()

# ||
# ||
# || Write the waveform data 
# || to an HDF5 file
def write_to_hdf5(waveforms: dict, filename: str):
    # print(waveforms.keys())
    # print(waveforms.values())

    # TODO: Change this to a suitable file location for the .h5 dump
    h = h5py.File(filename,'w')
    for k, v in waveforms.items():
        # print(np.array(v))
        # h.create_dataset(k, data=np.array(v, dtype=np.int8))
        h.create_dataset(f"/{k[0]}/{k[1]}", data=np.array(v))
        if(k[1]=='TOF Low Gain [dN]'):
            time = np.linspace(0, len(v), len(v))
            h.create_dataset(f"/{k[0]}/Time (high sampling) [dN]", data=time)
        if(k[1]=='Ion Grid CSA [dN]'):
            time = np.linspace(0, len(v), len(v))
            h.create_dataset(f"/{k[0]}/Time (low sampling) [dN]", data=time)
    # h.create_dataset("Time since ")



# || Test code: Import file and write the relevant data to an hdf5 file
if __name__ == "__main__":
    fname = str('sciData_2023_052_14_45_05')
    packets = IDEXPacket(fname)
    # print(packets.data.keys())
    # plot_full_event(packets.data)
    #write_to_hdf5(packets.data, 'IDEX_Sawtooth.h5')
    packets.write_to_cdf()

    # Read back in as xarray and plot some samples
    idex_data = cdflib.cdf_to_xarray("IDEX_Sawtooth.cdf")
    print(idex_data)
    idex_data['TOF_High'].isel(Epoch=1).plot()
    idex_data['TOF_High'].isel(Epoch=4).plot()
    plt.show()
