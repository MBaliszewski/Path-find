import arcpy
from dataStructures import Graph, Node, Edge
import math
import pyproj
import numpy as np


def xy_from_path(path):
    x = []
    y = []
    transformer = pyproj.Transformer.from_crs('EPSG:2180', 'EPSG:4326', always_xy=True)

    for i in range(len(path) - 1):
        node_first = path[i]
        node_last = path[i + 1]
        edge = node_first.edges[(node_first.id, node_last.id)]
        
        temp_x = []
        temp_y = []
        for part in edge.geometry:
            for vertex in part:
                x_2180, y_2180 = vertex.X, vertex.Y
                y_4326, x_4326 = transformer.transform(x_2180, y_2180)
                temp_x.append(x_4326)
                temp_y.append(y_4326)

        if edge.flip:
            temp_x.reverse()
            temp_y.reverse()

        x.extend(temp_x)
        y.extend(temp_y)

    return x, y


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

    with arcpy.da.SearchCursor(layer, ['OID@', 'SHAPE@', 'SHAPE@LENGTH', 'klasaDrogi', 'direction']) as cursor:
        for row in cursor:
            geom = row[1]
            length = row[2]
            road_class = row[3]
            direction = row[4]

            # Nieprzejezdna
            if direction == '0':
                continue
            
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

            # Dwukierunkowa
            if direction == '1':
                edge = Edge(fromn=node_start, to=node_end, length=length, road_class=road_class, geometry=geom)
                graph.add_edge(edge=edge)
                node_start.add_edge(edge=edge)
                if edge.max_speed > graph.max_speed_in_graph:
                    graph.max_speed_in_graph = edge.max_speed
                
                edge = Edge(fromn=node_end, to=node_start, length=length, road_class=road_class, geometry=geom, flip=True)
                graph.add_edge(edge=edge)
                node_end.add_edge(edge=edge)
                if edge.max_speed > graph.max_speed_in_graph:
                    graph.max_speed_in_graph = edge.max_speed
            # Kierunek zgodny z geometrią
            elif direction == '2':
                edge = Edge(fromn=node_start, to=node_end, length=length, road_class=road_class, geometry=geom)
                graph.add_edge(edge=edge)
                node_start.add_edge(edge=edge)
                if edge.max_speed > graph.max_speed_in_graph:
                    graph.max_speed_in_graph = edge.max_speed
            # Kierunek przeciwny do geometrii
            elif direction == '3':
                edge = Edge(fromn=node_end, to=node_start, length=length, road_class=road_class, geometry=geom, flip=True)
                graph.add_edge(edge=edge)
                node_end.add_edge(edge=edge)
                if edge.max_speed > graph.max_speed_in_graph:
                    graph.max_speed_in_graph = edge.max_speed

    return graph


def dijkstra(graph: Graph, type: str):
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
            return None, None

        min_d_node = min(Q, key=lambda n: d.get(n, None))  # wybranie z Q node o najmniejszym koszcie dojścia
        Q.remove(min_d_node)  # usunięcie go z Q
        S.add(min_d_node)
        visited[min_d_node] += 1

        for edge in min_d_node.edges.values():  # sprawdzenie wszystkich sąsiadów wybranego node,
            if edge.to not in S:  # którzy nie są w S
                if edge.to not in d:
                    visited[edge.to] = 1  # odwiedzony po raz pierwszy
                    d[edge.to] = d[edge.fromn] + edge.get_cost(type)  # przypisanie kosztu dojścia po raz pierwszy
                    p[edge.to] = edge.fromn  # przypisanie poprzednika po raz pierwszy
                else:
                    visited[edge.to] += 1  # odwiedzony kolejny raz
                    if d[edge.to] > d[edge.fromn] + edge.get_cost(type):  # relaksacja
                        d[edge.to] = d[edge.fromn] + edge.get_cost(type)  # nowy koszt dojścia
                        p[edge.to] = edge.fromn  # nowy poprzednik

                if edge.to not in Q:  # dodanie do Q
                    Q.append(edge.to)

    path = retrieve_path(p, start_node, end_node)

    # wyprintowanie wyników
    # print('---------- Path:')
    # for node in path:
    #     print(node)

    # print('---------- Number of visits for each node:')
    # for key, value in visited.items():
    #     print(f'{key}, visited: {value}')

    print('-----------')
    print(f'Arrival cost: {d[end_node] * 60 if "fastest" else d[end_node]}\nNumber of visited: {len(visited)}\nNumber of visits: {sum(visited.values())}')
    ##

    return [path], d[end_node] * 60 if "fastest" else d[end_node]


