import pytest

from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_12 import Prod12


class TestProd12:
    """Test suite for Production 12."""

    def test_apply_with_valid_t_edge_r0(self):
        """
        Production applies successfully when:
        - there is a 7-cycle on E-edges,
        - there is a T edge with R=0 incident with exactly 6 vertices of the cycle.
        """
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
            Edge(EdgeType.T, frozenset({"A", "B", "C", "D", "E", "F"}), {"R": 0})
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
            {"A", "B", "C", "D", "E", "F"}
        )

        # Check that T edge with R=0 no longer exists
        t_edges_r0 = [
            e
            for e in edges
            if e.get_type() == EdgeType.T and e.get_parameters().get("R") == 0
        ]
        assert len(t_edges_r0) == 0

        # Check that E edges are still present (7-cycle intact)
        e_edges = [e for e in edges if e.get_type() == EdgeType.E]
        assert len(e_edges) == 7

    def test_apply_with_no_t_edge(self):
        """
        Production returns None when there is no T edge with R=0,
        even if the boundary is a 7-cycle.
        """
        # Arrange
        hg = Hypergraph()
        # 7-cycle A-B-C-D-E-F-G-A
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "A"})))
        # extra boundary edge (still no T-edge)
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "C"})))

        prod12 = Prod12()

        # Act
        result = prod12.apply(hg)

        # Assert
        assert result is None

    def test_apply_with_t_edge_r1(self):
        """Production returns None when the only T edge has R=1 (already refined)."""
        # Arrange
        hg = Hypergraph()
        # 7-cycle A-B-C-D-E-F-G-A
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "A"})))
        # T-edge already marked R=1
        hg.add_edge(
            Edge(EdgeType.T, frozenset({"A", "B", "C", "D", "E", "F"}), {"R": 1})
        )

        prod12 = Prod12()

        # Act
        result = prod12.apply(hg)

        # Assert
        assert result is None

    def test_apply_with_missing_e_edge(self):
        """
        Production returns None when one or more E edges are missing
        and the boundary does not form a 7-cycle.
        """
        # Arrange
        hg = Hypergraph()
        # Broken cycle: no edge G-A, instead one diagonal A-C
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "C"})))  # extra edge, still no 7-cycle
        hg.add_edge(
            Edge(EdgeType.T, frozenset({"A", "B", "C", "D", "E", "F"}), {"R": 0})
        )

        prod12 = Prod12()

        # Act
        result = prod12.apply(hg)

        # Assert
        assert result is None

    def test_apply_empty_hypergraph_raises_value_error(self):
        """Production raises ValueError for a hypergraph with wrong size (no vertices/edges)."""
        # Arrange
        hg = Hypergraph()
        prod12 = Prod12()

        # Act / Assert
        with pytest.raises(ValueError):
            prod12.apply(hg)

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
        """RFC returning False prevents the production from applying."""
        # Arrange
        hg = Hypergraph()
        # valid 7-cycle
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "A"})))
        hg.add_edge(
            Edge(EdgeType.T, frozenset({"A", "B", "C", "D", "E", "F"}), {"R": 0})
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
        """Setting an RFC on the Hypergraph allows refinement when it returns True."""
        # Arrange
        hg = Hypergraph()
        # valid 7-cycle
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "A"})))
        hg.add_edge(
            Edge(EdgeType.T, frozenset({"A", "B", "C", "D", "E", "F"}), {"R": 0})
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

        t_edges_r1 = [
            e
            for e in result.get_edges()
            if e.get_type() == EdgeType.T and e.get_parameters().get("R") == 1
        ]
        assert len(t_edges_r1) == 1

    def test_apply_with_t_edge_on_5_vertices_returns_none(self):
        """
        Production should not apply when T edge is incident with only 5
        vertices of the 7-cycle instead of 6.
        """
        hg = Hypergraph()
        # 7-cycle A-B-C-D-E-F-G-A
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "A"})))
        # T-edge on only 5 vertices of the cycle
        hg.add_edge(
            Edge(EdgeType.T, frozenset({"A", "B", "C", "D", "E"}), {"R": 0})
        )

        prod12 = Prod12()
        result = prod12.apply(hg)

        assert result is None

    def test_apply_with_t_edge_on_7_vertices_returns_none(self):
        """
        Production should not apply when T edge is incident with all 7
        vertices of the cycle (must be exactly 6).
        """
        hg = Hypergraph()
        # 7-cycle A-B-C-D-E-F-G-A
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "A"})))
        # T-edge on all 7 vertices of the cycle
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
        Production should not apply when at least one E edge is not binary
        (connects more than two vertices).
        """
        hg = Hypergraph()
        # 6 proper binary E-edges
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        # 1 non-binary E-edge (3 vertices), still within A..G
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "C", "D"})))
        # T-edge with 6 vertices of the cycle (for shape)
        hg.add_edge(
            Edge(EdgeType.T, frozenset({"A", "B", "C", "D", "E", "F"}), {"R": 0})
        )

        prod12 = Prod12()
        result = prod12.apply(hg)

        # Non-binary E-edge should trigger the len(ev) != 2 check -> None
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
        # T-edge on 6 vertices with R=0
        hg.add_edge(
            Edge(EdgeType.T, frozenset({"A", "B", "C", "D", "E", "F"}), {"R": 0})
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
        Production should raise ValueError when the hypergraph has the correct
        number of vertices (7) but more than 8 edges (shape does not match P12).
        """
        hg = Hypergraph()
        # 7-cycle
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "A"})))
        # T-edge with R=0 on 6 vertices
        hg.add_edge(
            Edge(EdgeType.T, frozenset({"A", "B", "C", "D", "E", "F"}), {"R": 0})
        )
        # extra edge that does not add new vertices
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "C"})))

        prod12 = Prod12()

        with pytest.raises(ValueError):
            prod12.apply(hg)
