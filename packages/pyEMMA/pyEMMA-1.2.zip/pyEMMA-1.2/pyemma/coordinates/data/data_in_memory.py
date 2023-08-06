__author__ = 'noe, marscher'

import numpy as np

from pyemma.coordinates.data.interface import ReaderInterface


class DataInMemory(ReaderInterface):

    r"""
    multi-dimensional data fully stored in memory.

    Used to pass arbitrary coordinates to pipeline. Data is being flattened to 
    two dimensions to ensure it is compatible.

    Parameters
    ----------
    data : ndarray (nframe, ndim) or list of ndarrays (nframe, ndim)
        Data has to be either one 2d array which stores amount of frames in first
        dimension and coordinates/features in second dimension or a list of this
        arrays.
    """

    def __init__(self, data, chunksize=5000):
        super(DataInMemory, self).__init__(chunksize=chunksize)

        # storage
        self._data = []

        if not isinstance(data, (list, tuple)):
            data = [data]

        # everything is an array
        if all(isinstance(d, np.ndarray) for d in data):
            for d in data:
                self._add_array_to_storage(d)
        else:
            raise ValueError("supply 2d ndarray, list of 2d ndarray"
                             " or list of filenames storing 2d arrays."
                             " Your input was %s" % str(data))

        self.__set_dimensions_and_lenghts()
        self._parametrized = True

    @classmethod
    def load_from_files(cls, files):
        """ construct this by loading all files into memory

        Parameters
        ----------
        files: str or list of str
            filenames to read from
        """
        # import here to avoid cyclic import
        from pyemma.coordinates.data.numpy_filereader import NumPyFileReader

        reader = NumPyFileReader(files)
        data = reader.get_output()
        return cls(data)

    def __set_dimensions_and_lenghts(self):
        # number of trajectories/data sets
        self._ntraj = len(self._data)
        if self._ntraj == 0:
            raise ValueError("no valid data")

        # this works since everything is flattened to 2d
        self._lengths = [np.shape(d)[0] for d in self._data]

        # ensure all trajs have same dim
        ndims = [np.shape(x)[1] for x in self._data]
        if not np.unique(ndims).size == 1:
            raise ValueError("input data has different dimensions!"
                             "Dimensions are = %s" % ndims)

        self._ndim = ndims[0]

    def _reset(self, stride=1):
        """Resets the data producer
        """
        self._itraj = 0
        self._t = 0

    def _next_chunk(self, lag=0, stride=1):
        # finished once with all trajectories? so _reset the pointer to allow
        # multi-pass
        if self._itraj >= self._ntraj:
            self._reset()

        traj_len = self._lengths[self._itraj]
        traj = self._data[self._itraj]

        # complete trajectory mode
        if self._chunksize == 0:
            X = traj[::stride]
            self._itraj += 1

            if lag == 0:
                return X
            else:
                Y = traj[lag * stride:traj_len:stride]
                return (X, Y)
        # chunked mode
        else:
            upper_bound = min(
                self._t + (self._chunksize + 1) * stride, traj_len)
            slice_x = slice(self._t, upper_bound, stride)

            X = traj[slice_x]

            if lag == 0:
                self._t = upper_bound

                if upper_bound >= traj_len:
                    self._itraj += 1
                    self._t = 0
                return X
            else:
                # its okay to return empty chunks
                upper_bound = min(
                    self._t + (lag + self._chunksize + 1) * stride, traj_len)
                slice_y = slice(self._t + lag, upper_bound, stride)
                self._t += X.shape[0]

                if self._t >= traj_len:
                    self._itraj += 1
                    self._t = 0
                Y = traj[slice_y]
                return X, Y
