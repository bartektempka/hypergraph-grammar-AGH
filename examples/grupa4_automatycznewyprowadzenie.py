from typing import Any, Mapping, Optional
import matplotlib.pyplot as plt
from PIL import Image
import math

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


class PointBasedRFC:
    """
    RFC that filters edges based on proximity to a target (x, y) point.
    """

    def __init__(self, target_point: Optional[tuple[float, float]] = None, radius: float = 0.6):
        self.target_point = target_point
        self.radius = radius

    def is_valid(
        self,
        edge: Edge,
        hypergraph: Hypergraph,
        meta: Optional[Mapping[str, Any]] = None,
    ) -> bool:
        if self.target_point is None:
            return False

        tx, ty = self.target_point
        vertices = edge.get_vertices()
        if not vertices:
            return False

        # Calculate approximate center of the edge
        sum_x, sum_y, count = 0.0, 0.0, 0
        for v in vertices:
            params = hypergraph.get_vertex_parameters(v)
            if params:
                sum_x += params.get("x", 0.0)
                sum_y += params.get("y", 0.0)
                count += 1
        
        if count == 0:
            return False
            
        avg_x = sum_x / count
        avg_y = sum_y / count
        
        # Check distance from edge center to target point
        dist = math.sqrt((avg_x - tx)**2 + (avg_y - ty)**2)
        
        return dist <= self.radius

    def set_target_point(self, point: tuple[float, float]) -> None:
        self.target_point = point


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


def apply_step(
    hg: Hypergraph,
    rfc: PointBasedRFC,
    target_point: tuple[float, float],
    step_name: str,
    temp_dir: str,
    frame_list: list,
    image_counter: list
) -> Hypergraph:
    """Helper to apply one 'logical step' of refinement at a specific point."""
    print(f"\n=== Starting Step: {step_name} at {target_point} ===")
    
    # Update the RFC target
    rfc.set_target_point(target_point)
    
    # Productions
    refining_productions = [Prod0(rfc=rfc), Prod6(rfc=rfc), Prod9(rfc=rfc), Prod12(rfc=rfc)]
    modifying_productions = [Prod1(), Prod2(), Prod3(), Prod4(), Prod5(), Prod7(), Prod8(), Prod10(), Prod11()]

    # Phase 1: Refining
    print("--- Phase 1: Refining ---")
    while True:
        applied = False
        for prod in refining_productions:
            new_hg = prod.apply(hg)
            if new_hg:
                image_counter[0] += 1
                print(f"✓ {prod.__class__.__name__} applied")
                hg = new_hg
                applied = True
                
                # Save frame
                if temp_dir:
                    plt.figure(figsize=(10, 8))
                    plt.suptitle(f"{step_name}: {prod.__class__.__name__}", fontsize=14)
                    hg.draw(use_positional_parameters=True)
                    frame_path = os.path.join(temp_dir, f"frame_{image_counter[0]:03d}.png")
                    plt.savefig(frame_path, dpi=200, bbox_inches='tight')
                    plt.close()
                    frame_list.append(frame_path)
                break
        if not applied:
            break

    # Phase 2: Modifying
    print("--- Phase 2: Modifying ---")
    while True:
        applied = False
        for prod in modifying_productions:
            new_hg = prod.apply(hg)
            if new_hg:
                image_counter[0] += 1
                print(f"✓ {prod.__class__.__name__} applied")
                hg = new_hg
                applied = True
                
                # Save frame
                if temp_dir:
                    plt.figure(figsize=(10, 8))
                    plt.suptitle(f"{step_name}: {prod.__class__.__name__}", fontsize=14)
                    hg.draw(use_positional_parameters=True)
                    frame_path = os.path.join(temp_dir, f"frame_{image_counter[0]:03d}.png")
                    plt.savefig(frame_path, dpi=200, bbox_inches='tight')
                    plt.close()
                    frame_list.append(frame_path)
                break
        if not applied:
            break
            
    return hg


def main() -> None:
    outpath = Path("./output_4")
    if outpath.exists():
        import shutil
        shutil.rmtree(outpath)
    outpath.mkdir(parents=True, exist_ok=True)

    # 1. Setup
    hg = create_initial_graph()
    temp_dir = tempfile.mkdtemp()
    frame_list = []
    image_counter = [0]
    
    # Initialize our Point-Based RFC
    # Radius 0.6 is good for picking larger shapes like the Right/Top sections
    # without accidentally picking neighbors.
    rfc = PointBasedRFC(radius=0.6) 

    # Save initial state
    plt.figure(figsize=(10, 8))
    hg.draw(use_positional_parameters=True)
    plt.savefig("./output_4/initial_graph.png", dpi=300, bbox_inches='tight')
    plt.close()

    # ---------------------------------------------------------
    # STEP 1: Break the Right Hexagon
    # Center of Right Section approx (2.0, 0.5)
    # ---------------------------------------------------------
    hg = apply_step(
        hg, rfc, 
        target_point=(2.0, 0.5), 
        step_name="Step 1 (Right Hexagon)", 
        temp_dir=temp_dir, 
        frame_list=frame_list, 
        image_counter=image_counter
    )

    # ---------------------------------------------------------
    # STEP 2: Break the Top Shape
    # Center of Top Section approx (0.6, 1.5)
    # ---------------------------------------------------------
    hg = apply_step(
        hg, rfc, 
        target_point=(0.5, 1.5), 
        step_name="Step 2 (Top Shape)", 
        temp_dir=temp_dir, 
        frame_list=frame_list, 
        image_counter=image_counter
    )

    # ---------------------------------------------------------
    # STEP 3: Break the Middle Square
    # Center of Middle is (0.5, 0.5)
    # ---------------------------------------------------------
    hg = apply_step(
        hg, rfc, 
        target_point=(0.5, 0.5), 
        step_name="Step 3 (Center Square)", 
        temp_dir=temp_dir, 
        frame_list=frame_list, 
        image_counter=image_counter
    )

    # ---------------------------------------------------------
    # STEP 4: Break the Middle-Top Sub-Square
    # The top-right quadrant of the center is at (0.75, 0.75)
    # We reduce the radius slightly to ensure we only pick the sub-square
    # ---------------------------------------------------------
    rfc.radius = 0.35 # Tighten radius for smaller squares
    hg = apply_step(
        hg, rfc, 
        target_point=(0.75, 0.75), 
        step_name="Step 4 (Center Top-Right)", 
        temp_dir=temp_dir, 
        frame_list=frame_list, 
        image_counter=image_counter
    )

    # ---------------------------------------------------------
    # Finalize
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 10))
    final_clean = hg.draw(use_positional_parameters=True, clean=True)
    plt.savefig("./output_4/final_graph_clean.png", dpi=400, bbox_inches='tight')
    plt.close()
    
    # Generate GIF
    if frame_list:
        try:
            frames = [Image.open(fp) for fp in frame_list]
            gif_path = os.path.join("./output_4", "animation.gif")
            frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=800, loop=0)
            print(f"\nGIF saved: {gif_path}")
            import shutil
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error making GIF: {e}")

    print("Process Complete. Check ./output_4/final_graph_clean.png")

if __name__ == "__main__":
    main()