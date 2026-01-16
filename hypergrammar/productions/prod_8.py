import itertools
from typing import Optional, Tuple

from hypergrammar.edge import Edge, EdgeType
from hypergrammar.hypergraph import Hypergraph
from hypergrammar.productions.i_prod import IProd
from hypergrammar.rfc import RFC
from hypergrammar.utils import generate_vertex_name


class Prod8(IProd):
    def __init__(self, rfc: Optional[RFC] = None):
        self._rfc = rfc
        super().__init__()

    def apply(self, graph: Hypergraph) -> Hypergraph | None:
        p_edges = [
            e for e in graph.get_edges()
            if e.get_type() == EdgeType.P and e.get_parameters().get("R") == 1
        ]

        for p_edge in p_edges:
            vertices = list(p_edge.get_vertices())
            if len(vertices) != 5:
                continue

            if not self._validate_edge(p_edge, graph):
                continue

            valid_perm = None
            midpoints_map = {}

            for perm in itertools.permutations(vertices):
                midpoints = []
                is_broken_cycle = True

                for i in range(5):
                    v_start = perm[i]
                    v_end = perm[(i + 1) % 5]

                    midpoint = self._find_broken_edge_midpoint(graph, v_start, v_end)
                    if midpoint is None:
                        is_broken_cycle = False
                        break
                    midpoints.append(midpoint)

                if is_broken_cycle:
                    valid_perm = perm
                    midpoints_map = {
                        i: midpoints[i] for i in range(5)
                    }
                    break

            if valid_perm is None:
                continue

            new_center_v = generate_vertex_name()
            self._calculate_center_coords(graph, valid_perm, new_center_v)

            new_graph = graph
            new_graph.remove_edge(p_edge)

            for i in range(5):
                v_curr = valid_perm[i]

                m_next = midpoints_map[i]
                m_prev = midpoints_map[(i - 1) % 5]

                spoke_edge = Edge(
                    edge_type=EdgeType.E,
                    vertices=frozenset({new_center_v, m_next}),
                    parameters={"B": 0}
                )

                if not self._edge_exists(new_graph, spoke_edge):
                    new_graph.add_edge(spoke_edge)

                q_vertices = frozenset({v_curr, m_next, new_center_v, m_prev})
                new_q_edge = Edge(
                    edge_type=EdgeType.Q,
                    vertices=q_vertices,
                    parameters={"R": 0}
                )
                new_graph.add_edge(new_q_edge)

            return new_graph

        return None

    def _validate_edge(self, edge: Edge, graph: Hypergraph) -> bool:
        if self._rfc is not None:
            return self._rfc.is_valid(edge, graph)

        res = graph.edge_rfc_is_valid(edge)

        if res is None:
            return True

        return res

    def _find_broken_edge_midpoint(self, graph: Hypergraph, v1: str, v2: str) -> Optional[str]:
        v1_neighbors = set()
        v2_neighbors = set()

        for edge in graph.get_edges():
            if edge.get_type() == EdgeType.E:
                ev = list(edge.get_vertices())
                if len(ev) == 2:
                    if v1 in ev:
                        v1_neighbors.add(ev[0] if ev[1] == v1 else ev[1])
                    if v2 in ev:
                        v2_neighbors.add(ev[0] if ev[1] == v2 else ev[1])

        common = v1_neighbors.intersection(v2_neighbors)

        if not common:
            return None

        return list(common)[0]

    def _calculate_center_coords(self, graph: Hypergraph, vertices: Tuple[str, ...], new_v: str):
        sum_x = 0.0
        sum_y = 0.0

        for v in vertices:
            params = graph.get_vertex_parameters(v)
            sum_x += params.get("x", 0.0)
            sum_y += params.get("y", 0.0)

        count = len(vertices)
        graph.set_vertex_parameter(new_v, {"x": sum_x / count, "y": sum_y / count})

    def _edge_exists(self, graph: Hypergraph, target_edge: Edge) -> bool:
        for edge in graph.get_edges():
            if (edge.get_type() == target_edge.get_type() and
                    edge.get_vertices() == target_edge.get_vertices()):
                return True
        return False