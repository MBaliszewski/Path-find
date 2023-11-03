class Graph:
    def __init__(self, edges, nodes):
        self.edges = edges
        self.nodes = nodes

    def __str__(self):
        string = ''
        for node in self.nodes:
            w = node.weight
            e = [edge.to.weight for edge in node.edges]
            c = [edge.cost for edge in node.edges]
            h = node.h
            string += f'Node {node.id}: x={node.x}, y={node.y}, w={w}, Edges to: {e}, Costs: {c}, Heuristic: {h}\n'
            
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
    def __init__(self, fromn: Node, to: Node, length: float):
        self.fromn = fromn
        self.to = to
        self.cost = length