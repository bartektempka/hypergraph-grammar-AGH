from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.rfc import RFC
from typing import Optional


class Prod9:
    def __init__(self, rfc: Optional[RFC] = None):
        self._rfc = rfc

    def apply(self, graph: Hypergraph) -> Optional[Hypergraph]:
        candidates = [
            e for e in graph.get_edges()
            if e.get_type() == EdgeType.S and e.get_parameters().get("R", 0) == 0
        ]

        for edge in candidates:
            if len(edge.get_vertices()) != 6:
                continue

            if not self._validate_edge(edge, graph):
                continue

            new_params = edge.get_parameters().copy()
            new_params["R"] = 1
            new_edge = Edge(EdgeType.S, edge.get_vertices(), new_params)

            graph.remove_edge(edge)
            graph.add_edge(new_edge)
            return graph

        return None

    def _validate_edge(self, q_edge: Edge, graph: Hypergraph) -> bool:
        if self._rfc is not None:
            return self._rfc.is_valid(q_edge, graph)

        res = graph.edge_rfc_is_valid(q_edge)

        if res is None:
            return True

        return res
