from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_2 import Prod2


class TestProd2:
    """Test suite for Production 2."""

    def test_apply_with_valid_edges(self):
        """Test that production applies successfully when E edge with R=1, B=0 and all E edges are present."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"}), {"R": 1, "B":0}))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "A"})))

        hg.set_vertex_parameter("A", {"x": 0, "y": 2, "z": 0})
        hg.set_vertex_parameter("B", {"x": 0, "y": 0, "z": 0})
        hg.set_vertex_parameter("C", {"x": 1, "y": 1, "z": 0})

        prod2 = Prod2()

        # Act
        result = prod2.apply(hg)

        # Assert
        assert result is not None
        edges = result.get_edges()

        # Check that only 2 edges left
        assert len(edges) == 2

        # Check that both edges have R=0 and B=0
        e_edges_r0_b0 = [
            e
            for e in edges
            if e.get_type() == EdgeType.E
            and e.get_parameters().get("R") == 0
            and e.get_parameters().get("B") == 0
        ]
        assert len(e_edges_r0_b0) == 2

        # Check if one is between A and C and second between B and C
        both_edges_sets = [
            e_edges_r0_b0[0].get_vertices(),
            e_edges_r0_b0[1].get_vertices(),
        ]
        assert (
            frozenset({"A", "C"}) in both_edges_sets
            and frozenset({"B", "C"}) in both_edges_sets
        )

    def test_apply_with_no_r1_edge(self):
        """Test that production returns None when no edge has R = 1"""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "A"})))

        hg.set_vertex_parameter("A", {"x": 0, "y": 2, "z": 0})
        hg.set_vertex_parameter("B", {"x": 0, "y": 0, "z": 0})
        hg.set_vertex_parameter("C", {"x": 1, "y": 1, "z": 0})

        prod2 = Prod2()

        # Act
        result = prod2.apply(hg)

        # Assert
        assert result is None

    def test_apply_with_no_b0_edge(self):
        """Test that production returns None when no edge has B = 0"""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "A"})))

        hg.set_vertex_parameter("A", {"x": 0, "y": 2, "z": 0})
        hg.set_vertex_parameter("B", {"x": 0, "y": 0, "z": 0})
        hg.set_vertex_parameter("C", {"x": 1, "y": 1, "z": 0})

        prod2 = Prod2()

        # Act
        result = prod2.apply(hg)

        # Assert
        assert result is None

    def test_apply_with_not_enough_edges(self):
        """Test that production returns None when there isn't enough edges."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))

        hg.set_vertex_parameter("A", {"x": 0, "y": 2, "z": 0})
        hg.set_vertex_parameter("B", {"x": 0, "y": 0, "z": 0})
        hg.set_vertex_parameter("C", {"x": 1, "y": 1, "z": 0})

        prod2 = Prod2()

        # Act
        result = prod2.apply(hg)

        # Assert
        assert result is None

    def test_apply_with_no_cycle(self):
        """Test that production returns None when there's no cycle."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))

        hg.set_vertex_parameter("A", {"x": 0, "y": 3, "z": 0})
        hg.set_vertex_parameter("B", {"x": 0, "y": 1, "z": 0})
        hg.set_vertex_parameter("C", {"x": 1, "y": 2, "z": 0})
        hg.set_vertex_parameter("D", {"x": 1, "y": 0, "z": 0})

        prod2 = Prod2()

        # Act
        result = prod2.apply(hg)

        # Assert
        assert result is None

    def test_apply_to_one_of_possibilities(self):
        """Test that production applies succesfully to one of the possible subgraphs, but only one"""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "C"}), {"R": 1, "B": 0}))

        hg.set_vertex_parameter("A", {"x": 1, "y": 2, "z": 0})
        hg.set_vertex_parameter("B", {"x": 2, "y": 1, "z": 0})
        hg.set_vertex_parameter("C", {"x": 1, "y": 0, "z": 0})
        hg.set_vertex_parameter("D", {"x": 0, "y": 1, "z": 0})

        prod2 = Prod2()

        # Act
        result = prod2.apply(hg)

        # Assert
        assert result is not None

        edges = result.get_edges()

        # Check that only 4 edges left
        assert len(edges) == 4

        # Check that 2 of the edges have R=0 and B=0
        e_edges_r0_b0 = [
            e
            for e in edges
            if e.get_type() == EdgeType.E
            and e.get_parameters().get("R") == 0
            and e.get_parameters().get("B") == 0
        ]
        assert len(e_edges_r0_b0) == 2

        # Check if both edges are between A-B and B-C or C-D and D-A
        both_edges_sets = [
            e_edges_r0_b0[0].get_vertices(),
            e_edges_r0_b0[1].get_vertices(),
        ]
        b_between_edges = (
            frozenset({"A", "B"}) in both_edges_sets
            and frozenset({"B", "C"}) in both_edges_sets
        )
        d_between_edges = (
            frozenset({"C", "D"}) in both_edges_sets
            and frozenset({"D", "A"}) in both_edges_sets
        )
        assert b_between_edges or d_between_edges

    def test_apply_only_once_when_possible_only_once(self):
        """Test that production applies succesfully to one of the possible subgraphs, but only one"""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "C"}), {"R": 1, "B": 0}))

        hg.set_vertex_parameter("A", {"x": 1, "y": 2, "z": 0})
        hg.set_vertex_parameter("B", {"x": 2, "y": 1, "z": 0})
        hg.set_vertex_parameter("C", {"x": 1, "y": 0, "z": 0})
        hg.set_vertex_parameter("D", {"x": 0, "y": 1, "z": 0})

        prod2 = Prod2()

        # Act
        result = prod2.apply(hg)

        # Assert
        assert result is not None

        result2 = prod2.apply(hg)

        # Assert
        assert result2 is None
