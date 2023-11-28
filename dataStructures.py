import matplotlib.pyplot as plt
import math
import pyproj

class Graph:
    def __init__(self):
        self.edges = {}
        self.nodes = {}
        self.start_node = None
        self.end_node = None
        self.max_speed_in_graph = 0

    def add_node(self, node):
        self.nodes[node.id] = node

    def add_edge(self, edge):
        self.edges[(edge.fromn.id, edge.to.id)] = edge

    def set_val_of_in_prev_path(self, prev_path, value):
        for i in range(len(prev_path) - 1):
            node_first = prev_path[i]
            node_last = prev_path[i + 1]
            edge = node_first.edges[(node_first.id, node_last.id)]
            edge.in_prev_path = value

    def __str__(self):
        string = ''
        for node in self.nodes.values():
            c = [edge.cost for edge in node.edges.values()]
            string += f'Node {node.id}: x={node.x}, y={node.y}, costs: {c}\n'
            
        return string

    def draw_graph(self):
        # Inicjalizacja wykresu
        fig, ax = plt.subplots()

        for edge in self.edges.values():
            x1, y1 = edge.fromn.x, edge.fromn.y
            x2, y2 = edge.to.x, edge.to.y
            ax.plot([x1, x2], [y1, y2], 'bo-')  # rysuj krawędź jako niebieską linię

        for node in self.nodes.values():
            ax.plot(node.x, node.y, 'ro')  # rysuj węzeł jako czerwoną kropkę
            #ax.text(node.x, node.y, f'{len(node.edges)}', ha='center', va='center')
            ax.text(node.x, node.y, f'{node.id}', ha='center', va='center')

        plt.xlabel("X")
        plt.ylabel("Y")
        plt.grid(True)
        plt.show()
            
class Node:
    transformer = pyproj.Transformer.from_crs('EPSG:2180', 'EPSG:4326', always_xy=True)

    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.y_4326, self.x_4326 = self.convert_to_4326()
        self.edges = {}
        self.h = None

    def add_edge(self, edge):
        self.edges[(edge.fromn.id, edge.to.id)] = edge

    def convert_to_4326(self):
        return self.transformer.transform(self.x, self.y)

    def heuristics(self, end_node, type: str, max_speed: int):
        distance = math.dist([self.x, self.y], [end_node.x, end_node.y])
        if type == 'shortest':
            self.h = distance
        elif type == 'fastest':
            self.h = (distance / 1000) / 120
    
    def __str__(self):
        return f'Node {self.id}: x={self.x}, y={self.y}'

class Edge:
    types = {'A': 140,
            'S': 120,
            'GP': 100,
            'G': 80,
            'Z': 50,
            'L': 40,
            'D': 20,
            'I': 5}

    def __init__(self, fromn: Node, to: Node, length: float, road_class: str, geometry, flip=False):
        self.fromn = fromn
        self.to = to
        self.length = length
        self.road_class = road_class
        self.max_speed = self.types[self.road_class]
        self.geometry = geometry
        self.flip = flip
        self.in_prev_path = False

    def count_time(self, max_speed):
        return (self.length / 1000) / max_speed

    def get_cost(self, type: str):
        mulitplier = 1
        if self.in_prev_path:
            mulitplier = 2

        if type == 'shortest':
            return self.length * mulitplier
        elif type == 'fastest':
            return self.count_time(self.max_speed) * mulitplier