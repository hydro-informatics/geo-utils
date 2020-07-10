import networkx as nx
from geo_tools import *
import json
from shapely.geometry import asLineString, asMultiPoint

# according to Michael Diener
# https://github.com/mdiener21/python-geospatial-analysis-cookbook/tree/master/ch08
# usage: create_shortest_path(shp_file_name, start_node_id, end_node_id)


def create_shortest_path(line_shp_name, start_node_id, end_node_id):
    """
    Calcluate shortest path from a network of lines
    :param line_shp_name: STR of the input shapefile name
    :param start_node_id: INT of the start node
    :param end_node_id: INT of the end node
    :return: graph of nodes (coordinate pairs) connecting point1 and point2 via the provided Line_shp_name
    """

    # load shapefile
    nx_load_shp = nx.read_shp(line_shp_name)

    # with not all graphs connected, take the largest connected subgraph by using the connected_component_subgraphs function.
    nx_list_subgraph = list(nx.connected_component_subgraphs(nx_load_shp.to_undirected()))[0]

    # get all the nodes in the network
    nx_nodes = np.array(nx_list_subgraph.nodes())

    # output the nodes to a GeoJSON file
    network_nodes = asMultiPoint(nx_nodes)
    write_geojson(line_shp_name.split(".shp")[0] + "_nodes.geojson",
                  network_nodes.__geo_interface__)

    # Compute the shortest path. Dijkstra's algorithm.
    nx_short_path = nx.shortest_path(nx_list_subgraph,
                                     source=tuple(nx_nodes[start_node_id]),
                                     target=tuple(nx_nodes[end_node_id]),
                                     weight='distance')

    # create numpy array of coordinates representing result path
    nx_array_path = get_full_path(nx_short_path, nx_list_subgraph)

    # convert numpy array to Shapely Linestring
    shortest_path = asLineString(nx_array_path)

    write_geojson(line_shp_name.split(".shp")[0] + "_Xpath.geojson",
                  shortest_path.__geo_interface__)


def get_path(n0, n1, nx_list_subgraph):
    """n0 and n1 are connected nodes
    :param n0: Node 1
    :param n1: Node 2
    :param nx_list_subgraph: LIST (see create shortest path)
    :return: array of point coordinates along the line linking these two nodes."""
    return np.array(json.loads(nx_list_subgraph[n0][n1]['Json'])['coordinates'])


def get_full_path(path, nx_list_subgraph):
    """
    Create numpy array line result
    :param path: STR (result of nx.shortest_path)
    :param nx_list_subgraph: LIST (see create shortest path)
    :return: coordinate pairs along a path
    """
    p_list = []
    curp = None
    for i in range(len(path)-1):
        p = get_path(path[i], path[i+1], nx_list_subgraph)
        if curp is None:
            curp = p
        if np.sum((p[0]-curp)**2) > np.sum((p[-1]-curp)**2):
            p = p[::-1, :]
        p_list.append(p)
        curp = p[-1]
    return np.vstack(p_list)


def write_geojson(outfilename, indata):
    """
    Creates a new GeoJSON file
    :param outfilename: name of output file
    :param indata:
    :return: a new GeoJSON file
    """
    with open(outfilename, "w") as file_out:
        file_out.write(json.dumps(indata))

