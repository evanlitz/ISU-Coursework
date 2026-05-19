from objects import *
import random

EPSILON = 0.000001

# Read the DCEL input file and build three dictionaries: this incudes vertices, half-edges, and faces
def parse_dcel(filename):
    # Output the dictionaries keyed by name mapping to their obkects. Dictionaries of vertices, half_edges, faces
    vertices   = {}     # Vertices (v#)
    half_edges = {}     # Half edges (e#,#)
    faces      = {}     # Faces (f#)

    # Read the entire file and split on blank lines to find record blocks
    with open(filename, 'r') as f:     
        content = f.read()

    # Blocks wiil hold each group of consecutive non-empty lines as a list of strings
    blocks = []
    current_block = []

    # Strip the leading and trailing whitespace to handle the indentation and line endings
    for line in content.splitlines():
        stripped = line.strip()

        # Blank line signales the end of a record block, so save it and start a new one
        if stripped == '':
            if current_block:
                blocks.append(current_block)
                current_block = []
        
        # Non-blank lines belong to the current block. 
        else:
            current_block.append(stripped)
    
    # Handle the files that do not end with trailing blank line
    if current_block:
        blocks.append(current_block)

    # Use first character of block's first line to identigy which record type it is.
    # v = vertec block, f = face block, e = half edge block
    for block in blocks:
        first_char = block[0][0]

        if first_char == 'v':
            for line in block:
                # Firrst token is the vertex name
                tokens = line.split()
                name  = tokens[0]

                # Strip out the contents between parentheses to get exact x and y coordinates, then parse the x and y as floats
                coord = line[line.index('(')+1 : line.index(')')]
                x, y  = [float(c.strip()) for c in coord.split(',')]

                # Last token is the name of incident half-edge that is leaving this vertex
                inc   = tokens[-1]

                # Store the new Vertex object and differentiate it through its unique name
                vertices[name] = Vertex(name, x, y, inc)

        elif first_char == 'f':
            for line in block:
                tokens     = line.split()
                
                # File format is face_name, outer_compoennt, and inner_components
                name       = tokens[0]
                outer_str  = tokens[1]
                inner_str  = tokens[2] if len(tokens) > 2 else 'nil'

                # Set outer to none because it is the unbounded outer face with no enclosing boundary
                outer = None if outer_str == 'nil' else outer_str
                if inner_str == 'nil':
                    inner = []
                else:
                    # Inner components are half edge names seperated by semicolons.
                    inner = [x.strip().rstrip(';') for x in inner_str.split(';') if x.strip()]
                
                # Constructor: Face(name, inner_components, outer_component)
                faces[name] = Face(name, inner, outer)

        elif first_char == 'e':
            for line in block:
                tokens = line.split()
                
                # File columns are name, origin_vertex, twin_edge, incident_face, next_edge, and prev_edge
                name, origin, twin, face, next_e, prev_e = tokens

                # Constructor: HalfEdge(name, twin, face, origin, previous_edge, next_edge)
                half_edges[name] = HalfEdge(name, twin, face, origin, prev_e, next_e)

    return faces, half_edges, vertices

# Create a large rectange around all input vertices.
# This will then be the initial bounding trapezoid.
# All input segments will be inserted inside this box
def build_bounding_box(vertices):
    
    # Collect all of the x and y coordinates from input vertices to find the extent of the subdivision
    x_list = [v.x for v in vertices.values()]
    y_list = [v.y for v in vertices.values()]

    # Set pad to 1.0 to make sure that the bounding box contains all vertices with enough room to spare.
    pad = 1.0

    # Expand the bounding box by padding value (1.0) in all four directions
    x_min = min(x_list) - pad
    y_min = min(y_list) - pad

    x_max = x_max = max(x_list) + pad
    y_max = y_max = max(y_list) + pad

    # Intialize the four corner vertices of the bounding box. 
    c1 = Vertex('c1', x_min, y_max, 'L')   # upper-left corner
    c2 = Vertex('c2', x_min, y_min, 'B')   # lower-left corne r
    c3 = Vertex('c3', x_max, y_min, 'T')   # lower-right corner
    c4 = Vertex('c4', x_max, y_max, 'R')   # upper-right corner

    # Half-edges that represent the four walls of the bounding box
    # Used as the top and bottom of the initial trapezoid
    # No twin or next or prev are ever needed because these are never split or traversed as DCEL edges
    L = HalfEdge('L', 'c1', 'L', None, None, None)
    R = HalfEdge('R', 'c3', 'R', None, None, None)
    T = HalfEdge('T', 'c1', 'T', None, None, None)
    B = HalfEdge('B', 'c2', 'B', None, None, None)

    # Return in order of how the build trapezoidal map unpacks
    return c1, c2, c4, c3, L, R, T, B, x_min, x_max, y_min, y_max

