import fortranfile
import numpy as np
import struct

_NUM_SELECTIONS = 6
_NUM_PTYPES = 6

_ID_TYPE = np.dtype('int32')   # Datatype of Particle IDs in the file
_ID_SIZE = _ID_TYPE.itemsize   # Size in bytes of one ID value

_NAME_LENGTH = 500             # Size of the Selection name string

class GVSelectFile(object):
    def __init__(self, fname=None):
        """ A gadgetviewer selection file reader and writer.

            :param fname: A string containing the name of the file to read.
        """
        if fname is not None:
            self._selections = self._parse_file(fname)
        else:
            names = ("Selection %02d" % i for i in xrange(1, _NUM_SELECTIONS + 1))
            self._selections = [GVSelection(name) for name in names]

    @staticmethod
    def _parse_file(input_file):
        """ Parses a file-like object into a list of GVSelection objects

            :param input_file: A file like object open for reading in binary
        """

        fin = fortranfile.FortranFile(input_file)

        fin.readRecord()
        all_names = fin.readRecord()
        names = ["".join(all_names[_NAME_LENGTH*i:_NAME_LENGTH*(i+1)])\
                    for i in xrange(_NUM_SELECTIONS)]

        # Create the selection objects
        selections = [GVSelection(name) for name in names]

        for selection in selections:
            fin.readRecord()
            for pid in xrange(_NUM_PTYPES):
                if fin.readInts()[0] != 0:
                    selection.set_ids(pid, fin.readInts())

        return selections

    def get_ids(self, selection_id, p_type):
        """ Get the list of ids from a given selection and particle type

            :param selection_id: The id of the selection to query
            :param p_type: The particle type to query
        """
        return self._selections[selection_id].get_ids(p_type)

    def set_ids(self, selection_id, p_type, ids):
        """ Set the ids of a given selection and particle type

            :param selection_id: The id of the selection to set
            :param p_type: The particle type whos ids are to be set
            :param ids: The list of ids to set
        """
        self._selections[selection_id].set_ids(p_type, ids)

    def write_file(self, filename):
        """ Writes the gadgetviewer selection file.

            :param filename: The filename to output to
        """

        header = struct.pack( "iiii", _ID_SIZE, _NUM_SELECTIONS, _ID_SIZE, _NUM_SELECTIONS*_NAME_LENGTH )

        for i in xrange( _NUM_SELECTIONS ):
            header += self._selections[i].name

        header += struct.pack("i", _NUM_SELECTIONS*_NAME_LENGTH)

        body_outs = [self._selections[i].make_output() for i in xrange(_NUM_SELECTIONS)]
        body = np.array( np.concatenate( body_outs ), dtype=_ID_TYPE).tostring()

        fout = open(filename, 'wb').write(header + body)

class GVSelection(object):
    def __init__(self, name=""):
        """ A class representing a single gadgetviewer selection """
        self.name = name
        self.ids = [np.array([], dtype=np.int32) for _ in xrange(_NUM_PTYPES)]

    def __repr__(self):
        return "GVSelection: " + self.name.rstrip()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        """ Sets the name of the selection

            :param name: An ASCII string with the name to be stored - this will be
                         truncated to a maximum of 500 characters
        """
        try:
            name.decode('ascii')
        except UnicodeDecodeError:
            raise ValueError("Names must only contain ASCII characters")

        name = name[:500]
        self._name = name + " "*(500 - len(name))


    def set_ids(self, ptype, ids):
        """ Sets the ids of a given ptype in the selection

            :param ptype: The particle type to consider (0-5)
            :param ids:   An iterable containing the ids to set
        """
        self.ids[ptype] = np.asarray(ids, dtype=_ID_TYPE)

    def get_ids(self, ptype):
        """ Gets the ids stored of a given ptype in the selection

            :param ptype: The particle type to consider (0-5)
        """
        return self.ids[ptype]

    def make_output(self):
        """Converts a GVSelection object into a binary array to be added to the
        output file"""

        if max(len(idarray) for idarray in self.ids) == 0:
            ret_array = [8, 1, _NUM_PTYPES, 8] + [_ID_SIZE, 0, _ID_SIZE]*_NUM_PTYPES
            return np.array(ret_array, dtype=_ID_TYPE)

        ret_array = [8, 0, _NUM_PTYPES, 8]
        for idarray in self.ids:
            if idarray.size == 0:
                ret_array += [4, 0, 4]
            else:
                nbytes = _ID_SIZE*idarray.size
                ret_array += [_ID_SIZE, idarray.size, _ID_SIZE, nbytes]
                ret_array += list(idarray)
                ret_array += [nbytes]

        return np.array(ret_array, dtype=_ID_TYPE)

