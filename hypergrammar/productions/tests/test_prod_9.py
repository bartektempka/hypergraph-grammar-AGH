from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_9 import Prod9


class TestProd9():
    """Test suite for Production 9 (Marking Q for refinement)."""

    def test_apply_valid_hexagon_r0(self):
        """Test that P9 applies successfully to a valid hexagon with R=0."""
        # Arrange
        hg = Hypergraph()
        nodes = frozenset([f"v{i}" for i in range(6)])
        # Valid Q edge, 6 vertices, R=0
        hg.add_edge(Edge(EdgeType.S, nodes, {"R": 0}))

        prod9 = Prod9() # Default RFC allows everything or is ignored depending on impl, assuming valid here

        # Act
        result = prod9.apply(hg)

        # Assert
        assert result is not None, "Production should return a graph, not None"
        
        # Check Q edge state
        q_edges = [e for e in result.get_edges() if e.get_type() == EdgeType.S]
        assert len(q_edges) == 1
        assert q_edges[0].get_parameters()["R"] == 1, "R parameter should be updated to 1"

    def test_apply_already_marked_r1(self):
        """Test that P9 ignores hexagons that are already marked (R=1)."""
        # Arrange
        hg = Hypergraph()
        nodes = frozenset([f"v{i}" for i in range(6)])
        hg.add_edge(Edge(EdgeType.S, nodes, {"R": 1}))

        prod9 = Prod9()

        # Act
        result = prod9.apply(hg)

        # Assert
        assert result is None, "Should not apply if R is already 1"

    def test_apply_invalid_topology_not_hexagon(self):
        """Test that P9 ignores Q edges that do not have exactly 6 vertices."""
        # Arrange
        hg = Hypergraph()
        nodes = frozenset([f"v{i}" for i in range(5)]) # Pentagon
        hg.add_edge(Edge(EdgeType.S, nodes, {"R": 0}))

        prod9 = Prod9()

        # Act
        result = prod9.apply(hg)

        # Assert
        assert result is None, "Should not apply to non-hexagonal elements"

    def test_rfc_rejection(self):
        """Test that P9 does not apply if RFC returns False."""
        # Arrange
        hg = Hypergraph()
        nodes = frozenset([f"v{i}" for i in range(6)])
        hg.add_edge(Edge(EdgeType.S, nodes, {"R": 0}))

        class RejectRFC:
            def is_valid(self, edge, graph, meta=None):
                return False

        prod9 = Prod9(rfc=RejectRFC())

        # Act
        result = prod9.apply(hg)

        # Assert
        assert result is None, "Should not apply if RFC rejects the edge"

    def test_rfc_acceptance(self):
        """Test that P9 applies if RFC explicitly returns True."""
        # Arrange
        hg = Hypergraph()
        nodes = frozenset([f"v{i}" for i in range(6)])
        hg.add_edge(Edge(EdgeType.S, nodes, {"R": 0}))

        class AcceptRFC:
            def is_valid(self, edge, graph, meta=None):
                return True

        prod9 = Prod9(rfc=AcceptRFC())

        # Act
        result = prod9.apply(hg)

        # Assert
        assert result is not None
        assert list(result.get_edges())[0].get_parameters()["R"] == 1