import itertools
from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from typing import Optional


class Prod10:

    def apply(self, graph: Hypergraph) -> Optional[Hypergraph]:
        q_edges = [
            e for e in graph.get_edges()
            if e.get_type() == EdgeType.Q and e.get_parameters().get("R") == 1
        ]

        for q_edge in q_edges:
            vertices = list(q_edge.get_vertices())
            if len(vertices) != 6:
                continue

            valid_cycle = None

            for perm in itertools.permutations(vertices):
                if self._check_cycle(graph, perm):
                    valid_cycle = perm
                    break
            
            if valid_cycle is None:
                continue

            boundary_edges = self._get_edges_from_cycle(graph, valid_cycle)

            if all(e.get_parameters().get("R") == 1 for e in boundary_edges):
                continue

            for edge in boundary_edges:
                if edge.get_parameters().get("R", 0) == 0:
                    new_params = edge.get_parameters().copy()
                    new_params["R"] = 1
                    new_e = Edge(EdgeType.E, edge.get_vertices(), new_params)
                    
                    graph.remove_edge(edge)
                    graph.add_edge(new_e)

            return graph

        return None

    def _e_edges_match(self, graph: Hypergraph, edges_vertices: frozenset[str]) -> bool:
        for edge in graph.get_edges():
            if edge.get_type() == EdgeType.E and edge.get_vertices() == edges_vertices:
                return True
        return False

    def _check_cycle(self, graph: Hypergraph, cycle: tuple[str, ...]) -> bool:
        for i in range(len(cycle)):
            v1 = cycle[i]
            v2 = cycle[(i + 1) % len(cycle)]
            if not self._e_edges_match(graph, frozenset([v1, v2])):
                return False
        return True

    def _get_edges_from_cycle(self, graph: Hypergraph, cycle: tuple[str, ...]) -> list[Edge]:
        found_edges = []
        for i in range(len(cycle)):
            v1 = cycle[i]
            v2 = cycle[(i + 1) % len(cycle)]
            target = frozenset([v1, v2])
            
            for edge in graph.get_edges():
                if edge.get_type() == EdgeType.E and edge.get_vertices() == target:
                    found_edges.append(edge)
                    break
        return found_edges