# Create the starting trapezoid that fills the whole bounding box.
# ALso wrap it in a Leaf to form the initial one node DAG
def initialize_trapezoid(Trap_top, Trap_bottom, leftp_vertex, rightp_vertex):
    
    # This is the initali trapezoid that spans bounding box. top = T wall and bottom = B wall
    # leftp = upper left corner and rightp = upper right corner.
    t0 = Trapezoid(Trap_top, Trap_bottom, leftp_vertex, rightp_vertex)
    
    # Leaf is the DAG root at this point, so all queries walk to this leaf until first segment is inserted and leaf is replaced by x node or y node.
    root = Leaf(t0)
    return t0, root     # the root is the DAG root

# Return true if v1 comes before v2 in left to right order and break ties by bottom to top.
# This is used in a lot of places when segment direction decision is needed.
# General position tie breaking rule
def vertex_order(v1, v2):
    if abs(v1.x - v2.x) > EPSILON:
        return v1.x < v2.x
    return v1.y < v2.y

# Returns the leftmost endpoint of the undirected segment represented by passed in half_edge.
# Every segment has two directed half edgesm and this is  the p endpoint.
def left_endpoint(half_edge, halfedges, vertices) :
    origin = vertices[half_edge.origin]
    destination = vertices[halfedges[half_edge.twin].origin]
    return origin if vertex_order(origin, destination) else destination

# Determines if the point p lies above the directed segment using 2D cross product. 
# Geometric test for y-node queries in the DAG
def is_point_above_segment(p, segment, vertices, halfedges):
    
    # Left endpoint of the segment (origin of half-edge)
    a = vertices[segment.origin]

    # Right endpoint of the segment 
    b = vertices[halfedges[segment.twin].origin]

    # 2D cross product of vector a-b with a-p
    # Positive means p is to left of a-b and above the segment
    # Zero means p is on the line through a-b
    # Negative menas p is to the right and below the segment
    cross = (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x)

    # Return true or false depending on if epsilon value is amassed to avoid false positives
    return cross > EPSILON


def get_segments(halfedges, vertices):
    # Build a list of segments to insert into trapezoidal map
    # Each undirected edge in DCEL is represented by two half edges (twins)
    # Pick exactly one per edge and then orient it so its origin is the left endpoint.
    visited = set()
    segments = []
    for h_e in halfedges.values() :
        if h_e.name in ('L', 'R', 'T', 'B'):    # Skip four bounding box sentinel edges, as not input segments
            continue
        if h_e.name in visited or h_e.twin in visited:      # Skip if we processed this undirected edge through the other half-edge
            continue
        
        # Label the edge as seen so the twin is skipped on later iteration
        visited.add(h_e.name)

        # Two endpoints of this undirected edge
        origin = vertices[h_e.origin]
        twin_origin = vertices[halfedges[h_e.twin].origin]

        # Always store the half edge whose origin is the lexigraphic left endpoint. Must run left to right
        if vertex_order(origin, twin_origin):
            segments.append(h_e)
        else :
            segments.append(halfedges[h_e.twin])
    return segments


# Randomly shuffle the segment list in place. 
# Used for randomized incremental construction algorithm that needs segments to be inserted in random order for O(n log n) build time and O(log n) query time through backward analysis
def random_permutation(segments):
    random.shuffle(segments)
    return segments

