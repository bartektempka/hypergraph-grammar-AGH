import itertools
from typing import Optional, List

from hypergrammar.productions.i_prod import IProd
from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.utils import canonical_rotation
from hypergrammar.rfc import RFC


class Prod6(IProd):
    def __init__(self, rfc: Optional[RFC] = None):
        self._rfc = rfc
        super().__init__()

    def apply(self, graph: Hypergraph) -> Hypergraph | None:
        hg_edges = graph.get_edges()

        # Find evry Q edge with R=0
        p_edges: List[Edge] = []
        for edge in hg_edges:
            # TODO: Do not know if (R != 1) check is neccessary
            if edge.get_type() == EdgeType.P and edge.get_parameters().get("R") != 1:
                p_edges.append(edge)

        if not p_edges:
            return None

        for q_edge in p_edges:

            q_edge_vertices = q_edge.get_vertices()
            if len(q_edge_vertices) != 5:
                raise ValueError(
                    f"Q edge must connect exactly 5 vertices, but got {len(q_edge_vertices)}"
                )

            unique_cycles = set()
            for perm in itertools.permutations(q_edge_vertices):
                unique_cycles.add(canonical_rotation(list(perm)))

            cycle_matches = False
            for unique_cycle in unique_cycles:
                cycle_matches = self._check_cycle(graph, unique_cycle)
                if cycle_matches:
                    break

            if not cycle_matches:
                continue

            # # valid edge found -> check refinement criterion (rfc)
            if not self._validate_edge(q_edge, graph):
                continue

            q_edge.set_parameter("R", 1)
            return graph

        return None

    def _check_cycle(self, graph: Hypergraph, cycle: tuple[str, ...]) -> bool:

        for i in range(len(cycle)):
            v1 = list(cycle)[i]
            v2 = list(cycle)[(i + 1) % len(cycle)]
            edges_match = self._e_edges_match(graph, frozenset([v1, v2]))
            if not edges_match:
                return False
        return True

    def _e_edges_match(self, graph: Hypergraph, edges_vertices: frozenset[str]) -> bool:
        for edge in graph.get_edges():
            if edge.get_type() == EdgeType.E and edge.get_vertices() == edges_vertices:
                return True
        return False

    def _validate_edge(self, q_edge: Edge, graph: Hypergraph) -> bool:
        if self._rfc is not None:
            return self._rfc.is_valid(q_edge, graph)

        res = graph.edge_rfc_is_valid(q_edge)

        # no rfc was found
        if res is None:
            return True

        return res
