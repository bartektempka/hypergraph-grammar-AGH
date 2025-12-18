from typing import Any, Mapping, Optional
import matplotlib.pyplot as plt

import os
import sys

proj_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(str(proj_root))

from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_0 import Prod0
from hypergrammar.rfc import RFC


class InteractiveRFC:
    def __init__(self, target_edge: Optional[str] = None):
        self.target_edge = target_edge

    def is_valid(
        self,
        edge: Edge,
        hypergraph: Hypergraph,
        meta: Optional[Mapping[str, Any]] = None,
    ) -> bool:
        if self.target_edge is None:
            return True
        return edge == self.target_edge

    def set_target_edge(self, edge: Optional[str]) -> None:
        self.target_edge = edge


def create_initial_graph() -> Hypergraph:
    """Create the initial hypergraph with a complex structure."""
    hg = Hypergraph()

    # First quadrilateral
    hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
    hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
    hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
    hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))
    hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 1}))

    # Second quadrilateral
    hg.add_edge(Edge(EdgeType.E, frozenset({"C", "E"})))
    hg.add_edge(Edge(EdgeType.E, frozenset({"D", "F"})))
    hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
    hg.add_edge(Edge(EdgeType.Q, frozenset({"C", "D", "E", "F"}), {"R": 0}))

    # Third quadrilateral
    hg.add_edge(Edge(EdgeType.E, frozenset({"B", "G"})))
    hg.add_edge(Edge(EdgeType.E, frozenset({"C", "H"})))
    hg.add_edge(Edge(EdgeType.E, frozenset({"G", "H"})))
    hg.add_edge(Edge(EdgeType.Q, frozenset({"B", "C", "G", "H"}), {"R": 0}))

    # Fourth quadrilateral (with R=0 for potential refinement)
    hg.add_edge(Edge(EdgeType.E, frozenset({"I", "E"})))
    hg.add_edge(Edge(EdgeType.E, frozenset({"I", "H"})))
    hg.add_edge(Edge(EdgeType.Q, frozenset({"H", "C", "I", "E"}), {"R": 0}))

    # Set vertex positions
    hg.set_vertex_parameter("A", {"x": 0, "y": 0})
    hg.set_vertex_parameter("B", {"x": 0.5, "y": 0})
    hg.set_vertex_parameter("C", {"x": 0.5, "y": 0.5})
    hg.set_vertex_parameter("D", {"x": 0, "y": 0.5})
    hg.set_vertex_parameter("E", {"x": 0.5, "y": 1})
    hg.set_vertex_parameter("F", {"x": 0, "y": 1})
    hg.set_vertex_parameter("G", {"x": 1, "y": 0})
    hg.set_vertex_parameter("H", {"x": 1, "y": 0.5})
    hg.set_vertex_parameter("I", {"x": 1, "y": 1})

    return hg


def print_q_edges(hg: Hypergraph) -> None:
    print("\nAvailable Q edges for refinement (R=0):")
    print("-" * 50)
    q_edges_r0 = [
        e for e in hg.get_edges() if e.get_type() == EdgeType.Q and e.get_parameters().get("R") == 0
    ]
    for i, edge in enumerate(q_edges_r0):
        params = edge.get_parameters()
        vertices = edge.get_vertices()
        print(
            f"  [{i}] Vertices: {vertices}, R={params.get('R', 0)}"
        )
    print("-" * 50)
    return q_edges_r0


def main() -> None:

    hg = create_initial_graph()
    rfc = InteractiveRFC()
    prod0 = Prod0(rfc=rfc)

    hg.draw(use_positional_parameters=True)
    plt.show()

    while True:
        print(f"\n-------------")

        # Show available Q edges
        q_edges_r0 = print_q_edges(hg)

        if not q_edges_r0:
            print("No Q edges with R=0 available for refinement. Exiting.")
            break

        # Get user input
        try:
            edge_index = int(
                input(
                    f"\nSelect edge index to refine (0-{len(q_edges_r0) - 1}) or -1 to exit: "
                )
            )
            if edge_index == -1:
                print("Exiting...")
                break

            if edge_index < 0 or edge_index >= len(q_edges_r0):
                print("Invalid index. Please try again.")
                continue

            # Set RFC to target the selected edge
            target_edge = q_edges_r0[edge_index]
            rfc.set_target_edge(target_edge)

            # Apply Production 0 with the RFC
            new_hg = prod0.apply(hg)

            if new_hg:
                hg = new_hg
                hg.draw(use_positional_parameters=True)
                plt.show()
            else:
                print(f"Production 0 could not be applied to edge {edge_index}")
                print("Exiting...")
                break

        except ValueError:
            print("Invalid input. Please enter a valid integer.")
            continue


if __name__ == "__main__":
    main()