# Return the ordered list of trapezoids that segment p--q passes through in trapezoidal map.
# These are tapezoids that are split when segment is inserted
def get_intersected_trapezoids(segment, dag_root, vertices, halfedges):

    # p is the lexicographic left endpoint, and q is the lexicographic right endpoint
    p = vertices[segment.origin]
    q = vertices[halfedges[segment.twin].origin]

    # Find the trapezoid that contains p by walking the DAG
    first_trapezoid = query_dag(p, dag_root, vertices, halfedges)

    traps = [first_trapezoid]
    current = first_trapezoid

    # Walk right as long as the current trapezoid's right boundary has not reached q
    while vertex_order(current.rightp, q):
        
        # Right boundary vertex is above the segment, so segment exits through lower right neighbor. Else the right boundary vertex is below or on segment, so segment exits through upper right neighbor
        if is_point_above_segment(current.rightp, segment, vertices, halfedges):
            current = current.lower_right
        else :
            current = current.upper_right
        traps.append(current)

    return traps
    
# Return true if two vertices are at same position in float point tolerance
def lex_equal(v1, v2):
    return abs(v1.x - v2.x) < EPSILON and abs(v1.y - v2.y) < EPSILON

# Turn existing leaf node into a different DAG node type without obstructing parent pointers. All nodes that point to this leaf will still point to the same object.
def replace_leaf(leaf, new_node):
    leaf.__class__ = new_node.__class__         # Change object type
    leaf.__dict__ = new_node.__dict__.copy()    # Replace all instance attributes with one of new node.

# Updates the DAG after insertion of a segment p-->q
# For old trapezoid delta that the segment crosses, the leaf node is replaced with subtree that routes quieries to correct new trapezoid.
def update_dag(traps, segment, p, q, upper_map, lower_map, left_trap, right_trap):
    
    
    for i, delta in enumerate(traps):
        is_first = (i == 0)
        is_last  = (i == len(traps) - 1)

        # NEw trapezoid above andd below the segment for this slot.
        # Upper map and lower map can point to same trapezoid when adjacent
        # Old trapezoids are merged into one with shared top or shared bottom edge .

        upper = upper_map[i]
        lower = lower_map[i]

        # Get or create leaves for upper and lower. Shared if they are merged.
        # IF the trapezoid was just created, then it has no leaf yet and need to build manually
        # IF it was already merged from prev iteration, then reuse the leaf so multiple y-nodes in DAG point to the same leaf with correct sharing
        if upper.leaf is None:
            upper.leaf = Leaf.__new__(Leaf)
            upper.leaf.trapezoid = upper
        upper_leaf = upper.leaf

        # Same code as above except for the lower
        if lower.leaf is None:
            lower.leaf = Leaf.__new__(Leaf)
            lower.leaf.trapezoid = lower
        lower_leaf = lower.leaf

        # The inner node splits the above vs the below the segment
        # Every replaced leaf gets at minimum at this y node --> go above = upper trap and go below = lower trap.
        y_node = YNode(segment)
        y_node.above = upper_leaf
        y_node.below = lower_leaf

        # Build the full subtree that replaces delta.leaf
        # The segment fits entirely one trapezoid and up to 4 new trapezoids
        # This includes the left end cap, the above segment and below segment, and the right end cap
        if is_first and is_last:

            # p is inside delta but q coincides with delta's right boundary
            # DAG subtree: XNode(p) -> left  = Leaf(left_trap) and right = y_node
            if left_trap is not None and right_trap is not None:
                x_q = XNode(q)
                x_q.left  = y_node
                x_q.right = Leaf(right_trap)
                x_p = XNode(p)
                x_p.left  = Leaf(left_trap)
                x_p.right = x_q
                replace_leaf(delta.leaf, x_p)

            # p is strictly inside the delta but q conincides with delta's right bundary. DAG subtree is XNode(p) --> left = Leaf(Left_trap) and Right = y_node
            elif left_trap is not None:
                x_p = XNode(p)
                x_p.left  = Leaf(left_trap)
                x_p.right = y_node
                replace_leaf(delta.leaf, x_p)

            # p conincides with delta's left boundary but q is inside the DAG subtree with XNode(q) --> Left = y_node and right = Leaf(right_trap_)
            elif right_trap is not None:
                x_q = XNode(q)
                x_q.left  = y_node
                x_q.right = Leaf(right_trap)
                replace_leaf(delta.leaf, x_q)

            # Both endpoints coincide with existing boundaries so just y-node
            else:
                replace_leaf(delta.leaf, y_node)

        # First of the trapezoids that the segment crosses, so only p's x node is needed as q's x-node goes in the last trapezoid
        elif is_first:
            # p is strictly indside and insert the x-node for p
            if left_trap is not None:
                x_p = XNode(p)
                x_p.left  = Leaf(left_trap)
                x_p.right = y_node
                replace_leaf(delta.leaf, x_p)
            # q coincides with delta's right boundary and just the y node
            else:
                replace_leaf(delta.leaf, y_node)

        # Last of the trapezoids that the segment crosses, and only q's x-node is needed
        elif is_last:
            if right_trap is not None:
                x_q = XNode(q)
                x_q.left  = y_node
                x_q.right = Leaf(right_trap)
                replace_leaf(delta.leaf, x_q)
            else:
                # q coincides with delta's right boundary and just the y node
                replace_leaf(delta.leaf, y_node)

        else:
            # Middle trapezoid that the segment passes traight through, so no end caps are needed.
            replace_leaf(delta.leaf, y_node)

