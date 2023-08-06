import networkx as nx
import numpy as np


def init_edge_weights(g):
    edge_datas = []
    edge_lengths = []
    for _, _, edata in g.edges(data=True):
        if not edata['visible']:
            continue
        edge = edata.get('entity')
        if edge and 'length' in edge.static_data:
            edge_datas.append(edata)
            edge_lengths.append(edge.static_data['length'])
        else:
            edge_lengths.append(1)

    # calculate edge weights by length
    edge_length_arr = np.asarray(edge_lengths, 'f')
    edge_weight_arr = 1 / edge_length_arr
    lmin = edge_weight_arr.min()
    lmax = edge_weight_arr.max()
    edge_weight_arr = np.interp(edge_weight_arr, [lmin, lmax], [1, lmax / lmin])
    for i, edata in enumerate(edge_datas):
        edata['weight'] = edge_weight_arr[i]


def init_data(g, nodelist, dim=2, edge_weight=False):
    """ Sets the default positions and visability data
    edge_weight calculation should only be done if a graph already converged
    """
    nodeset = set(nodelist)

    for node, ndata in g.nodes(data=True):
        ndata['visible'] = nvisible = node in nodeset
        if not nvisible:
            continue
        ndata.setdefault('pos', np.random.random(dim))

    for node1, node2, edata in g.edges(data=True):
        edata['visible'] = node1 in nodeset and node2 in nodeset

    if edge_weight:
        init_edge_weights(g)


def init_nodelist(g, nodelist=None):
    if not nodelist:
        nodelist = g.nodes()
    return nodelist


def length_arr(delta, minimum=0, squared=False):
    """ Return the length for each node in delta
    delta = [[x1,x2,x3...],[y1,y2,y3...]
    length_arr = [length1, length2, length3...]

    delta: the numpy (dim,nnodes) array
    minimum: the minimum lengths to return"""
    ret = (delta ** 2).sum(axis=0)

    if squared:
        minimum **= 2
    else:
        ret = np.sqrt(ret)

    if minimum > 0:
        ret[ret < minimum] = float(minimum)
    return ret


class SpeedModel:
    """ see: https://github.com/gephi/gephi/tree/master/modules/LayoutPlugin/src/main/java/org/gephi/layout/plugin/forceAtlas2/ForceAtlas.java"""

    def __init__(self, mass_arr, ratio=0.01, k_s=1, k_s_max=10, max_rise=0.5):
        """ calculator for global and local adaptive speed, depending on the actual and previous force.

        mass_arr: degree(node)+1 for each node
        ratio: squared jitter tolerance
        k_s: local speed factor (set to 0.1 on prevent overlap)
        k_s_max: maximum local speed factor
        max_rise: the maximum rising percentage of global speed (0.5 = 50%)
        """
        self.mass_arr = mass_arr
        self.ratio = ratio
        self.k_s = k_s
        self.k_s_max = k_s_max
        self.max_rise = max_rise
        self.global_speed = 1
        self.prev_force_arr = None

    def get_speed_arr(self, force_arr):
        """Return the local adaptive speed as array for each node.
        Call this once in each iteration after force calculation and before applying forces"""
        if self.prev_force_arr is None:
            self.prev_force_arr = np.zeros(np.shape(force_arr))

        traction_arr = length_arr(force_arr + self.prev_force_arr) / 2
        swinging_arr = length_arr(force_arr - self.prev_force_arr)

        new_global_speed = self.ratio * (self.mass_arr * traction_arr).sum() / (self.mass_arr * swinging_arr).sum()
        self.global_speed = min(new_global_speed, self.global_speed * (1 + self.max_rise))

        speed_arr = self.k_s * self.global_speed / (1 + self.global_speed * np.sqrt(swinging_arr))
        maxspeed = self.k_s_max / length_arr(force_arr)
        speed_arr = np.where(speed_arr > maxspeed, maxspeed, speed_arr)

        self.prev_force_arr = force_arr

        return speed_arr


