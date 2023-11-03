import arcpy
from dataStructurs import Graph, Node, Edge
import math

def generate_id_from_xy(x, y):
    return (math.floor(x), math.floor(y))


def make_graph(workspace, layer):
    arcpy.env.workspace = workspace

    nodes = {}              # node id -> node
    edges = {}              # edge id -> edge
    index_nodes = {}        # generate_id_from_xy(x, y) -> node id
    generator_node_id = 1

    with arcpy.da.SearchCursor(layer, ['OID@', 'SHAPE@', 'SHAPE@LENGTH']) as cursor:
        for row in cursor:
            idx = row[0]
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

            # to samo dla geom.lastPoint

            # edge = Edge(from=node_start, to=node_from, cost=length)
            # node_start.edges.append(edge)
            # node_end.edges.append(edge)

            print(idx)
            print(f'Start: {geom.firstPoint.X}, {geom.firstPoint.Y}')
            print(f'End: {geom.lastPoint.X}, {geom.lastPoint.Y}')
            print(f'Len: {row[2]}')


workspace = 'E:\\sem5\\PAG\\dane\\torun'
#layer = 'L4_1_BDOT10k__OT_SKJZ_L.shp'
layer = 'testowa.shp'
make_graph(workspace, layer)
