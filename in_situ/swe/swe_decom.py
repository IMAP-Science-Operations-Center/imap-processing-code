from pathlib import Path
from space_packet_parser import xtcedef, parser
import bitstring

packet_file = Path('science_block_20221116_163611Z_idle.bin')
with packet_file.open(mode='rb') as fh:
    binary_data = bitstring.ConstBitStream(fh)

xtce_document = Path('swe_packet_definition.xml')
packet_definition = xtcedef.XtcePacketDefinition(xtce_document)

# Initialize parser with custom XTCE definition
my_parser = parser.PacketParser(packet_definition)

# Generator object that spits out parsed Packet objects containing header and data attributes
packet_generator = my_parser.generator(binary_data)

for packet in packet_generator:
    # Do something with the packet data
    print(packet.header)
