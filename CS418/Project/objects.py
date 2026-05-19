_trapezoid_count = 0    # Global counter for each of the new trapezoids t1, t2, ...


class Vertex:
    def __init__(self, name, x, y, incident_edge):  
        self.x = x  # x coordinate of vertex
        self.y = y  # y coordinate of vertex
        self.name = name  # name of vertex for calling/reference
        self.incident_edge = incident_edge # this is the hald edge name passed in as string

class Face:
    def __init__(self, name, inner_components, outer_component):
        self.inner_component = inner_components     # list of inner components that are the half-edge names
        self.outer_component = outer_component      # the name of half edge that is outer component or can be None
        self.name = name    # name of face
    def __str__(self):
        return self.name    # Return face name when printed or converted to string

class HalfEdge:
    def __init__(self, name, twin, face, origin, previous_edge, next_edge):
        self.name = name        # name of half edge
        self.twin = twin        # half edge name
        self.face = face        # name of face
        self.origin = origin        # vertex name
        self.previous_edge = previous_edge      # previous half edge name
        self.next_edge = next_edge      # next half edge name
    def __str__(self):      # Return HalfEdge name when printed
        return self.name
    
class Trapezoid:
    def __init__(self, top, bottom, leftp, rightp):
        global _trapezoid_count     # Count the trapezoids so that each trapezoid has a unique name
        _trapezoid_count += 1       # Iterate the counter by 1 so each trapezoid name is unique
        self.name = f't{_trapezoid_count}'      # Set the name of the trapezoid name 
        self.top = top          # Set top HalfEdge of trapezoid
        self.bottom = bottom     # Set the bottom HalfEdge of trapezoid
        self.leftp = leftp      # Assign the left endpoint vertex of trapezoid
        self.rightp = rightp        # Assign the right endpoint vertex of trapezoid
        self.leaf = None        # Set leaf object to none for now, will be used for cross reference back to DAG node that wraps trapezoid later
        self.upper_right = None     # Trapezoid object that is neighbor to this trapezoid at upper half of trapezoid right wall
        self.upper_left = None      # Trapezoid object that is neighbor to this trapezoid at upper half of trapezoid left wall
        self.lower_right = None     # Trapezoid object that is neighbor to this trapezoid at lower half of trapezoid right wall
        self.lower_left = None     # Trapezoid object that is neighbor to this trapezoid at lower half of trapezoid left wall

    def __str__(self):
        return self.name

class Node:        # Abstraction vfor base class for DAG nodes --> includes XNode, YNode, and Leaf that inherits from this
    pass

class XNode(Node):
    def __init__(self, vertex):
        self.vertex = vertex   # Vertex object
        self.left = None       # The point that is left of the vertex --> child Node 
        self.right = None      # The point that is right of the vertex --> parent node
    def __str__(self):          # Return vertex name the x-node splits on
        return self.vertex.name         
    

class YNode(Node):
    def __init__(self, halfedge):
        self.halfedge = halfedge  # The segment which is the half edge object
        self.above = None         # The point that is above the segment --> child node
        self.below = None         # The point that is below the segment --> parent node
    def __str__(self):            # Return half edge name the y node splits on
        return self.halfedge.name
    

class Leaf(Node):
    def __init__(self, trapezoid):
        self.trapezoid = trapezoid      # Trapezoid is stored at this leaf. Query that reaches this leaf lands in the trapezoid
        trapezoid.leaf = self           # Back reference --> trapezoid knows which leaf points to it. This will be used for DAG updates
    def __str__(self):                  # Return trapezoid name when printed.
        return self.trapezoid.name