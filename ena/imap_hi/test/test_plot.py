#!/usr/bin/python
import numpy as np
import struct

def read_qABCs(filename):
    esas = np.zeros((0,6,60), dtype=np.uint8)
    METs = []
    # TODO:  DON'T CRASH ON BAD FILENAME
    with open(filename, 'rb') as f:
        p = f.read()
        i = 0
        unpack_ubytes = struct.Struct('BBBBBBBBBB').unpack
        while i + 6 < len(p):
            hdr = unpack_ubytes(p[i:i+10])
            apid = (hdr[0]<<8 | hdr[1]) & 0x7FF
            pkt_siz = ((hdr[4]<<8 | hdr[5]) & 0xFFF) + 1
            # p[i+12] check is for "full" 48-spin data
            # hist_l is on 96-spin cadence so you'd check for 96
            # Packet APIDs and data:
            # 0x3B1  HIST_Q  48 spins qABC, qAB, qBC   360 bytes each
            # 0x3B2  HIST_M  48 spins qAC, lAB, lB     360 bytes each
            # 0x3B3  HIST_L  96 spins lABC, lBC, lAC   360 bytes each
            # 0x3A5  BACKGROUND 48 spins  bg, lA, lC   240/360/360 bytes
            # I recall Python2 vs Python3 is snippy about "== 48" vs "==
            # ASCII character 48", so if the array comes back zero length,
            # that's why.
            # if apid == 0x3B1 and p[i+12] == 48:  ### Python3
            if apid == 0x3B1 and p[i+12] == '0':    ### Python2
                METs.append((hdr[6]<<24) | (hdr[7]<<16) | (hdr[8]<<8) | hdr[9])
                # qAB is 360 bytes further in and qBC is 360 bytes further yet
                # If this were bg, you'd read in 4*60 not 6*60 bytes
                #   and you'd want to uncompress.
                tmp = np.frombuffer(p[i+13:i+13+360], dtype=np.uint8, count=360)
                esas = np.concatenate((esas, tmp.reshape(1,6,60)))
            i += pkt_siz + 6

    f.close()

    return METs, esas


# sample silly usage
if __name__ == '__main__':
    import sys
    import matplotlib.pyplot as plt

    if len(sys.argv) < 2:
        print('usage:  readqabc filename.pkt_pl')
        sys.exit()
    mets, qabc_data = read_qABCs(sys.argv[1])
    plt.figure()
    for i in range(6):
       a = plt.subplot(6,1,i+1)
       plt.imshow(qabc_data[:,i,:].transpose(), origin='lower')
       plt.setp(a.get_xticklabels(), visible=False)
       plt.setp(a.get_yticklabels(), visible=False)
    plt.show()