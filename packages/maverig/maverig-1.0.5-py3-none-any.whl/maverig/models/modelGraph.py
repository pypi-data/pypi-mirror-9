import networkx


class ModelGraph(networkx.Graph):
    """A ``networkx.Graph`` representation of the
    *model element ports* as *nodes* and element internal lines between them as *edges*.

    This graph can be used for layout optimization algorithms.

    Example connection scenario::

        ('House', '0') --- ('House', '1') -> ('PQBus_1', '0')

        ('PQBus_1', '0') <- ('Branch', '0') --- ('Branch', '1') -> ('PQBus_2', '0')


    Where ``---`` are lines and ``<-``, ``->`` are dockings.

    This scenario would be represented in ``ModelGraph`` as follows::

        ('House', '0') --- ('PQBus_1', '0') --- ('PQBus_2', '0'))

    Where ``---`` are edges and the element ports are nodes.

    Ports with outgoing dockings (endpoints in view) get represented by their docked Port as Node, because they
    share the same position."""

    def __init__(self, model, data=None, **attr):
        super().__init__(data, **attr)
        self.model = model

        self.represented_ep_node = dict()

        self.__build()

        model.dockings_event += self.__build
        model.elements_event += self.__build

    def set_pos(self, ep, pos):
        """Change the position of an ``ElemPort`` node to pos (``PySide.QtCore.QPointF``).
        This method gets called by model when a position is set there."""
        if self.has_node(ep):
            self.node[ep]['pos'] = pos.toTuple()

    def __build(self):
        """Builds the ``networkx.Graph`` with element ports as nodes and the connections between them as edges.
        """
        self.clear()

        for elem_id, elem in self.model.elements.items():

            # gather nodes by outgoing docked (e.g. bus/refbus) or the element port itself (endpoints)
            self.represented_ep_node.clear()  # mapping element ep --> represented ep node

            for ep in self.model.elem_ports(elem_id):
                if self.model.dockings_out(ep):
                    # node = docked element (e.g. bus instead of endpoint)
                    self.represented_ep_node[ep] = self.model.dockings_out(ep)[0]
                else:
                    self.represented_ep_node[ep] = ep
                    self.add_node(ep, pos=self.model.docking_port(ep)['pos'])

            # add edges from first node if there is more than one detected node
            for ep in self.model.elem_ports(elem_id)[1:]:
                node_from = self.represented_ep_node[(elem_id, '0')]
                node_to = self.represented_ep_node[ep]
                self.add_edge(node_from, node_to)