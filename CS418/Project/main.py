from trapezoid_map import *       # all geometry, DAG, and output functions
from types import SimpleNamespace  # used to bundle x/y into a point object for queries


def main():
    print('Point Location Using Trapezoidal Maps\n')
    trial = 1   # tracks which trial we are on; used to name the output file

    while True:
        print(f'Trial {trial}:')
        filename = input('Name of the input planar subdivision file: ').strip()

        if filename == 'x':
            # 'x' is the sentinel to quit the entire program
            print('\nEnd of execution')
            break

        # Parse the DCEL input file into three dictionaries
        faces, halfedges, vertices = parse_dcel(filename)

        # Build the trapezoidal map and DAG search structure from the DCEL
        dag_root = build_trapezoidal_map(vertices, halfedges)

        out_name = f'trapezoidalMap{trial}.txt'   # output file name for this trial

        # Group all trapezoids by the face they belong to, then write the output file
        traps_by_face = collect_trapezoids_by_face(dag_root, faces, halfedges)
        write_trapezoidal_map(out_name, traps_by_face, vertices, halfedges)
        print(f'Trapezoidal map constructed in the file {out_name}\n')

        # Show the graphical visualization of the trapezoidal map
        visualize_trapezoidal_map(dag_root, vertices, halfedges, faces)

        # Query loop: accept point queries until the user types 'x'
        while True:
            raw = input('Query point: ').strip()

            if raw == 'x':
                # 'x' exits the query loop and moves to the next trial
                print('End of all queries in this map.\n')
                break

            x, y = parse_point(raw)   # parse '(x, y)' or 'x, y' into floats
            point = SimpleNamespace(x=x, y=y)   # wrap as an object so code can use point.x / point.y

            # Walk the DAG to find which trapezoid contains the query point
            trap = query_dag(point, dag_root, vertices, halfedges)

            # Determine if the point is on a vertex, edge, or inside a face
            result_type, result = classify_point(point, trap, vertices, halfedges, faces)

            if result_type == 'vertex':
                print('Vertex of the input subdivision:')
                print(print_vertex(result))
            elif result_type == 'edge':
                print('On an edge of the input subdivision:')
                print(print_halfedge(result))
            else:
                # Point is in the interior of a trapezoid — print integer coords if whole numbers
                xd = int(x) if x == int(x) else x
                yd = int(y) if y == int(y) else y
                print(f'Trapezoid containing the point ({xd}, {yd}):')
                print(print_trapezoid(result, vertices, halfedges))
            print()   # blank line between query results for readability

        trial += 1   # advance to next trial


if __name__ == '__main__':
    main()