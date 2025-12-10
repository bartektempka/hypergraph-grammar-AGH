from hypergrammar.hypergraph import Hypergraph
from hypergrammar.utils import generate_vertex_name
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_4 import Prod4
from mock import patch

class TestProd0:
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


