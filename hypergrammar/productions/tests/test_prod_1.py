from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_1 import Prod1

class TestProd1:
    """Test suite for Production 1."""

    def test_apply_with_valid_q_edge_r1(self):
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))
        hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 1}))
        prod1 = Prod1()
        result = prod1.apply(hg)
        assert result is not None
        edges = result.get_edges()
        # Q edge with R=1 should still exist
        q_edges_r1 = [e for e in edges if e.get_type() == EdgeType.Q and e.get_parameters().get("R") == 1]
        assert len(q_edges_r1) == 1
        # E edges should have R=1
        e_edges_r1 = [e for e in edges if e.get_type() == EdgeType.E and e.get_parameters().get("R") == 1]
        assert len(e_edges_r1) == 4
    
    def test_apply_with_no_q_edge(self):
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        prod1 = Prod1()
        result = prod1.apply(hg)
        assert result is None
    
    def test_apply_with_q_edge_r0(self):
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))
        hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 0}))
        prod1 = Prod1()
        result = prod1.apply(hg)
        assert result is None
    
    def test_apply_with_missing_e_edge(self):
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        # Missing E edge between D and A
        hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 1}))
        prod1 = Prod1()
        result = prod1.apply(hg)
        assert result is None
    
    def test_apply_empty_hypergraph(self):
        hg = Hypergraph()
        prod1 = Prod1()
        result = prod1.apply(hg)
        assert result is None
    
    def test_check_cycle_valid_square(self):
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))
        prod1 = Prod1()
        cycle = ["A", "B", "C", "D"]
        assert prod1._check_cycle(hg, cycle) is True
    
    def test_check_cycle_invalid_square(self):
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        # Missing edge between C and D
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))
        prod1 = Prod1()
        cycle = ["A", "B", "C", "D"]
        assert prod1._check_cycle(hg, cycle) is False
    
    def test_get_edges_returns_correct_edges(self):
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))
        prod1 = Prod1()
        cycle = ["A", "B", "C", "D"]
        edges = prod1._get_edges(hg, cycle)
        assert all(e is not None for e in edges)
        assert len(edges) == 4