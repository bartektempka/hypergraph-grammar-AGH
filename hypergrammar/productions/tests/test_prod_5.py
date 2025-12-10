from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_5 import Prod5

class TestProd5:
    """Test suite for Production 5."""

    def test_apply_with_valid_q_edge_r1_and_broken_edges(self):
        hg = Hypergraph()
        # Vertices: A, B, C, D; intermediates: X, Y, Z, W
        # Each E edge is 'broken' via an intermediate
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "X"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"X", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "Y"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"Y", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "Z"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"Z", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "W"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"W", "A"})))
        hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 1}))
        prod5 = Prod5()
        result = prod5.apply(hg)
        assert result is not None
    
    def test_apply_with_no_q_edge(self):
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "X"})))
        prod5 = Prod5()
        result = prod5.apply(hg)
        assert result is None
    
    def test_apply_with_q_edge_r0(self):
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "X"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"X", "B"})))
        hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 0}))
        prod5 = Prod5()
        result = prod5.apply(hg)
        assert result is None
    
    def test_apply_with_missing_broken_edge(self):
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "X"})))
        # Missing E edge X-B
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "Y"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"Y", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "Z"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"Z", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "W"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"W", "A"})))
        hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 1}))
        prod5 = Prod5()
        result = prod5.apply(hg)
        assert result is None
    
    def test_apply_empty_hypergraph(self):
        hg = Hypergraph()
        prod5 = Prod5()
        result = prod5.apply(hg)
        assert result is None
    
    def test_e_edges_match_private_method(self):
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "X"})))
        prod5 = Prod5()
        assert prod5._e_edges_match(hg, frozenset({"A", "X"})) is True
        assert prod5._e_edges_match(hg, frozenset({"X", "B"})) is False
    
    def test_check_all_edges_broken(self):
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "X"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"X", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "Y"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"Y", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "Z"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"Z", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "W"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"W", "A"})))
        prod5 = Prod5()
        cycle = ("A", "B", "C", "D")
        result = prod5._check_all_edges_broken(hg, cycle)
        assert result is not False
        assert len(result) == 4
    
    def test_get_broken_edge_other(self):
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "X"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"X", "B"})))
        prod5 = Prod5()
        other = prod5.get_broken_edge_other(hg, "A", "B", {"A", "B"})
        assert other == "X"