# Updates all trapezoid neighbor pointers after segment insertion: Including upper_left, upper_right, lower_left, lower_right
# Goes in both directions, as if A.upper_right = B then B.upper_left = A
# 
# Pointers ???????????
def _set_neighbors(left_trap, right_trap, above_traps, below_traps, old_traps):
    
    # Connect the left end cap to the first above or below trapezoid if left trap is not none
    if left_trap is not None:
        left_trap.upper_right = above_traps[0]
        left_trap.lower_right = below_traps[0]
        above_traps[0].upper_left = left_trap
        below_traps[0].lower_left = left_trap

    # Connect consecutive above segment trapezoids in left to right order
    for i in range(len(above_traps) - 1):
        above_traps[i].upper_right = above_traps[i + 1]
        above_traps[i + 1].upper_left = above_traps[i]

    # Connect consecutive below segment trapezoids in left to right order
    for i in range(len(below_traps) - 1):
        below_traps[i].lower_right = below_traps[i + 1]
        below_traps[i + 1].lower_left = below_traps[i]

    # Connect the last above and below trapezoid to the right end cap
    if right_trap is not None:
        above_traps[-1].upper_right = right_trap
        below_traps[-1].lower_right = right_trap
        right_trap.upper_left = above_traps[-1]
        right_trap.lower_left = below_traps[-1]
    # No right end cap so inherid what was to the right of the last old trapezoid
    else:
        above_traps[-1].upper_right = old_traps[-1].upper_right
        below_traps[-1].lower_right = old_traps[-1].lower_right
        # Update the neighbors left pointers to point back to the new traps
        if old_traps[-1].upper_right:
            old_traps[-1].upper_right.upper_left = above_traps[-1]
        if old_traps[-1].lower_right:
            old_traps[-1].lower_right.lower_left = below_traps[-1]
    # Adjust the left neighbors of the first old trapezoid to point to the new traps
    prev_upper = old_traps[0].upper_left
    prev_lower = old_traps[0].lower_left
    if prev_upper is not None:
        if left_trap is not None:
            
            # Left endcap sits between the prev_upper and new above traps

            prev_upper.upper_right = left_trap
            left_trap.upper_left = prev_upper
        else:
            # No left end cap so prev_upper connects to the first above
            prev_upper.upper_right = above_traps[0]
            above_traps[0].upper_left = prev_upper
    if prev_lower is not None:
        if left_trap is not None:
            prev_lower.lower_right = left_trap
            left_trap.lower_left = prev_lower
        else:
            prev_lower.lower_right = below_traps[0]
            below_traps[0].lower_left = prev_lower

