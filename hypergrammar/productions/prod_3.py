import uuid
from hypergrammar.productions.i_prod import IProd
from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.rfc import RFC
from typing import Optional


class Prod3(IProd):

    def __init__(self, rfc: Optional[RFC] = None):
        self._rfc = rfc
        super().__init__()

    def apply(self, graph: Hypergraph) -> Hypergraph | None:
        # Look for nonboundary (B=0) edge E with R=1
        target_edge = None
        for edge in graph.get_edges():
            if edge.get_type() == EdgeType.E and edge.get_parameters().get("R") == 1 and edge.get_parameters().get("B") == 0:
                target_edge = edge
                break

        if target_edge is None:
            return None

        vertices = list(target_edge.get_vertices())
        if len(vertices) != 2:
            return None

        v_a_id, v_b_id = vertices[0], vertices[1]

        # Get coordinates of two vertices
        param_a = graph.get_vertex_parameters(v_a_id)
        param_b = graph.get_vertex_parameters(v_b_id)

        if "x" not in param_a or "y" not in param_a or "x" not in param_b or "y" not in param_b:
            return None
        
        x1, y1 = param_a.get("x", 0), param_a.get("y", 0)
        x2, y2 = param_b.get("x", 0), param_b.get("y", 0)

        # Create new vertex between initial ones
        new_c_id = f"v_{uuid.uuid4().hex[:6]}"
        new_c_params = {
            "x": (x1 + x2) / 2.0,
            "y": (y1 + y2) / 2.0
        }
        graph.set_vertex_parameter(new_c_id, new_c_params)

        # Prepare params for new edges, copy 'B' value, set R=0
        old_params = target_edge.get_parameters().copy()
        new_params = old_params.copy()
        new_params["R"] = 0
        
        # Create new edges with params
        edge_ac = Edge(EdgeType.E, frozenset([v_a_id, new_c_id]), new_params)
        edge_cb = Edge(EdgeType.E, frozenset([new_c_id, v_b_id]), new_params)
        edge_ab = Edge(EdgeType.E, frozenset([v_a_id, v_b_id]), new_params) # Triangle base

        # Remove old edge from graph and add 3 edges from previous step
        graph.remove_edge(target_edge)
        graph.add_edge(edge_ac)
        graph.add_edge(edge_cb)
        graph.add_edge(edge_ab)

        return graph