def astar(graph: Graph, type: str, alternative = False):
    start_node = graph.start_node
    end_node = graph.end_node

    for node in graph.nodes.values():
        node.heuristics(end_node, type, graph.max_speed_in_graph)

    S = set()
    Q = {}  # {node: access cost + heuristic}
    d = {}  # access costs
    p = {}  # previous node
    visited = {}  # Number of visits for each visited node

    S.add(start_node)
    visited[start_node] = 0
    d[start_node] = 0
    p[start_node] = None
    Q[start_node] = 0

    while end_node not in S:
        min_f_node = min(Q, key=Q.get) # wybranie z Q node o najmniejszym szacowanym koszcie dojścia
        del Q[min_f_node]  # i usunięcie go z Q
        if min_f_node == end_node:
            break
        S.add(min_f_node)  # i dodanie go do S

        visited[min_f_node] += 1  # odwiedzony kolejny raz w zbiorze S
        # przejrzenie sąsiadów node dodanego do S na końcu
        for edge in min_f_node.edges.values():
            if edge.to not in S:
                f = d[edge.fromn] + edge.get_cost(type)+ edge.to.h  # szacowany koszt dojścia do końca

                if edge.to in visited:
                    visited[edge.to] += 1  # odwiedzony kolejny raz
                    if f < Q[edge.to]:
                        d[edge.to] = d[edge.fromn] + edge.get_cost(type)  # koszt dojścia do node
                        Q[edge.to] = f
                        p[edge.to] = edge.fromn  # zapisanie poprzednika
                    else:
                        continue
                else:
                    visited[edge.to] = 1  # odwiedzony pierwszy raz
                    d[edge.to] = d[edge.fromn] + edge.get_cost(type)  # koszt dojścia do node
                    Q[edge.to] = f
                    p[edge.to] = edge.fromn  # zapisanie poprzednika

        # Jeśli brak trasy
        if len(Q) == 0:
            return None, None

    path = retrieve_path(p, start_node, end_node)

    # wyprintowanie wyników
    # print('---------- Path:')
    # for node in path:
    #     print(node)

    # print('---------- Number of visits for each node:')
    # for key, value in visited.items():
    #     print(f'{key}, visited: {value}')

    print('-----------')
    print(f'Arrival cost: {d[end_node] * 60 if "fastest" else d[end_node]}\nNumber of visited: {len(visited)}\nNumber of visits: {sum(visited.values())}')
    #

    if alternative:
        graph.set_val_of_in_prev_path(prev_path=path, value=True)
        alternative_path, _ = astar(graph, type, alternative=False)
        graph.set_val_of_in_prev_path(prev_path=path, value=False)
        return [path, alternative_path[0]], d[end_node] * 60 if 'fastest' else d[end_node]

    return [path], d[end_node] * 60 if 'fastest' else d[end_node]

def retrieve_path(p, s, e):
    path = []

    while e != s:
        path.append(e)
        e = p[e]

    path.append(s)
    path.reverse()

    return path


# workspace = 'dane\\torun'
# #layer = 'L4_1_BDOT10k__OT_SKJZ_L.shp'
# layer = 'testowa.shp'
# #layer = 'przyciete.shp'

# graph = make_graph(workspace, layer)
# graph.start_node = graph.nodes[1]
# graph.end_node = graph.nodes[8]
# paths, _ = astar(graph=graph, type='fastest', alternative=True)
# #path, _ = astar(graph)
# save_result('E:\sem5\PAG\dane\output', 'result_path_first.shp', paths[0])
# save_result('E:\sem5\PAG\dane\output', 'result_path_second.shp', paths[1])
