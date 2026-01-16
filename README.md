# Hypergraph Grammar AGH

## Setup

### Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies
```bash
pip install xgi pytest mypy black pylint shapely mock
```

## Development Commands

### Running Tests
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest hypergrammar/productions/tests/test_prod_0.py
```

### Type Checking
```bash
# Check all files
mypy hypergrammar/

# Check specific file
mypy hypergrammar/hypergraph.py
```

### Code Quality
```bash
# Format code with black
black hypergrammar/
```

```bash 
# Lint code with pylint
pylint hypergrammar/
```

## Usage

### Basic Usage in Python
```python
from hypergrammar.hypergraph import Hypergraph
from hypergrammar.edge import Edge, EdgeType
from hypergrammar.visualization import draw_hypergraph
from hypergrammar.productions.prod_0 import Prod0

# Create hypergraph
hg = Hypergraph()
hg.add_edge(Edge(EdgeType.E, frozenset({"A", "B"})))
hg.add_edge(Edge(EdgeType.E, frozenset({"B", "C"})))
hg.add_edge(Edge(EdgeType.E, frozenset({"C", "D"})))
hg.add_edge(Edge(EdgeType.E, frozenset({"D", "A"})))
hg.add_edge(Edge(EdgeType.Q, frozenset({"A", "B", "C", "D"}), {"R": 0}))

# Apply production
prod0 = Prod0()
new_hg = prod0.apply(hg)

# Visualize
new_hg.draw()
```
