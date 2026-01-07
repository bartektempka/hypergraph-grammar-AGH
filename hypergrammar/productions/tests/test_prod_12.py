import pytest

from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_12 import Prod12


class TestProd12:
    """Test suite for Production 12."""

    def test_apply_with_valid_t_edge_r0(self):
        """Test that production applies successfully when T edge with R=0 and all E edges are present."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "A"})))
        hg.add_edge(
            Edge(EdgeType.T, frozenset({"A", "B", "C", "D", "E", "F", "G"}), {"R": 0})
        )

        prod12 = Prod12()

        # Act
        result = prod12.apply(hg)

        # Assert
        assert result is not None
        edges = result.get_edges()

        # Check that T edge with R=1 exists
        t_edges_r1 = [
            e
            for e in edges
            if e.get_type() == EdgeType.T and e.get_parameters().get("R") == 1
        ]
        assert len(t_edges_r1) == 1
        assert t_edges_r1[0].get_vertices() == frozenset(
            {"A", "B", "C", "D", "E", "F", "G"}
        )

        # Check that T edge with R=0 no longer exists
        t_edges_r0 = [
            e
            for e in edges
            if e.get_type() == EdgeType.T and e.get_parameters().get("R") == 0
        ]
        assert len(t_edges_r0) == 0

        # Check that E edges are still present
        e_edges = [e for e in edges if e.get_type() == EdgeType.E]
        assert len(e_edges) == 7

    def test_apply_with_no_t_edge(self):
        """Test that production returns None when there is no T edge."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))

        prod12 = Prod12()

        # Act
        result = prod12.apply(hg)

        # Assert
        assert result is None

    def test_apply_with_t_edge_r1(self):
        """Test that production returns None when T edge has R=1."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "A"})))
        hg.add_edge(
            Edge(EdgeType.T, frozenset({"A", "B", "C", "D", "E", "F", "G"}), {"R": 1})
        )

        prod12 = Prod12()

        # Act
        result = prod12.apply(hg)

        # Assert
        assert result is None

    def test_apply_with_missing_e_edge(self):
        """Test that production returns None when one or more E edges are missing."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        # Missing E edge between G and A
        hg.add_edge(
            Edge(EdgeType.T, frozenset({"A", "B", "C", "D", "E", "F", "G"}), {"R": 0})
        )

        prod12 = Prod12()

        # Act
        result = prod12.apply(hg)

        # Assert
        assert result is None

    def test_apply_empty_hypergraph(self):
        """Test that production returns None for an empty hypergraph."""
        # Arrange
        hg = Hypergraph()
        prod12 = Prod12()

        # Act
        result = prod12.apply(hg)

        # Assert
        assert result is None

    def test_e_edges_match_private_method(self):
        """Test the _e_edges_match helper method."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))

        prod12 = Prod12()

        # Act & Assert
        # pylint: disable=protected-access
        assert prod12._e_edges_match(hg, frozenset({"A", "B"})) is True
        assert prod12._e_edges_match(hg, frozenset({"C", "D"})) is True
        assert prod12._e_edges_match(hg, frozenset({"A", "C"})) is False
        assert prod12._e_edges_match(hg, frozenset({"X", "Y"})) is False

    def test_check_cycle_valid_septagon(self):
        """Test _check_cycle with a valid septagon cycle."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "A"})))

        prod12 = Prod12()
        cycle = ["A", "B", "C", "D", "E", "F", "G"]

        # Act & Assert
        # pylint: disable=protected-access
        assert prod12._check_cycle(hg, cycle) is True

    def test_check_cycle_invalid_septagon(self):
        """Test _check_cycle with an invalid septagon cycle."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        # Missing edge between F and G
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "A"})))

        prod12 = Prod12()
        cycle = ["A", "B", "C", "D", "E", "F", "G"]

        # Act & Assert
        # pylint: disable=protected-access
        assert prod12._check_cycle(hg, cycle) is False

    def test_rfc_mechanism_rejects_refinement_when_false(self):
        """Test that an RFC returning False prevents the production from applying."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "A"})))
        hg.add_edge(
            Edge(EdgeType.T, frozenset({"A", "B", "C", "D", "E", "F", "G"}), {"R": 0})
        )

        class RejectRFC:
            def is_valid(self, edge, hypergraph, meta=None):
                return False

        prod12 = Prod12(rfc=RejectRFC())

        # Act
        result = prod12.apply(hg)

        # Assert
        assert result is None

    def test_rfc_mechanism_allows_refinement_when_set_on_hypergraph(self):
        """Test that setting an RFC on the Hypergraph allows refinement accordingly."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "A"})))
        hg.add_edge(
            Edge(EdgeType.T, frozenset({"A", "B", "C", "D", "E", "F", "G"}), {"R": 0})
        )

        class AllowRFC:
            def is_valid(self, edge, hypergraph, meta=None):
                return True

        hg.set_rfc(AllowRFC())

        prod12 = Prod12()

        # Act
        result = prod12.apply(hg)

        # Assert
        assert result is not None

        # pylint: disable=protected-access
        t_edges_r1 = [
            e
            for e in result.get_edges()
            if e.get_type() == EdgeType.T and e.get_parameters().get("R") == 1
        ]
        assert len(t_edges_r1) == 1

    def test_apply_with_t_edge_on_5_vertices_returns_none(self):
        """
        T edge incident with only 5 vertices (instead of 7) is treated as
        an invalid element and causes ValueError.
        """
        hg = Hypergraph()
        # 5-cycle A-B-C-D-E-A just to have some structure
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "A"})))
        # T-edge on 5 vertices with R=0
        hg.add_edge(
            Edge(EdgeType.T, frozenset({"A", "B", "C", "D", "E"}), {"R": 0})
        )

        prod12 = Prod12()

        with pytest.raises(ValueError):
            prod12.apply(hg)

    def test_apply_with_t_edge_on_7_vertices_returns_none(self):
        """
        Even when T edge is incident with 7 vertices, production does not
        apply if there is no 7-cycle on E-edges.
        """
        hg = Hypergraph()
        # T-edge alone, no E-edges forming boundary
        hg.add_edge(
            Edge(
                EdgeType.T,
                frozenset({"A", "B", "C", "D", "E", "F", "G"}),
                {"R": 0},
            )
        )

        prod12 = Prod12()
        result = prod12.apply(hg)

        assert result is None

    def test_apply_with_non_binary_e_edge_returns_none(self):
        """
        Production should not apply when edges along the boundary are not
        all binary – here one of the cycle edges is a 3-vertex E edge.
        """
        hg = Hypergraph()
        # Six proper binary edges
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        # Non-binary "edge" instead of G-A
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "A", "X"})))
        # T-edge on 7 vertices with R=0
        hg.add_edge(
            Edge(
                EdgeType.T,
                frozenset({"A", "B", "C", "D", "E", "F", "G"}),
                {"R": 0},
            )
        )

        prod12 = Prod12()
        result = prod12.apply(hg)

        # There is no binary edge {G, A}, so 7-cycle cannot be formed
        assert result is None

    def test_rfc_mechanism_rejects_refinement_when_set_on_hypergraph(self):
        """
        RFC attached to the Hypergraph can prevent refinement when it
        returns False for the candidate T edge.
        """
        hg = Hypergraph()
        # valid 7-cycle
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "A"})))
        # T-edge on 7 vertices with R=0
        hg.add_edge(
            Edge(
                EdgeType.T,
                frozenset({"A", "B", "C", "D", "E", "F", "G"}),
                {"R": 0},
            )
        )

        class RejectRFC:
            def is_valid(self, edge, hypergraph, meta=None):
                return False

        hg.set_rfc(RejectRFC())

        prod12 = Prod12()
        result = prod12.apply(hg)

        assert result is None

    def test_apply_with_extra_edge_raises_value_error(self):
        """
        Extra test for invalid T edge size: T incident with 6 vertices
        instead of 7 causes ValueError.
        """
        hg = Hypergraph()
        # 6-cycle just for context
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "A"})))
        # T-edge with R=0 on only 6 vertices
        hg.add_edge(
            Edge(
                EdgeType.T,
                frozenset({"A", "B", "C", "D", "E", "F"}),
                {"R": 0},
            )
        )
        # an extra edge that does not add new vertices (doesn't matter for the error)
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "C"})))

        prod12 = Prod12()

        with pytest.raises(ValueError):
            prod12.apply(hg)