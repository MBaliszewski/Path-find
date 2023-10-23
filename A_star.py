
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
    def __init__(self, x, y, weight):
        self.id = id
        self.x = x
        self.y = y
        self.weight = weight
        self.edges = []
        self.h = None

    def heuristics(self, x_end, y_end):
        return (x_end - self.x) + (y_end - self.y)
    
    def __str__(self):
        return f'Node {self.id}: x={self.x}, y={self.y}'

class Edge:
    def __init__(self, fromn: Node, to: Node):
        self.fromn = fromn
        self.to = to
        self.cost = abs(int((self.fromn.weight + self.to.weight) / 2))

def make_graph(file_path):
    file = open(file_path, 'r')
    nodes_list = []
    edges_list = []

    # Nodes read - only x, y and weight
    x = 0
    y = 0
    for line in file:
        y += 1
        nodes = line.split()
        for n in nodes:
            x += 1
            nodes_list.append(Node(x, y, int(n))) 
        x = 0

    ending_node = nodes_list[-1]
    # Edges read, heuristics count
    for idx_node, node in enumerate(nodes_list):
        # left edge
        if node.x != 1:
            edge = Edge(fromn=node, to=nodes_list[idx_node-1])
            node.edges.append(edge)
            edges_list.append(edge)
        # up edge
        if node.y != 1:
            edge = Edge(fromn=node, to=nodes_list[idx_node-ending_node.x])
            node.edges.append(edge)
            edges_list.append(edge)
        # right edge
        if node.x != ending_node.x:
            edge = Edge(fromn=node, to=nodes_list[idx_node+1])
            node.edges.append(edge)
            edges_list.append(edge)
        # down edge
        if node.y != ending_node.y:
            edge = Edge(fromn=node, to=nodes_list[idx_node+ending_node.x])
            node.edges.append(edge)
            edges_list.append(edge)

        node.h = node.heuristics(ending_node.x, ending_node.y)
        node.id = idx_node+1

    return Graph(edges=edges_list, nodes=nodes_list)


def retrieve_path(p, s, e):
    path = []

    while e != s:
        path.append(e)
        e = p[e]

    path.append(s)
    path.reverse()
    
    return path 

def astar(graph):
    start_node = graph.nodes[0]
    end_node = graph.nodes[-1]
    S = []
    Q = {}  # {node: access cost + heuristic}
    d = {}  # access costs
    p = {}  # previous node
    visited = {}  # Number of visits for each visited node

    S.append(start_node)
    visited[start_node] = 0
    d[start_node] = 0
    p[start_node] = None

    while end_node not in S:
        
        visited[S[-1]] += 1  # odwiedzony kolejny raz w zbiorze S
        # przejrzenie sąsiadów node dodanego do S na końcu
        for edge in S[-1].edges:
            if edge.to not in S:
                f = d[edge.fromn] + edge.cost + edge.to.h  # szacowany koszt dojścia do końca

                if edge.to in visited:
                    visited[edge.to] += 1                       # odwiedzony kolejny raz
                    if f < Q[edge.to]:
                        d[edge.to] = d[edge.fromn] + edge.cost  # koszt dojścia do node
                        Q[edge.to] = f
                        p[edge.to] = edge.fromn                 # zapisanie poprzednika
                    else:
                        continue
                else:
                    visited[edge.to] = 1                    # odwiedzony pierwszy raz
                    d[edge.to] = d[edge.fromn] + edge.cost  # koszt dojścia do node
                    Q[edge.to] = f
                    p[edge.to] = edge.fromn                 # zapisanie poprzednika

        min_f_node = min(Q, key=Q.get)  # wybranie z Q node o najmniejszym szacowanym koszcie dojścia
        del Q[min_f_node]               # i usunięcie go z Q
        S.append(min_f_node)            # i dodanie go do S

    path = retrieve_path(p, start_node, end_node)

    # wyprintowanie wyników
    print('---------- Path:')
    for node in path:
        print(node)

    print('---------- Number of visits for each node:')
    for key, value in visited.items():
        print(f'{key}, visited: {value}')

    print('-----------')
    print(f'Arrival cost: {d[min_f_node]}\nNumber of visited: {len(visited)}\nNumber of visits: {sum(visited.values())}')
    ##

    return d[min_f_node], len(visited), sum(visited.values())

graph = make_graph('dane/graf6.txt')
cost, visited_num, visits_num = astar(graph)
