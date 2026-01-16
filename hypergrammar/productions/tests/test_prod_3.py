import unittest
from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.productions.prod_3 import Prod3

class TestProd3(unittest.TestCase):

    def setUp(self):
        self.prod = Prod3()

    def test_1_minimal_working_example(self):
        """Test Prod3 on graph on minimal working example graph"""
        hg = Hypergraph()

        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"}), {"R": 1, "B": 0}))
        hg.set_vertex_parameter("A", {"x": 0, "y": 0})
        hg.set_vertex_parameter("B", {"x": 2, "y": 0})

        result = self.prod.apply(hg)
        
        self.assertIsNotNone(result, "Production should be applied")
        self.assertEqual(len(result.get_edges()), 3, "Production should generate 3 edges")

        vertices = set(hg._node_parameters.keys())
        new_v = (vertices - {"A", "B"}).pop()
        params = result.get_vertex_parameters(new_v)

        self.assertEqual(params["x"], 1.0)
        self.assertEqual(params["y"], 0.0)

    def test_2_subgraph(self):
        """Test Prod3 on graph that contains desired edge"""
        hg = Hypergraph()

        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"}), {"R": 1, "B": 0}))
        # Another suitable edge but we only apply P3 to first one we find
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"}), {"R": 1, "B": 0}))

        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"}), {"R": 0, "B": 0}))
        hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 0}))
        
        hg.set_vertex_parameter("A", {"x": 0, "y": 0})
        hg.set_vertex_parameter("B", {"x": 2, "y": 0})
        hg.set_vertex_parameter("C", {"x": 2, "y": 2})
        hg.set_vertex_parameter("D", {"x": 0, "y": 2})

        initial_edges_count = len(hg.get_edges())
        result = self.prod.apply(hg)

        self.assertIsNotNone(result)
        self.assertEqual(len(result.get_edges()), initial_edges_count + 2)

    def test_3_missing_vertex(self):
        """Test Prod3 on graph with missing vertex"""
        hg = Hypergraph()

        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"}), {"R": 1, "B": 0}))
        hg.set_vertex_parameter("A", {"x": 0, "y": 0})

        result = self.prod.apply(hg)
        self.assertIsNone(result, "Production should not be applied when missing vertex")

    def test_4_missing_edge(self):
        """Test Prod3 on graph without edges"""
        hg = Hypergraph()
        hg.set_vertex_parameter("A", {"x": 0, "y": 0})
        hg.set_vertex_parameter("B", {"x": 2, "y": 0})
        
        result = self.prod.apply(hg)
        self.assertIsNone(result, "Production should not be applied when there are no edges")

    def test_5_incorrect_label(self):
        """Test Prod3 on graph with incorrect label"""
        hg = Hypergraph()
        # Case 1: R=0
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"}), {"R": 0, "B": 0}))
        hg.set_vertex_parameter("A", {"x": 0, "y": 0})
        hg.set_vertex_parameter("B", {"x": 2, "y": 0})

        result = self.prod.apply(hg)
        self.assertIsNone(result, "R=0 should not apply production")

        # Case 2: B=1
        hg_boundary = Hypergraph()
        hg_boundary.add_edge(Edge(EdgeType.E, frozenset({"A", "B"}), {"R": 1, "B": 1}))
        hg_boundary.set_vertex_parameter("A", {"x": 0, "y": 0})
        hg_boundary.set_vertex_parameter("B", {"x": 2, "y": 0})
        
        result_b = self.prod.apply(hg_boundary)
        self.assertIsNone(result_b, "B=1 should not apply production")

    def test_6_incomplete_coordinates(self):
        """Test Prod3 on graph with incomplete x or y coordinates"""
        hg = Hypergraph()
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"}), {"R": 1, "B": 0}))

        hg.set_vertex_parameter("A", {"x": 0}) 
        hg.set_vertex_parameter("B", {"x": 2, "y": 0})

        result = self.prod.apply(hg)
        self.assertIsNone(result, "Incomplete coordinates should block production")
    
    def test_7_bigger_example(self):
        """Test Prod3 on bigger graph"""
        hg = Hypergraph()

        # Outside edges
        hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"}), {"R": 0, "B": 1}))
        hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"}), {"R": 0, "B": 1}))
        hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"}), {"R": 0, "B": 1}))
        hg.add_edge(Edge(EdgeType.E, frozenset({"D", "E"}), {"R": 0, "B": 1}))
        hg.add_edge(Edge(EdgeType.E, frozenset({"E", "F"}), {"R": 0, "B": 1}))
        hg.add_edge(Edge(EdgeType.E, frozenset({"F", "G"}), {"R": 0, "B": 1}))
        hg.add_edge(Edge(EdgeType.E, frozenset({"G", "H"}), {"R": 0, "B": 1}))
        hg.add_edge(Edge(EdgeType.E, frozenset({"H", "A"}), {"R": 0, "B": 1}))

        # Inside edges, only two eligible for applying P3
        hg.add_edge(Edge(EdgeType.E, frozenset({"I", "B"}), {"R": 0, "B": 0}))
        hg.add_edge(Edge(EdgeType.E, frozenset({"I", "D"}), {"R": 0, "B": 0}))
        hg.add_edge(Edge(EdgeType.E, frozenset({"I", "F"}), {"R": 1, "B": 0}))
        hg.add_edge(Edge(EdgeType.E, frozenset({"I", "H"}), {"R": 1, "B": 0}))

        # Vertices
        hg.set_vertex_parameter("A", {"x": 0, "y": 0})
        hg.set_vertex_parameter("B", {"x": 2, "y": 0})
        hg.set_vertex_parameter("C", {"x": 4, "y": 0})
        hg.set_vertex_parameter("D", {"x": 4, "y": 2})
        hg.set_vertex_parameter("E", {"x": 4, "y": 4})
        hg.set_vertex_parameter("F", {"x": 2, "y": 4})
        hg.set_vertex_parameter("G", {"x": 0, "y": 4})
        hg.set_vertex_parameter("H", {"x": 0, "y": 2})
        hg.set_vertex_parameter("I", {"x": 2, "y": 2})

        initial_edges_count = len(hg.get_edges())

        result = self.prod.apply(hg)
        self.assertIsNotNone(result, "P3 should be applied on the first time")
        result = self.prod.apply(hg)
        self.assertIsNotNone(result, "P3 should be applied on the second time")

        self.assertEqual(len(result.get_edges()), initial_edges_count + 4)