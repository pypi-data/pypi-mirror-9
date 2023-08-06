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

from .tsonis import TsonisClimateNetwork


#
#  Define class PartialCorrelationClimateNetwork
#

class PartialCorrelationClimateNetwork(TsonisClimateNetwork):

    """
    Encapsulates a partial correlation climate network.

    Constructs a static climate network based on partial correlation, as in
    [Ueoka2008]_.

    Derived from the class TsonisClimateNetwork.
    """

    #
    #  Defines internal methods
    #

    def __init__(self, data, threshold=None, link_density=None,
                 non_local=False, node_weight_type="surface", winter_only=True,
                 silence_level=0):
        """
        Initialize an instance of PartialCorrelationClimateNetwork.

        .. note::
           Either threshold **OR** link_density have to be given!

        Possible choices for ``node_weight_type``:
          - None (constant unit weights)
          - "surface" (cos lat)
          - "irrigation" (cos**2 lat)

        :type data: :class:`.ClimateData`
        :arg data: The climate data used for network construction.
        :arg float threshold: The threshold of similarity measure, above which
            two nodes are linked in the network.
        :arg float link_density: The networks's desired link density.
        :arg bool non_local: Determines, whether links between spatially close
            nodes should be suppressed.
        :arg str node_weight_type: The type of geographical node weight to be
            used.
        :arg bool winter_only: Determines, whether only data points from the
            winter months (December, January and February) should be used for
            analysis. Possibly, this further suppresses the annual cycle in the
            time series.
        :arg int silence_level: The inverse level of verbosity of the object.
        """
        if silence_level <= 1:
            print "Generating a partial correlation climate network..."

        #  Call constructor of parent class TsonisClimateNetwork
        TsonisClimateNetwork.__init__(self, data=data, threshold=threshold,
                                      link_density=link_density,
                                      non_local=non_local,
                                      node_weight_type=node_weight_type,
                                      winter_only=winter_only,
                                      silence_level=silence_level)

    def __str__(self):
        """
        Return a string representation of PartialCorrelationClimateNetwork.
        """
        text = "Partial correlation climate network: \n"
        text += TsonisClimateNetwork.__str__(self)

        return text

    #
    #  Defines methods to calculate the correlation matrix
    #

    def _calculate_correlation(self, anomaly):
        """
        Return the partial correlation matrix at zero lag.

        :type anomaly: 2D Numpy array (time, index)
        :arg anomaly: the anomaly time series from to calculate the partial
                      correlation matrix at zero lag.

        :rtype: 2D Numpy array (index, index)
        :return: the partial correlation matrix at zero lag.
        """
        if self.silence_level <= 1:
            print "Calculating partial correlation matrix at zero lag from \
anomaly values..."

        #  Calculate the correlation matrix, cast to float64 for precise
        #  calculation of inverse matrix.
        C = np.corrcoef(anomaly.transpose()).astype("float64")

        #  Calculate the inverse correlation matrix
        C_inv = np.linalg.inv(C)

        #  Clean up
        del C

        #  Get the diagonal of the inverse correlation matrix
        diag = C_inv.diagonal()[:]

        #  Calculate matrix of normalizations
        norm = np.sqrt(np.outer(diag, diag))

        return - C_inv / norm
