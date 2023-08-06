from spinnman.data.abstract_byte_reader import AbstractByteReader


class LittleEndianByteArrayByteReader(AbstractByteReader):
    """ A byte reader that reads from a byte array using little endian notation
    """
    
    def __init__(self, data):
        """
        
        :param data: The byte array to read the data from
        :type data: bytearray
        """
        self._data = data
        self._read_pointer = 0

    def is_at_end(self):
        """ee :py:meth:`spinnman.data.abstract_byte_reader.AbstractByteReader.is_at_end`
        """
        if self._read_pointer == len(self._data):
            return True
        return False
    
    def read_byte(self):
        """ See :py:meth:`spinnman.data.abstract_byte_reader.AbstractByteReader.read_byte`
        """
        if self._read_pointer >= len(self._data):
            raise EOFError("End of stream")
        value = self._data[self._read_pointer]
        self._read_pointer += 1
        return value
    
    def read_bytes(self, size=None):
        """ See :py:meth:`spinnman.data.abstract_byte_reader.AbstractByteReader.read_bytes`
        """
        if size is None:
            if self._read_pointer == len(self._data):
                return bytearray()
            value = self._data[self._read_pointer:]
            self._read_pointer = len(self._data)
            return value
        
        if self._read_pointer + (size - 1) >= len(self._data):
            raise EOFError("Not enough bytes to read {} bytes".format(size))
        new_pointer = self._read_pointer + size
        value = self._data[self._read_pointer:new_pointer]
        self._read_pointer = new_pointer
        return value
        
    def read_short(self):
        """ See :py:meth:`spinnman.data.abstract_byte_reader.AbstractByteReader.read_short`
        """
        if self._read_pointer + 1 >= len(self._data):
            raise EOFError("Not enough bytes to read a short")
        value = (self._data[self._read_pointer]
                 | (self._data[self._read_pointer + 1] << 8))
        self._read_pointer += 2
        return value
    
    def read_int(self):
        """ See :py:meth:`spinnman.data.abstract_byte_reader.AbstractByteReader.read_int`
        """
        if self._read_pointer + 3 >= len(self._data):
            raise EOFError("Not enough bytes to read an int")
        value = (self._data[self._read_pointer]
                 | (self._data[self._read_pointer + 1] << 8)
                 | (self._data[self._read_pointer + 2] << 16)
                 | (self._data[self._read_pointer + 3] << 24))
        self._read_pointer += 4
        return value
        
    def read_long(self):
        """ See :py:meth:`spinnman.data.abstract_byte_reader.AbstractByteReader.read_long`
        """
        if self._read_pointer + 7 >= len(self._data):
            raise EOFError("Not enough bytes to read a long")
        value = (self._data[self._read_pointer]
                 | (self._data[self._read_pointer + 1] << 8)
                 | (self._data[self._read_pointer + 2] << 16)
                 | (self._data[self._read_pointer + 3] << 24)
                 | (self._data[self._read_pointer + 4] << 32)
                 | (self._data[self._read_pointer + 5] << 40)
                 | (self._data[self._read_pointer + 6] << 48)
                 | (self._data[self._read_pointer + 7] << 56))
        self._read_pointer += 8
        return value
