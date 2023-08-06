from spinnman.messages.eieio.command_messages.eieio_command_message\
    import EIEIOCommandMessage
from spinnman.messages.eieio.command_messages.eieio_command_header\
    import EIEIOCommandHeader
from spinnman import constants


class SpinnakerRequestReadData(EIEIOCommandMessage):

    def __init__(self, x, y, p, region_id, sequence_no, start_address,
                 space_available):
        EIEIOCommandMessage.__init__(
            self, EIEIOCommandHeader(
                constants.EIEIO_COMMAND_IDS.SPINNAKER_REQUEST_READ_DATA.value))
        self._x = x
        self._y = y
        self._p = p
        self._region_id = region_id
        self._sequence_no = sequence_no
        self._start_address = start_address
        self._space_available = space_available

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def p(self):
        return self._p

    @property
    def region_id(self):
        return self._region_id

    @property
    def sequence_no(self):
        return self._sequence_no

    @property
    def space_available(self):
        return self._space_available

    @staticmethod
    def get_min_packet_length():
        return 16

    @staticmethod
    def read_eieio_command_message(command_header, byte_reader):
        x = byte_reader.read_byte()
        y = byte_reader.read_byte()
        processor = byte_reader.read_byte()
        p = (processor >> 3) & 0x1F
        _ = byte_reader.read_byte()
        region_id = byte_reader.read_byte() & 0xF
        sequence_no = byte_reader.read_byte()
        start_address = byte_reader.read_int()
        space_available = byte_reader.read_int()
        return SpinnakerRequestReadData(x, y, p, region_id, sequence_no,
                                        start_address, space_available)

    def write_eieio_message(self, writer):
        EIEIOCommandMessage.write_eieio_message(self, writer)
        writer.write_byte(self._x)
        writer.write_byte(self._y)
        writer.write_byte(self._p << 3)
        writer.write_byte(0)
        writer.write_byte(self._region_id)
        writer.write_byte(self._sequence_no)
        writer.write_int(self._start_address)
        writer.write_int(self._space_available)
