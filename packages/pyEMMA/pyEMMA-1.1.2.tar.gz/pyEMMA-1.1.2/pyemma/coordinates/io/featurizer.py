from pyemma.util.annotators import deprecated
__author__ = 'noe'

import mdtraj
from mdtraj.geometry.dihedral import _get_indices_phi, \
    _get_indices_psi, compute_dihedrals

import numpy as np
import warnings

from pyemma.util.log import getLogger

log = getLogger('Featurizer')

__all__ = ['MDFeaturizer',
           'CustomFeature',
           ]


def _describe_atom(topology, index):
    """
    Returns a string describing the given atom

    :param topology:
    :param index:
    :return:
    """
    at = topology.atom(index)
    return "%s %i %s %i" % (at.residue.name, at.residue.index, at.name, at.index)


class CustomFeature(object):

    """
    A CustomFeature is the base class for all self defined features. You shall
    calculate your quantities in map method and return it as an ndarray.

    If you simply want to call a function with arguments, you do not need to derive.


    Parameters
    ----------
    func : function
        will be invoked with given args and kwargs on mapping traj
    args : list of positional args (optional)
    kwargs : named arguments

    Examples
    --------
    We use a FeatureReader to read md-trajectories and add a CustomFeature to
    transform coordinates:

    >>> reader = FeatureReader(...)
    >>> my_feature = CustomFeature(lambda x: 1.0 / x**2)
    >>> reader.featurizer.add_custom_feature(my_feature, output_dimension=3)

    Now a pipeline using this reader will apply the :math:`1 / x^2` transform on
    every frame being red.

    """

    def __init__(self, func=None, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def describe(self):
        return "override me to get proper description!"

    def map(self, traj):
        feature = self._func(traj, self._args, self._kwargs)
        assert isinstance(feature, np.ndarray)
        return feature


class DistanceFeature:

    def __init__(self, top, distance_indexes):
        self.top = top
        self.distance_indexes = np.array(distance_indexes)
        self.prefix_label = "DIST:"

    def describe(self):
        labels = []
        for pair in self.distance_indexes:
            labels.append("%s%s - %s" % (self.prefix_label,
                                         _describe_atom(self.top, pair[0]),
                                         _describe_atom(self.top, pair[1])))
        return labels

    def map(self, traj):
        return mdtraj.compute_distances(traj, self.distance_indexes)


class InverseDistanceFeature(DistanceFeature):

    def __init__(self, top, distance_indexes):
        DistanceFeature.__init__(self, top, distance_indexes)
        self.prefix_label = "INVDIST:"

    def map(self, traj):
        return 1.0 / mdtraj.compute_distances(traj, self.distance_indexes)


class BackboneTorsionFeature:

    def __init__(self, topology):
        self.topology = topology

        # this is needed for get_indices functions, since they expect a Trajectory,
        # not a Topology
        class fake_traj():
            def __init__(self, top):
                self.top = top

        ft = fake_traj(topology)
        _, indices = _get_indices_phi(ft)
        self._phi_inds = indices

        _, indices = _get_indices_psi(ft)
        self._psi_inds = indices

        self.dim = len(self._phi_inds) + len(self._psi_inds)

    def describe(self):
        top = self.topology
        labels_phi = ["PHI %s %i" % (top.atom(ires[0]).residue.name, ires[0])
                      for ires in self._phi_inds]

        labels_psi = ["PHI %s %i" % (top.atom(ires[0]).residue.name, ires[0])
                      for ires in self._psi_inds]

        return labels_phi + labels_psi

    def map(self, traj):
        y1 = compute_dihedrals(traj, self._phi_inds).astype(np.float32)
        y2 = compute_dihedrals(traj, self._psi_inds).astype(np.float32)
        return np.hstack((y1, y2))


class MDFeaturizer(object):

    """extracts features from MD trajectories.

    Parameters
    ----------

    topfile : str
        a path to a topology file (pdb etc.)
    """

    def __init__(self, topfile):
        self.topology = (mdtraj.load(topfile)).topology

        self.distance_indexes = []
        self.inv_distance_indexes = []
        self.contact_indexes = []
        self.angle_indexes = []

        self.active_features = []
        self._dim = 0

    def describe(self):
        """
        Returns a list of strings, one for each feature selected,
        with human-readable descriptions of the features.

        :return:
        """
        labels = []

        for f in self.active_features:
            labels.append(f.describe())

        return labels

    def select(self, selstring):
        """
        Selects using the given selection string

        :param selstring:
        :return:
        """
        return self.topology.select(selstring)

    def select_Ca(self):
        """
        Selects Ca atoms

        :return:
        """
        return self.topology.select("name CA")

    def select_Backbone(self):
        """
        Selects backbone C, CA and N atoms

        :return:
        """
        # FIXME: this string raises
        return self.topology.select("backbone name C[A] N")

    def select_Heavy(self):
        """
        Selects all heavy atoms

        :return:
        """
        return self.topology.select("mass >= 2")

    @staticmethod
    def pairs(sel):
        """
        Creates all pairs between indexes, except for 1 and 2-neighbors

        :return:
        """
        nsel = np.shape(sel)[0]
        npair = ((nsel - 2) * (nsel - 3)) / 2
        pairs = np.zeros((npair, 2))
        s = 0
        for i in range(0, nsel - 3):
            d = nsel - 3 - i
            pairs[s:s + d, 0] = sel[i]
            pairs[s:s + d, 1] = sel[i + 3:nsel]
            s += d

        return pairs

    @deprecated
    def distances(self, atom_pairs):
        return self.add_distances(atom_pairs)

    def add_distances(self, atom_pairs):
        """
        Adds the set of distances to the feature list
        :param atom_pairs:
        """
        #assert atom_pairs.shape ==...
        # TODO: shall we instead append here?
        self.distance_indexes = atom_pairs
        f = DistanceFeature(self.topology, distance_indexes=atom_pairs)
        self.active_features.append(f)
        self._dim += np.shape(atom_pairs)[0]

    @deprecated
    def distancesCa(self):
        return self.add_distances_ca()

    def add_distances_ca(self):
        """
        Adds the set of Ca-distances to the feature list
        """
        self.distance_indexes = self.pairs(self.select_Ca())

        f = DistanceFeature(self.topology, atom_pairs=self.distance_indexes)
        self.active_features.append(f)
        self._dim += np.shape(self.distance_indexes)[0]

    @deprecated
    def inverse_distances(self, atom_pairs):
        return self.add_inverse_distances(atom_pairs)

    def add_inverse_distances(self, atom_pairs):
        """
        Adds the set of inverse distances to the feature list

        :param atom_pairs:
        """
        self.inv_distance_indexes = atom_pairs

        f = InverseDistanceFeature(atom_pairs=self.inv_distance_indexes)
        self.active_features.append(f)
        self._dim += np.shape(self.distance_indexes)[0]

    @deprecated
    def contacts(self, atom_pairs):
        return self.add_contacts(atom_pairs)

    def add_contacts(self, atom_pairs):
        """
        Adds the set of contacts to the feature list
        :param atom_pairs:
        """
        #assert atom_pairs.shape == ...
        #assert in_bounds , ... 
        f = CustomFeature(mdtraj.compute_contacts, atom_pairs=atom_pairs)

        def describe():
            labels = []
            for pair in self.contact_indexes:
                labels.append("CONTACT: %s - %s" % (_describe_atom(self.topology, pair[0]),
                                                    _describe_atom(self.topology, pair[1])))
            return labels
        f.describe = describe
        f.topology = self.topology

        self._dim += np.shape(atom_pairs)[0]
        self.active_features.append(f)

    @deprecated
    def angles(self, indexes):
        return self.add_angles(indexes)

    def add_angles(self, indexes):
        """
        Adds the list of angles to the feature list

        Parameters
        ----------
        indexes : np.ndarray, shape=(num_pairs, 3), dtype=int
            an array with triplets of atom indices
        """
        #assert indexes.shape == 

        f = CustomFeature(mdtraj.compute_angles, indexes=indexes)

        def describe():
            labels = []
            for triple in self.angle_indexes:
                labels.append("ANGLE: %s - %s - %s " %
                              (_describe_atom(self.topology, triple[0]),
                               _describe_atom(self.topology, triple[1]),
                               _describe_atom(self.topology, triple[2])))

            return labels

        f.describe = describe
        f.topology = self.topology

        self.active_features.append(f)
        self.angle_indexes = indexes
        self._dim += np.shape(indexes)[0]

    @deprecated
    def backbone_torsions(self):
        return self.add_backbone_torsions()

    def add_backbone_torsions(self):
        """
        Adds all backbone torsions
        """
        f = BackboneTorsionFeature(self.topology)
        self.active_features.append(f)
        log.debug("adding %i torsions angles" % f.dim)
        self._dim += f.dim

    def add_custom_feature(self, feature, output_dimension):
        """
        Parameters
        ----------
        feature : object
            an object with interface like CustomFeature (map, describe methods)
        output_dimension : int
            a mapped feature coming from has this dimension.
        """
        assert output_dimension > 0, "tried to add empty feature"
        assert hasattr(feature, 'map'), "no map method in given feature"
        assert hasattr(feature, 'describe')

        self.active_features.append(feature)
        self._dim += output_dimension

    def dimension(self):
        """ current dimension due to selected features """
        return self._dim

    def map(self, traj):
        """
        Computes the features for the given trajectory
        :return:
        """
        # if there are no features selected, return given trajectory
        if self._dim == 0:
            warnings.warn("You have no features selected. Returning plain coordinates.")
            return traj.xyz

        # TODO: define preprocessing step (RMSD etc.)

        # otherwise build feature vector.
        feature_vec = []

        # only iterate over unique
        # TODO: implement __hash__ and __eq__, see
        # https://stackoverflow.com/questions/2038010/sets-of-instances
        for f in set(self.active_features):
            feature_vec.append(f.map(traj).astype(np.float32))

        return np.hstack(feature_vec)
