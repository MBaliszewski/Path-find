import matplotlib.pyplot as plt

class Graph:
    def __init__(self):
        self.edges = {}
        self.nodes = {}
        self.start_node = None
        self.end_node = None

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

    def heuristics(self, x_end, y_end):
        return abs(x_end - self.x) + abs(y_end - self.y)
    
    def __str__(self):
        return f'Node {self.id}: x={self.x}, y={self.y}'

class Edge:
    def __init__(self, fromn: Node, to: Node, cost: float, geometry):
        self.fromn = fromn
        self.to = to
        self.cost = cost
        self.geometry = geometry