def insert_segment(segment, dag_root, vertices, halfedges):
    q = vertices[halfedges[segment.twin].origin]
    p = vertices[segment.origin]

    traps = get_intersected_trapezoids(segment, dag_root, vertices, halfedges)


    above_segment_traps = []
    below_segment_traps = []
    upper_map = []
    lower_map = []

    left_trap = None
    right_trap = None

    for i, delta in enumerate(traps) :

        if i == 0 and not lex_equal(delta.leftp, p) :
            left_trap = Trapezoid(delta.top, delta.bottom, delta.leftp, p)


        upper_leftp = p     if i == 0 else traps[i-1].rightp
        upper_rightp = q    if (i == len(traps) - 1) else delta.rightp
        upper = Trapezoid(delta.top, segment, upper_leftp, upper_rightp)


        if above_segment_traps and above_segment_traps[-1].top is upper.top :
            above_segment_traps[-1].rightp = upper.rightp
            upper_map.append(above_segment_traps[-1])

        else :
            above_segment_traps.append(upper)
            upper_map.append(upper)

        
        lower_leftp = p     if i == 0 else traps[i-1].rightp
        lower_rightp = q    if (i == len(traps) - 1) else delta.rightp
        lower = Trapezoid(halfedges[segment.twin], delta.bottom, lower_leftp, lower_rightp)

        if below_segment_traps and below_segment_traps[-1].bottom is lower.bottom:
            below_segment_traps[-1].rightp = lower.rightp
            lower_map.append(below_segment_traps[-1])
        else:
            below_segment_traps.append(lower)
            lower_map.append(lower)

        if (i == len(traps) - 1) and not lex_equal(delta.rightp, q):
            right_trap = Trapezoid(delta.top, delta.bottom, q, delta.rightp)

    _set_neighbors(left_trap, right_trap, above_segment_traps, below_segment_traps, traps)
    
    update_dag(traps, segment, p, q, upper_map, lower_map, left_trap, right_trap)



def query_dag(point, dag_root, vertices, halfedges):
    node = dag_root
    while not isinstance(node, Leaf):
        if isinstance(node, XNode):
            v = node.vertex
            if vertex_order(point, v):
                node = node.left
            else :
                node = node.right
            
        elif isinstance(node, YNode):
            if is_point_above_segment(point, node.halfedge, vertices, halfedges):
                node = node.above
            else :
                node = node.below
    return node.trapezoid

def is_point_on_segment(p, segment, vertices, halfedges):
    a = vertices[segment.origin]
    b = vertices[halfedges[segment.twin].origin]
    cross = (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x)
    if abs(cross) > EPSILON:
        return False

    return (min(a.x, b.x) - EPSILON <= p.x <= max(a.x, b.x) + EPSILON and
            min(a.y, b.y) - EPSILON <= p.y <= max(a.y, b.y) + EPSILON)


def classify_point(point, trap, vertices, halfedges, faces):
    unbounded = next((f for f, obj in faces.items() if obj.outer_component is None), None)
    bb_vertices = {'c1', 'c2', 'c3', 'c4'}

    for v in vertices.values():
        if v.name in bb_vertices:
            continue
        if abs(point.x - v.x) < EPSILON and abs(point.y - v.y) < EPSILON:
            return ('vertex', v)

    for he_name in [trap.top.name, trap.bottom.name]:
        if he_name in ('T', 'B', 'L', 'R'):
            continue
        h_e = halfedges[he_name]
        if is_point_on_segment(point, h_e, vertices, halfedges):
            twin = halfedges[h_e.twin]
            if h_e.face == unbounded and twin.face != unbounded:
                return ('edge', twin)
            return ('edge', h_e)

    return ('trapezoid', trap)


