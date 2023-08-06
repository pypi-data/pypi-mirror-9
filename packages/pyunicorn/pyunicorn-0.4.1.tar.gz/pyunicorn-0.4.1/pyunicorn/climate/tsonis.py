#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of pyunicorn.
# Copyright (C) 2008--2015 Jonathan F. Donges and pyunicorn authors
# URL: <http://www.pik-potsdam.de/members/donges/software>
# License: BSD (3-clause)

"""
Provides classes for generating and analyzing complex climate networks.
"""

#
#  Import essential packages
#

#  Import NumPy for the array object and fast numerics
import numpy as np

from .climate_network import ClimateNetwork
from .climate_data import ClimateData
from ..core.network import cached_const


#
#  Define class TsonisClimateNetwork
#

# TODO: Reconsider storage of correlation matrix without taking absolute value.
class TsonisClimateNetwork(ClimateNetwork):

    """
    Encapsulates a Tsonis climate network.

    Construct a static climate network following Tsonis et al. from the
    Pearson correlation matrix at zero lag.

    Hence, Tsonis climate networks are undirected due to the symmetry of the
    correlation matrix.

    References: [Tsonis2004]_, [Tsonis2006]_, [Tsonis2008b]_, [Tsonis2008c]_.

    Derived from the class ClimateNetwork.
    """

    #
    #  Defines internal methods
    #

    def __init__(self, data, threshold=None, link_density=None,
                 non_local=False, node_weight_type="surface", winter_only=True,
                 silence_level=0):
        """
        Initialize an instance of TsonisClimateNetwork.

        .. note::
           Either threshold **OR** link_density have to be given!

        Possible choices for ``node_weight_type``:
          - None (constant unit weights)
          - "surface" (cos lat)
          - "irrigation" (cos**2 lat)

        :type data: :classL`.ClimateData`
        :arg data: The climate data used for network construction.
        :arg float threshold: The threshold of similarity measure, above which
            two nodes are linked in the network.
        :arg float link_density: The networks's desired link density.
        :arg bool non_local: Determines, whether links between spatially close
            nodes should be suppressed.
        :arg str ode_weight_type: The type of geographical node weight to be
            used.
        :arg bool winter_only: Determines, whether only data points from the
            winter months (December, January and February) should be used for
            analysis. Possibly, this further suppresses the annual cycle in the
            time series.
        :arg int silence_level: The inverse level of verbosity of the object.
        """
        if silence_level <= 1:
            print "Generating a Tsonis climate network..."

        #  Set instance variables
        self.data = data
        """(ClimateData) - The climate data used for network construction."""

        self.N = self.data.grid.N
        self._threshold = threshold
        self._prescribed_link_density = link_density
        self._non_local = non_local
        self.node_weight_type = node_weight_type
        self.silence_level = silence_level

        #  Constructor of ClimateNetwork is called within this method
        self.set_winter_only(winter_only)

    def __str__(self):
        """
        Return a string representation of TsonisClimateNetwork.

        **Example:**

        >>> print TsonisClimateNetwork.SmallTestNetwork()
        Tsonis climate network:
        Undirected network, 6 nodes, 6 links, link_density 0.4
        Geographical network boundaries:
                 time     lat     lon
           min    0.0    0.00    2.50
           max    9.0   25.00   15.00
        Threshold = 0.5
        Local connections filtered out: False
        Use only data points from winter months: False
        """
        text = "Tsonis climate network: \n"
        text += ClimateNetwork.__str__(self)
        text += "\nUse only data points from winter months: " \
                + str(self.winter_only())

        return text

    #
    #  Methods for testing purposes
    #

    @staticmethod
    def SmallTestNetwork():
        """
        Return a 6-node undirected test climate network from a test data set.

        **Example:**

        >>> r(TsonisClimateNetwork.SmallTestNetwork().adjacency)
        array([[0, 0, 1, 0, 1, 0], [0, 0, 0, 1, 0, 1], [1, 0, 0, 0, 1, 0],
               [0, 1, 0, 0, 0, 1], [1, 0, 1, 0, 0, 0], [0, 1, 0, 1, 0, 0]])

        :rtype: Network instance
        """
        return TsonisClimateNetwork(data=ClimateData.SmallTestData(),
                                    threshold=0.5,
                                    winter_only=False,
                                    silence_level=2)

    #
    #  Defines methods to calculate the correlation matrix
    #

    def _calculate_correlation(self, anomaly):
        """
        Return the correlation matrix at zero lag.

        :type anomaly: 2D Numpy array (time, index)
        :arg anomaly: the anomaly time series from which to calculate the
                      correlation matrix at zero lag.

        :rtype: 2D Numpy array (index, index)
        :return: the correlation matrix at zero lag.
        """
        if self.silence_level <= 1:
            print "Calculating correlation matrix at zero lag from anomaly \
values..."
        #  Cast to float32 type to save memory since correlation coefficients
        #  are not needed in high floating point precision.
        correlation = np.corrcoef(anomaly.transpose()).astype("float32")

        return correlation

    def calculate_similarity_measure(self, anomaly):
        """
        Encapsulate the calculation of the correlation matrix at zero lag.

        **Example:**

        >>> TsonisClimateNetwork.SmallTestNetwork()._calculate_correlation(
        ...     anomaly=ClimateData.SmallTestData().anomaly())
        array([[ 1.        , -0.25377226, -1.        ,
                 0.25377226,  1.        , -0.25377226],
               [-0.25377226,  1.        ,  0.25377226,
                -1.        , -0.25377226,  1.        ],
               [-1.        ,  0.25377226,  1.        ,
                -0.25377226, -1.        ,  0.25377226],
               [ 0.25377226, -1.        , -0.25377226,
                 1.        ,  0.25377226, -1.        ],
               [ 1.        , -0.25377226, -1.        ,
                 0.25377226,  1.        , -0.25377226],
               [-0.25377226,  1.        ,  0.25377226,
                -1.        , -0.25377226,  1.        ]], dtype=float32)

        :type anomaly: 2D Numpy array (time, index)
        :arg anomaly: the anomaly time series from which to calculate the
                      correlation matrix at zero lag.

        :rtype: 2D Numpy array (index, index)
        :return: the correlation matrix at zero lag.
        """
        return self._calculate_correlation(anomaly)

    @cached_const('base', 'correlation')
    def correlation(self):
        """
        Return the correlation matrix at zero lag.

        **Example:**

        >>> TsonisClimateNetwork.SmallTestNetwork().correlation()
        array([[ 1.        ,  0.25377226,  1.        ,
                 0.25377226,  1.        ,  0.25377226],
               [ 0.25377226,  1.        ,  0.25377226,
                 1.        ,  0.25377226,  1.        ],
               [ 1.        ,  0.25377226,  1.        ,
                 0.25377226,  1.        ,  0.25377226],
               [ 0.25377226,  1.        ,  0.25377226,
                 1.        ,  0.25377226,  1.        ],
               [ 1.        ,  0.25377226,  1.        ,
                 0.25377226,  1.        ,  0.25377226],
               [ 0.25377226,  1.        ,  0.25377226,
                 1.        ,  0.25377226,  1.        ]], dtype=float32)

        :rtype: 2D Numpy array (index, index)
        :return: the correlation matrix at zero lag.
        """
        corr = self.similarity_measure()
        self.set_link_attribute('correlation', abs(corr))
        return corr

    def winter_only(self):
        """
        Indicate, if only winter months were used for network generation.

        **Example:**

        >>> TsonisClimateNetwork.SmallTestNetwork().winter_only()
        False

        :return bool: whether only winter months were used for network
            generation.
        """
        return self._winter_only

    def set_winter_only(self, winter_only):
        """
        Toggle use of exclusively winter data points for network generation.

        Also explicitly re(generates) the instance of TsonisClimateNetwork.

        **Example:**

        >>> net = TsonisClimateNetwork.SmallTestNetwork()
        >>> net.set_winter_only(winter_only=False)
        >>> net.n_links
        6

        :arg bool winter_only: Indicates, whether only winter months were used
            for network generation.
        """
        self._winter_only = winter_only

        if winter_only:
            winter_anomaly = self.data.anomaly_selected_months([0, 1, 11])
            correlation = self._calculate_correlation(winter_anomaly)
        else:
            correlation = self._calculate_correlation(self.data.anomaly())

        #  Call the constructor of the parent class ClimateNetwork
        ClimateNetwork.__init__(self, grid=self.data.grid,
                                similarity_measure=correlation,
                                threshold=self.threshold(),
                                link_density=self._prescribed_link_density,
                                non_local=self.non_local(),
                                directed=False,
                                node_weight_type=self.node_weight_type,
                                silence_level=self.silence_level)

    #
    #  Defines methods to calculate  weighted network measures
    #

    def correlation_weighted_average_path_length(self):
        """
        Return correlation weighted average path length.

        **Example:**

        >>> TsonisClimateNetwork.SmallTestNetwork().\
                correlation_weighted_average_path_length()
        1.0

        :return float: the correlation weighted average path length.
        """
        self.correlation()
        return self.average_path_length('correlation')

    def correlation_weighted_closeness(self):
        """
        Return correlation weighted closeness.

        **Example:**

        >>> TsonisClimateNetwork.SmallTestNetwork().\
                correlation_weighted_closeness()
        array([ 0.25, 0.25, 0.25, 0.25, 0.25, 0.25])

        :rtype: 1D Numpy array [index]
        :return: the correlation weighted closeness sequence.
        """
        self.correlation()
        return self.closeness('correlation')

    def local_correlation_weighted_vulnerability(self):
        """
        Return correlation weighted vulnerability.

        **Example:**

        >>> TsonisClimateNetwork.SmallTestNetwork().\
                local_correlation_weighted_vulnerability()
        array([ 0., 0., 0., 0., 0., 0.])

        :rtype: 1D Numpy array [index]
        :return: the correlation weighted vulnerability sequence.
        """
        self.correlation()
        return self.local_vulnerability('correlation')
