from __future__ import annotations
from typing import Protocol, Any, Mapping, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from hypergrammar.edge import Edge
    from hypergrammar.hypergraph import Hypergraph


class RFC(Protocol):
    """Refinement criterion protocol.

    Implementations should provide an `is_valid(edge, hypergraph, meta)`
    method that returns a boolean: True when edge should be flagged for refinement,
    False when the refinement is not needed.
    """

    def is_valid(
        self,
        edge: Edge,
        hypergraph: Hypergraph,
        meta: Optional[Mapping[str, Any]] = None,
    ) -> bool: ...


__all__ = ["RFC"]
