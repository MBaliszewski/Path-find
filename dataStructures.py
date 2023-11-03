import matplotlib.pyplot as plt

class Graph:
    def __init__(self, edges, nodes):
        self.edges = edges
        self.nodes = nodes

    def __str__(self):
        string = ''
        for node in self.nodes:
            c = [edge.cost for edge in node.edges]
            string += f'Node {node.id}: x={node.x}, y={node.y}, costs: {c}\n'
            
        return string

    def draw_graph(self):
        # Inicjalizacja wykresu
        fig, ax = plt.subplots()

        for edge in self.edges:
            x1, y1 = edge.fromn.x, edge.fromn.y
            x2, y2 = edge.to.x, edge.to.y
            ax.plot([x1, x2], [y1, y2], 'bo-')  # rysuj krawędź jako niebieską linię

        for node in self.nodes:
            ax.plot(node.x, node.y, 'ro')  # rysuj węzeł jako czerwoną kropkę
            ax.text(node.x, node.y, f'{len(node.edges)}', ha='center', va='center')

        # Dodaj etykiety dla krawędzi
        for edge in self.edges:
            x1, y1 = edge.fromn.x, edge.fromn.y
            x2, y2 = edge.to.x, edge.to.y
            #ax.annotate(f'Cost: {edge.cost}', ((x1 + x2) / 2, (y1 + y2) / 2), ha='center')

        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Graph Visualization")
        plt.grid(True)
        plt.show()
            
class Node:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.edges = []
        self.h = None

    def heuristics(self, x_end, y_end):
        return abs(x_end - self.x) + abs(y_end - self.y)
    
    def __str__(self):
        return f'Node {self.id}: x={self.x}, y={self.y}'

class Edge:
    def __init__(self, fromn: Node, to: Node, cost: float):
        self.fromn = fromn
        self.to = to
        self.cost = cost