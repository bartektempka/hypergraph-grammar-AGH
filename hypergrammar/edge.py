from enum import Enum, auto


class EdgeType(Enum):
  
    E = auto() # E represent edges of the polygon
    Q = auto() # Q represent interior nodes of quadrilateral elements
    P = auto() # P represent interior nodes of pentagonal elements

class Edge:
    def __init__(
        self,
        edge_type: EdgeType,
        vertices: frozenset[str],
        parameters: dict[str, int] | None = None,
    ):
        self.edge_type = edge_type
        self.vertices = vertices
        self.parameters = parameters or {}

    def get_type(self) -> EdgeType:
        return self.edge_type

    def get_vertices(self) -> frozenset[str]:
        return self.vertices

    def get_parameters(self) -> dict[str, int]:
        return self.parameters

    def set_parameter(self, param: str, value: int) -> None:
        self.parameters[param] = value

    def __hash__(self) -> int:
        return hash((self.edge_type, self.vertices, frozenset(self.parameters.items())))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Edge):
            return NotImplemented
        return (
            self.edge_type == other.edge_type
            and self.vertices == other.vertices
            and self.parameters == other.parameters
        )

    def __str__(self) -> str:
        return f"{self.edge_type.name}"

    def __repr__(self) -> str:
        return (
            f"Edge(type={self.edge_type}, "
            f"vertices={self.vertices}, "
            f"parameters={self.parameters})"
        )
