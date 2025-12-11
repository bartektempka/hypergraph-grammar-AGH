import uuid


def canonical_rotation(seq: list[str]) -> tuple[str, ...]:
    min_index = seq.index(min(seq))
    return tuple(seq[min_index:] + seq[:min_index])


def generate_vertex_name():
    return str(uuid.uuid4())[:8]
