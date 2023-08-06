import networkx


class ModelGraph(networkx.Graph):
    def __init__(self, model, data=None, **attr):
        super().__init__(data, **attr)
        self.model = model

        self.represented_ep_node = dict()

        self.__build()

        model.dockings_event += self.__build
        model.elements_event += self.__build

    def set_pos(self, ep, pos):
        if self.has_node(ep):
            self.node[ep]['pos'] = pos.toTuple()

    def __build(self):
        self.clear()

        for elem_id, elem in self.model.elements.items():

            # gather nodes by outgoing docked (e.g. bus/refbus) or the element port itself (endpoints)
            self.represented_ep_node.clear()  # mapping element ep --> represented ep node

            for ep in self.model.elem_ports(elem_id):
                if self.model.dockings_out(ep):
                    self.represented_ep_node[ep] = self.model.dockings_out(ep)[0]  # node = docked element (e.g. bus instead of endpoint)
                else:
                    self.represented_ep_node[ep] = ep
                    self.add_node(ep, pos=self.model.docking_port(ep)['pos'])

            # add edges from first node if there is more than one detected node
            for ep in self.model.elem_ports(elem_id)[1:]:
                node_from = self.represented_ep_node[(elem_id, '0')]
                node_to = self.represented_ep_node[ep]
                self.add_edge(node_from, node_to)