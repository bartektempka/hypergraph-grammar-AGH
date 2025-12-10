import itertools
from typing import Optional

from hypergrammar.productions.i_prod import IProd
from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.utils import canonical_rotation
from hypergrammar.rfc import RFC

from typing import TypedDict

# Define the structure
class Coordinates(TypedDict):
    x: int
    y: int


class Prod5(IProd):

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
            cycle = []
            for unique_cycle in unique_cycles:
                cycle_matches = self._check_all_edges_broken(graph, unique_cycle)
                if cycle_matches:
                    cycle = unique_cycle
                    break

            if not cycle_matches:
                continue

            all_vertices = []
            middle_vertices = []
            for i in range(len(cycle)):
                v1 = cycle[i]
                v2 = cycle[(i + 1) % len(cycle)]
                all_vertices.append(v1)
                other = self.get_broken_edge_other(graph, v1, v2, set(cycle))
                all_vertices.append(other)
                middle_vertices.append(other)

            new_graph = graph

            print(middle_vertices)

            new_graph.remove_edge(q_edge)
            
            contral_vertex_name = self._generate_central_vertex_name(new_graph)
            print("Central vertex:", contral_vertex_name)
            coords = self._get_central_vertex_position(new_graph, cycle)

            new_graph.set_vertex_parameter(contral_vertex_name, coords)

            for middle_vertex in middle_vertices:
                print("Adding edge:", contral_vertex_name, middle_vertex)
                new_edge = Edge(
                    EdgeType.E,
                    frozenset({middle_vertex, contral_vertex_name}),
                )
                new_graph.add_edge(new_edge)
            
            for i in range(len(cycle)):
                v_original = cycle[i]
                intermediate1 = middle_vertices[i]
                intermediate2 = middle_vertices[(i - 1) % len(cycle)]

                # Create Q hyperedge with 4 vertices
                new_q_edge = Edge(
                    edge_type=EdgeType.Q,
                    vertices=frozenset([contral_vertex_name, intermediate1, intermediate2, v_original]),
                    parameters={"R": 0},
                )
                new_graph.add_edge(new_q_edge)
            
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
    
    def _get_edges(self, graph: Hypergraph, cycle: tuple[str, ...]) -> list[Edge]:

        edges = []
        for i in range(len(cycle)):
            v1 = list(cycle)[i]
            v2 = list(cycle)[(i + 1) % len(cycle)]
            edges.append(self._get_edge(graph, frozenset([v1, v2])))

        return edges

    def _check_all_edges_broken(
        self, graph: Hypergraph, cycle: tuple[str, ...]
    ) -> bool | list[str]:
        """Check if all edges in the cycle are broken."""
        cycle_vertices = set(cycle)

        others = []
        for i in range(len(cycle)):
            v1 = cycle[i]
            v2 = cycle[(i + 1) % len(cycle)]

            # Check if edge between v1 and v2 is broken
            other = self._is_edge_broken(graph, v1, v2, cycle_vertices)
            if not other:
                return False
            others.append(other)

        return others

    def _is_edge_broken(
        self, graph: Hypergraph, v1: str, v2: str, s_vertices: set[str]
    ) -> bool:
        for edge in graph.get_edges():
            vert = edge.get_vertices()
            if edge.get_type() == EdgeType.E and v1 in vert and v2 not in vert:
                other = list(vert - {v1})[0]
                if other in s_vertices:
                    continue
                if self._e_edges_match(graph, frozenset([other, v2])):
                    return True
        return False
    
    def get_broken_edge_other(
        self, graph: Hypergraph, v1: str, v2: str, s_vertices: set[str]
    ) -> Optional[str]:
        for edge in graph.get_edges():
            vert = edge.get_vertices()
            if edge.get_type() == EdgeType.E and v1 in vert and v2 not in vert:
                other = list(vert - {v1})[0]
                if other in s_vertices:
                    continue
                if self._e_edges_match(graph, frozenset([other, v2])):
                    return other
        return None
    
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

    def _get_central_vertex_position(
        self, graph: Hypergraph, cycle: tuple[str, ...]
    ) -> Coordinates | None:
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
            print("Average x:", avg_x)
            print("Average y:", avg_y)
            return {"x": avg_x, "y": avg_y}
        return None