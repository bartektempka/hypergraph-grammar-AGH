import uuid
from hypergrammar.edge import Edge


def canonical_rotation(seq: list[str]) -> tuple[str, ...]:
    min_index = seq.index(min(seq))
    return tuple(seq[min_index:] + seq[:min_index])


def generate_vertex_name() -> str:
    id_len = 4
    return str(uuid.uuid4())[:id_len]


def get_edge_color(edge: Edge) -> str:
    if edge.parameters.get("R") == 1 and edge.parameters.get("B") == 1:
        return "purple"
    if edge.parameters.get("R") == 1:
        return "red"
    if edge.parameters.get("B") == 1:
        return "blue"

    return "black"
