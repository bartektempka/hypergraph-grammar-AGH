import itertools
from typing import Optional

from hypergrammar.productions.i_prod import IProd
from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.utils import canonical_rotation
from hypergrammar.rfc import RFC


class Prod1(IProd):

    def __init__(self, rfc: Optional[RFC] = None):
        self._rfc = rfc
        super().__init__()

    def apply(self, graph: Hypergraph) -> Hypergraph | None:
        hg_edges = graph.get_edges()

        # Find evry Q edge with R=1
        q_edges = []
        for edge in hg_edges:
            if edge.get_type() == EdgeType.Q and edge.get_parameters().get("R") == 1:
                q_edges.append(edge)

        if not q_edges:
            return None

        for q_edge in q_edges:

            q_edge_vertices = q_edge.get_vertices()
            if len(q_edge_vertices) != 4:
                raise ValueError(
                    f"Q edge must connect exactly 4 vertices, but got {len(q_edge_vertices)}"
                )

            unique_cycles = set()
            for perm in itertools.permutations(q_edge_vertices):
                unique_cycles.add(canonical_rotation(list(perm)))

            cycle_matches = False
            cycle = ()
            for unique_cycle in unique_cycles:
                cycle_matches = self._check_cycle(graph, unique_cycle)
                if cycle_matches:
                    cycle = unique_cycle
                    break

            if not cycle_matches:
                continue

            edges = self._get_edges(graph, cycle)
            new_edges = []

            for edge in edges:
                new_edge = Edge(
                    edge_type=EdgeType.E,
                    vertices=edge.get_vertices(),
                    parameters={"R": 1},
                )
                new_edges.append(new_edge)

            new_graph = graph

            for edge in edges:
                new_graph.remove_edge(edge)
            for edge in new_edges:
                new_graph.add_edge(edge)

            return new_graph

        return None

    def _validate_edge(self, q_edge: Edge, graph: Hypergraph) -> bool:
        if self._rfc is not None:
            return self._rfc.is_valid(q_edge, graph)

        res = graph.edge_rfc_is_valid(q_edge)

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
    
    def _get_edge(self, graph: Hypergraph, edges_vertices: frozenset[str]) -> Edge | None:
        for edge in graph.get_edges():
            if edge.get_type() == EdgeType.E and edge.get_vertices() == edges_vertices:
                return edge
        return None
    
    def _get_edges(self, graph: Hypergraph, cycle: tuple[str, ...]) -> bool:

        edges = []
        for i in range(len(cycle)):
            v1 = list(cycle)[i]
            v2 = list(cycle)[(i + 1) % len(cycle)]
            edges.append(self._get_edge(graph, frozenset([v1, v2])))

        return edges
