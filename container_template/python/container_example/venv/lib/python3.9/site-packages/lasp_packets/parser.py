"""Module for parsing CCSDS packets using packet definitions"""
# Standard
from collections import namedtuple
import logging
from typing import Tuple
# Installed
import bitstring
# Local
from lasp_packets import xtcedef, csvdef

logger = logging.getLogger(__name__)


CcsdsPacketHeaderElement = namedtuple('CcsdsPacketHeaderElement', ['name', 'format_string'])

CCSDS_HEADER_DEFINITION = [
    CcsdsPacketHeaderElement('VERSION', 'uint:3'),
    CcsdsPacketHeaderElement('TYPE', 'uint:1'),
    CcsdsPacketHeaderElement('SEC_HDR_FLG', 'uint:1'),
    CcsdsPacketHeaderElement('PKT_APID', 'uint:11'),
    CcsdsPacketHeaderElement('SEQ_FLGS', 'uint:2'),
    CcsdsPacketHeaderElement('SRC_SEQ_CTR', 'uint:14'),
    CcsdsPacketHeaderElement('PKT_LEN', 'uint:16')
]

CCSDS_HEADER_LENGTH_BITS = 48

Packet = namedtuple('Packet', ['header', 'data'])


class ParsedDataItem(xtcedef.AttrComparable):
    """Representation of a parsed parameter"""

    def __init__(self, name: str, raw_value: any, unit: str = None, derived_value: float or str = None):
        """Constructor

        Parameters
        ----------
        name : str
            Parameter name
        unit : str
            Parameter units
        raw_value : any
            Raw representation of the parsed value. May be lots of different types but most often an integer
        derived_value : float or str
            May be a calibrated value or an enum lookup
        """
        if name is None or raw_value is None:
            raise ValueError("Invalid ParsedDataItem. Must define name and raw_value.")
        self.name = name
        self.raw_value = raw_value
        self.unit = unit
        self.derived_value = derived_value

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"{self.name}, raw={self.raw_value}, derived={self.derived_value}, unit={self.unit}"
                f")")


class UnrecognizedPacketTypeError(Exception):
    """Error raised when we can't figure out which kind of packet we are dealing with based on the header"""
    pass


