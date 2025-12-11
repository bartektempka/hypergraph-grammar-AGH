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

        # collect all vertices present in the graph
        vertices: set[str] = set()
        for edge in hg_edges:
            vertices.update(edge.get_vertices())

        num_vertices = len(vertices)
        num_edges = len(hg_edges)

        # left-hand side of P12: 7 vertices, 8 edges (7 E + 1 T)
        if num_vertices != 7 or num_edges != 8:
            raise ValueError("The graph is not suitable for this production")

        # separate E- and candidate T-edges
        e_edges = [e for e in hg_edges if e.get_type() == EdgeType.E]
        t_edges = [
            e
            for e in hg_edges
            if e.get_type() == EdgeType.T and e.get_parameters().get("R") == 0
        ]

        # we need exactly 7 boundary E-edges and at least one T-edge with R == 0
        if len(e_edges) != 7 or not t_edges:
            return None

        # sanity check: every E-edge must connect exactly two vertices
        for e in e_edges:
            ev = list(e.get_vertices())
            if len(ev) != 2:
                # this production assumes simple boundary edges
                return None

        # check if there exists a 7-cycle going through all vertices
        vertices_list = list(vertices)

        unique_cycles: set[tuple[str, ...]] = set()
        for perm in itertools.permutations(vertices_list):
            # canonical_rotation normalizes the cycle to avoid duplicates
            unique_cycles.add(tuple(canonical_rotation(list(perm))))

        has_7_cycle = False
        for cycle in unique_cycles:
            # _check_cycle verifies that every consecutive pair in cycle
            # (including last->first) is connected by an E-edge
            if self._check_cycle(graph, cycle):
                has_7_cycle = True
                break

        if not has_7_cycle:
            # the boundary does not form a single 7-cycle
            return None

        for t_edge in t_edges:
            t_vertices = set(t_edge.get_vertices())

            # T must be incident with exactly 6 vertices of the 7-cycle
            if len(t_vertices) != 6:
                continue
            if not t_vertices.issubset(vertices):
                continue

            missing = vertices - t_vertices
            # exactly one vertex of the cycle is not connected to T
            if len(missing) != 1:
                continue

            # check refinement criterion (RFC), if any
            if not self._validate_edge(t_edge, graph):
                continue

            new_t_edge = Edge(
                edge_type=EdgeType.T,
                vertices=t_edge.get_vertices(),
                parameters={**t_edge.get_parameters(), "R": 1},
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
