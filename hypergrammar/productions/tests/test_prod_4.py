from mock import patch

from hypergrammar.edge import Edge, EdgeType
from hypergrammar.hypergraph import Hypergraph
from hypergrammar.productions.prod_4 import Prod4


class TestProd4:
    """Test suite for Production 4."""

    def test_func(self):
        """Test that production returns None when there is no Q edge."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        # hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.set_vertex_parameter("A", {"x": 1, "y": 1})
        hg.set_vertex_parameter("B", {"x": 0, "y": 0})

        new_vert = "C"

        with patch.object(Prod4, "get_new_vert") as mocked_prod:
            mocked_prod.return_value  = new_vert
        # Act
            result = Prod4().apply(hg)
            

            # Assert
            assert result is not None
            edges = result.get_edges()
            e_edges_= [
                e
                for e in edges
                if e.get_type() == EdgeType.E
            ]
            assert len(e_edges_) == 2
            
            print(e_edges_)
            print(hg.get_vertex_parameters(new_vert))
            assert hg.get_vertex_parameters(new_vert) == {'x': 0.5, "y" : 0.5}
            
    
    
        
    def test_apply_with_no_e_edge(self):
        """Test that production returns None when there is no Q edge."""
        # Arrange
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.Q, frozenset({"B", "C"})))

        prod0 = Prod4()

        # Act
        result = prod0.apply(hg)

        # Assert
        assert result is None

    def test_raises_value_error_for_invalid_vertex_count(self):
        """Test that ValueError is raised if E edge connects 3 vertices instead of 2."""
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B", "C"})))

        prod4 = Prod4()

        try:
            prod4.apply(hg)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "must connect exactly 2 vertices" in str(e)

    def test_apply_returns_none_when_rfc_blocks(self):
        """Test that production applies nothing if RFC returns False."""
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.set_vertex_parameter("A", {"x": 0, "y": 0})
        hg.set_vertex_parameter("B", {"x": 2, "y": 2})

        class BlockingRFC:
            def is_valid(self, edge, hypergraph, meta=None):
                return False

        prod4 = Prod4(rfc=BlockingRFC())

        result = prod4.apply(hg)

        assert result is None

    def test_apply_empty_graph(self):
        """Test that production returns None for empty graph."""
        hg = Hypergraph()
        prod4 = Prod4()

        result = prod4.apply(hg)

        assert result is None

    def test_apply_skips_invalid_edge_and_processes_next(self):
        """Test that if RFC rejects the first edge, production continues to the next one."""
        hg = Hypergraph()

        edge_blocked = Edge(EdgeType.E, frozenset({"A", "B"}))
        edge_allowed = Edge(EdgeType.E, frozenset({"C", "D"}))

        hg.add_edge(edge_blocked)
        hg.add_edge(edge_allowed)

        hg.set_vertex_parameter("A", {"x": 0, "y": 0})
        hg.set_vertex_parameter("B", {"x": 0, "y": 0})
        hg.set_vertex_parameter("C", {"x": 0, "y": 0})
        hg.set_vertex_parameter("D", {"x": 2, "y": 2})

        class SelectiveRFC:
            def is_valid(self, edge, hypergraph, meta=None):
                return edge == edge_allowed

        prod4 = Prod4(rfc=SelectiveRFC())
        result = prod4.apply(hg)

        assert result is not None

        remaining_edges = list(result.get_edges())
        assert edge_blocked in remaining_edges
        assert edge_allowed not in remaining_edges

    def test_new_edges_have_correct_parameters(self):
        """Test that newly created E edges have R=0 parameter."""
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.set_vertex_parameter("A", {"x": 0, "y": 0})
        hg.set_vertex_parameter("B", {"x": 2, "y": 2})

        with patch.object(Prod4, "get_new_vert") as mocked_prod:
            mocked_prod.return_value = "NewV"
            result = Prod4().apply(hg)

            edges = result.get_edges()
            new_edges = [e for e in edges if "NewV" in e.get_vertices()]

            assert len(new_edges) == 2
            for e in new_edges:
                assert e.get_parameters().get("R") == 0


if __name__ == "__main__":
    test = TestProd4()
    try:
        test.test_func()
        test.test_apply_with_no_e_edge()
        test.test_raises_value_error_for_invalid_vertex_count()
        test.test_apply_returns_none_when_rfc_blocks()
        test.test_apply_empty_graph()
        test.test_apply_skips_invalid_edge_and_processes_next()
        test.test_new_edges_have_correct_parameters()
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")

