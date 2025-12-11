import pytest
from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_7 import Prod7

# Helper to mock EdgeType.P if it doesn't exist in the environment yet
if not hasattr(EdgeType, 'P'):
    # This is a runtime hack for testing if the Enum cannot be modified directly
    import aenum
    aenum.extend_enum(EdgeType, 'P', 99)

class TestProd7:
    """Test suite for Production 7."""

    def test_apply_valid_p7(self):
        """Test that P7 applies correctly to a valid pentagon with R=1."""
        hg = Hypergraph()
        
        # Vertices
        verts = ["v1", "v2", "v3", "v4", "v5"]
        
        # 1. Create boundary E edges (Pentagon cycle)
        # (v1-v2, v2-v3, v3-v4, v4-v5, v5-v1)
        # Start with arbitrary R values (e.g., R=0) to verify they change to 1
        hg.add_edge(Edge(EdgeType.E, frozenset({"v1", "v2"}), {"R": 0, "B": 10}))
        hg.add_edge(Edge(EdgeType.E, frozenset({"v2", "v3"}), {"R": 0, "B": 20}))
        hg.add_edge(Edge(EdgeType.E, frozenset({"v3", "v4"}), {"R": 0, "B": 30}))
        hg.add_edge(Edge(EdgeType.E, frozenset({"v4", "v5"}), {"R": 0, "B": 40}))
        hg.add_edge(Edge(EdgeType.E, frozenset({"v5", "v1"}), {"R": 0, "B": 50}))

        # 2. Create the central P edge with R=1 (Required condition)
        hg.add_edge(Edge(EdgeType.P, frozenset(verts), {"R": 1}))

        prod7 = Prod7()
        result = prod7.apply(hg)

        assert result is not None
        
        edges = result.get_edges()
        
        # Check P edge still exists with R=1
        p_edges = [e for e in edges if e.get_type() == EdgeType.P]
        assert len(p_edges) == 1
        assert p_edges[0].get_parameters()["R"] == 1
        
        # Check E edges
        e_edges = [e for e in edges if e.get_type() == EdgeType.E]
        assert len(e_edges) == 5
        
        # Verify ALL E edges now have R=1
        for edge in e_edges:
            assert edge.get_parameters()["R"] == 1
            # Verify B params are preserved (check one as example)
            # Since edges are re-created, we check set properties
            
        # Verify specific B value preservation for one edge
        e_v1_v2 = next(e for e in e_edges if e.get_vertices() == frozenset({"v1", "v2"}))
        assert e_v1_v2.get_parameters()["B"] == 10

    def test_apply_fails_if_p_has_wrong_r(self):
        """Test that P7 does NOT apply if P edge has R != 1."""
        hg = Hypergraph()
        verts = ["v1", "v2", "v3", "v4", "v5"]
        
        # Add cycle
        hg.add_edge(Edge(EdgeType.E, frozenset({"v1", "v2"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"v2", "v3"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"v3", "v4"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"v4", "v5"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"v5", "v1"})))

        # Add P edge with R=0 (Should fail)
        hg.add_edge(Edge(EdgeType.P, frozenset(verts), {"R": 0}))

        prod7 = Prod7()
        result = prod7.apply(hg)
        assert result is None

    def test_apply_fails_broken_topology(self):
        """Test that P7 does NOT apply if the E-edges do not form a closed pentagon."""
        hg = Hypergraph()
        verts = ["v1", "v2", "v3", "v4", "v5"]
        
        # Broken cycle (missing v5-v1)
        hg.add_edge(Edge(EdgeType.E, frozenset({"v1", "v2"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"v2", "v3"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"v3", "v4"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"v4", "v5"})))
        # Missing v5-v1 edge

        hg.add_edge(Edge(EdgeType.P, frozenset(verts), {"R": 1}))

        prod7 = Prod7()
        result = prod7.apply(hg)
        assert result is None

    def test_apply_fails_wrong_vertex_count(self):
        """Test that P7 does not apply to a square (4 vertices) even if labeled P."""
        hg = Hypergraph()
        verts = ["v1", "v2", "v3", "v4"]
        
        hg.add_edge(Edge(EdgeType.E, frozenset({"v1", "v2"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"v2", "v3"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"v3", "v4"})))
        hg.add_edge(Edge(EdgeType.E, frozenset({"v4", "v1"})))

        hg.add_edge(Edge(EdgeType.P, frozenset(verts), {"R": 1}))

        prod7 = Prod7()
        result = prod7.apply(hg)
        assert result is None