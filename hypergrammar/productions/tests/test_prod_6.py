from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_6 import Prod6


class TestProd6:
    """Test suite for Production 6."""

    def test_apply_with_valid_cycle(self):
        """
        Test that production is applied successfully when:
            - there is 5-length cycle connected by E-Edges
            - there is one P-Edge that connects to all verticles
        """
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "A"})))
        hg.add_edge(Edge(EdgeType.P, frozenset({"A", "B", "C", "D", "E"}), {"R": 67}))

        prod0 = Prod6()

        # Act
        result = prod0.apply(hg)

        # Assert
        assert result is not None

        edges = result.get_edges()

        # Check that P edge with R=1 exists
        q_edges_r1 = [
            e
            for e in edges
            if e.get_type() == EdgeType.P and e.get_parameters().get("R") == 1
        ]
        assert len(q_edges_r1) == 1
        assert q_edges_r1[0].get_vertices() == frozenset({"A", "B", "C", "D", "E"})

        # Check that P edge with R != 1 no longer exists
        q_edges_r0 = [
            e
            for e in edges
            if e.get_type() == EdgeType.P and e.get_parameters().get("R") == 67
        ]
        assert len(q_edges_r0) == 0

        # Check that E edges are still present
        e_edges = [e for e in edges if e.get_type() == EdgeType.E]
        assert len(e_edges) == 5

    def test_apply_with_edge_p_set_to_1(self):
        """Test apply when valid graph is provided but R argument of P edge is already set to 1"""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "A"})))
        hg.add_edge(Edge(EdgeType.P, frozenset({"A", "B", "C", "D", "E"}), {"R": 1}))

        prod0 = Prod6()

        # Act
        result = prod0.apply(hg)

        # Assert
        assert result is None

    def test_apply_with_not_present_edge_p(self):
        """Test apply when vthere is no P edge"""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "A"})))
        hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D", "E"}), {"R": 67}))

        prod0 = Prod6()

        # Act
        result = prod0.apply(hg)

        # Assert
        assert result is None

    def test_apply_when_cycle_to_short(self):
        """Test apply when founded cycle is to short"""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))
        hg.add_edge(Edge(EdgeType.P, frozenset({"A", "B", "C", "D"}), {"R": 67}))

        prod0 = Prod6()

        # Act
        result = None
        try:
            result = prod0.apply(hg)
        except ValueError:
            pass

        # Assert
        assert result is None

    def test_apply_when_there_is_no_cycle(self):
        """Test apply when there is no cycle"""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "A"})))

        hg.add_edge(Edge(EdgeType.P, frozenset({"A", "B", "C", "D", "E"}), {"R": 67}))

        prod0 = Prod6()

        # Act
        result = prod0.apply(hg)

        # Assert
        assert result is None

    def test_apply_when_rfc_for_prod_provided(self):
        """Test apply when rfc (that returns false) is provided"""

        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "A"})))
        hg.add_edge(Edge(EdgeType.P, frozenset({"A", "B", "C", "D", "E"}), {"R": 67}))

        class AllowRFC:
            def is_valid(self, edge, hypergraph, meta=None):
                return False

        prod0 = Prod6(AllowRFC())

        # Act
        result = prod0.apply(hg)

        # Assert
        assert result is None
