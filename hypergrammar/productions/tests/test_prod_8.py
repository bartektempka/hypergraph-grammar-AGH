from typing import Dict
from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_8 import Prod8


class TestProd8:
    """Test suite for Production 8."""

    def _create_broken_edge(self, hg: Hypergraph, v1: str, v2: str, mid_name: str, coords: Dict[str, Dict[str, float]]):
        """Helper method to create a split edge with a midpoint."""
        hg.set_vertex_parameter(v1, coords[v1])
        hg.set_vertex_parameter(v2, coords[v2])

        p1 = coords[v1]
        p2 = coords[v2]

        mid_coords = {
            "x": (p1["x"] + p2["x"]) / 2,
            "y": (p1["y"] + p2["y"]) / 2
        }
        hg.set_vertex_parameter(mid_name, mid_coords)

        hg.add_edge(Edge(EdgeType.E, frozenset({v1, mid_name}), {"B": 1}))
        hg.add_edge(Edge(EdgeType.E, frozenset({mid_name, v2}), {"B": 1}))

    def _setup_valid_pentagon(self, hg: Hypergraph, suffix: str, offset_x: float = 0.0):
        corners = [f"V{i}_{suffix}" for i in range(1, 6)]
        midpoints = [f"M{i}_{suffix}" for i in range(1, 6)]

        base_coords = [
            (0.0, 0.0), (2.0, 0.0), (2.5, 1.5), (1.5, 2.5), (-0.5, 1.5)
        ]

        coords_data = {}
        for i, (x, y) in enumerate(base_coords):
            coords_data[corners[i]] = {"x": x + offset_x, "y": y}

        for i in range(5):
            self._create_broken_edge(
                hg, corners[i], corners[(i + 1) % 5], midpoints[i], coords_data
            )

        p_edge = Edge(EdgeType.P, frozenset(corners), {"R": 1})
        hg.add_edge(p_edge)
        return p_edge

    def test_apply_valid_pentagon_refinement(self):
        """Test that production applies successfully when P edge with R=1 and all boundaries are broken."""
        hg = Hypergraph()
        corners = ["V1", "V2", "V3", "V4", "V5"]
        midpoints = ["M1", "M2", "M3", "M4", "M5"]

        coords_data = {
            "V1": {"x": 0.0, "y": 0.0},
            "V2": {"x": 2.0, "y": 0.0},
            "V3": {"x": 2.5, "y": 1.5},
            "V4": {"x": 1.5, "y": 2.5},
            "V5": {"x": -0.5, "y": 1.5}
        }

        for i in range(5):
            self._create_broken_edge(
                hg, corners[i], corners[(i + 1) % 5], midpoints[i], coords_data
            )

        hg.add_edge(Edge(EdgeType.P, frozenset(corners), {"R": 1}))

        prod8 = Prod8()
        result = prod8.apply(hg)

        assert result is not None, "Production should apply to valid graph"
        edges = list(result.get_edges())

        p_edges = [e for e in edges if e.get_type() == EdgeType.P]
        assert len(p_edges) == 0, "P edge should be removed"

        q_edges = [e for e in edges if e.get_type() == EdgeType.Q]
        assert len(q_edges) == 5, "Should have 5 new Q edges"
        for q in q_edges:
            assert q.get_parameters().get("R") == 0, "New Q edges should have R=0"

        all_verts = set()
        for e in edges:
            all_verts.update(e.get_vertices())

        known_verts = set(corners + midpoints)
        new_verts = list(all_verts - known_verts)
        assert len(new_verts) == 1, "Exactly one new center vertex should be created"

        center_v = new_verts[0]
        params = result.get_vertex_parameters(center_v)

        epsilon = 1e-6
        assert abs(params["x"] - 1.1) < epsilon, f"Expected x ~ 1.1, got {params['x']}"
        assert abs(params["y"] - 1.1) < epsilon, f"Expected y ~ 1.1, got {params['y']}"

    def test_apply_with_invalid_r_parameter(self):
        """Test that production returns None when P edge has R=0."""
        hg = Hypergraph()
        corners = ["V1", "V2", "V3", "V4", "V5"]
        coords = {k: {"x": 0.0, "y": 0.0} for k in corners}

        for i in range(5):
            self._create_broken_edge(
                hg, corners[i], corners[(i + 1) % 5], f"M{i}", coords
            )

        hg.add_edge(Edge(EdgeType.P, frozenset(corners), {"R": 0}))

        prod8 = Prod8()
        result = prod8.apply(hg)

        assert result is None, "Should not apply if R=0"

    def test_apply_with_unbroken_boundary(self):
        """Test that production returns None when boundary is not fully broken."""
        hg = Hypergraph()
        corners = ["V1", "V2", "V3", "V4", "V5"]
        coords = {k: {"x": 0.0, "y": 0.0} for k in corners}

        for i in range(4):
            self._create_broken_edge(
                hg, corners[i], corners[i + 1], f"M{i}", coords
            )

        hg.set_vertex_parameter("V5", coords["V5"])
        hg.add_edge(Edge(EdgeType.E, frozenset({"V5", "V1"})))

        hg.add_edge(Edge(EdgeType.P, frozenset(corners), {"R": 1}))

        prod8 = Prod8()
        result = prod8.apply(hg)

        assert result is None, "Should not apply if any boundary edge is unbroken"

    def test_apply_with_invalid_vertex_count(self):
        """Test that production returns None when P edge has wrong number of vertices."""
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.P, frozenset({"A", "B", "C", "D"}), {"R": 1}))

        prod8 = Prod8()
        result = prod8.apply(hg)

        assert result is None, "Should not apply if P edge does not have 5 vertices"

    def test_apply_empty_hypergraph(self):
        """Test that production returns None for an empty hypergraph."""
        hg = Hypergraph()
        prod8 = Prod8()

        result = prod8.apply(hg)

        assert result is None

    def test_apply_fails_on_disconnected_topology(self):
        """Test that production returns None if the broken edges do not form a closed cycle."""
        hg = Hypergraph()
        corners = ["V1", "V2", "V3", "V4", "V5"]
        coords = {k: {"x": 0.0, "y": 0.0} for k in corners}

        self._create_broken_edge(hg, "V1", "V2", "M1", coords)
        self._create_broken_edge(hg, "V3", "V4", "M3", coords)

        hg.add_edge(Edge(EdgeType.P, frozenset(corners), {"R": 1}))

        prod8 = Prod8()
        result = prod8.apply(hg)

        assert result is None

    def test_apply_returns_none_when_rfc_blocks(self):
        """Test that production applies nothing if RFC returns False."""
        hg = Hypergraph()
        corners = ["V1", "V2", "V3", "V4", "V5"]
        coords = {k: {"x": 0.0, "y": 0.0} for k in corners}
        midpoints = ["M1", "M2", "M3", "M4", "M5"]

        for i in range(5):
            self._create_broken_edge(
                hg, corners[i], corners[(i + 1) % 5], midpoints[i], coords
            )

        hg.add_edge(Edge(EdgeType.P, frozenset(corners), {"R": 1}))

        class BlockingRFC:
            def is_valid(self, edge, hypergraph, meta=None):
                return False

        prod8 = Prod8(rfc=BlockingRFC())
        result = prod8.apply(hg)

        assert result is None

    def test_new_internal_edges_have_correct_parameters(self):
        """Test that newly created internal E edges have B=0 and new Q edges have R=0."""
        hg = Hypergraph()
        corners = ["V1", "V2", "V3", "V4", "V5"]
        coords = {k: {"x": 0.0, "y": 0.0} for k in corners}

        for i in range(5):
            self._create_broken_edge(
                hg, corners[i], corners[(i + 1) % 5], f"M{i}", coords
            )

        hg.add_edge(Edge(EdgeType.P, frozenset(corners), {"R": 1}))

        prod8 = Prod8()
        result = prod8.apply(hg)

        assert result is not None
        edges = list(result.get_edges())

        all_verts = set()
        for e in edges:
            all_verts.update(e.get_vertices())

        known_verts = set(corners + [f"M{i}" for i in range(5)])
        center_node = list(all_verts - known_verts)[0]

        spoke_edges = [
            e for e in edges
            if e.get_type() == EdgeType.E and center_node in e.get_vertices()
        ]
        assert len(spoke_edges) == 5
        for e in spoke_edges:
            assert e.get_parameters().get("B") == 0

        q_edges = [e for e in edges if e.get_type() == EdgeType.Q]
        assert len(q_edges) == 5
        for e in q_edges:
            assert e.get_parameters().get("R") == 0

    def test_apply_ignores_unrelated_edges(self):
        """Test that production ignores unrelated Q edges or P edges with R=0 present in the graph."""
        hg = Hypergraph()
        corners = ["V1", "V2", "V3", "V4", "V5"]
        coords = {k: {"x": 0.0, "y": 0.0} for k in corners}

        for i in range(5):
            self._create_broken_edge(
                hg, corners[i], corners[(i + 1) % 5], f"M{i}", coords
            )

        hg.add_edge(Edge(EdgeType.P, frozenset(corners), {"R": 1}))

        hg.add_edge(Edge(EdgeType.Q, frozenset({"X", "Y"}), {"R": 1}))
        hg.add_edge(Edge(EdgeType.P, frozenset({"Z1", "Z2", "Z3", "Z4", "Z5"}), {"R": 0}))

        prod8 = Prod8()
        result = prod8.apply(hg)

        assert result is not None
        edges = list(result.get_edges())

        unrelated_q = [e for e in edges if e.get_type() == EdgeType.Q and e.get_parameters().get("R") == 1]
        assert len(unrelated_q) == 1

        unrelated_p = [e for e in edges if e.get_type() == EdgeType.P and e.get_parameters().get("R") == 0]
        assert len(unrelated_p) == 1

    def test_apply_skips_rejected_candidate_and_picks_next(self):
        hg = Hypergraph()

        p1_edge = self._setup_valid_pentagon(hg, suffix="A", offset_x=0.0)
        p2_edge = self._setup_valid_pentagon(hg, suffix="B", offset_x=10.0)

        class SelectiveRFC:
            def is_valid(self, edge, hypergraph, meta=None):
                return edge == p2_edge

        prod8 = Prod8(rfc=SelectiveRFC())
        result = prod8.apply(hg)

        assert result is not None
        edges = list(result.get_edges())

        assert p1_edge in edges

        assert p2_edge not in edges

        q_edges = [e for e in edges if e.get_type() == EdgeType.Q]
        assert len(q_edges) == 5

    def test_apply_sequential_refinement_of_two_pentagons(self):
        hg = Hypergraph()

        self._setup_valid_pentagon(hg, suffix="A", offset_x=0.0)
        self._setup_valid_pentagon(hg, suffix="B", offset_x=10.0)

        prod8 = Prod8()

        hg = prod8.apply(hg)
        assert hg is not None

        p_edges_iter1 = [e for e in hg.get_edges() if e.get_type() == EdgeType.P and e.get_parameters().get("R") == 1]
        assert len(p_edges_iter1) == 1

        hg = prod8.apply(hg)
        assert hg is not None

        p_edges_iter2 = [e for e in hg.get_edges() if e.get_type() == EdgeType.P and e.get_parameters().get("R") == 1]
        assert len(p_edges_iter2) == 0

        q_edges = [e for e in hg.get_edges() if e.get_type() == EdgeType.Q]
        assert len(q_edges) == 10


if __name__ == "__main__":
    test = TestProd8()
    try:
        test.test_apply_valid_pentagon_refinement()
        test.test_apply_with_invalid_r_parameter()
        test.test_apply_with_unbroken_boundary()
        test.test_apply_with_invalid_vertex_count()
        test.test_apply_empty_hypergraph()
        test.test_apply_fails_on_disconnected_topology()
        test.test_apply_returns_none_when_rfc_blocks()
        test.test_new_internal_edges_have_correct_parameters()
        test.test_apply_ignores_unrelated_edges()
        test.test_apply_skips_rejected_candidate_and_picks_next()
        test.test_apply_sequential_refinement_of_two_pentagons()
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")