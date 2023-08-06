"""
Part of library for data saving.
"""


def data_bytes(data):
    """
    Function that data(number, string...) converts to bytes.*
    """
    final = bytearray()
    if type(data) == str:
        final.append(1)  # starting number of strings
        for l in data:
            final.append(ord(l))
        final.append(1)  # ending number of strings
    elif type(data) == int:
        final.append(0)  # starting number of numbers
        for x in range(int(data / 250)):
            final.append(255)
            data -= 250
        final.append(data + 5)
        final.append(0)  # ending number of numbers
    elif type(data) == float:
        final.append(0)  # starting number of numbers
        for x in range(int(data / 250)):
            final.append(255)
            data -= 250
        final.append(int(data) + 5)
        data -= int(data)
        final.append(2)  # floating point (.) number
        for x in range(int(round(data, 3) * 1000 / 250)):
            final.append(255)
            data -= 0.250
        final.append(int(data * 1000) + 5)
        final.append(0)  # ending number of strings
    elif type(data) == list:
        final.append(3)  # starting number of lists
        for x in data:
            for bit in data_bytes(x):
                final.append(bit)
        final.append(4)  # ending number of lists
    return final


class Knowledge:
    """Class for all data in program.

    :param str filename: name of data file without extension
    :param str ext: extension of data file
    """
    def __init__(self, filename, ext='.knw'):
        self.data = {}
        self.filename = filename + ext
        self.save = bytearray()

    def __repr__(self):
        self.ret = ''
        for x in self.data:
            self.ret += str(x)
            self.ret += ' : '
            self.ret += str(self.data[x])
            self.ret += '\n'
        return self.ret[:-1]  # so last \n is deleted

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def save_data(self):
        """Saves all data.
        """
        for thing in self.data:
            for bit in data_bytes(thing):
                self.save.append(bit)
            for bit in data_bytes(self.data[thing]):
                self.save.append(bit)
        with open(self.filename, 'wb') as output:
            output.write(self.save)


def bytes_data(binary):
    """Function that bytes converts to data(numbers, strings...).*
    """
    thing = None
    decimal = False
    ret = None
    nested = 0
    for x in binary:
        if thing == 'integer':
            if x == 0:
                thing = None
                decimal = False
                yield ret
                ret = None
            elif x == 2:
                decimal = True
            else:
                if decimal:
                    ret += x / 1000 + 0.005
                else:
                    ret += x - 5
        elif thing == 'string':
            if x == 1:
                thing = None
                yield ret
                ret = None
            else:
                ret += chr(x)
        elif thing == 'list':
            if x == 3:
                nested += 1
            if x == 4:
                if nested:
                    nested -= 1
                    ret.append(x)
                else:
                    thing = None
                    fin = []
                    for b in bytes_data(ret):
                        fin.append(b)
                    yield fin
                    ret = None
            else:
                ret.append(x)
        else:
            if x == 0:
                thing = 'integer'
                ret = 0
            elif x == 1:
                thing = 'string'
                ret = ''
            elif x == 3:
                thing = 'list'
                ret = bytearray()


def load(filename, ext='.knw'):
    """Function that loads saved data and returns Knowledge object.

    :param str filename: name of data file without extension
    :param str ext: extension of data file
    :returns: data from file
    :rtype: :py:class:`Knowledge`
    """
    with open(filename + ext, 'rb') as infile:
        a = bytearray(infile.read())
    res = Knowledge(filename)
    state = 'key'
    key = None
    data = None
    for x in bytes_data(a):
        if state == 'key':
            key = x
            state = 'data'
        else:
            data = x
            state = 'key'
            res[key] = data
            key = None
            data = None
    return res
