import matplotlib.pyplot as plt
import math

class Graph:
    def __init__(self):
        self.edges = {}
        self.nodes = {}
        self.start_node = None
        self.end_node = None
        self.max_speed_in_graph = 0

    def add_node(self, node):
        self.nodes[node.id] = node

    def add_edge(self, node_from, node_to, edge):
        self.edges[(node_from.id, node_to.id)] = edge

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
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.edges = {}
        self.h = None

    def add_edge(self, node_from, node_to, edge):
        self.edges[(node_from.id, node_to.id)] = edge

    def heuristics(self, end_node, type: str, max_speed: int):
        distance = math.dist([self.x, self.y], [end_node.x, end_node.y])
        if type == 'shortest':
            self.h = distance
        elif type == 'fastest':
            self.h = (distance / 1000) / 120
    
    def __str__(self):
        return f'Node {self.id}: x={self.x}, y={self.y}'

class Edge:
    types = {'A': 120,
            'S': 100,
            'GP': 90,
            'G': 70,
            'Z': 60,
            'L': 50,
            'D': 30,
            'I': 20}

    def __init__(self, fromn: Node, to: Node, length: float, road_class: str, geometry):
        self.fromn = fromn
        self.to = to
        self.length = length
        self.road_class = road_class
        self.max_speed = self.types[self.road_class]
        self.geometry = geometry

    def count_time(self, max_speed):
        return (self.length / 1000) / max_speed

    def get_cost(self, type: str):
        if type == 'shortest':
            return self.length
        elif type == 'fastest':
            return self.count_time(self.max_speed)