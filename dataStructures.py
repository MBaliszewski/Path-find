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