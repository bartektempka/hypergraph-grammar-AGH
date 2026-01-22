import itertools
from typing import Optional

from hypergrammar.productions.i_prod import IProd
from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.utils import canonical_rotation
from hypergrammar.rfc import RFC


class Prod11(IProd):

    def __init__(self, rfc: Optional[RFC] = None):
        self._rfc = rfc
        super().__init__()

    def apply(self, graph: Hypergraph) -> Hypergraph | None:
        hg_edges = graph.get_edges()

        # Find every S edge with R=1
        s_edges = []
        for edge in hg_edges:
            if edge.get_type() == EdgeType.S and edge.get_parameters().get("R") == 1:
                s_edges.append(edge)

        if not s_edges:
            return None

        for s_edge in s_edges:

            s_edge_vertices = s_edge.get_vertices()
            if len(s_edge_vertices) != 6:
                raise ValueError(
                    f"S edge must connect exactly 6 vertices, but got {len(s_edge_vertices)}"
                )

            unique_cycles = set()
            for perm in itertools.permutations(s_edge_vertices):
                unique_cycles.add(canonical_rotation(list(perm)))

            cycle_matches = False
            matching_cycle = None
            for unique_cycle in unique_cycles:
                cycle_matches = self._check_all_edges_broken(graph, unique_cycle)
                if cycle_matches:
                    matching_cycle = unique_cycle
                    break

            if not cycle_matches or matching_cycle is None:
                continue

            # valid edge found -> check refinement criterion (rfc)
            if not self._validate_edge(s_edge, graph):
                continue

            # Break the hexagonal element
            new_graph = self._break_hexagon(graph, s_edge, matching_cycle)

            return new_graph

        return None

    def _validate_edge(self, s_edge: Edge, graph: Hypergraph) -> bool:
        if self._rfc is not None:
            return self._rfc.is_valid(s_edge, graph)

        res = graph.edge_rfc_is_valid(s_edge)

        # no rfc was found
        if res is None:
            return True

        return res

    def _check_all_edges_broken(
        self, graph: Hypergraph, cycle: tuple[str, ...]
    ) -> bool:
        """Check if all edges in the cycle are broken."""
        cycle_vertices = set(cycle)

        for i in range(len(cycle)):
            v1 = cycle[i]
            v2 = cycle[(i + 1) % len(cycle)]

            # Check if edge between v1 and v2 is broken
            if not self._is_edge_broken(graph, v1, v2, cycle_vertices):
                return False

        return True

    def _is_edge_broken(
        self, graph: Hypergraph, v1: str, v2: str, s_vertices: set[str]
    ) -> bool:
        """
        Check if edge between v1 and v2 is broken.
        Edge is broken if there exists a vertex G such that:
        - E edge exists between v1 and G
        - E edge exists between G and v2
        - G is not in s_vertices (not part of the S hyperedge)
        """
        # Get all vertices in the graph
        all_vertices = set()
        for edge in graph.get_edges():
            if edge.get_type() == EdgeType.E:
                all_vertices.update(edge.get_vertices())

        # Check for intermediate vertices
        for intermediate in all_vertices:
            if intermediate in s_vertices:
                # Skip if intermediate is part of S
                continue

            # Check if v1-intermediate-v2 path exists
            has_v1_intermediate = self._e_edge_exists(
                graph, frozenset([v1, intermediate])
            )
            has_intermediate_v2 = self._e_edge_exists(
                graph, frozenset([intermediate, v2])
            )

            if has_v1_intermediate and has_intermediate_v2:
                return True

        return False

    def _e_edge_exists(self, graph: Hypergraph, edge_vertices: frozenset[str]) -> bool:
        """Check if an E edge with given vertices exists."""
        for edge in graph.get_edges():
            if edge.get_type() == EdgeType.E and edge.get_vertices() == edge_vertices:
                return True
        return False

    def _break_hexagon(
        self, graph: Hypergraph, s_edge: Edge, cycle: tuple[str, ...]
    ) -> Hypergraph:
        """
        Break the hexagonal element by:
        1. Removing the old S edge with R=1
        2. Creating a new central vertex from the S hyperedge
        3. Creating E edges from central vertex to all intermediate vertices with B=0
        4. Creating 6 Q hyperedges (quadrilaterals), each with 4 vertices:
           - The central vertex
           - Two adjacent intermediate vertices
           - One vertex from the original hexagon
        """
        # Find all intermediate vertices for each edge in the cycle
        s_vertices = set(cycle)
        intermediates = []

        for i in range(len(cycle)):
            v1 = cycle[i]
            v2 = cycle[(i + 1) % len(cycle)]

            # Find the intermediate vertex
            intermediate = self._find_intermediate_vertex(graph, v1, v2, s_vertices)
            if intermediate:
                intermediates.append(intermediate)
            else:
                # If we can't find an intermediate, the edge is not properly broken
                return graph

        if len(intermediates) != 6:
            # Not all edges are properly broken
            return graph

        new_graph = graph

        # Remove the old S edge
        new_graph.remove_edge(s_edge)

        # Create a new central vertex (the S hyperedge becomes a vertex)
        # Generate a unique name for the central vertex
        central_vertex = self._generate_central_vertex_name(graph)

        # Set position of central vertex as average of 6 original vertices
        self._set_central_vertex_position(new_graph, central_vertex, cycle)

        # Create E edges from central vertex to all intermediate vertices with B=0
        for intermediate in intermediates:
            new_e_edge = Edge(
                edge_type=EdgeType.E,
                vertices=frozenset([central_vertex, intermediate]),
                parameters={"B": 0},
            )
            new_graph.add_edge(new_e_edge)

        # Create 6 Q hyperedges
        for i in range(len(cycle)):
            v_original = cycle[i]
            intermediate1 = intermediates[i]
            intermediate2 = intermediates[(i - 1) % len(cycle)]

            # Create Q hyperedge with 4 vertices
            new_q_edge = Edge(
                edge_type=EdgeType.Q,
                vertices=frozenset([central_vertex, intermediate1, intermediate2, v_original]),
                parameters={"R": 0},
            )
            new_graph.add_edge(new_q_edge)

        return new_graph

    def _generate_central_vertex_name(self, graph: Hypergraph) -> str:
        """Generate a unique name for the central vertex."""
        # Collect all existing vertex names
        existing_vertices = set()
        for edge in graph.get_edges():
            existing_vertices.update(edge.get_vertices())

        # Generate a unique name
        counter = 0
        while True:
            candidate = f"M{counter}"
            if candidate not in existing_vertices:
                return candidate
            counter += 1

    def _set_central_vertex_position(
        self, graph: Hypergraph, central_vertex: str, cycle: tuple[str, ...]
    ) -> None:
        """Set the position of the central vertex as the average of the 6 original vertices."""
        # Check if all original vertices have x and y parameters
        total_x = 0.0
        total_y = 0.0
        count = 0

        for vertex in cycle:
            params = graph.get_vertex_parameters(vertex)
            if "x" in params and "y" in params:
                total_x += params["x"]
                total_y += params["y"]
                count += 1

        # Only set position if all vertices have coordinates
        if count == len(cycle):
            avg_x = total_x / count
            avg_y = total_y / count
            # REMOVED int() casting here:
            graph.set_vertex_parameter(central_vertex, {"x": avg_x, "y": avg_y})

    def _find_intermediate_vertex(
        self, graph: Hypergraph, v1: str, v2: str, s_vertices: set[str]
    ) -> Optional[str]:
        """Find the intermediate vertex between v1 and v2 that's not in s_vertices."""
        all_vertices = set()
        for edge in graph.get_edges():
            if edge.get_type() == EdgeType.E:
                all_vertices.update(edge.get_vertices())

        for intermediate in all_vertices:
            if intermediate in s_vertices:
                continue

            has_v1_intermediate = self._e_edge_exists(
                graph, frozenset([v1, intermediate])
            )
            has_intermediate_v2 = self._e_edge_exists(
                graph, frozenset([intermediate, v2])
            )

            if has_v1_intermediate and has_intermediate_v2:
                return intermediate

        return None
