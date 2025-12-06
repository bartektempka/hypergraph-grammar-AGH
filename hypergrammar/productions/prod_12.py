import itertools
from typing import Optional

from hypergrammar.productions.i_prod import IProd
from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.utils import canonical_rotation
from hypergrammar.rfc import RFC


class Prod12(IProd):

    def __init__(self, rfc: Optional[RFC] = None):
        self._rfc = rfc
        super().__init__()

    def apply(self, graph: Hypergraph) -> Hypergraph | None:
        hg_edges = graph.get_edges()

        # Find every T edge with R=0
        t_edges = []
        for edge in hg_edges:
            if edge.get_type() == EdgeType.T and edge.get_parameters().get("R") == 0:
                t_edges.append(edge)

        if not t_edges:
            return None

        for t_edge in t_edges:

            t_edge_vertices = t_edge.get_vertices()
            if len(t_edge_vertices) != 7:
                raise ValueError(
                    f"T edge must connect exactly 7 vertices, but got {len(t_edge_vertices)}"
                )

            unique_cycles = set()
            for perm in itertools.permutations(t_edge_vertices):
                unique_cycles.add(canonical_rotation(list(perm)))

            cycle_matches = False
            for unique_cycle in unique_cycles:
                cycle_matches = self._check_cycle(graph, unique_cycle)
                if cycle_matches:
                    break

            if not cycle_matches:
                continue

            # valid edge found -> check refinement criterion (rfc)
            if not self._validate_edge(t_edge, graph):
                continue

            new_t_edge = Edge(
                edge_type=EdgeType.T,
                vertices=t_edge_vertices,
                parameters={"R": 1},
            )

            new_graph = graph

            new_graph.remove_edge(t_edge)
            new_graph.add_edge(new_t_edge)

            return new_graph

        return None

    def _validate_edge(self, t_edge: Edge, graph: Hypergraph) -> bool:
        if self._rfc is not None:
            return self._rfc.is_valid(t_edge, graph)

        res = graph.edge_rfc_is_valid(t_edge)

        # no rfc was found
        if res is None:
            return True

        return res

    def _e_edges_match(self, graph: Hypergraph, edges_vertices: frozenset[str]) -> bool:
        for edge in graph.get_edges():
            if edge.get_type() == EdgeType.E and edge.get_vertices() == edges_vertices:
                return True
        return False

    def _check_cycle(self, graph: Hypergraph, cycle: tuple[str, ...]) -> bool:

        for i in range(len(cycle)):
            v1 = list(cycle)[i]
            v2 = list(cycle)[(i + 1) % len(cycle)]
            edges_match = self._e_edges_match(graph, frozenset([v1, v2]))
            if not edges_match:
                return False
        return True
