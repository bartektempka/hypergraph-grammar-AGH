import itertools
from typing import Optional

from hypergrammar.productions.i_prod import IProd
from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.utils import canonical_rotation, generate_vertex_name
from hypergrammar.rfc import RFC
from copy import deepcopy


class Prod4(IProd):

    def __init__(self, rfc: Optional[RFC] = None):
        self._rfc = rfc
        super().__init__()

    def apply(self, graph: Hypergraph) -> Hypergraph | None:
        hg_edges = graph.get_edges()
        # Find evry Q edge with R=0
        e_edges = []
        for edge in hg_edges:
            if edge.get_type() == EdgeType.E and "R" in edge.parameters and edge.parameters["R"] == 1 and "B" in edge.parameters and edge.parameters["B"] == 1:
                e_edges.append(edge)

        if not e_edges:
            return None

        for e_edge in e_edges:

            e_edge_vertices = e_edge.get_vertices()
            if len(e_edge_vertices) != 2:
                raise ValueError(
                    f"E edge must connect exactly 2 vertices, but got {len(e_edge_vertices)}"
                )

            # valid edge found -> check refinement criterion (rfc)
            if not self._validate_edge(e_edge, graph):
                continue
            
            new_v = self.get_new_vert(graph)
            vvv = []
            for i in e_edge_vertices:
                vvv.append(i)
            for v in e_edge_vertices:
                v1 = graph.get_vertex_parameters(vvv[0])
                v2 = graph.get_vertex_parameters(vvv[1])
            
            
            graph.set_vertex_parameter(new_v, {"x": (v1["x"] + v2["x"])/2 , "y":  (v1["y"] + v2["y"])/2})
            new_edges = [ ]
            
            for v in e_edge_vertices:
                new_e_edge = Edge(
                    edge_type=EdgeType.E,
                    vertices=frozenset({v, new_v}),
                    parameters=deepcopy(e_edge.get_parameters()),
                )
                new_e_edge.get_parameters()["R"] = 0
                new_edges.append(new_e_edge)
            
            

            new_graph = graph

            new_graph.remove_edge(e_edge)
            
            for e in new_edges:
                new_graph.add_edge(e)
                

            return new_graph

        return None

    def _validate_edge(self, e_edge: Edge, graph: Hypergraph) -> bool:
        if self._rfc is not None:
            return self._rfc.is_valid(e_edge, graph)

        res = graph.edge_rfc_is_valid(e_edge)

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

    def get_new_vert(self, graph: Hypergraph):
        return generate_vertex_name()