def build_trapezoidal_map(vertices, halfedges):
    ul, ll, ur, lr, L, R, T, B, x_min, x_max, y_min, y_max = build_bounding_box(vertices)

    # Add bounding box edges and vertices to the dicts so queries can find them
    halfedges['L'] = L
    halfedges['R'] = R
    halfedges['T'] = T
    halfedges['B'] = B

    t0, dag_root = initialize_trapezoid(T, B, ul, ur)

    segments = get_segments(halfedges, vertices)
    random_permutation(segments)

    for seg in segments:
        insert_segment(seg, dag_root, vertices, halfedges)

    return dag_root


def parse_point(raw):
    """Parse '(1, 2)' or '1, 2' into (float, float)."""
    cleaned = raw.strip().strip('()')
    x, y = cleaned.split(',')
    return float(x.strip()), float(y.strip())


def collect_trapezoids_by_face(dag_root, faces, halfedges):
    """Walk the DAG and collect all leaf trapezoids, grouped by face."""
    all_traps = []
    visited_leaves = set()

    # DFS through the DAG collecting all Leaf nodes
    stack = [dag_root]
    while stack:
        node = stack.pop()
        if id(node) in visited_leaves:
            continue
        visited_leaves.add(id(node))

        if isinstance(node, Leaf):
            all_traps.append(node.trapezoid)
        elif isinstance(node, XNode):
            if node.left:  stack.append(node.left)
            if node.right: stack.append(node.right)
        elif isinstance(node, YNode):
            if node.above: stack.append(node.above)
            if node.below: stack.append(node.below)

    # Find the unbounded face (outer_component is None)
    unbounded = next((f for f, obj in faces.items() if obj.outer_component is None), None)

    bb = {'T', 'B', 'L', 'R'}
    result = {f: [] for f in faces}
    for trap in all_traps:
        # Skip zero-width trapezoids (artifact of vertical input edges)
        if abs(trap.leftp.x - trap.rightp.x) < EPSILON:
            continue
        face_name = None
        if trap.bottom.name not in bb:
            # Trapezoid is ABOVE its bottom edge; bottom.face = that face
            face_name = trap.bottom.face
        elif trap.top.name not in bb:
            face_name = trap.top.face
        else:
            # Both edges are bounding box — belongs to unbounded face
            face_name = unbounded
        if face_name and face_name in result:
            result[face_name].append(trap)

    return result


def print_vertex(v):
    x = int(v.x) if v.x == int(v.x) else v.x
    y = int(v.y) if v.y == int(v.y) else v.y
    return f'{v.name}  ({x}, {y})  {v.incident_edge}'

def print_halfedge(he):
    return f'{he.name}  {he.origin}  {he.twin}  {he.face}  {he.next_edge}  {he.previous_edge}'

def print_trapezoid(trap, vertices=None, halfedges=None):
    bb = {'T', 'B', 'L', 'R'}
    if trap.leftp.name in ('c1', 'c2'):
        leftp_name = 'L'
    elif vertices is not None and halfedges is not None and trap.bottom.name not in bb:
        # When a vertical input edge forms the left boundary, the stored leftp is its
        # upper endpoint; use the bottom edge's left endpoint if it's at the same x but lower.
        bottom_lp = left_endpoint(trap.bottom, halfedges, vertices)
        if abs(bottom_lp.x - trap.leftp.x) < EPSILON and bottom_lp.y < trap.leftp.y - EPSILON:
            leftp_name = bottom_lp.name
        else:
            leftp_name = trap.leftp.name
    else:
        leftp_name = trap.leftp.name

    rightp_name = 'R' if trap.rightp.name in ('c3', 'c4') else trap.rightp.name
    return f'{trap.top.name}\n{trap.bottom.name}\n{leftp_name}\n{rightp_name}'


def write_trapezoidal_map(filename, trapezoids, vertices, halfedges):
    with open(filename, 'w') as f:
        f.write('****** Trapezoidal Map******\n\n')
        for face_name, trap_list in trapezoids.items():
            n = len(trap_list)
            plural = 'trapezoid' if n == 1 else 'trapezoids'
            f.write(f'Face {face_name} contains {n} {plural}:\n\n')
            for trap in trap_list:
                f.write(print_trapezoid(trap, vertices, halfedges) + '\n\n')


