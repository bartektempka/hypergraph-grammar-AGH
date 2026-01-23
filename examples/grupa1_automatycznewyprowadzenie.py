from typing import Any, Mapping, Optional
import matplotlib.pyplot as plt
from PIL import Image

import os
import sys
from pathlib import Path
import tempfile

proj_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(str(proj_root))

##########################################################################
# Disclaimer: produkcja 2 nie działa czasem a 11 źle liczy parametry x i y
##########################################################################

from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_0 import Prod0
from hypergrammar.productions.prod_1 import Prod1
from hypergrammar.productions.prod_2 import Prod2
from hypergrammar.productions.prod_3 import Prod3
from hypergrammar.productions.prod_4 import Prod4
from hypergrammar.productions.prod_5 import Prod5
from hypergrammar.productions.prod_6 import Prod6
from hypergrammar.productions.prod_7 import Prod7
from hypergrammar.productions.prod_8 import Prod8
from hypergrammar.productions.prod_9 import Prod9
from hypergrammar.productions.prod_10 import Prod10
from hypergrammar.productions.prod_11 import Prod11
from hypergrammar.productions.prod_12 import Prod12
from hypergrammar.rfc import RFC


class VertexBasedRFC:
    """RFC that filters edges based on a target vertex."""

    def __init__(self, target_vertex: Optional[str] = None):
        self.target_vertex = target_vertex

    def is_valid(
        self,
        edge: Edge,
        hypergraph: Hypergraph,
        meta: Optional[Mapping[str, Any]] = None,
    ) -> bool:
        assert(self.target_vertex is not None)
        # Check if the edge contains the target vertex
        return self.target_vertex in edge.get_vertices()

    def set_target_vertex(self, vertex: Optional[str]) -> None:
        self.target_vertex = vertex


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
    hg.add_edge(Edge(EdgeType.E, frozenset({"I", "J"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"J", "F"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.S, frozenset({"C", "D", "I", "J", "H", "F"}), {"R": 0}))

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
    
    hg.set_vertex_parameter("I", {"x": 3, "y": 1})
    hg.set_vertex_parameter("J", {"x": 3, "y": 0})
    hg.set_vertex_parameter("K", {"x": -1, "y": 1})
    hg.set_vertex_parameter("L", {"x": -1, "y": 0})

    return hg


def apply_all_productions_automatically(
    hg: Hypergraph,
    target_vertex: Optional[str] = None,
    depth: int = 2,
    save_images: bool = True,
    output_dir: str = "./output"
) -> Hypergraph:
    rfc = VertexBasedRFC(target_vertex=target_vertex)
    
    refining_productions = [
        Prod0(rfc=rfc),
        Prod6(rfc=rfc),
        Prod9(rfc=rfc),
        Prod12(rfc=rfc)
    ]
    
    modifying_productions = [
        Prod1(),
        Prod2(),
        Prod3(),
        Prod4(),
        Prod5(),
        Prod7(),
        Prod8(),
        Prod10(),
        Prod11(),
    ]
    
    # Temporary directory for storing frames for GIF
    temp_dir = "output"
    frame_list = []
    if save_images:
        # temp_dir = tempfile.mkdtemp()
        ...

    image_id = 0
    big_iteration = 0
    
    # Main loop: repeatedly apply refinement then modification phases
    while big_iteration < depth:
        big_iteration += 1
        print(f"\n=== Big Iteration {big_iteration} ===")
        
        # Phase 1: Apply all refining productions
        print("\n--- Phase 1: Applying Refining Productions ---")
        phase1_any_applied = False
        while True:
            any_applied = False
            
            for prod in refining_productions:
                new_hg = prod.apply(hg)
                if new_hg:
                    image_id += 1
                    prod_name = prod.__class__.__name__
                    print(f"✓ {prod_name} applied successfully")
                    hg = new_hg
                    any_applied = True
                    phase1_any_applied = True

                    if save_images and temp_dir:
                        plt.figure(figsize=(14, 10))
                        plt.suptitle(f"Production: {prod_name}", fontsize=16, fontweight='bold')
                        hg.draw(use_positional_parameters=True)
                        frame_path = os.path.join(temp_dir, f"frame_{image_id:03d}.png")
                        plt.savefig(frame_path, dpi=400, bbox_inches='tight')
                        plt.close()
                        frame_list.append(frame_path)
                    break
            
            if not any_applied:
                print("No more refining productions can be applied.")
                break
        
        # Phase 2: Apply all modifying productions
        print("\n--- Phase 2: Applying Modifying Productions ---")
        phase2_any_applied = False
        while True:
            any_applied = False
            
            for prod in modifying_productions:
                new_hg = prod.apply(hg)
                if new_hg:
                    image_id += 1
                    prod_name = prod.__class__.__name__
                    print(f"✓ {prod_name} applied successfully")
                    hg = new_hg
                    any_applied = True
                    phase2_any_applied = True

                    if save_images and temp_dir:
                        plt.figure(figsize=(14, 10))
                        plt.suptitle(f"Production: {prod_name}", fontsize=16, fontweight='bold')
                        hg.draw(use_positional_parameters=True)
                        frame_path = os.path.join(temp_dir, f"frame_{image_id:03d}.png")
                        plt.savefig(frame_path, dpi=400, bbox_inches='tight')
                        plt.close()
                        frame_list.append(frame_path)
                    break
            
            if not any_applied:
                print("No more modifying productions can be applied.")
                break
        
        # Check if we should continue or stop
        if not phase1_any_applied and not phase2_any_applied:
            print(f"\nBoth phases completed without changes. Stopping.")
            break

    print(f"\nTotal iterations: {image_id}")
    print(f"Total big iterations: {big_iteration}")

    # Create GIF from frames
    if save_images and frame_list:
        try:
            frames = [Image.open(frame_path) for frame_path in frame_list]
            gif_path = os.path.join(output_dir, "animation.gif")
            frames[0].save(
                gif_path,
                save_all=True,
                append_images=frames[1:],
                duration=500,
                loop=0
            )
            print(f"GIF saved: {gif_path}")
            
            # Clean up temporary frames
            import shutil
            # shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error creating GIF: {e}")

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
