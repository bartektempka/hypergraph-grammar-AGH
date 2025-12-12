import itertools
from typing import Literal, Optional

from hypergrammar.productions.i_prod import IProd
from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.rfc import RFC


# def checkParamAvg(graph: Hypergraph, param: Literal["x", "y", "z"], v1: str, v2:str, v3: str):
#     x1 = graph.get_vertex_parameters(vertex=v1)[param]
#     x2 = graph.get_vertex_parameters(vertex=v2)[param]
#     x3 = graph.get_vertex_parameters(vertex=v3)[param]
#     return x3 == (x1+x2)/2


class Prod2(IProd):

    def __init__(self, rfc: Optional[RFC] = None):
        self._rfc = rfc
        super().__init__()

    def apply(self, graph: Hypergraph) -> Hypergraph | None:

        edges_e = [e for e in graph.get_edges() if e.get_type() == EdgeType.E]

        # potential e1s - first edge, to be removed, have to have R=1 and B=0
        e1s = [
            e
            for e in edges_e
            if e.get_parameters().get("R") == 1 and e.get_parameters().get("B") == 0
        ]
        for e1 in e1s:

            # v1 and v2, two od e1's verticles
            v1s = e1.get_vertices()
            all_pairs = list(itertools.combinations(v1s, 2))
            for pair in all_pairs:
                v1 = pair[0]
                v2 = pair[1]

                # potential e2s - edge connected to v1, not connected to v2 and connected to some verticle v3
                e2s = [
                    e
                    for e in edges_e
                    if v1 in e.get_vertices()
                    and v2 not in e.get_vertices()
                    and len(e.get_vertices()) > 1
                ]
                for e2 in e2s:

                    # potential v3s linked with e2, other than v1 and matching v1 and v2's averages
                    v3s = [v for v in e2.get_vertices() if v != v1]
                    #   and checkParamAvg(graph, 'x', v1, v2, v3)
                    #   and checkParamAvg(graph, 'y', v1, v2, v3)
                    #   and checkParamAvg(graph, 'z', v1, v2, v3)

                    for v3 in v3s:

                        # potential e3s - edge closing the cycle (having v2 and v3, but not v1)
                        e3s = [
                            e
                            for e in edges_e
                            if v1 not in e.get_vertices()
                            and v2 in e.get_vertices()
                            and v3 in e.get_vertices()
                        ]

                        if len(e3s) > 0:

                            # e3 found - not sure if can be more than one, just taking first possible
                            e3 = e3s[0]

                            # remove e1
                            graph.remove_edge(e1)

                            # move v3 to align with v1 and v2
                            v1_params = graph.get_vertex_parameters(vertex=v1)
                            v2_params = graph.get_vertex_parameters(vertex=v2)
                            v3_x = (v1_params["x"] + v2_params["x"]) / 2
                            v3_y = (v1_params["y"] + v2_params["y"]) / 2
                            graph.set_vertex_parameter(
                                v3, {"x": v3_x, "y": v3_y}
                            )

                            # set e2 and e3 B=0 and R=0
                            new_e2 = Edge(
                                edge_type=EdgeType.E,
                                vertices=e2.get_vertices(),
                                parameters={"R": 0, "B": 0},
                            )
                            new_e3 = Edge(
                                edge_type=EdgeType.E,
                                vertices=e3.get_vertices(),
                                parameters={"R": 0, "B": 0},
                            )
                            graph.remove_edge(e2)
                            graph.remove_edge(e3)
                            graph.add_edge(new_e2)
                            graph.add_edge(new_e3)
                            return graph
        return None
