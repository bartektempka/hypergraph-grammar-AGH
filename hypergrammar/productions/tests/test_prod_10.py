from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_10 import Prod10


class TestProd10():
    """Test suite for Production 10 (Propagating refinement to boundary edges)."""

    def _create_hexagon(self, q_r: int, e_r: int):
        """Helper to create a standard topological hexagon."""
        hg = Hypergraph()
        nodes = [f"v{i}" for i in range(6)]
        
        # Add Q (Center)
        hg.add_edge(Edge(EdgeType.S, frozenset(nodes), {"R": q_r}))
        
        # Add E (Boundary)
        for i in range(6):
            u, v = nodes[i], nodes[(i + 1) % 6]
            hg.add_edge(Edge(EdgeType.E, frozenset([u, v]), {"R": e_r}))
            
        return hg

    def test_apply_standard_propagation(self):
        """Test that P10 sets R=1 on all boundary edges when Q has R=1."""
        # Arrange
        # Q=1 (Ready), E=0 (Needs update)
        hg = self._create_hexagon(q_r=1, e_r=0) 
        prod10 = Prod10()

        # Act
        result = prod10.apply(hg)

        # Assert
        assert result is not None
        
        # Verify all E edges now have R=1
        e_edges = [e for e in result.get_edges() if e.get_type() == EdgeType.E]
        assert len(e_edges) == 6
        for e in e_edges:
            assert e.get_parameters()["R"] == 1, f"Edge {e.get_vertices()} should have R=1"

    def test_apply_partial_update(self):
        """Test that P10 updates only those E edges that are R=0."""
        # Arrange
        hg = Hypergraph()
        nodes = [f"v{i}" for i in range(6)]
        hg.add_edge(Edge(EdgeType.S, frozenset(nodes), {"R": 1}))
        
        # 3 edges have R=1, 3 edges have R=0
        for i in range(6):
            u, v = nodes[i], nodes[(i + 1) % 6]
            r_val = 1 if i % 2 == 0 else 0
            hg.add_edge(Edge(EdgeType.E, frozenset([u, v]), {"R": r_val}))

        prod10 = Prod10()

        # Act
        result = prod10.apply(hg)

        # Assert
        assert result is not None
        e_edges = [e for e in result.get_edges() if e.get_type() == EdgeType.E]
        assert all(e.get_parameters()["R"] == 1 for e in e_edges), "All edges should end up with R=1"

    def test_apply_nothing_to_do(self):
        """Test that P10 returns None if all boundary edges are already R=1."""
        # Arrange
        hg = self._create_hexagon(q_r=1, e_r=1) # Everything already marked
        prod10 = Prod10()

        # Act
        result = prod10.apply(hg)

        # Assert
        assert result is None, "Should not apply if all boundary edges are already R=1"

    def test_apply_no_anchor_q(self):
        """Test that P10 returns None if there is no Q with R=1."""
        # Arrange
        hg = self._create_hexagon(q_r=0, e_r=0) # Q is not marked for refinement
        prod10 = Prod10()

        # Act
        result = prod10.apply(hg)

        # Assert
        assert result is None, "Should not apply if Q has R=0"

    def test_apply_broken_boundary(self):
        """Test that P10 fails if the hexagon boundary is incomplete (missing edges)."""
        # Arrange
        hg = Hypergraph()
        nodes = [f"v{i}" for i in range(6)]
        hg.add_edge(Edge(EdgeType.S, frozenset(nodes), {"R": 1}))
        
        # Add only 5 edges (boundary broken)
        for i in range(5): 
            u, v = nodes[i], nodes[(i + 1) % 6]
            hg.add_edge(Edge(EdgeType.E, frozenset([u, v]), {"R": 0}))

        prod10 = Prod10()

        # Act
        result = prod10.apply(hg)

        # Assert
        assert result is None, "Should not apply if boundary is topologically incomplete"

    def test_apply_topology_mismatch(self):
        """Test that P10 ignores Q edges that have R=1 but aren't hexagons (e.g. pentagon)."""
        # Arrange
        hg = Hypergraph()
        nodes = [f"v{i}" for i in range(5)] # 5 nodes
        hg.add_edge(Edge(EdgeType.S, frozenset(nodes), {"R": 1}))
        
        # Add 5 boundary edges
        for i in range(5):
            u, v = nodes[i], nodes[(i + 1) % 5]
            hg.add_edge(Edge(EdgeType.E, frozenset([u, v]), {"R": 0}))

        prod10 = Prod10()

        # Act
        result = prod10.apply(hg)

        # Assert
        assert result is None, "Should check that Q has exactly 6 vertices"
