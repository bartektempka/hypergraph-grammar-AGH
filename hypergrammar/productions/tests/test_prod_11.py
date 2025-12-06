from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_11 import Prod11


class TestProd11:
    """Test suite for Production 11."""

    def test_apply_with_valid_s_edge_r1_all_edges_broken(self):
        """Test that production applies successfully when S edge with R=1 and all edges are broken."""
        # Arrange
        hg = Hypergraph()
        
        # Create hexagon vertices
        vertices = ["A", "B", "C", "D", "E", "F"]
        
        # Create intermediate vertices (breaking the edges)
        intermediates = ["G1", "G2", "G3", "G4", "G5", "G6"]
        
        # Add E edges from each hexagon vertex to adjacent intermediates
        # A connects to G1 and G6, B connects to G1 and G2, etc.
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "G1"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G1", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "G2"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G2", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "G3"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G3", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "G4"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G4", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "G5"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G5", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G6"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G6", "A"})))
        
        # Add S hyperedge with R=1
        hg.add_edge(Edge(EdgeType.S, frozenset(vertices), {"R": 1}))
        
        prod11 = Prod11()
        
        # Act
        result = prod11.apply(hg)
        
        # Assert
        assert result is not None
        edges = result.get_edges()
        
        # Check that S edge with R=1 no longer exists
        s_edges_r1 = [
            e
            for e in edges
            if e.get_type() == EdgeType.S and e.get_parameters().get("R") == 1
        ]
        assert len(s_edges_r1) == 0
        
        # Check that 6 Q edges with R=0 were created
        q_edges_r0 = [
            e
            for e in edges
            if e.get_type() == EdgeType.Q and e.get_parameters().get("R") == 0
        ]
        assert len(q_edges_r0) == 6
        
        # Check that each Q edge has 4 vertices
        for q_edge in q_edges_r0:
            assert len(q_edge.get_vertices()) == 4
        
        # Check that E edges with B=0 were created (from central vertex to intermediates)
        e_edges_b0 = [
            e
            for e in edges
            if e.get_type() == EdgeType.E and e.get_parameters().get("B") == 0
        ]
        assert len(e_edges_b0) == 6
        
        # Check that original E edges are still present
        e_edges_no_b = [
            e
            for e in edges
            if e.get_type() == EdgeType.E and "B" not in e.get_parameters()
        ]
        assert len(e_edges_no_b) == 12

    def test_apply_with_no_s_edge(self):
        """Test that production returns None when there is no S edge."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        
        prod11 = Prod11()
        
        # Act
        result = prod11.apply(hg)
        
        # Assert
        assert result is None

    def test_apply_with_s_edge_r0(self):
        """Test that production returns None when S edge has R=0."""
        # Arrange
        hg = Hypergraph()
        vertices = ["A", "B", "C", "D", "E", "F"]
        intermediates = ["G1", "G2", "G3", "G4", "G5", "G6"]
        
        # Add broken edges
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "G1"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G1", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "G2"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G2", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "G3"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G3", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "G4"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G4", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "G5"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G5", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G6"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G6", "A"})))
        
        # Add S edge with R=0 (not marked for refinement)
        hg.add_edge(Edge(EdgeType.S, frozenset(vertices), {"R": 0}))
        
        prod11 = Prod11()
        
        # Act
        result = prod11.apply(hg)
        
        # Assert
        assert result is None

    def test_apply_with_not_all_edges_broken(self):
        """Test that production returns None when not all edges are broken."""
        # Arrange
        hg = Hypergraph()
        vertices = ["A", "B", "C", "D", "E", "F"]
        
        # Add only some broken edges, but not all
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "G1"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G1", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))  # Not broken
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))  # Not broken
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))  # Not broken
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))  # Not broken
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "A"})))  # Not broken
        
        # Add S hyperedge with R=1
        hg.add_edge(Edge(EdgeType.S, frozenset(vertices), {"R": 1}))
        
        prod11 = Prod11()
        
        # Act
        result = prod11.apply(hg)
        
        # Assert
        assert result is None

    def test_apply_empty_hypergraph(self):
        """Test that production returns None for an empty hypergraph."""
        # Arrange
        hg = Hypergraph()
        prod11 = Prod11()
        
        # Act
        result = prod11.apply(hg)
        
        # Assert
        assert result is None

    def test_check_all_edges_broken_valid(self):
        """Test _check_all_edges_broken with all edges properly broken."""
        # Arrange
        hg = Hypergraph()
        vertices = ["A", "B", "C", "D", "E", "F"]
        intermediates = ["G1", "G2", "G3", "G4", "G5", "G6"]
        
        # Add all broken edges
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "G1"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G1", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "G2"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G2", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "G3"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G3", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "G4"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G4", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "G5"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G5", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G6"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G6", "A"})))
        
        prod11 = Prod11()
        
        # Act & Assert
        # pylint: disable=protected-access
        assert prod11._check_all_edges_broken(hg, tuple(vertices)) is True

    def test_check_all_edges_broken_invalid(self):
        """Test _check_all_edges_broken with some edges not broken."""
        # Arrange
        hg = Hypergraph()
        vertices = ["A", "B", "C", "D", "E", "F"]
        
        # Add only direct edges (not broken)
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "A"})))
        
        prod11 = Prod11()
        
        # Act & Assert
        # pylint: disable=protected-access
        assert prod11._check_all_edges_broken(hg, tuple(vertices)) is False

    def test_is_edge_broken_true(self):
        """Test _is_edge_broken when edge is broken."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "B"})))
        
        prod11 = Prod11()
        s_vertices = {"A", "B", "C", "D", "E", "F"}
        
        # Act & Assert
        # pylint: disable=protected-access
        assert prod11._is_edge_broken(hg, "A", "B", s_vertices) is True

    def test_is_edge_broken_false(self):
        """Test _is_edge_broken when edge is not broken."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        
        prod11 = Prod11()
        s_vertices = {"A", "B", "C", "D", "E", "F"}
        
        # Act & Assert
        # pylint: disable=protected-access
        assert prod11._is_edge_broken(hg, "A", "B", s_vertices) is False

    def test_rfc_mechanism_rejects_refinement_when_false(self):
        """Test that an RFC returning False prevents the production from applying."""
        # Arrange
        hg = Hypergraph()
        vertices = ["A", "B", "C", "D", "E", "F"]
        intermediates = ["G1", "G2", "G3", "G4", "G5", "G6"]
        
        # Add broken edges
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "G1"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G1", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "G2"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G2", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "G3"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G3", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "G4"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G4", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "G5"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G5", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G6"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G6", "A"})))
        
        hg.add_edge(Edge(EdgeType.S, frozenset(vertices), {"R": 1}))
        
        class RejectRFC:
            def is_valid(self, edge, hypergraph, meta=None):
                return False
        
        prod11 = Prod11(rfc=RejectRFC())
        
        # Act
        result = prod11.apply(hg)
        
        # Assert
        assert result is None

    def test_rfc_mechanism_allows_refinement_when_set_on_hypergraph(self):
        """Test that setting an RFC on the Hypergraph allows refinement accordingly."""
        # Arrange
        hg = Hypergraph()
        vertices = ["A", "B", "C", "D", "E", "F"]
        intermediates = ["G1", "G2", "G3", "G4", "G5", "G6"]
        
        # Add broken edges
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "G1"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G1", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "G2"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G2", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "G3"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G3", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "G4"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G4", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "G5"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G5", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G6"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G6", "A"})))
        
        hg.add_edge(Edge(EdgeType.S, frozenset(vertices), {"R": 1}))
        
        class AllowRFC:
            def is_valid(self, edge, hypergraph, meta=None):
                return True
        
        hg.set_rfc(AllowRFC())
        
        prod11 = Prod11()
        
        # Act
        result = prod11.apply(hg)
        
        # Assert
        assert result is not None
        
        # pylint: disable=protected-access
        q_edges_r0 = [
            e
            for e in result.get_edges()
            if e.get_type() == EdgeType.Q and e.get_parameters().get("R") == 0
        ]
        assert len(q_edges_r0) == 6

    def test_break_hexagon_creates_central_vertex_and_edges(self):
        """Test _break_hexagon creates central vertex, E edges with B=0, and Q edges."""
        # Arrange
        hg = Hypergraph()
        vertices = ["A", "B", "C", "D", "E", "F"]
        intermediates = ["G1", "G2", "G3", "G4", "G5", "G6"]
        
        # Add broken edges
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "G1"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G1", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "G2"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G2", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "G3"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G3", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "G4"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G4", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "G5"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G5", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G6"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G6", "A"})))
        
        s_edge = Edge(EdgeType.S, frozenset(vertices), {"R": 1})
        hg.add_edge(s_edge)
        
        prod11 = Prod11()
        
        # Act
        # pylint: disable=protected-access
        result = prod11._break_hexagon(hg, s_edge, tuple(vertices))
        
        # Assert
        edges = result.get_edges()
        
        # Check S edge is removed
        s_edges = [e for e in edges if e.get_type() == EdgeType.S]
        assert len(s_edges) == 0
        
        # Check 6 E edges with B=0 exist (central vertex to intermediates)
        e_edges_b0 = [
            e
            for e in edges
            if e.get_type() == EdgeType.E and e.get_parameters().get("B") == 0
        ]
        assert len(e_edges_b0) == 6
        
        # Check all E edges with B=0 contain a central vertex (M0, M1, etc.)
        central_vertices = set()
        for e in e_edges_b0:
            for v in e.get_vertices():
                if v.startswith("M"):
                    central_vertices.add(v)
        assert len(central_vertices) == 1
        
        # Check 6 Q edges with R=0 exist
        q_edges = [
            e
            for e in edges
            if e.get_type() == EdgeType.Q and e.get_parameters().get("R") == 0
        ]
        assert len(q_edges) == 6
        
        # Check each Q edge has 4 vertices including the central vertex
        central_vertex = central_vertices.pop()
        for q_edge in q_edges:
            assert len(q_edge.get_vertices()) == 4
            assert central_vertex in q_edge.get_vertices()

    def test_break_hexagon_returns_original_graph_if_intermediate_missing(self):
        """Test _break_hexagon returns original graph if an intermediate vertex is missing."""
        # Arrange
        hg = Hypergraph()
        vertices = ["A", "B", "C", "D", "E", "F"]
        
        # Add incomplete broken edges (missing some intermediates)
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "G1"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G1", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))  # Not broken
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))  # Not broken
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))  # Not broken
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))  # Not broken
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "A"})))  # Not broken
        
        s_edge = Edge(EdgeType.S, frozenset(vertices), {"R": 1})
        hg.add_edge(s_edge)
        
        prod11 = Prod11()
        
        # Act
        # pylint: disable=protected-access
        result = prod11._break_hexagon(hg, s_edge, tuple(vertices))
        
        # Assert - should return original graph unchanged
        assert result == hg
        # S edge should still exist
        s_edges = [e for e in result.get_edges() if e.get_type() == EdgeType.S]
        assert len(s_edges) == 1

    def test_find_intermediate_vertex_found(self):
        """Test _find_intermediate_vertex finds the correct intermediate vertex."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "B"})))
        
        prod11 = Prod11()
        s_vertices = {"A", "B", "C", "D", "E", "F"}
        
        # Act
        # pylint: disable=protected-access
        result = prod11._find_intermediate_vertex(hg, "A", "B", s_vertices)
        
        # Assert
        assert result == "G"

    def test_find_intermediate_vertex_not_found(self):
        """Test _find_intermediate_vertex returns None when no intermediate exists."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))  # Direct edge
        
        prod11 = Prod11()
        s_vertices = {"A", "B", "C", "D", "E", "F"}
        
        # Act
        # pylint: disable=protected-access
        result = prod11._find_intermediate_vertex(hg, "A", "B", s_vertices)
        
        # Assert
        assert result is None

    def test_find_intermediate_vertex_ignores_s_vertices(self):
        """Test _find_intermediate_vertex ignores vertices that are part of S."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "B"})))
        
        prod11 = Prod11()
        s_vertices = {"A", "B", "C", "D", "E", "F"}  # C is part of S
        
        # Act
        # pylint: disable=protected-access
        result = prod11._find_intermediate_vertex(hg, "A", "B", s_vertices)
        
        # Assert
        assert result is None  # C should be ignored because it's in s_vertices

    def test_set_central_vertex_position_calculates_average(self):
        """Test _set_central_vertex_position sets position as average of cycle vertices."""
        # Arrange
        hg = Hypergraph()
        vertices = ["A", "B", "C", "D", "E", "F"]
        
        # Set positions for vertices
        hg.set_vertex_parameter("A", {"x": 0, "y": 10})
        hg.set_vertex_parameter("B", {"x": 10, "y": 10})
        hg.set_vertex_parameter("C", {"x": 20, "y": 10})
        hg.set_vertex_parameter("D", {"x": 20, "y": 0})
        hg.set_vertex_parameter("E", {"x": 10, "y": 0})
        hg.set_vertex_parameter("F", {"x": 0, "y": 0})
        
        prod11 = Prod11()
        central_vertex = "M0"
        
        # Act
        # pylint: disable=protected-access
        prod11._set_central_vertex_position(hg, central_vertex, tuple(vertices))
        
        # Assert
        central_params = hg.get_vertex_parameters(central_vertex)
        assert "x" in central_params
        assert "y" in central_params
        # Average x = (0+10+20+20+10+0)/6 = 60/6 = 10
        # Average y = (10+10+10+0+0+0)/6 = 30/6 = 5
        assert central_params["x"] == 10
        assert central_params["y"] == 5

    def test_set_central_vertex_position_no_position_when_missing_coords(self):
        """Test _set_central_vertex_position doesn't set position if some vertices lack coordinates."""
        # Arrange
        hg = Hypergraph()
        vertices = ["A", "B", "C", "D", "E", "F"]
        
        # Set positions for only some vertices
        hg.set_vertex_parameter("A", {"x": 0, "y": 0})
        hg.set_vertex_parameter("B", {"x": 10, "y": 10})
        # C, D, E, F have no position
        
        prod11 = Prod11()
        central_vertex = "M0"
        
        # Act
        # pylint: disable=protected-access
        prod11._set_central_vertex_position(hg, central_vertex, tuple(vertices))
        
        # Assert
        central_params = hg.get_vertex_parameters(central_vertex)
        # Should not set position because not all vertices have coordinates
        assert "x" not in central_params
        assert "y" not in central_params
