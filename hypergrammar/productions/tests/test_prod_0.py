from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_0 import Prod0


class TestProd0:
    """Test suite for Production 0."""

    def test_apply_with_valid_q_edge_r0(self):
        """Test that production applies successfully when Q edge with R=0 and all E edges are present."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))
        hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 0}))

        prod0 = Prod0()

        # Act
        result = prod0.apply(hg)

        # Assert
        assert result is not None
        edges = result.get_edges()

        # Check that Q edge with R=1 exists
        q_edges_r1 = [
            e
            for e in edges
            if e.get_type() == EdgeType.Q and e.get_parameters().get("R") == 1
        ]
        assert len(q_edges_r1) == 1
        assert q_edges_r1[0].get_vertices() == frozenset({"A", "B", "C", "D"})

        # Check that Q edge with R=0 no longer exists
        q_edges_r0 = [
            e
            for e in edges
            if e.get_type() == EdgeType.Q and e.get_parameters().get("R") == 0
        ]
        assert len(q_edges_r0) == 0

        # Check that E edges are still present
        e_edges = [e for e in edges if e.get_type() == EdgeType.E]
        assert len(e_edges) == 4

    def test_apply_with_no_q_edge(self):
        """Test that production returns None when there is no Q edge."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))

        prod0 = Prod0()

        # Act
        result = prod0.apply(hg)

        # Assert
        assert result is None

    def test_apply_with_q_edge_r1(self):
        """Test that production returns None when Q edge has R=1."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))
        hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 1}))

        prod0 = Prod0()

        # Act
        result = prod0.apply(hg)

        # Assert
        assert result is None

    def test_apply_with_missing_e_edge(self):
        """Test that production returns None when one or more E edges are missing."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        # Missing E edge between D and A
        hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 0}))

        prod0 = Prod0()

        # Act
        result = prod0.apply(hg)

        # Assert
        assert result is None

    def test_apply_empty_hypergraph(self):
        """Test that production returns None for an empty hypergraph."""
        # Arrange
        hg = Hypergraph()
        prod0 = Prod0()

        # Act
        result = prod0.apply(hg)

        # Assert
        assert result is None

    def test_e_edges_match_private_method(self):
        """Test the _e_edges_match helper method."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))

        prod0 = Prod0()

        # Act & Assert
        # pylint: disable=protected-access
        assert prod0._e_edges_match(hg, frozenset({"A", "B"})) is True
        assert prod0._e_edges_match(hg, frozenset({"C", "D"})) is True
        assert prod0._e_edges_match(hg, frozenset({"A", "C"})) is False
        assert prod0._e_edges_match(hg, frozenset({"X", "Y"})) is False

    def test_check_cycle_valid_square(self):
        """Test _check_cycle with a valid square cycle."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))

        prod0 = Prod0()
        cycle = ["A", "B", "C", "D"]

        # Act & Assert
        # pylint: disable=protected-access
        assert prod0._check_cycle(hg, cycle) is True

    def test_check_cycle_invalid_square(self):
        """Test _check_cycle with an invalid square cycle."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        # Missing edge between C and D
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))

        prod0 = Prod0()
        cycle = ["A", "B", "C", "D"]

        # Act & Assert
        # pylint: disable=protected-access
        assert prod0._check_cycle(hg, cycle) is False

    def test_rfc_mechanism_rejects_refinement_when_false(self):
        """Test that an RFC returning False prevents the production from applying."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))
        hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 0}))

        class RejectRFC:
            def is_valid(self, edge, hypergraph, meta=None):
                return False

        prod0 = Prod0(rfc=RejectRFC())

        # Act
        result = prod0.apply(hg)

        # Assert
        assert result is None

    def test_rfc_mechanism_allows_refinement_when_set_on_hypergraph(self):
        """Test that setting an RFC on the Hypergraph allows refinement accordingly."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))
        hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 0}))

        class AllowRFC:
            def is_valid(self, edge, hypergraph, meta=None):
                return True

        hg.set_rfc(AllowRFC())

        prod0 = Prod0()

        # Act
        result = prod0.apply(hg)

        # Assert
        assert result is not None

        # pylint: disable=protected-access
        q_edges_r1 = [
            e
            for e in result.get_edges()
            if e.get_type() == EdgeType.Q and e.get_parameters().get("R") == 1
        ]
        assert len(q_edges_r1) == 1