class PacketParser:
    """Class for parsing CCSDS packets"""

    def __init__(self, packet_definition: xtcedef.XtcePacketDefinition or csvdef.CsvPacketDefinition,
                 word_size: int = None, header_name_mappings: dict = None):
        """Constructor

        Parameters
        ----------
        packet_definition: xtcedef.XtcePacketDefinition or csvdef.CsvPacketDefinition
            The packet definition object to use for parsing incoming data.
        word_size: int, Optional
            Number of bits per word. If set, binary parameters are assumed to end on a word boundary and any unused bits
            at the end of each binary parameter are skipped. Default is no word boundary enforcement. Typical usecase
            is 32bit words.
        header_name_mappings : dict, Optional
            If the XTCE definition uses different header item names than VERSION, TYPE, SEC_HDR_FLG, PKT_APID,
            SEQ_FLGS, SRC_SEQ_CTR, and PKT_LEN, you can pass in a dict mapping these to other names for purposes of
            restrictions or logical operations during parsing.
        """
        self.packet_definition = packet_definition
        self.word_size = word_size
        self.header_name_mappings = header_name_mappings

    @staticmethod
    def _parse_header(packet_data: bitstring.ConstBitStream,
                      start_position: int = None,
                      reset_cursor: bool = False,
                      header_name_mappings: dict = None) -> dict:
        """Parses the CCSDS standard header.

        Parameters
        ----------
        packet_data : bitstring.ConstBitStream
            Binary data stream of packet data.
        start_position : int
            Position from which to start parsing. If not provided, will start whenever the cursor currently is.
        reset_cursor : bool
            If True, upon parsing the header data, reset the cursor to the original position in the stream.
            This still applies even if start_position is specified. start_position will be used only for parsing the
            header and then the cursor will be returned to the location it was at before this function was called.
        header_name_mappings : dict, Optional
            If set, used to rename the parsed header values to the custom names.

        Returns
        -------
        header : dict
            Dictionary of header items.
        """
        def _rename(name: str):
            """Renames header items to custom names if specified"""
            if header_name_mappings and name in header_name_mappings:
                return header_name_mappings[name]
            return name

        original_cursor_position = packet_data.pos

        if start_position:
            packet_data.pos = start_position

        header = {
            _rename(item.name): ParsedDataItem(name=_rename(item.name), unit=None,
                                               raw_value=packet_data.read(item.format_string))
            for item in CCSDS_HEADER_DEFINITION
        }

        if reset_cursor:
            packet_data.pos = original_cursor_position

        return header

    def _determine_packet_by_restrictions(self, parsed_header: dict) -> Tuple[str, list]:
        """Examines a dictionary representation of a CCSDS header and determines which packet type applies.
        This packet type must be unique. If the header data satisfies the restrictions for more than one packet
        type definition, an exception is raised.

        Parameters
        ----------
        parsed_header : dict
            Pre-parsed header data in dictionary form for evaluating restriction criteria.
            NOTE: Restriction criteria can ONLY be evaluated against header items. There is no reasonable way to
            start parsing all the BaseContainer inheritance restrictions without assuming that all restrictions will
            be based on header items, which can be parsed ahead of time due to the consistent nature of a CCSDS header.

        Returns
        -------
        : str
            Name of packet definition.
        : list
            A list of Parameter objects
        """
        flattened_containers = self.packet_definition.flattened_containers
        meets_requirements = []
        for container_name, flattened_container in flattened_containers.items():
            try:
                checks = [
                    criterion.evaluate(parsed_header)
                    for criterion in flattened_container.restrictions
                ]
            except AttributeError as err:
                raise ValueError("Hitherto unparsed parameter name found in restriction criteria for container "
                                 f"{container_name}. Because we can't parse packet data until we know the type, "
                                 "only higher up parameters (e.g. APID) are permitted as container "
                                 "restriction criteria.") from err

            if all(checks):
                meets_requirements.append(container_name)

        if len(meets_requirements) == 1:
            name = meets_requirements.pop()
            return name, flattened_containers[name].entry_list

        if len(meets_requirements) > 1:
            raise UnrecognizedPacketTypeError(
                "Found more than one possible packet definition based on restriction criteria. "
                f"{meets_requirements}")

        if len(meets_requirements) < 1:
            raise UnrecognizedPacketTypeError(
                "Header does not allow any packet definitions based on restriction criteria. "
                f"Unable to choose a packet type to parse. parsed_header={parsed_header}. "
                "Note: Restricting container inheritance based on non-header data items is not possible in a "
                "general way and is not supported by this package.")

    @staticmethod
    def parse_packet(packet_data: bitstring.ConstBitStream, entry_list: list, **parse_value_kwargs) -> Packet:
        """Parse binary packet data according to the self.packet_definition object

        Parameters
        ----------
        packet_data : bitstring.BitString
            Binary packet data to parse into Packets
        entry_list : list
            List of Parameter objects

        Returns
        -------
        Packet
            A Packet object container header and data attributes.
        """
        header = {}
        for parameter in entry_list[0:7]:
            # logger.debug(f'Parsing header item {parameter}')
            parsed_value, _ = parameter.parameter_type.parse_value(packet_data, header)

            header[parameter.name] = ParsedDataItem(
                name=parameter.name,
                unit=parameter.parameter_type.unit,
                raw_value=parsed_value
            )

        user_data = {}
        for parameter in entry_list[7:]:
            logger.debug(f'Parsing {parameter} of type {parameter.parameter_type}')
            combined_parsed_data = dict(**header)
            combined_parsed_data.update(user_data)
            parsed_value, derived_value = parameter.parameter_type.parse_value(
                packet_data, parsed_data=combined_parsed_data, **parse_value_kwargs)

            logger.debug(f"Parsed value: {parsed_value}")
            user_data[parameter.name] = ParsedDataItem(
                name=parameter.name,
                unit=parameter.parameter_type.unit,
                raw_value=parsed_value,
                derived_value=derived_value
            )

        return Packet(header=header, data=user_data)

    def generator(self, binary_data: bitstring.ConstBitStream, parse_bad_pkts=True,
                  skip_header_bits: int = 0):
        """Create and return a Packet generator. Creating a generator object to return allows the user to create
        many generators from a single Parser and pass those generators around without having to pass the
        entire Parser object.

        Parameters
        ----------
        binary_data : bitstring.ConstBitStream
            Binary data to parse into Packets.
        parse_bad_pkts : bool, Optional
            If set to True when the generator encounters a packet with a bad length it will still attempt
            to decode and return the packet. If false the generator will skip the bad packet.
        skip_header_bits : int, Optional
            If provided, the parser skips this many bits at the beginning of every packet. This allows dynamic stripping
            of additional header data that may be prepended to packets.

        Yields
        -------
        : Packet
            Generator yields Packet objects containing the parsed packet data for each subsequent packet.
        """
        total_length = len(binary_data)
        while binary_data.pos < total_length:
            if skip_header_bits:
                binary_data.pos += skip_header_bits

            # Parse the header but leave the cursor in the original position because the header is defined
            #   in the overall packet definition as well. We only parse the header here, so we can determine the
            #   packet definition type (usually by APID, VERSION, and TYPE but potentially based on
            #   any header data).
            packet_starting_position = binary_data.pos
            logger.debug(f"Parsing starting at {packet_starting_position}")
            header = self._parse_header(binary_data, reset_cursor=True)
            assert binary_data.pos == packet_starting_position  # Make sure cursor hasn't moved
            logger.debug(
                f"Parsing packet with header: "
                f"{' '.join([str(parsed_param) for param_name, parsed_param in header.items()])}")

            try:
                # Try to infer the packet type definition based on header data
                packet_def_name, parameter_list = self._determine_packet_by_restrictions(header)
            except UnrecognizedPacketTypeError:
                logger.info(f'Unrecognized packet type. Could not find a matching definition for packet '
                            f'based on header data.')
                binary_data.pos += 8 * (header['PKT_LEN'].raw_value + 1 + 6)
                continue

            logger.debug(f"Packet determined to be of type {packet_def_name}")
            assert binary_data.pos == packet_starting_position  # Make sure cursor hasn't moved
            packet = self.parse_packet(binary_data, parameter_list, word_size=self.word_size)
            assert packet.header['PKT_LEN'].raw_value == header['PKT_LEN'].raw_value, (
                f"Hardcoded header parsing found a different packet length {header['PKT_LEN'].raw_value} "
                f"than the definition-based parsing found {packet.header['PKT_LEN'].raw_value}.")

            # 4.1.3.5.3 The length count C shall be expressed as:
            #   C = (Total Number of Octets in the Packet Data Field) – 1
            # We also just re-parsed the CCSDS header though as well, so that's an additional 6 octets
            specified_packet_data_length = 8 * (header['PKT_LEN'].raw_value + 1 + 6)
            actual_length_parsed = binary_data.pos - packet_starting_position

            if actual_length_parsed != specified_packet_data_length:
                logger.warning(f"Parsed packet length starting at bit position: {binary_data.pos} did not match "
                               "length specified in header. Updating bit string position to correct position "
                               "indicated by CCSDS header")
                binary_data.pos += specified_packet_data_length - actual_length_parsed
                if not parse_bad_pkts:
                    logger.warning("Skipping bad packet")
                    continue

            yield packet
        print(len(binary_data), total_length, binary_data.pos)
