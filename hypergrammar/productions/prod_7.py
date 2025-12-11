from typing import Set, Optional
import copy

from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType

class Prod7:
    """
    Production P7: Marks edges of a pentagonal element for refinement.
    
    LHS: A hyperedge P with 5 vertices and parameter R=1. 
         These 5 vertices must form a pentagon cycle via edges of type E.
    RHS: The R parameter of all boundary E edges is set to 1.
    """
    
    def apply(self, hypergraph: Hypergraph) -> Optional[Hypergraph]:
        # 1. Find candidate P edges
        # We look for type P, 5 vertices, and R=1
        candidate_edges = [
            e for e in hypergraph.get_edges()
            if e.get_type() == EdgeType.P 
            and len(e.get_vertices()) == 5
            and e.get_parameters().get("R") == 1 #R0 = 1
        ]

        for p_edge in candidate_edges:
            vertices = p_edge.get_vertices()
            
            # 2. Check topology: Do these 5 vertices form a pentagon boundary of E edges?
            boundary_edges = self._find_boundary_edges(hypergraph, vertices)
            
            # We need exactly 5 boundary edges forming a cycle
            if len(boundary_edges) == 5 and self._is_cycle(vertices, boundary_edges):
                return self._apply_transformation(hypergraph, p_edge, boundary_edges)

        return None

    def _find_boundary_edges(self, hypergraph: Hypergraph, vertices: frozenset[str]) -> Set[Edge]:
        """Finds all E-type edges that connect exactly 2 vertices within the given set."""
        found_edges = set()
        for edge in hypergraph.get_edges():
            if (edge.get_type() == EdgeType.E 
                and edge.get_vertices().issubset(vertices) 
                and len(edge.get_vertices()) == 2):
                found_edges.add(edge)
        return found_edges

    def _is_cycle(self, vertices: frozenset[str], edges: Set[Edge]) -> bool:
        # 1. Build an adjacency list for just these vertices
        adj = {v: set() for v in vertices}
        for edge in edges:
            # verifying edge is strictly inside the set of vertices we care about
            if not edge.get_vertices().issubset(vertices): continue
            
            v_list = list(edge.get_vertices())
            v1, v2 = v_list[0], v_list[1]
            adj[v1].add(v2)
            adj[v2].add(v1)

        # 2. Check Degree Condition: In a simple cycle, every node has exactly 2 neighbors
        for v in vertices:
            if len(adj[v]) != 2:
                return False

        # 3. Check Connectivity: traverse from one node to ensure we visit all others
        start_node = next(iter(vertices))
        visited = set()
        stack = [start_node]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                stack.extend(adj[node] - visited)
        
        # If we visited every node, it's a single connected cycle
        return len(visited) == len(vertices)

    def _apply_transformation(self, 
                            original_hg: Hypergraph, 
                            p_edge_match: Edge, 
                            boundary_edges: Set[Edge]) -> Hypergraph:
        """Constructs the new hypergraph with updated R parameters."""
        new_hg = Hypergraph(rfc=original_hg.get_rfc())
        
        # Copy node parameters
        # (Assuming we can iterate keys or just copy known vertices from edges)
        # Since Hypergraph stores params in a dict, we can try to copy them if accessible, 
        # or re-set them based on vertices in edges. 
        # Accessing private _node_parameters directly for deep copy simulation:
        # pylint: disable=protected-access
        new_hg._node_parameters = copy.deepcopy(original_hg._node_parameters)

        # Process edges
        for edge in original_hg.get_edges():
            if edge in boundary_edges:
                # This is a boundary E edge: Create new edge with R=1
                new_params = edge.get_parameters().copy()
                new_params["R"] = 1
                new_edge = Edge(edge.get_type(), edge.get_vertices(), new_params)
                new_hg.add_edge(new_edge)
            else:
                # Keep other edges (including the P edge) as is
                new_hg.add_edge(edge)
                
        return new_hg