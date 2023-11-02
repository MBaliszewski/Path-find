
class Graph:
    def __init__(self, edges, nodes, start, end):
        self.edges = edges
        self.nodes = nodes
        self.start = start
        self.end = end

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
        return abs(x_end - self.x) + abs(y_end - self.y)

    def __str__(self):
        return f'Node {self.id}: x={self.x}, y={self.y}'


class Edge:
    def __init__(self, fromn: Node, to: Node):
        self.fromn = fromn
        self.to = to
        self.cost = int((self.fromn.weight + self.to.weight) / 2)


def make_graph(file_path, start_node, end_node):
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
            nodes_list.append(Node(x=x, y=y, weight=int(n)))
        x = 0

    corner_node = nodes_list[-1]
    # Edges read, heuristics count
    for idx_node, node in enumerate(nodes_list):
        # left edge
        if node.x != 1:
            edge = Edge(fromn=node, to=nodes_list[idx_node - 1])
            node.edges.append(edge)
            edges_list.append(edge)
        # up edge
        if node.y != 1:
            edge = Edge(fromn=node, to=nodes_list[idx_node - corner_node.x])
            node.edges.append(edge)
            edges_list.append(edge)
        # right edge
        if node.x != corner_node.x:
            edge = Edge(fromn=node, to=nodes_list[idx_node + 1])
            node.edges.append(edge)
            edges_list.append(edge)
        # down edge
        if node.y != corner_node.y:
            edge = Edge(fromn=node, to=nodes_list[idx_node + corner_node.x])
            node.edges.append(edge)
            edges_list.append(edge)

        node.h = node.heuristics(nodes_list[end_node].x, nodes_list[end_node].y)
        node.id = idx_node + 1

    return Graph(edges=edges_list, nodes=nodes_list, start=nodes_list[start_node], end=nodes_list[end_node])


def retrieve_path(p, s, e):
    path = []

    while e != s:
        path.append(e)
        e = p[e]

    path.append(s)
    path.reverse()

    return path


def astar(graph):
    start_node = graph.start
    end_node = graph.end
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
        for edge in min_f_node.edges:
            if edge.to not in S:
                f = d[edge.fromn] + edge.cost + edge.to.h  # szacowany koszt dojścia do końca

                if edge.to in visited:
                    visited[edge.to] += 1  # odwiedzony kolejny raz
                    if f < Q[edge.to]:
                        d[edge.to] = d[edge.fromn] + edge.cost  # koszt dojścia do node
                        Q[edge.to] = f
                        p[edge.to] = edge.fromn  # zapisanie poprzednika
                    else:
                        continue
                else:
                    visited[edge.to] = 1  # odwiedzony pierwszy raz
                    d[edge.to] = d[edge.fromn] + edge.cost  # koszt dojścia do node
                    Q[edge.to] = f
                    p[edge.to] = edge.fromn  # zapisanie poprzednika

            # Jeśli brak trasy
            if len(Q) == 0:
                return None


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
    #

    return d[end_node], len(visited), sum(visited.values())


def dijkstra(graph):
    start_node = graph.nodes[0]
    end_node = graph.nodes[-1]
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
            return None, None, None

        min_d_node = min(Q, key=lambda n: d.get(n, None))  # wybranie z Q node o najmniejszym koszcie dojścia
        Q.remove(min_d_node)  # usunięcie go z Q
        visited[min_d_node] += 1

        for edge in min_d_node.edges:  # sprawdzenie wszystkich sąsiadów wybranego node,
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

    return d[end_node], len(visited), sum(visited.values())

#graph = make_graph('dane/graf6.txt')
#cost, visited_num, visits_num = dijkstra(graph)
#cost, visited_num, visits_num = astar(graph)
