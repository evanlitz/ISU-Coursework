# CS418 Project: Trapezoidal Map Point Location

**Course**: CS418 – Computational Geometry, Iowa State University

## Overview

Implements point location in a planar subdivision using a **trapezoidal map** and a **DAG (Directed Acyclic Graph)** search structure. Given a planar subdivision encoded as a DCEL, the program builds a trapezoidal map via randomized incremental segment insertion and answers point location queries in expected O(log n) time.

## Algorithm

1. Parse a DCEL input file to extract vertices, half-edges, and faces.
2. Initialize a bounding-box trapezoid and its corresponding DAG leaf.
3. Randomly permute the segments and insert each one into the map:
   - Find all trapezoids intersected by the segment by walking the DAG.
   - Split trapezoids above and below the segment; merge adjacent ones that share the same top/bottom edges.
   - Replace DAG leaf nodes with subtrees of **XNodes** (vertical splits) and **YNodes** (segment splits).
4. Answer queries by walking the DAG from the root until reaching a leaf, then classify the point as lying on a vertex, on an edge, or in a face interior.

Expected construction time: **O(n log n)**. Expected query time: **O(log n)**.

## Files

| File | Description |
|------|-------------|
| `main.py` | Entry point; handles file I/O and the interactive query loop |
| `objects.py` | Data structures: `Vertex`, `HalfEdge`, `Face`, `Trapezoid`, `XNode`, `YNode`, `Leaf` |
| `trapezoid_map.py` | Core algorithm: DCEL parsing, map construction, DAG updates, queries, visualization |

## Usage

```
python main.py
```

When prompted, provide the path to a DCEL input file. The program will build the trapezoidal map, then enter a loop where you can query individual points. Results are printed to the screen and written to an output file. A visualization of the trapezoidal map is displayed if `matplotlib` is available.

### DCEL Input Format

The input file should contain `vertex`, `half_edge`, and `face` records describing a valid planar subdivision. See the course materials for the exact format.

## Dependencies

- Python 3
- `matplotlib` (optional, for visualization)