class ForceAtlas2:
    """ Basic concept taken from: https://github.com/tpoisot/nxfa2 (Timothée Poisot). Completely revised.
    
    A ForceAtlas2-algorithm graph layouter.
    Numpy optimized version with additional options, but no barnes-hut-grid approach.
    """

    def __init__(self, g, nodelist=None, attr_weight=None, attr_size=None, avoidoverlap=False, linlog=False,
                 dissuadehubs=False, scale=2, dim=2, repulsion_factor=150, standard_size=15):
        """ Creates an ForceAtlas2-layouter - repeatingly call *do_layout* afterwards, to apply an iteration
        
        g: the graph to layout
        :type g: nx.Graph

        nodelist: only layout nodes and edges corresponding to nodelist

        attr_weight: the edge weight attribute string. Use 'weight' attribute!

        attr_size: the node size attribute string. Edge lengths should be taken into consideration. Use 'size' attribute!

        avoidoverlap: Whether to avoid overlap of nodes according to node sizes

        linlog: whether to use linear or logarithmic repulsion (more compaction)

        dissuadehubs: Centralize nodes with high indegree (authorities); push nodes with high outdegree (hubs) out.
                      Only apply on a directed graph!

        scale: a multiplicator for the graph size

        dim: the number of dimensions """
        self.g = g
        self.nodelist = init_nodelist(g, nodelist)
        self.nnodes = len(self.nodelist)
        self.attr_weight = attr_weight
        self.attr_size = attr_size
        self.avoidoverlap = avoidoverlap
        self.linlog = linlog
        self.dissuadehubs = dissuadehubs
        self.scale = float(scale)
        self.dim = dim

        self.repulsion_factor = repulsion_factor  # 1
        self.standard_size = standard_size  # 0.5

        # #
        #----------------------------- init layout -----------------------------#
        #                                                                       #
        init_data(self.g, self.nodelist, self.dim)
        init_edge_weights(self.g)

        self.pos_arr = np.asarray([self.g.node[node]['pos'] for node in self.nodelist], dtype='f')

        adjacency_matrix = nx.to_numpy_matrix(self.g, nodelist=self.nodelist, weight=self.attr_weight)
        self.edgeWeight_matrix = np.asarray(adjacency_matrix, 'f')

        # node weighted degrees
        degree_arr = np.asarray(list(self.g.degree(nbunch=self.nodelist, weight=self.attr_weight).values()), 'f')
        self.mass_arr = 1 + degree_arr

        # node sizes
        self.size_arr = np.asarray([self.g.node[node].get(self.attr_size, self.standard_size)
                                    for node in self.nodelist], dtype='f')

        self.speed_model = SpeedModel(self.mass_arr)

    def do_layout(self):
        """ do one layout calculation step. position data is assigned as 'pos' attribute to each node """
        self.pos_arr = np.asarray([self.g.node[node]['pos'] for node in self.nodelist], dtype='f')

        force_arr = np.zeros((self.dim, self.nnodes))

        for n_id in range(self.nnodes):
            # vectors from node position to all others
            delta_arr = (-self.pos_arr[n_id] + self.pos_arr).T  # [[x for each node], [y for each node]...]
            sqr_delta_length_arr = (delta_arr ** 2).sum(axis=0) + float(0.0001)  # avoid division by zero later on

            if self.avoidoverlap:
                delta_length_arr = np.sqrt(sqr_delta_length_arr)
                delta_sizedlength_arr = delta_length_arr - self.size_arr[n_id] - self.size_arr

                # Maximum repulsion area below 0.01 distance (not the original ForceAtlas2 approach)
                delta_sizedlength_arr[delta_sizedlength_arr < 0.01] = float(0.01)

                delta_arr *= delta_sizedlength_arr / delta_length_arr
                sqr_delta_length_arr = delta_sizedlength_arr ** 2

            # displacement "force" [repulsion to each node]
            repulsion_arr = self.repulsion_factor * self.mass_arr[n_id] * self.mass_arr / sqr_delta_length_arr

            attraction_arr = self.edgeWeight_matrix[n_id]

            if self.linlog:
                delta_length_arr = np.sqrt(sqr_delta_length_arr)
                attraction_arr *= np.log(1 + delta_length_arr) / delta_length_arr

            if self.dissuadehubs:
                attraction_arr /= self.mass_arr[n_id]

            # calculate force [x,y] displacement
            force_arr[:, n_id] += (delta_arr * self.scale * (-repulsion_arr + attraction_arr)).sum(axis=1)

        # update adaptive speed
        speed_arr = self.speed_model.get_speed_arr(force_arr)

        # apply force
        self.pos_arr += (force_arr * speed_arr).T
        for i, n in enumerate(self.nodelist):
            self.g.node[n]['pos'] = self.pos_arr[i]  # update Layout