def visualize_trapezoidal_map(dag_root, vertices, halfedges, faces):
    # Draws the trapezoidal map: trapezoid outlines in blue, input edges in black, vertex labels.
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print('matplotlib not installed — skipping visualization')
        return

    # Recompute bounding box extents (same padding as build_bounding_box)
    x_vals = [v.x for v in vertices.values()]
    y_vals = [v.y for v in vertices.values()]
    pad = 1.0
    x_min = min(x_vals) - pad
    x_max = max(x_vals) + pad
    y_min = min(y_vals) - pad
    y_max = max(y_vals) + pad

    def y_at_x(edge, x):
        # y-coordinate of edge at a given x, used to compute trapezoid corners
        if edge.name == 'T': return y_max
        if edge.name == 'B': return y_min
        a = vertices[edge.origin]
        b = vertices[halfedges[edge.twin].origin]
        if abs(b.x - a.x) < EPSILON:
            return (a.y + b.y) / 2
        return a.y + (b.y - a.y) * (x - a.x) / (b.x - a.x)

    # Collect all leaf trapezoids from the DAG via DFS
    all_traps = []
    visited = set()
    stack = [dag_root]
    while stack:
        node = stack.pop()
        if id(node) in visited:
            continue
        visited.add(id(node))
        if isinstance(node, Leaf):
            all_traps.append(node.trapezoid)
        elif isinstance(node, XNode):
            if node.left:  stack.append(node.left)
            if node.right: stack.append(node.right)
        elif isinstance(node, YNode):
            if node.above: stack.append(node.above)
            if node.below: stack.append(node.below)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_aspect('equal')
    ax.set_title('Trapezoidal Map')

    # Draw each trapezoid as a closed outline (4 corners → back to start)
    for trap in all_traps:
        if abs(trap.leftp.x - trap.rightp.x) < EPSILON:
            continue   # skip zero-width artifacts from vertical edges
        lx, rx = trap.leftp.x, trap.rightp.x
        bl = (lx, y_at_x(trap.bottom, lx))
        br = (rx, y_at_x(trap.bottom, rx))
        tr = (rx, y_at_x(trap.top,    rx))
        tl = (lx, y_at_x(trap.top,    lx))
        ax.plot([bl[0], br[0], tr[0], tl[0], bl[0]],
                [bl[1], br[1], tr[1], tl[1], bl[1]], 'b-', linewidth=0.8)

    # Label each face at the centroid of its trapezoids
    traps_by_face = collect_trapezoids_by_face(dag_root, faces, halfedges)
    for face_name, trap_list in traps_by_face.items():
        cx_sum = cy_sum = 0.0
        count = 0
        for trap in trap_list:
            if abs(trap.leftp.x - trap.rightp.x) < EPSILON:
                continue
            mx = (trap.leftp.x + trap.rightp.x) / 2
            my = (y_at_x(trap.top, mx) + y_at_x(trap.bottom, mx)) / 2
            cx_sum += mx
            cy_sum += my
            count += 1
        if count:
            ax.text(cx_sum / count, cy_sum / count, face_name,
                    ha='center', va='center', fontsize=10, color='darkgreen')

    # Draw input edges in bold black (each undirected edge once)
    bb = {'T', 'B', 'L', 'R'}
    drawn = set()
    for he in halfedges.values():
        if he.name in bb or he.origin is None:
            continue
        key = tuple(sorted([he.name, he.twin]))
        if key in drawn:
            continue
        drawn.add(key)
        a = vertices[he.origin]
        b = vertices[halfedges[he.twin].origin]
        ax.plot([a.x, b.x], [a.y, b.y], 'k-', linewidth=2)

    # Draw and label each input vertex
    for v in vertices.values():
        ax.plot(v.x, v.y, 'ko', markersize=4)
        ax.annotate(v.name, (v.x, v.y), textcoords='offset points', xytext=(4, 4), fontsize=9)

    plt.tight_layout()
    plt.show()


