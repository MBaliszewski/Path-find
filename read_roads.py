import arcpy
from dataStructures import Graph, Node, Edge
import math

def save_result(output_path, output_name, path):
    geom = []
    for i in range(len(path) - 1):
        start_node = path[i]
        end_node = path[i + 1]
        edge = start_node.edges[(start_node.id, end_node.id)]
        geom.append(edge.geometry)

    arcpy.env.overwriteOutput = True
    arcpy.CreateFeatureclass_management(output_path, output_name, "POLYLINE")

    with arcpy.da.InsertCursor(output_path + '\\' + output_name, ["SHAPE@"]) as cursor:
        for g in geom:
            cursor.insertRow([g])


def generate_id_from_xy(x, y):
    return (math.floor(x), math.floor(y))


def make_graph(workspace, layer):
    arcpy.env.workspace = workspace

    nodes = {}              # node id -> node
    index_nodes = {}        # generate_id_from_xy(x, y) -> node id
    graph = Graph()
    generator_node_id = 1

    with arcpy.da.SearchCursor(layer, ['OID@', 'SHAPE@', 'SHAPE@LENGTH']) as cursor:
        for row in cursor:
            geom = row[1]
            length = row[2]
            
            x_start =  geom.firstPoint.X
            y_start =  geom.firstPoint.Y
            if generate_id_from_xy(x_start, y_start) in index_nodes:
                node_start = nodes[index_nodes[generate_id_from_xy(x_start, y_start)]]
            else:
                node_start = Node(id=generator_node_id, x=x_start, y=y_start)
                nodes[generator_node_id] = node_start
                index_nodes[generate_id_from_xy(node_start.x, node_start.y)] = generator_node_id
                graph.add_node(node_start)
                generator_node_id += 1

            x_end =  geom.lastPoint.X
            y_end =  geom.lastPoint.Y
            if generate_id_from_xy(x_end, y_end) in index_nodes:
                node_end = nodes[index_nodes[generate_id_from_xy(x_end, y_end)]]
            else:
                node_end = Node(id=generator_node_id, x=x_end, y=y_end)
                nodes[generator_node_id] = node_end
                index_nodes[generate_id_from_xy(node_end.x, node_end.y)] = generator_node_id
                graph.add_node(node_end)
                generator_node_id += 1

            edge = Edge(fromn=node_start, to=node_end, cost=length, geometry=geom)
            graph.add_edge(node_from=node_start, node_to=node_end, edge=edge)
            node_start.add_edge(node_from=node_start, node_to=node_end, edge=edge)
            
            # W ten sposób dublują się krawędzie, ale czy da się inaczej? Bez tego można się zablokować w jakimś wierzchołku
            edge = Edge(fromn=node_end, to=node_start, cost=length, geometry=geom)
            graph.add_edge(node_from=node_end, node_to=node_start, edge=edge)
            node_end.add_edge(node_from=node_end, node_to=node_start, edge=edge)

    return graph


def dijkstra(graph: Graph):
    start_node = graph.start_node
    end_node = graph.end_node
    S = set()
    Q = []
    p = {}
    d = {}
    visited = {}

    Q.append(start_node)
    visited[start_node] = 1
    d[start_node] = 0
    p[start_node] = None

    while end_node not in S:
        if len(Q) == 0:
            print(min_d_node)
            return None, None

        min_d_node = min(Q, key=lambda n: d.get(n, None))  # wybranie z Q node o najmniejszym koszcie dojścia
        Q.remove(min_d_node)  # usunięcie go z Q
        visited[min_d_node] += 1

        for edge in min_d_node.edges.values():  # sprawdzenie wszystkich sąsiadów wybranego node,
            if edge.to not in S:  # którzy nie są w S
                if edge.to not in d:
                    visited[edge.to] = 1  # odwiedzony po raz pierwszy
                    d[edge.to] = d[edge.fromn] + edge.cost  # przypisanie kosztu dojścia po raz pierwszy
                    p[edge.to] = edge.fromn  # przypisanie poprzednika po raz pierwszy
                else:
                    visited[edge.to] += 1  # odwiedzony kolejny raz
                    if d[edge.to] > d[edge.fromn] + edge.cost:  # relaksacja
                        d[edge.to] = d[edge.fromn] + edge.cost  # nowy koszt dojścia
                        p[edge.to] = edge.fromn  # nowy poprzednik

                if edge.to not in Q:  # dodanie do Q
                    Q.append(edge.to)

        S.add(min_d_node)

    path = retrieve_path(p, start_node, end_node)

    # wyprintowanie wyników
    print('---------- Path:')
    for node in path:
        print(node)

    print('---------- Number of visits for each node:')
    for key, value in visited.items():
        print(f'{key}, visited: {value}')

    print('-----------')
    print(f'Arrival cost: {d[end_node]}\nNumber of visited: {len(visited)}\nNumber of visits: {sum(visited.values())}')
    ##

    return path, d[end_node]


def retrieve_path(p, s, e):
    path = []

    while e != s:
        path.append(e)
        e = p[e]

    path.append(s)
    path.reverse()

    return path


workspace = 'dane\\torun'
#layer = 'L4_1_BDOT10k__OT_SKJZ_L.shp'
#layer = 'testowa.shp'
layer = 'przyciete.shp'

graph = make_graph(workspace, layer)
graph.draw_graph()
graph.start_node = graph.nodes[73]
graph.end_node = graph.nodes[730]
print(graph.start_node, graph.end_node)
path, _ = dijkstra(graph)
save_result('E:\sem5\PAG\dane\output', 'result.shp', path)
