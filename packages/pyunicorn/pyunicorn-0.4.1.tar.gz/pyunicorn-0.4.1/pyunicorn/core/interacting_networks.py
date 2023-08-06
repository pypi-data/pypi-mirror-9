#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of pyunicorn.
# Copyright (C) 2008--2015 Jonathan F. Donges and pyunicorn authors
# URL: <http://www.pik-potsdam.de/members/donges/software>
# License: BSD (3-clause)

"""
Provides classes for analyzing spatially embedded complex networks, handling
multivariate data and generating time series surrogates.
"""

#
#  Import essential packages
#

#  Import NumPy for the array object and fast numerics
import numpy as np
from numpy import random

#  C++ code embedding
import weave

#  Import Network base class
from .network import Network


#
#  Define class InteractingNetworks
#

class InteractingNetworks(Network):

    """
    Encapsulates an ensemble of interacting networks.

    Provides measures to analyze the interaction topology of different pairs of
    subnetworks (groups of vertices).

    So far, most methods only give meaningful results for undirected networks!

    The idea of interacting networks and measures for their analysis are
    described in [Donges2011a]_.

    Consistently node-weighted measures for interacting network topologies are
    derived, described and applied in [Wiedermann2011]_.

    Derived from class Network.
    """
    #
    #  Definitions of internal methods
    #

    def __init__(self, adjacency, directed=False, node_weights=None,
                 silence_level=0):
        """
        Initialize an instance of InteractingNetworks.

        :type adjacency: square numpy array or list [node,node] of 0s and 1s
        :arg  adjacency: Adjacency matrix of the new network.  Entry [i,j]
            indicates whether node i links to node j.  Its diagonal must be
            zero.  Must be symmetric if directed=False.
        :arg bool directed: Indicates whether the network shall be considered
            as directed. If False, adjacency must be symmetric.
        :type node_weights: 1d numpy array or list [node] of floats >= 0
        :arg  node_weights: Optional array or list of node weights to be used
            for node splitting invariant network measures.  Entry [i] is the
            weight of node i.  (Default: list of ones)
        :arg int silence_level: The inverse level of verbosity of the object.
        """
        #  Call constructor of parent class Network
        Network.__init__(self, adjacency=adjacency,
                         directed=directed,
                         node_weights=node_weights,
                         silence_level=silence_level)

    def __str__(self):
        """Return a string representation of InteractingNetworks object."""
        return Network.__str__(self)

    #
    #  Graph generation methods
    #

    @staticmethod
    def SmallTestNetwork():
        """
        Return a 6-node undirected test network.

        The network looks like this::

                3 - 1
                |   | \\
            5 - 0 - 4 - 2

        :rtype: InteractingNetworks instance
        :return: an InteractingNetworks instance for testing purposes.
        """
        return InteractingNetworks(adjacency=[[0, 0, 0, 1, 1, 1],
                                              [0, 0, 1, 1, 1, 0],
                                              [0, 1, 0, 0, 1, 0],
                                              [1, 1, 0, 0, 0, 0],
                                              [1, 1, 1, 0, 0, 0],
                                              [1, 0, 0, 0, 0, 0]],
                                   directed=False,
                                   node_weights=[0.6, 0.8, 1.0, 1.2, 1.4, 1.6],
                                   silence_level=2)

    @staticmethod
    def RandomlySetCrossLinks(network, node_list1, node_list2,
                              cross_link_density=None,
                              number_cross_links=None):
        """
        Creates a set of random cross links between the considered
        interacting subnetworks. The number of cross links to be set
        can be chosen either explicitly or via a predefined cross link density.
        By not choosing any of either, a null model is created under
        preservation of the cross link density of the initial network.

        Implementation:

        Determines the number of cross links to be set.
        Creates an empty cross adjacency matrix.
        Randomly picks the coordinates of an entry and sets it to one.
        Repeats the procedure until the desired cross link density
        is reached.

        :type network: InteractingNetworks instance
        :arg network: The base network for setting random cross links.
        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :rtype:  :class:`InteractingNetworks`
        :return: The initial InteractingNetworks with random cross links
        """

        #  retrieve number of nodes
        N1, N2 = len(node_list1), len(node_list2)

        #  store node lists as arrays
        nodes1 = np.array(node_list1, dtype=int)
        nodes2 = np.array(node_list2, dtype=int)

        #  retrieve cross adjacency matrix
        cross_A = network.cross_adjacency(node_list1, node_list2).copy()

        #  determine number of cross links
        if cross_link_density is not None:
            number_cross_links = int(cross_link_density * (N1 * N2))
            print "Setting number of cross links according to \
chosen link density."
        elif cross_link_density is None and number_cross_links is None:
            number_cross_links = int(cross_A.sum())
            print "Creating a null model for the given interacting networks."
        #  else: take the explicitly chosen number of cross links

        if number_cross_links > (N1 * N2):
            print "The number of cross links exceeds maximum."
            print "Setting link density of initial interacting network."
            number_cross_links = int(cross_A.sum())

        #  retrieve adjacency matrix of the full interacting network
        A_new = network.adjacency.copy()

        #  create new empty cross adjacency matrix
        cross_A_new = np.zeros((N1, N2))

        code = """
        int n_1, n_2, node1, node2;

        //  initialize random generator
        srand48(time(0));

        //  create random cross links
        for (int i =0 ; i < number_cross_links; i++) {
            do {
                n_1 = floor(drand48() * N1);
                n_2 = floor(drand48() * N2);
            } while (cross_A_new(n_1,n_2) == 1);

            cross_A_new(n_1,n_2) = 1;
        }

        //  overwrite the initial adjacency matrix of the full interacting
        //  network with the randomly rewired cross edges of the considered
        //  two subnetworks
        for (int i = 0; i < N1; i++) {
            for (int j = 0; j < N2; j++) {
                node1 = nodes1(i);
                node2 = nodes2(j);

                A_new(node1,node2) = A_new(node2,node1) = cross_A_new(i,j);
            }
        }

        """
        args = ['cross_A_new', 'number_cross_links', 'nodes1', 'nodes2',
                'N1', 'N2', 'A_new']
        weave.inline(code, arg_names=args,
                     type_converters=weave.converters.blitz, compiler='gcc',
                     extra_compile_args=['-O3'])

        #  Initialize new instance of InteractingNetworks
        return InteractingNetworks(adjacency=A_new,
                                   directed=network.directed,
                                   node_weights=network.node_weights,
                                   silence_level=network.silence_level)

    @staticmethod
    def RandomlySetCrossLinks_sparse(network, node_list1, node_list2,
                                     cross_link_density=None,
                                     number_cross_links=None):
        """
        Creates a set of random cross links between the considered
        interacting subnetworks. The number of cross links to be set
        can be chosen either explicitly or via a predefined cross link density.
        By not choosing any of either, a null model is created under
        preservation of the cross link density of the initial network.

        Implementation:

        Determines the number of cross links to be set.
        Creates an empty cross adjacency matrix.
        Randomly picks the coordinates of an entry and sets it to one.
        Repeats the procedure until the desired cross link density
        is reached.

        :type network: InteractingNetworks instance
        :arg network: The base network for setting random cross links.
        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :rtype:  :class:`InteractingNetworks`
        :return: The initial InteractingNetworks with random cross links
        """

        #  retrieve number of nodes
        N1, N2 = len(node_list1), len(node_list2)

        #  store node lists as arrays
        nodes1 = np.array(node_list1, dtype=int)
        nodes2 = np.array(node_list2, dtype=int)

        #  retrieve cross adjacency matrix
        cross_A = network.cross_adjacency_sparse(node_list1, node_list2).copy()

        #  determine number of cross links
        if cross_link_density is not None:
            number_cross_links = int(cross_link_density * (N1 * N2))
            print "Setting number of cross links according to chosen \
                  link density."
        elif cross_link_density is None and number_cross_links is None:
            number_cross_links = int(sum(cross_A.values()))
            print "Creating a null model for the given interacting networks."
        #  else: take the explicitly chosen number of cross links

        if number_cross_links > (N1 * N2):
            print "The number of cross links exceeds maximum."
            print "Setting link density of initial interacting network."
            number_cross_links = int(sum(cross_A.values()))

        #  retrieve adjacency matrix of the full interacting network
        A_new = network.sp_A.copy()

        #  create new empty cross adjacency matrix
        cross_A_new = np.zeros((N1, N2))

        n_1, n_2 = 0, 0
        node1, node2 = 0, 0
        for i in range(number_cross_links):
            while True:
                n_1 = int(random.random() * N1)
                n_2 = int(random.random() * N2)
                if not (cross_A_new[n_1, n_2] == 1):
                    break
            cross_A_new[n_1, n_2] = 1
        for i in range(N1):
            for j in range(N2):
                node1 = int(nodes1[i])
                node2 = int(nodes2[j])
                A_new[node1, node2] = cross_A_new[i, j]
                A_new[node2, node1] = cross_A_new[i, j]

        #  Initialize new instance of InteractingNetworks
        return InteractingNetworks(adjacency=A_new,
                                   directed=network.directed,
                                   node_weights=network.node_weights,
                                   silence_level=network.silence_level)

    @staticmethod
    def RandomlyRewireCrossLinks(network, node_list1, node_list2, swaps):
        """
        Randomize the cross links between two subnetworks under preservation of
        cross degree centrality of both subnetworks.

        Chooses randomly two cross links and swaps their ending points in
        subnetwork 2.

        Implementation:

        Stores the coordinates of the "1"-entries of the cross adjacency matrix
        in a tuple. Chooses randomly two entries of the tuple (ergo two cross
        links) allowing for the constraints that

        (1) the chosen links have distinct starting points in subnetwork 1 and
            distinct ending points in subnetwork 2
        (2) there do not exist intermediate links such that starting point of
            link 1 is connected to ending point of link 2 and vice versa.

        [In case two links have the same starting point or / and the same
        ending point, condition (2) is never satisfied. Therefore only
        condition (2) is implemented.]

        Swaps the ending points of the links in subnetwork 2 and overwrites the
        coordinates of the initial links in the tuple. The number of
        permutation procedures is determined by the "swaps" argument and the
        initial number of cross links. Creates a new adjacency matrix out of
        the altered tuple of coordinates.

        **Example** (Degree and cross degree sequences should be the same after
        rewiring):

        >>> net = InteractingNetworks.SmallTestNetwork()
        >>> print "Degree:", net.degree()
        Degree: [3 3 2 2 3 1]
        >>> print "Cross degree:", net.cross_degree(
        ...     node_list1=[0,3,5], node_list2=[1,2,4])
        Cross degree: [1 1 0]
        >>> rewired_net = net.RandomlyRewireCrossLinks(
        ...     network=net, node_list1=[0,3,5],
        ...     node_list2=[1,2,4], swaps=10.)
        >>> print "Degree:", rewired_net.degree()
        Degree: [3 3 2 2 3 1]
        >>> print "Cross degree:", rewired_net.cross_degree(
        ...     node_list1=[0,3,5], node_list2=[1,2,4])
        Cross degree: [1 1 0]

        :type network: :class:`InteractingNetworks` instance
        :arg network: The base network for rewiring cross links.
        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :arg float internal: Gives the fraction number_swaps /
            number_cross_links.
        :rtype:  :class:`InteractingNetworks`
        :return: The initial InteractingNetworks with swapped cross links
        """
        #  retrieve cross adjacency matrix of the considered interacting
        #  network
        cross_A = network.cross_adjacency(node_list1, node_list2).copy()

        #  determine number of cross links
        number_cross_links = int(cross_A.sum())

        #  retrieve number of nodes of the considered two subnetworks
        N1, N2 = len(node_list1), len(node_list2)

        #  Store node lists as arrays
        nodes1 = np.array(node_list1, dtype=int)
        nodes2 = np.array(node_list2, dtype=int)

        #  retrieve adjacency matrix of the full interacting network
        A_new = network.adjacency.copy()

        #  determine number of cross link permutations that will be performed
        number_swaps = int(swaps * number_cross_links)

        #  Create list of cross links
        cross_links = np.array(cross_A.nonzero()).transpose()

        code = """
        int e_1, e_2, ending_point_e_1, node1, node2, a, b, c, d;

        //  implement permutations

        //  initialize random number generator
        srand48(time(0));

        for (int i = 0; i < number_swaps; i++) {
            do {
                //  choose two random edges (accessible via the vector
                //  cross_links
                e_1 = floor(drand48() * number_cross_links);
                e_2 = floor(drand48() * number_cross_links);

                a = cross_links(e_1,0);
                b = cross_links(e_1,1);
                c = cross_links(e_2,0);
                d = cross_links(e_2,1);

                //  repeat the procedure in case there already exists
                //  a link between starting point of e_1 and
                // ending point of e_2 or vice versa
            } while (cross_A(a,d) == 1 || cross_A(c,b) == 1);

            //  delete initial edges within the cross adjacency matrix
            cross_A(a,b) = 0;
            cross_A(c,d) = 0;

            //  create new edges within the cross adjacency matrix by
            //  swapping the ending points of e_1 and e_2
            cross_A(a,d) = 1;
            cross_A(c,b) = 1;

            // likewise, adjust the vector cross_links:
            ending_point_e_1 = cross_links(e_1,1);
            cross_links(e_1,1) = cross_links(e_2,1);
            cross_links(e_2,1) = ending_point_e_1;
        }

        //  overwrite the initial adjacency matrix of the full interacting
        //  network with the randomly rewired cross edges of the considered
        //  two subnetworks
        for (int i = 0; i < N1; i++) {
            for (int j = 0; j < N2; j++) {
                node1 = nodes1(i);
                node2 = nodes2(j);

                A_new(node1,node2) = A_new(node2,node1) = cross_A(i,j);
            }
        }
        """
        args = ['cross_A', 'cross_links', 'number_cross_links', 'number_swaps',
                'N1', 'N2', 'A_new', 'nodes1', 'nodes2']
        weave.inline(code, arg_names=args,
                     type_converters=weave.converters.blitz, compiler='gcc',
                     extra_compile_args=['-O3'])

        #  Initialize new instance of InteractingNetworks
        return InteractingNetworks(adjacency=A_new,
                                   directed=network.directed,
                                   node_weights=network.node_weights,
                                   silence_level=network.silence_level)

    #
    #  Define methods for handling the interacting networks
    #

    def subnetwork(self, node_list):
        """
        Return the subnetwork induced by a subset of nodes as a Network object.

        This can be used to conveniently analyze the subnetwork separately,
        e.g., for calculation network measures solely this subnetwork.

        :arg [int] node_list: list of node indices describing the subnetwork
        :rtype: Network
        :return: the subnetwork induced by the nodes in node_list.
        """
        return Network(adjacency=self.internal_adjacency(node_list),
                       directed=self.directed,
                       node_weights=self.node_weights[node_list],
                       silence_level=self.silence_level)

    def internal_adjacency(self, node_list):
        """
        Return the adjacency matrix of a subnetwork induced by a subset of
        nodes.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                internal_adjacency([0,3,5])
        array([[0, 1, 1], [1, 0, 0], [1, 0, 0]], dtype=int8)
        >>> InteractingNetworks.SmallTestNetwork().\
                internal_adjacency([1,2,4])
        array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], dtype=int8)

        :arg [int] node_list: list of node indices describing the subnetwork
        :rtype: 2D array [node index, node index]
        :return: the subnetwork's adjacency matrix.
        """
        #  Create igraph Graph object describing the subgraph
        subgraph = self.graph.subgraph(node_list)
        #  Get adjacency matrix
        adjacency = \
            np.array(subgraph.get_adjacency(type=2).data).astype("int8")

        return adjacency

    def cross_adjacency(self, node_list1, node_list2):
        """
        Return cross adjacency matrix describing the interaction of two
        subnetworks.

        The cross adjacency matrix entry :math:`CA_{ij} = 1` describes that
        node i in the first subnetwork is linked to node j in the second
        subnetwork.  Vice versa, :math:`CA_{ji} = 1` indicates that node j in
        the first subnetwork is linked to node i in the second subnetwork.

        .. note::
           The Cross adjacency matrix is NEITHER square NOR symmetric in
           general!

        **Examples:**

        >>> r(InteractingNetworks.SmallTestNetwork().\
                cross_adjacency([1,2,4], [0,3,5]))
        array([[0, 1, 0], [0, 0, 0], [1, 0, 0]])
        >>> r(InteractingNetworks.SmallTestNetwork().\
                cross_adjacency([1,2,3,4], [0,5]))
        array([[0, 0], [0, 0], [1, 0], [1, 0]])

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :rtype: 2D array [node index_1, node index_2]
        :return: the cross adjacency matrix.
        """
        return self.adjacency[node_list1, :][:, node_list2]

    def cross_adjacency_sparse(self, node_list1, node_list2):
        """
        Return cross adjacency matrix describing the interaction of two
        subnetworks.

        The cross adjacency matrix entry M{CA_ij = 1} describes that node i
        in the first subnetwork is linked to node j in the second subnetwork.
        Vice versa, M{CA_ji = 1} indicates that node j in the first subnetwork
        is linked to node i in the second subnetwork.

        .. note::

           The Cross adjacency matrix is NEITHER square NOR symmetric in
           general!

        Examples:

        >>> print InteractingNetworks.SmallTestNetwork().\
                cross_adjacency_sparse([1,2,4], [0,3,5])
        [[0 1 0] [0 0 0] [1 0 0]]

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :rtype: 2D array [node index_1, node index_2]
        :return: the cross adjacency matrix.
        """
        return self.sp_A[node_list1, :][:, node_list2].A

    def internal_path_lengths(self, node_list, link_attribute=None):
        """
        Return internal path length matrix of an induced subnetwork.

        Contains the paths length between all pairs of nodes within the
        subnetwork. However, the paths themselves will generally contain nodes
        from the full network. To avoid this and only consider paths lying
        within the subnetwork, do the following:

        >>> InteractingNetworks.SmallTestNetwork().\
                subnetwork([0,3,5]).path_lengths()
        array([[ 0., 1., 1.], [ 1., 0., 2.], [ 1., 2., 0.]])

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                internal_path_lengths([0,3,5], None)
        array([[ 0., 1., 1.], [ 1., 0., 2.], [ 1., 2., 0.]])
        >>> InteractingNetworks.SmallTestNetwork().\
                internal_path_lengths([1,2,4], None)
        array([[ 0., 1., 1.], [ 1., 0., 1.], [ 1., 1., 0.]])

        :arg [int] node_list: list of node indices describing the subnetwork
        :arg str link_attribute: Optional name of the link attribute to be used
            as the links' length. If None, links have length 1. (Default: None)
        :rtype: 2D array [node index, node index]
        :return: the internal path length matrix of an induced subnetwork.
        """
        return self.\
            path_lengths(link_attribute)[node_list, :][:, node_list]

    def cross_path_lengths(self, node_list1, node_list2, link_attribute=None):
        """
        Return cross path length matrix for a pair of subnetworks.

        Contains the path length between nodes from different subnetworks. The
        paths may generally contain nodes from the full network.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                cross_path_lengths([0,3,5], [1,2,4], None)
        array([[ 2.,  2.,  1.], [ 1.,  2.,  2.], [ 3.,  3.,  2.]])
        >>> InteractingNetworks.SmallTestNetwork().\
                cross_path_lengths([0,5], [1,2,3,4], None)
        array([[ 2.,  2.,  1.,  1.], [ 3.,  3.,  2.,  2.]])

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :arg str link_attribute: Optional name of the link attribute to be used
            as the links' length. If None, links have length 1. (Default: None)
        :rtype: 2D array [index1, index2]
        :return: the cross path length matrix for a pair of subnetworks.
        """
        return self.\
            path_lengths(link_attribute)[node_list1, :][:, node_list2]

    #
    #  Define scalar statistics for interacting networks
    #

    def number_cross_links(self, node_list1, node_list2):
        """
        Return the number of links connecting the two subnetworks.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                number_cross_links([0,3,5], [1,2,4])
        2
        >>> InteractingNetworks.SmallTestNetwork().\
                number_cross_links([0,5], [1,2,3,4])
        2

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :return int: the number of links between nodes from different
            subnetworks.
        """
        if self.directed:
            print "Not implemented yet!"
        else:
            return self.cross_adjacency(node_list1, node_list2).sum()

    def number_internal_links(self, node_list):
        """
        Return the number of links within an induced subnetwork.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                number_internal_links([0,3,5])
        2
        >>> InteractingNetworks.SmallTestNetwork().\
                number_internal_links([1,2,4])
        3

        :arg [int] node_list: list of node indices describing the subnetwork
        :return int: the number of links within a given subnetwork.
        """
        n_links = self.internal_adjacency(node_list).sum()

        if self.directed:
            return n_links
        else:
            return n_links / 2

    def cross_link_density(self, node_list1, node_list2):
        """
        Return the density of links between two subnetworks.

        **Examples:**

        >>> r(InteractingNetworks.SmallTestNetwork().\
                cross_link_density([0,3,5], [1,2,4]))
        0.2222
        >>> InteractingNetworks.SmallTestNetwork().\
                cross_link_density([0,5], [1,2,3,4])
        0.25

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :return float: the density of links between two subnetworks.
        """
        N1, N2 = len(node_list1), len(node_list2)

        if self.directed:
            print "Not implemented yet!"
        else:
            n_cl = self.number_cross_links(node_list1, node_list2)
            return float(n_cl) / (N1 * N2)

    def internal_link_density(self, node_list):
        """
        Return the density of links within an induced subnetwork.

        **Examples:**

        >>> r(InteractingNetworks.SmallTestNetwork().\
                internal_link_density([0,3,5]))
        0.6667
        >>> r(InteractingNetworks.SmallTestNetwork().\
                internal_link_density([1,2,3,4]))
        0.6667

        :arg [int] node_list: list of node indices describing the subnetwork
        :return float: the density of links within a subnetwork.
        """
        N = len(node_list)
        n_links = self.number_internal_links(node_list)

        if self.directed:
            return float(n_links) / (N * (N - 1))
        else:
            return 2 * float(n_links) / (N * (N - 1))

    def internal_global_clustering(self, node_list):
        """
        Return internal global clustering coefficients for an induced
        subnetwork.

        Internal global clustering coefficients are calculated as mean values
        from the local clustering sequence of the whole network. This
        implies that triangles spanning different subnetworks will generally
        contribute to the internal clustering coefficient.

        To avoid this and consider only triangles lying within the subnetwork:

        >>> r(InteractingNetworks.SmallTestNetwork().\
                subnetwork([0,3,5]).global_clustering())
        0.0

        **Examples:**

        >>> r(InteractingNetworks.SmallTestNetwork().\
                internal_global_clustering([0,3,5]))
        0.0
        >>> r(InteractingNetworks.SmallTestNetwork().\
                internal_global_clustering([1,2,4]))
        0.5556

        :arg [int] node_list: list of node indices describing the subnetwork
        :return float: the internal global clustering coefficient for a
            subnetwork.
        """
        clustering = self.local_clustering()
        internal_clustering = clustering[node_list].mean()

        return internal_clustering

    def cross_global_clustering(self, node_list1, node_list2):
        """
        Return global cross clustering for a pair of subnetworks.

        The global cross clustering coefficient C_v gives the average
        probability, that two randomly drawn neighbors in subnetwork 2 of node
        v in subnetwork 1 are also neighbors and vice versa. It counts
        triangles having one vertex in subnetwork 1 and two vertices in
        subnetwork 2 and vice versa.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                cross_global_clustering([0,3,5], [1,2,4])
        0.0
        >>> InteractingNetworks.SmallTestNetwork().\
                cross_global_clustering([2], [1,3,4])
        1.0
        >>> InteractingNetworks.SmallTestNetwork().\
                cross_global_clustering([3,4], [1,2])
        0.5

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :return float: the cross global clustering coefficient for a pair of
            subnetworks.
        """
        #  Get cross local clustering sequences
        cc = self.cross_local_clustering(node_list1, node_list2)

        return cc.mean()

    def cross_global_clustering_sparse(self, node_list1, node_list2):
        """
        Return global cross clustering for a pair of subnetworks.

        The global cross clustering coefficient C_v gives the average
        probability, that two randomly drawn neighbors in subnetwork 2 of node
        v in subnetwork 1 are also neighbors and vice versa. It counts
        triangles having one vertex in subnetwork 1 and two vertices in
        subnetwork 2 and vice versa.

        Examples:

        >>> InteractingNetworks.SmallTestNetwork().cross_global_clustering(
        ...                                                   [0,3,5], [1,2,4])
        0.0

        >>> InteractingNetworks.SmallTestNetwork().cross_global_clustering(
        ...                                                       [2], [1,3,4])
        1.0

        >>> InteractingNetworks.SmallTestNetwork().cross_global_clustering(
        ...                                                       [3,4], [1,2])
        0.5

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :return float: the cross global clustering coefficient for a pair of
            subnetworks.
        """
        #  Get cross local clustering sequences
        cc = self.cross_local_clustering_sparse(node_list1, node_list2)

        return cc.mean()

    def cross_transitivity(self, node_list1, node_list2):
        """
        Return cross transitivity for a pair of subnetworks.

        The cross transitivity is the probability, that two randomly drawn
        neighbors in subnetwork 2 of node v in subnetwork 1 are also neighbors.
        It counts triangles having one vertex in subnetwork 1 and two vertices
        in subnetwork 2. Cross transitivity tends to weight low cross degree
        vertices less strongly when compared to the global cross clustering
        coefficient (see [Newman2003]_).

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                cross_transitivity([0,3,5], [1,2,4])
        0.0
        >>> InteractingNetworks.SmallTestNetwork().\
                cross_transitivity([2], [1,3,4])
        1.0
        >>> InteractingNetworks.SmallTestNetwork().\
                cross_transitivity([3,4], [1,2])
        1.0

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :return float: the cross transitivity for a pair of subnetworks.
        """
        #  Get full adjacency matrix
        A = self.adjacency
        #  Get subnetwork sizes
        N1, N2 = len(node_list1), len(node_list2)
        #  Convert node lists to Numpy arrays
        nodes1, nodes2 = np.array(node_list1), np.array(node_list2)

        #  Initialize
        cross_transitivity = np.zeros(1)

        code = """
        long counter_triangles, counter_triples;
        int node1, node2, node3;

        //  Set counter
        counter_triangles = 0;
        counter_triples = 0;

        //  Calculate cross transitivity from subnetwork 1 to subnetwork 2

        //  Loop over nodes in subnetwork 1
        for (int i = 0; i < N1; i++) {
            node1 = nodes1(i);

            //  Loop over unique pairs of nodes in subnetwork 2
            for (int j = 0; j < N2; j++) {
                node2 = nodes2(j);

                for (int k = 0; k < j; k++) {
                    node3 = nodes2(k);

                    if (A(node1,node2) == 1 && A(node2,node3) == 1
                        && A(node3,node1) == 1) {
                        counter_triangles++;
                    }
                    if (A(node1,node2) == 1 && A(node1,node3) == 1) {
                        counter_triples++;
                    }
                }
            }
        }

        if (counter_triples != 0) {
            cross_transitivity(0) =
                counter_triangles / double(counter_triples);
        }
        """
        args = ['N1', 'N2', 'A', 'nodes1', 'nodes2', 'cross_transitivity']
        weave.inline(code, arg_names=args,
                     type_converters=weave.converters.blitz, compiler='gcc',
                     extra_compile_args=['-O3'])
        return cross_transitivity[0]

    def cross_transitivity_sparse(self, node_list1, node_list2):
        """
        Return cross transitivity for a pair of subnetworks.

        The cross transitivity is the probability, that two randomly drawn
        neighbors in subnetwork 2 of node v in subnetwork 1 are also
        neighbors. It counts triangles having one vertex in
        subnetwork 1 and two vertices in subnetwork 2. Cross
        transitivity tends to weight low cross degree vertices less strongly
        when compared to the global cross clustering coefficient (see Newman,
        SIAM Review, 2003).

        Examples:

        >>> InteractingNetworks.SmallTestNetwork().\
                cross_transitivity_sparse([0,3,5], [1,2,4])
        0.0
        >>> InteractingNetworks.SmallTestNetwork().\
                cross_transitivity_sparse([3,4], [1,2])
        1.0

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :return float: the cross transitivity for a pair of subnetworks.
        """
        cross_degree = self.cross_degree(node_list1, node_list2)

        #  Get sparse adjacency matrix
        A = self.sp_A[node_list1+node_list2, :][:, node_list1+node_list2]
        #  Get subnetwork sizes
        N1, N2 = len(node_list1), len(node_list2)
        #  Initialize
        cross_transitivity = 0.0
        #  Set counter
        counter_triangles = 0.0
        counter_triples = 0.0
        #  Calculate cross transitivity from subnetwork 1 to subnetwork 2
        #  Loop over nodes in subnetwork 1
        for i in range(N1):
            node1 = i
            if cross_degree[i] > 1:
                #  Loop over unique pairs of nodes in subnetwork 2
                for j in range(N1, N1+N2):
                    node2 = j
                    for k in range(N1, j):
                        node3 = k
                        if A[node1, node2] == 1 and A[node1, node3] == 1:
                            counter_triples += 1
                            if A[node2, node3] == 1:
                                counter_triangles += 1

        if not counter_triples == 0:
            cross_transitivity = counter_triangles / counter_triples
        return cross_transitivity

    def _calculate_general_average_path_length(self, path_lengths,
                                               internal=False):
        """
        Calculate general average path length for interacting networks.

        :type path_lengths: 2D array [index, index]
        :arg path_lengths: The path length matrix.
        :arg bool internal: Indicates, whether internal or cross average path
            length shall be calculated.
        :return float: the general average path length.
        """
        #  Get shape of path lengths array for normalization
        (N, M) = path_lengths.shape

        #  Identify unconnected pairs and save in binary array isinf
        unconnected_pairs = np.isinf(path_lengths)
        #  Count the number of unconnected pairs
        n_unconnected_pairs = unconnected_pairs.sum()
        #  Set infinite entries corresponding to unconnected pairs to zero
        path_lengths[unconnected_pairs] = 0

        #  Take average of shortest geographical path length matrix optionally
        #  excluding the diagonal, since it is always zero, and all unconnected
        #  pairs. The diagonal should never contain infinities, so that should
        #  not be a problem.
        if internal:
            norm = float((N - 1) * M - n_unconnected_pairs)
        else:
            norm = float(N * M - n_unconnected_pairs)

        average_path_length = path_lengths.sum() / norm

        #  Reverse changes to path_lengths
        path_lengths[unconnected_pairs] = np.inf

        return average_path_length

    def cross_average_path_length(self, node_list1, node_list2,
                                  link_attribute=None):
        """
        Return cross average path length.

        Return the average (weighted) shortest path length between two induced
        subnetworks.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                cross_average_path_length([0,3,5], [1,2,4], None)
        2.0
        >>> InteractingNetworks.SmallTestNetwork().\
                cross_average_path_length([0,5], [1,2,3,4], None)
        2.0

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :arg str link_attribute: Optional name of the link attribute to be used
            as the links' length. If None, links have length 1. (Default: None)
        :return float: the cross average path length between a pair of
            subnetworks.
        """
        path_lengths = self.cross_path_lengths(node_list1, node_list2,
                                               link_attribute)
        return self._calculate_general_average_path_length(path_lengths,
                                                           internal=False)

    def internal_average_path_length(self, node_list, link_attribute=None):
        """
        Return internal average path length for an induced subnetwork.

        Return the average (weighted) shortest path length between all pairs
        of nodes within a subnetwork separately for which a path exists. Paths
        between nodes from different subnetworks are not included in the
        average!

        However, even if the end points lie within the same layer, the paths
        themselves will generally contain nodes from the whole network. To
        avoid this and only consider paths lying within the subnetwork, do the
        following:

        >>> r(InteractingNetworks.SmallTestNetwork().\
                subnetwork([0,3,5]).average_path_length(None))
        1.3333

        **Examples:**

        >>> r(InteractingNetworks.SmallTestNetwork().\
                internal_average_path_length([0,3,5], None))
        1.3333
        >>> r(InteractingNetworks.SmallTestNetwork().\
                internal_average_path_length([1,2,4], None))
        1.0

        :arg [int] node_list: list of node indices describing the subnetwork
        :arg str link_attribute: Optional name of the link attribute to be used
            as the links' length. If None, links have length 1. (Default: None)
        :return float: the internal average path length.
        """
        path_lengths = self.internal_path_lengths(node_list, link_attribute)

        return self._calculate_general_average_path_length(path_lengths,
                                                           internal=True)

    #
    #  Define local measures for interacting networks
    #

    def cross_degree(self, node_list1, node_list2):
        """
        Return the cross degree sequence for one subnetwork with respect to a
        second subnetwork.

        Gives the number of links from a specific node in the first subnetwork
        projecting to the second subnetwork.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                cross_degree([0,3,5], [1,2,4])
        array([1, 1, 0])
        >>> InteractingNetworks.SmallTestNetwork().\
                cross_degree([1,2,4], [0,3,5])
        array([1, 0, 1])
        >>> InteractingNetworks.SmallTestNetwork().\
                cross_degree([1,2,3,4], [0,5])
        array([0, 0, 1, 1])

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :rtype: 1D array [node index]
        :return: the cross degree sequence.
        """
        if self.directed:
            print "Not implemented yet!"
        else:
            cross_A = self.cross_adjacency(node_list1, node_list2)
            cross_degree = cross_A.sum(axis=1)

            return cross_degree

    def internal_degree(self, node_list):
        """
        Return the internal degree sequence of one induced subnetwork.

        Gives the number of links from a specific node to other nodes within
        the same induced subnetwork.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().internal_degree([0,3,5])
        array([2, 1, 1])
        >>> InteractingNetworks.SmallTestNetwork().internal_degree([1,2,4])
        array([2, 2, 2])

        :arg [int] node_list: list of node indices describing the subnetwork
        :rtype: 1D array [node index]
        :return: the internal degree sequence.
        """
        if self.directed:
            print "Not implemented yet!"
        else:
            degree = self.internal_adjacency(node_list).sum(axis=0)

            return degree

    def cross_local_clustering(self, node_list1, node_list2):
        """
        Return local cross clustering for a pair of subnetworks.

        The local cross clustering coefficient C_v gives the probability, that
        two randomly drawn neighbors in subnetwork 1 of node v in subnetwork 1
        are also neighbors. It counts triangles having one vertex in
        subnetwork 1 and two vertices in subnetwork 2.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                cross_local_clustering([0,3,5], [1,2,4])
        array([ 0.,  0.,  0.])
        >>> InteractingNetworks.SmallTestNetwork().\
                cross_local_clustering([2], [1,3,4])
        array([ 1.])
        >>> InteractingNetworks.SmallTestNetwork().\
                cross_local_clustering([3,4], [1,2])
        array([ 0.,  1.])

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :rtype: 1D array [node index]
        :return: the cross local clustering coefficient.
        """
        #  Get cross degree sequence
        cross_degree = self.cross_degree(node_list1, node_list2)
        #  Get full adjacency matrix
        A = self.adjacency
        #  Get layer sizes
        N1, N2 = len(node_list1), len(node_list2)
        #  Convert node lists to Numpy arrays
        nodes1, nodes2 = np.array(node_list1), np.array(node_list2)

        #  Initialize
        cross_clustering = np.zeros(N1)

        #  Prepare normalization factor
        norm = cross_degree * (cross_degree - 1) / 2.

        code = """
        long counter;
        int node1, node2, node3;

        //  Calculate cross clustering from subnetwork 1 to subnetwork 2
        for (int i = 0; i < N1; i++) {
            node1 = nodes1(i);

            //  Check if node1(i) has cross degree larger than 1
            if (norm(i) != 0) {
                //  Reset counter
                counter = 0;

                //  Loop over unique pairs of nodes in subnetwork 2
                for (int j = 0; j < N2; j++) {
                    node2 = nodes2(j);

                    for (int k = 0; k < j; k++) {
                        node3 = nodes2(k);

                        if (A(node1,node2) == 1 && A(node2,node3) == 1
                            && A(node3,node1) == 1) {
                            counter++;
                        }
                    }
                }
                cross_clustering(i) = counter / norm(i);
            }
        }
        """
        args = ['N1', 'N2', 'A', 'norm', 'nodes1', 'nodes2',
                'cross_clustering']
        weave.inline(code, arg_names=args,
                     type_converters=weave.converters.blitz, compiler='gcc',
                     extra_compile_args=['-O3'])
        return cross_clustering

    def cross_local_clustering_sparse(self, node_list1, node_list2):
        """
        Return local cross clustering for a pair of subnetworks.

        The local cross clustering coefficient C_v gives the probability, that
        two randomly drawn neighbors in subnetwork 1 of node v in subnetwork 1
        are also neighbors. It counts triangles having one vertex in
        subnetwork 1 and two vertices in subnetwork 2.

        Examples:

        >>> InteractingNetworks.SmallTestNetwork().\
                cross_local_clustering_sparse([0,3,5], [1,2,4])
        array([ 0.,  0.,  0.])

        >>> InteractingNetworks.SmallTestNetwork().\
                cross_local_clustering_sparse([2], [1,3,4])
        array([ 1.])

        >>> InteractingNetworks.SmallTestNetwork().\
                cross_local_clustering_sparse([3,4], [1,2])
        array([ 0.,  1.])

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :rtype: 1D array [node index]
        :return: the cross local clustering coefficient.
        """
        #  Get cross degree sequence
        cross_degree = self.cross_degree(node_list1, node_list2)
        #  Get full adjacency matrix
        A = self.sp_A[node_list1+node_list2, :][:, node_list1+node_list2]
        #  Get layer sizes
        N1, N2 = len(node_list1), len(node_list2)
        #  Convert node lists to Numpy arrays
        nodes1, nodes2 = np.array(node_list1), np.array(node_list2)

        #  Initialize
        cross_clustering = np.zeros(N1)
        #  Prepare normalization factor
        norm = cross_degree * (cross_degree - 1) / 2

        # Calculate cross clustering from subnetwork 1 to subnetwork 2
        counter = 0
        for node1 in range(N1):
            if not norm[node1] == 0:
                # Reset counter
                counter = 0
                #  Loop over unique pairs of nodes in subnetwork 2
                for node2 in range(N1, N1+N2):
                    for node3 in range(N1, node2):
                        if (A[node1, node2] == 1 and A[node2, node3] == 1
                                and A[node3, node1] == 1):
                            counter += 1
                cross_clustering[node1] = counter / norm[node1]

        return cross_clustering

    def _calculate_general_closeness(self, path_lengths, internal=True):
        """
        Calculate general closeness sequence for interacting networks.

        :type path_lengths: 2D array [node,node] of floats
        :arg  path_lengths: Path lengths to use
        :arg bool internal: Indicates, whether internal or cross closeness
            shall be calculated.
        :rtype:  1D array [index]
        :return: the general closeness sequence.
        """
        #  Get shape of path lengths array
        (N, M) = path_lengths.shape

        #  Set total number of nodes to be considered for calculation
        if internal:
            n_nodes = N
            norm = M - 1
        else:
            n_nodes = self.N  # All nodes of the whole network here!
            norm = M

        #  Closeness has the length of the first dimension of path lengths
        closeness = np.zeros(N)

        #  Identify unconnected pairs and save in binary array isinf
        unconnected_pairs = np.isinf(path_lengths)
        #  Set infinite entries corresponding to unconnected pairs to maximum
        #  possible path length.
        path_lengths[unconnected_pairs] = n_nodes - 1

        #  Some nodes have a distance of zero to all their
        #  neighbors. These nodes get zero closeness centrality.
        path_length_sum = path_lengths.sum(axis=1)
        #  M entries have been summed over, so we also have to normalize by M
        closeness[path_length_sum != 0] = \
            norm / path_length_sum[path_length_sum != 0]

        #  Reverse changes to path_lengths
        path_lengths[unconnected_pairs] = np.inf

        return closeness

    def cross_closeness(self, node_list1, node_list2, link_attribute=None):
        """
        Return cross closeness sequence for a pair of induced subnetworks.

        Gives the inverse average geodesic distance from a node in subnetwork 1
        to all nodes in subnetwork 2.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                cross_closeness([0,3,5], [1,2,4], None)
        array([ 0.6  ,  0.6  ,  0.375])
        >>> InteractingNetworks.SmallTestNetwork().\
                cross_closeness([0,5], [1,2,3,4], None)
        array([ 0.66666667,  0.4       ])

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :arg str link_attribute: Optional name of the link attribute to be used
            as the links' length. If None, links have length 1. (Default: None)
        :rtype: 1D arrays [index]
        :return: the cross closeness sequence.
        """
        path_lengths = self.cross_path_lengths(node_list1, node_list2,
                                               link_attribute)
        return self._calculate_general_closeness(path_lengths, internal=False)

    def internal_closeness(self, node_list, link_attribute=None):
        """
        Return internal closeness sequence for an induced subnetwork.

        Gives the inverse average geodesic distance from a node to all other
        nodes in the same induced subnetwork.

        However, the included paths will generally contain nodes from the whole
        network. To avoid this, do the following:

        >>> r(InteractingNetworks.SmallTestNetwork().\
                subnetwork([0,3,5]).closeness(None))
        array([ 1. , 0.6667, 0.6667])

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                internal_closeness([0,3,5], None)
        array([ 1.        ,  0.66666667,  0.66666667])
        >>> InteractingNetworks.SmallTestNetwork().\
                internal_closeness([1,2,4], None)
        array([ 1.,  1.,  1.])

        :arg [int] node_list: list of node indices describing the subnetwork
        :arg str link_attribute: Optional name of the link attribute to be used
            as the links' length. If None, links have length 1. (Default: None)
        :rtype: 1D array [index]
        :return: the internal closeness sequence.
        """
        path_lengths = self.internal_path_lengths(node_list, link_attribute)
        return self._calculate_general_closeness(path_lengths, internal=True)

    def cross_betweenness(self, node_list1, node_list2):
        """
        Return the cross betweenness sequence for the whole network with
        respect to a pair of subnetworks.

        Gives the normalized number of shortest paths only between nodes from
        **two** subnetworks, in which a node :math:`i` is contained. This is
        equivalent to the inter-regional / inter-group betweenness with respect
        to subnetwork 1 and subnetwork 2.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                cross_betweenness([2], [3,5])
        array([ 1.,  1.,  0.,  0.,  1.,  0.])
        >>> InteractingNetworks.SmallTestNetwork().\
                cross_betweenness(range(0,6), range(0,6))
        array([ 9.,  3.,  0.,  2.,  6.,  0.])

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :rtype: 1D arrays [node index]
        :return: the cross betweenness sequence for the whole network with
            respect to two subnetworks.
        """
        return self.interregional_betweenness(sources=node_list1,
                                              targets=node_list2)

    def internal_betweenness(self, node_list):
        """
        Return the internal betweenness sequence for an induced subnetwork.

        Gives the normalized number of shortest paths only between nodes from
        subnetwork 1, in which a node :math:`i` from the whole network is
        contained.  This is equivalent to the inter-regional / inter-group
        betweenness with respect to subnetwork 1 and subnetwork 1.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                internal_betweenness(range(0,6))
        array([ 9.,  3.,  0.,  2.,  6.,  0.])

        :arg [int] node_list: list of node indices describing the subnetwork
        :rtype: 1D array [node index]
        :return: the internal betweenness sequence for layer 1.
        """
        return self.interregional_betweenness(sources=node_list,
                                              targets=node_list)

    def nsi_cross_degree(self, node_list1, node_list2):
        """
        Return the n.s.i. cross-degree for a pair of induced subnetworks.

        Gives an estimation about the quota of the whole domain of interest of
        the subnetwork 2 any node in the subnetwork 1 is connected to.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_cross_degree([0,1,2],[3,4,5])
        array([ 4.2,  2.6,  1.4])
        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_cross_degree([0,2,5],[1,4])
        array([ 1.4,  2.2,  0. ])

        :arg [int] node_list1: list of node indices describing the subnetwork 1
        :arg [int] node_list2: list of node indices describing the subnetwork 2
        :rtype: 1D array [node index]
        :return: the n.s.i. cross-degree for layer 1.
        """

        cross_A = (self.adjacency +
                   np.eye(self.N))[node_list1, :][:, node_list2]
        node_weights = self.node_weights

        nsi_cross_degree = (cross_A * node_weights[node_list2]).sum(axis=1)

        return nsi_cross_degree

    def nsi_cross_mean_degree(self, node_list1, node_list2):
        """
        Return the n.s.i. cross-mean degree for a pair of induced subnetworks.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_cross_mean_degree([0,1,2],[3,4,5])
        2.5
        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_cross_mean_degree([0,2,5],[1,4])
        0.94999999999999996

        :arg [int] node_list1: list of node indices describing the subnetwork 1
        :arg [int] node_list2: list of node indices describing the subnetwork 2
        :return float: the n.s.i. cross-mean degree for layer 1.
        """

        nsi_cross = self.nsi_cross_degree(node_list1, node_list2)
        node_weights = self.node_weights[node_list1]

        W_i = sum(node_weights)

        return sum(nsi_cross * node_weights) / W_i

    def nsi_internal_degree(self, node_list):
        """
        Return the n.s.i. internal degree sequence of one induced subnetwork.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_internal_degree([0,3,5])
        array([ 3.4,  1.8,  2.2])
        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_internal_degree([0,1,3,5])
        array([ 3.4,  2. ,  2.6,  2.2])

        :arg [int] node_list: list of node indices describing the subnetwork
        :rtype: 1D array [node index]
        :return: the n.s.i. internal degree sequence
        """

        return self.nsi_cross_degree(node_list, node_list)

    def nsi_cross_local_clustering(self, node_list1, node_list2):
        """
        Return the n.s.i. cross-local clustering coefficient for a pair of
        induced subnetworks.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_cross_local_clustering([0,1,2],[3,4,5])
        array([ 0.33786848,  0.50295858,  1.  ])
        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_cross_local_clustering([0,2,5],[1,4])
        array([ 1.,  1.,  0.])

        :arg [int] node_list1: list of node indices describing the subnetwork 1
        :arg [int] node_list2: list of node indices describing the subnetwork 2
        :rtype: 1D array [node index]
        :return: the n.s.i. cross-local clustering coefficient for layer 1.
        """

        node_list1 = np.array(node_list1)
        node_list2 = np.array(node_list2)

        A = self.adjacency + np.eye(self.N)
        node_weight = self.node_weights

        norm = self.nsi_cross_degree(node_list1, node_list2)**2
        N1, N2 = len(node_list1), len(node_list2)

        nsi_cc = np.zeros(N1)

        code = """
        int node_v, node_p, node_q;

        for(int v=0; v<N1; v++) {
            node_v = node_list1(v);

            for(int p=0; p<N2; p++) {
                node_p = node_list2(p);
                if( A(node_v,node_p) == 1) {
                    nsi_cc(v) = nsi_cc(v) +
                        node_weight(node_p) * node_weight(node_p);

                    for(int q=p+1; q<N2; q++) {
                        node_q = node_list2(q);
                        if( A(node_p,node_q) && A(node_q,node_v) == 1) {
                            nsi_cc(v) = nsi_cc(v) +
                                2 * node_weight(node_p) * node_weight(node_q);
                        }
                    }
                }
            }
        }
        """
        args = ['N1', 'N2', 'A', 'nsi_cc',
                'node_weight', 'node_list1', 'node_list2']
        weave.inline(code, arg_names=args,
                     type_converters=weave.converters.blitz, compiler='gcc',
                     extra_compile_args=['-O3'])

        nsi_cc[norm != 0] = nsi_cc[norm != 0] / norm[norm != 0]
        nsi_cc[norm == 0] = 0

        return nsi_cc

    def nsi_cross_closeness_centrality(self, node_list1, node_list2):
        """
        Return the n.s.i. cross-closeness centrality for a pair of induced
        subnetworks.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_cross_closeness_centrality([0,1,2],[3,4,5])
        array([ 1.        ,  0.56756757,  0.48837209])
        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_cross_closeness_centrality([0,2,5],[1,4])
        array([ 0.73333333,  1.        ,  0.42307692])

        :arg [int] node_list1: list of node indices describing the subnetwork 1
        :arg [int] node_list2: list of node indices describing the subnetwork 2
        :rtype: 1D array [node index]
        :return: the n.s.i. cross-closeness for layer 1.
        """

        shortest_paths = self.path_lengths()
        node_weights = self.node_weights

        nsi_shortest_paths = shortest_paths + np.eye(len(shortest_paths))
        nsi_shortest_paths[np.isinf(nsi_shortest_paths)] = self.N - 1

        nsi_cross_paths = nsi_shortest_paths[node_list1, :][:, node_list2]
        W = sum(node_weights[node_list2])

        nsi_cross_closeness = \
            W / np.dot(nsi_cross_paths, node_weights[node_list2])

        return nsi_cross_closeness

    def nsi_internal_closeness_centrality(self, node_list):
        """
        Return the n.s.i. internal closeness sequence of one induced
        subnetwork.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_internal_closeness_centrality([0,3,5])
        array([ 1.        ,  0.68      ,  0.73913043])
        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_internal_closeness_centrality([0,1,3,5])
        array([ 0.84      ,  0.525     ,  0.72413793,  0.6       ])

        :arg [int] node_list: list of node indices describing the subnetwork
        :rtype: 1D array [node index]
        :return: the n.s.i. internal closeness sequence
        """

        return self.nsi_cross_closeness_centrality(node_list, node_list)

    def nsi_cross_global_clustering(self, node_list1, node_list2):
        """
        Return the n.s.i. cross-global clustering coefficient for an induced
        subnetwork 1 with regard to a second induced subnetwork 2.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_cross_global_clustering([0,1,2],[3,4,5])
        0.66878664680862498

        :arg [int] node_list1: list of node indices describing the subnetwork 1
        :arg [int] node_list2: list of node indices describing the subnetwork 2
        :return float: the n.s.i. cross-global clustering coefficient for the
            subnetwork 1 with regard to subnetwork 2.
        """

        nsi_cc = self.nsi_cross_local_clustering(node_list1, node_list2)
        node_weights = self.node_weights

        W = sum(node_weights[node_list1])

        return sum(node_weights[node_list1] * nsi_cc) / W

    def nsi_internal_local_clustering(self, node_list):

        """
        Return the n.s.i. internal cross-local clustering coefficient for an
        induced subnetwork.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_internal_local_clustering([1,2,3,5])
        array([ 0.73333333,  1.        ,  1.        ,  1.        ])
        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_internal_local_clustering([0,2,4])
        array([ 1.        ,  1.        ,  0.86666667])

        :arg [int] node_list: list of node indices describing the subnetwork
        :rtype: 1D numpy array [node_index]
        :return: the n.s.i. internal-local clustering coefficient for all nodes
            within the induced subnetwork
        """

        return self.nsi_cross_local_clustering(node_list, node_list)

    def nsi_cross_betweenness(self, node_list1, node_list2):
        """
        Return the n.s.i. cross betweenness sequence for the whole network with
        respect to a pair of subnetworks.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_cross_betweenness([0,4,5],[1,3])
        array([ 6.53333333,  1.2       ,  0.        ,
                0.67692308,  0.67692308,  0.        ])
        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_cross_betweenness([0,1],[2,3,4,5])
        array([ 2.13333333,  0.        ,  0.        ,
                0.49230769,  0.92087912,  0.        ])

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :rtype: 1D arrays [node index]
        :return: the n.s.i. cross betweenness sequence for the whole network
            with respect to two subnetworks.
        """

        return self.nsi_interregional_betweenness(
            sources=node_list1, targets=node_list2)

    def nsi_cross_edge_density(self, node_list1, node_list2):
        """
        Return the n.s.i. density of edges between two subnetworks.

        **Examples:**

        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_cross_edge_density([1,2,3],[0,5])
        0.10909090909090907
        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_cross_edge_density([0],[1,4,5])
        0.78947368421052622

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :return float: the n.s.i. cross density of edges between two
            subnetworks 1 and 2.
        """

        node_weights = self.node_weights

        W_j = sum(node_weights[node_list2])
        mean_degree = self.nsi_cross_mean_degree(node_list1, node_list2)

        return mean_degree / W_j

    def nsi_cross_transitivity(self, node_list1, node_list2):
        """
        Return n.s.i. cross-transitivity for a pair of subnetworks.

        **Examples:**

        >>> r(InteractingNetworks.SmallTestNetwork().\
                nsi_cross_transitivity([1,2],[0,3,4,5]))
        0.6352
        >>> InteractingNetworks.SmallTestNetwork().\
                nsi_cross_transitivity([0,2,3],[1])
        1.0


        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :return float: the n.s.i. cross transitivity for a pair of subnetworks
            1 and 2.
        """

        node_list1 = np.array(node_list1)
        node_list2 = np.array(node_list2)

        A = self.adjacency + np.eye(self.N)
        node_weight = self.node_weights

        N1, N2 = len(node_list1), len(node_list2)

        T = np.zeros(1)

        code = """
        int node_v, node_p, node_q;
        double T_1=0, T_2=0;

        for(int v=0; v<N1; v++) {
            node_v = node_list1(v);

            for(int p=0; p<N2; p++) {
                node_p = node_list2(p);
                if( A(node_v, node_p) == 1) {
                    T_1 = T_1 + node_weight(node_p) *
                            node_weight(node_p) * node_weight(node_v);
                    T_2 = T_2 + node_weight(node_p) *
                            node_weight(node_p) * node_weight(node_v);

                    for(int q=p+1; q<N2; q++) {
                        node_q = node_list2(q);
                        if( A(node_v, node_q) == 1) {
                            T_2 = T_2 + 2 * node_weight(node_v) *
                                    node_weight(node_p) * node_weight(node_q);
                            if ( A(node_p, node_q) == 1) {
                                T_1 = T_1 + 2 * node_weight(node_v) *
                                    node_weight(node_p) * node_weight(node_q);
                            }
                        }
                    }
                }
            }
        }

        T(0) = T_1 / T_2;
        """
        args = ['N1', 'N2', 'A', 'T',
                'node_weight', 'node_list1', 'node_list2']
        weave.inline(code, arg_names=args,
                     type_converters=weave.converters.blitz, compiler='gcc',
                     extra_compile_args=['-O3'])
        return T[0]

    def nsi_cross_average_path_length(self, node_list1, node_list2):
        """
        Return n.s.i. cross average path length between two induced
        subnetworks.

        **Examples:**

        >>> net = InteractingNetworks.SmallTestNetwork()
        >>> r(net.nsi_cross_average_path_length([0,5],[1,2,4]))
        3.3306
        >>> r(net.nsi_cross_average_path_length([1,3,4,5],[2]))
        0.376

        :arg [int] node_list1: list of node indices describing the first
            subnetwork
        :arg [int] node_list2: list of node indices describing the second
            subnetwork
        :return float: the n.s.i. cross-average path length between a pair of
            subnetworks.
        """

        shortest_paths = self.path_lengths()

        nsi_shortest_paths = shortest_paths + np.eye(len(shortest_paths))

        node_weights = self.node_weights

        Wi = sum(node_weights[node_list1])
        Wj = sum(node_weights[node_list1])

        w_v = np.zeros([len(node_list2), len(node_list1)])
        w_v[:] = node_weights[node_list1]

        w_q = np.zeros([len(node_list1), len(node_list2)])
        w_q[:] = node_weights[node_list2]

        Wij = w_v.transpose() + w_q

        nsi_cross_paths = nsi_shortest_paths[node_list1, :][:, node_list2]

        Wij = Wij[np.isinf(nsi_cross_paths)].sum()

        nsi_shortest_paths[np.isinf(nsi_shortest_paths)] = self.N - 1

        nsi_cross_paths = nsi_shortest_paths[node_list1, :][:, node_list2]

        Lij = np.sum(nsi_cross_paths*node_weights[node_list2], axis=1)

        Lij = np.sum(Lij * node_weights[node_list1], axis=0)

        return Lij / (Wi*Wj - Wij)
