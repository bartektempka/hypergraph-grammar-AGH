from typing import Any, Mapping, Optional
import matplotlib.pyplot as plt
from PIL import Image

import os
import sys
from pathlib import Path
from grupa1_automatycznewyprowadzenie import apply_all_productions_automatically


proj_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(str(proj_root))

from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType


def create_initial_graph() -> Hypergraph:
    """Create the initial hypergraph with the shape from the image."""
    hg = Hypergraph()

    # Define vertices for the 3D-like shape
    # Center
    hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 0}))

    # bottom
    hg.add_edge(Edge(EdgeType.E, frozenset({"A", "E"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"F", "D"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "D", "F", "E"}), {"R": 0}))

    # top
    hg.add_edge(Edge(EdgeType.E, frozenset({"B", "G"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"G", "H"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"H", "C"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.Q, frozenset({"B", "C", "H", "G"}), {"R": 0}))

    # Right
    hg.add_edge(Edge(EdgeType.E, frozenset({"H", "I"}), {"R": 0, "B": 1}))
#     hg.add_edge(Edge(EdgeType.E, frozenset({"I", "J"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"I", "F"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.P, frozenset({"C", "D", "I", "H", "F"}), {"R": 0}))

    # Left
    hg.add_edge(Edge(EdgeType.E, frozenset({"G", "K"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"K", "L"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"L", "E"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.S, frozenset({"A", "B", "K", "L", "G", "E"}), {"R": 0}))

    # center
    hg.set_vertex_parameter("A", {"x": 0, "y": 0})
    hg.set_vertex_parameter("B", {"x": 0, "y": 1})
    hg.set_vertex_parameter("C", {"x": 1, "y": 1})
    hg.set_vertex_parameter("D", {"x": 1, "y": 0})

    # bottom
    hg.set_vertex_parameter("E", {"x": -0.5, "y": -1})
    hg.set_vertex_parameter("F", {"x": 2, "y": -1})

    # top
    hg.set_vertex_parameter("G", {"x": -0.5, "y": 2})
    hg.set_vertex_parameter("H", {"x": 2, "y": 2})

    hg.set_vertex_parameter("I", {"x": 3, "y": 0.5})
#     hg.set_vertex_parameter("J", {"x": 3, "y": 0})
    hg.set_vertex_parameter("K", {"x": -1, "y": 1})
    hg.set_vertex_parameter("L", {"x": -1, "y": 0})

    return hg

def main() -> None:
    outpath = Path("./output")
    if outpath.exists():
        import shutil
        shutil.rmtree(outpath)
    outpath.mkdir(parents=True, exist_ok=True)

    hg = create_initial_graph()

    plt.figure(figsize=(14, 10))
    hg.draw(use_positional_parameters=True)
    plt.savefig("./output/initial_graph.png", dpi=400, bbox_inches='tight')
    plt.close()
    print("Image saved: ./output/initial_graph.png")

    final_hg = apply_all_productions_automatically(
        hg,
        target_vertex="H",
        depth=3,
        save_images=True,
        output_dir="./output"
    )

    plt.figure(figsize=(14, 10))
    final_hg.draw(use_positional_parameters=True)
    plt.savefig("./output/final_graph.png", dpi=400, bbox_inches='tight')
    plt.close()
    plt.figure(figsize=(14, 10))
    final_hg.draw(use_positional_parameters=True, clean=True)
    plt.savefig("./output/final_graph_clean.png", dpi=400, bbox_inches='tight')
    plt.close()
    print("Image saved: ./output/final_graph.png")


if __name__ == "__main__":
    main()