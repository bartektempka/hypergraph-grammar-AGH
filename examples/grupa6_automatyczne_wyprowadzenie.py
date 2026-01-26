from typing import Any, Mapping, Optional
import matplotlib.pyplot as plt
from PIL import Image
import math
import os
import sys
from pathlib import Path
import tempfile
import shutil

proj_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(str(proj_root))

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


class Group6PointRFC:

    def __init__(self, target_point: Optional[tuple[float, float]] = None, radius: float = 0.6):
        self.target_point = target_point
        self.radius = radius

    def is_valid(self, edge: Edge, hypergraph: Hypergraph, meta: Optional[Mapping[str, Any]] = None) -> bool:
        if self.target_point is None: return False
        tx, ty = self.target_point
        vertices = edge.get_vertices()
        if not vertices: return False

        sum_x, sum_y, count = 0.0, 0.0, 0
        for v in vertices:
            params = hypergraph.get_vertex_parameters(v)
            if params:
                sum_x += params.get("x", 0.0)
                sum_y += params.get("y", 0.0)
                count += 1
        if count == 0: return False
        avg_x, avg_y = sum_x / count, sum_y / count
        dist = math.sqrt((avg_x - tx) ** 2 + (avg_y - ty) ** 2)
        return dist <= self.radius

    def set_target_point(self, point: tuple[float, float]) -> None:
        self.target_point = point


def create_initial_graph() -> Hypergraph:
    hg = Hypergraph()

    # --- CENTRUM (Kwadrat Q) ---
    hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 0}))

    # --- DÓŁ (Trapez Q) ---
    hg.add_edge(Edge(EdgeType.E, frozenset({"A", "E"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"F", "D"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "D", "F", "E"}), {"R": 0}))

    # --- GÓRA (Trapez Q) ---
    hg.add_edge(Edge(EdgeType.E, frozenset({"B", "G"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"G", "H"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"H", "C"}), {"R": 0, "B": 0}))
    hg.add_edge(Edge(EdgeType.Q, frozenset({"B", "C", "H", "G"}), {"R": 0}))

    # --- PRAWY (Pięciokąt P) ---
    hg.add_edge(Edge(EdgeType.E, frozenset({"H", "I"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"I", "F"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.P, frozenset({"C", "D", "F", "I", "H"}), {"R": 0}))

    # --- LEWY (Sześciokąt S) ---
    hg.add_edge(Edge(EdgeType.E, frozenset({"G", "K"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"K", "L"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.E, frozenset({"L", "E"}), {"R": 0, "B": 1}))
    hg.add_edge(Edge(EdgeType.S, frozenset({"A", "B", "K", "L", "G", "E"}), {"R": 0}))

    # Koordynaty
    hg.set_vertex_parameter("A", {"x": 0, "y": 0})
    hg.set_vertex_parameter("B", {"x": 0, "y": 1})
    hg.set_vertex_parameter("C", {"x": 1, "y": 1})
    hg.set_vertex_parameter("D", {"x": 1, "y": 0})
    hg.set_vertex_parameter("E", {"x": -0.5, "y": -1})
    hg.set_vertex_parameter("F", {"x": 1.5, "y": -1})
    hg.set_vertex_parameter("G", {"x": -0.5, "y": 2})
    hg.set_vertex_parameter("H", {"x": 1.5, "y": 2})
    hg.set_vertex_parameter("I", {"x": 2.5, "y": 0.5})
    hg.set_vertex_parameter("K", {"x": -1, "y": 1})
    hg.set_vertex_parameter("L", {"x": -1, "y": 0})

    return hg


def apply_logical_step(hg: Hypergraph, rfc: Group6PointRFC, target: tuple, step_name: str,
                       frames: list, counter: list, tmp: str, radius: float = 0.4) -> Hypergraph:
    rfc.set_target_point(target)
    rfc.radius = radius

    refining_element = [Prod6(rfc=rfc), Prod0(rfc=rfc)]

    marking_edges = [Prod7(), Prod1()]

    modifying = [Prod2(), Prod4(), Prod3(), Prod8(), Prod5()]

    for phase in [refining_element, marking_edges, modifying]:
        while True:
            applied = False
            for p in phase:
                new_hg = p.apply(hg)
                if new_hg:
                    hg = new_hg
                    applied = True
                    counter[0] += 1
                    plt.figure(figsize=(10, 8))
                    plt.suptitle(f"{step_name}: {p.__class__.__name__}")
                    hg.draw(use_positional_parameters=True)
                    path = os.path.join(tmp, f"frame_{counter[0]:03d}.png")
                    plt.savefig(path, dpi=150)
                    plt.close()
                    frames.append(path)
                    break
            if not applied: break
    return hg


def main() -> None:
    out = Path("./output_6")
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    hg = create_initial_graph()
    plt.figure(figsize=(12, 10))
    hg.draw(use_positional_parameters=True, clean=True)
    plt.savefig(out / "initial_group6.png", dpi=300)
    plt.close()
    tmp = tempfile.mkdtemp()
    frames, counter = [], [0]
    rfc = Group6PointRFC()

    hg = apply_logical_step(hg, rfc, (1.8, 0.5), "Step 1: Pentagon", frames, counter, tmp, radius=0.6)
    hg = apply_logical_step(hg, rfc, (0.5, 1.5), "Step 2: Top Trapezoid", frames, counter, tmp, radius=0.5)
    hg = apply_logical_step(hg, rfc, (0.5, 0.5), "Step 3: Center Square", frames, counter, tmp, radius=0.4)
    hg = apply_logical_step(hg, rfc, (0.8, 0.8), "Step 4: Corner Refinement", frames, counter, tmp, radius=0.25)

    plt.figure(figsize=(12, 10))
    hg.draw(use_positional_parameters=True, clean=True)
    plt.savefig(out / "final_group6.png", dpi=300)
    plt.close()

    if frames:
        imgs = [Image.open(f) for f in frames]
        imgs[0].save(out / "animation_group6.gif", save_all=True, append_images=imgs[1:], duration=600, loop=0)

    shutil.rmtree(tmp)
    print(f"Done. Final results in {out}")


if __name__ == "__main__":
    main()
