""" 
    The tspio module basically contains the messy code that is avoided in the
    IOModule but has to exist, like showing file dialogues, parsing files
    and writing files, as well as some helper methods for string construction
    from data structures."""
import re
import ast
import os
import tsputil
from Node import Node
try:
    # for Python2
    from tkFileDialog import asksaveasfile, askopenfile
except ImportError:
    # for Python3
    from tkinter.filedialog import asksaveasfile, askopenfile


def parse_tsp_file(file):
    """ Parses data from a tspfile with regexes and returns a tuple
    holding the nodes and groupinformation"""
    # Parse Name
    name_regex = re.compile("NAME : (.*)")
    # Parse comment
    comment_regex = re.compile("COMMENT : (.*)")
    # Parse single startnode
    start_regex = re.compile("COMMENT : STARTNODE : ([0-9])+")
    start_regex2 = re.compile("COMMENT : STARTNODES : (.*)")
    # Parse nodes
    node_regex = re.compile("([0-9]+)\ *([0-9]*\.?[0-9]*)\ *([0-9]*\.?[0-9]*)",
                            re.MULTILINE)
    # Parse Clusters
    cluster_regex = re.compile("COMMENT : CLUSTERS : (.*)")

    name = "No Name"
    comment = ""
    startnodes = []
    nodes = []
    groups = []

    _file = open(file, 'r')
    lines = _file.readlines()
    for line in range(len(lines)):
        nar = re.match(name_regex, lines[line])
        nor = re.match(node_regex, lines[line])
        cor = re.match(comment_regex, lines[line])
        clr = re.match(cluster_regex, lines[line])
        if len(lines[line]):
            stre = re.match(start_regex, lines[line])
            stre2 = re.match(start_regex2, lines[line])
            # Match Filename
            if nar:
                name = nar.group(1)
            # Match coordinates
            if nor:
                x_value = int(float(nor.group(2)))
                y_value = int(float(nor.group(3)))
                nodes.append([x_value, y_value])
            # Match Comments
            if cor:
                # Match Clusters
                if clr:
                    groups = clr.group(1)
                    groups = groups.replace(" ", "")
                    groups = ast.literal_eval(groups)
                elif stre:
                    startnodes = [int(stre.group(1))]
                elif stre2:
                    startnodes = stre2.group(1)
                    startnodes = ast.literal_eval(startnodes)
                else:
                    comment = comment + cor.group(1) + "\n"
    _file.close()
    return (name, comment, startnodes, nodes, groups)


def get_groups(nodes):
    """ return an array holding all occuring colorids of the given nodeset"""
    groups = []
    for node in nodes:
        if node.color not in groups:
            groups.append(node.color)
    return groups


def construct_groups_string(nodes):
    """ Constructs a string representing the grouping of nodes """
    groups = get_groups(nodes)
    if len(groups) <= 1:
        return ""
    else:
        result = []
        for color in groups:
            # +1 because .tsp nodes are indexed with 1
            group = [node.nid + 1 for node in nodes if node.color == color]
            result.append(group)
        return str(result)


def construct_startnodes_string(nodes):
    """ Looksup every node with the start bit and constructs a string of 
        the list of the ids of those nodes."""
    res = [node.nid for node in nodes if node.start]
    if len(res):
        return str(res)
    else:
        return ""


def parse_solution_file(file):
    """ Returns the concatenated lines 1 to END """
    result = ""
    _file = open(file, 'r')
    lines = _file.readlines()
    for line in range(1, len(lines)):
        result += lines[line]
    return result


def import_tsp(scale):
    """ Shows a filedialog to select a file to open and calls the callback
        with the parsed data  """
    # show a open-file-dialog
    filename = askopenfile()
    # if the user selected a file, delete old data,parse the file and
    # load the new data. If the user canceled the selection, do nothing.
    if filename:
        name, comment, startnodes, nodes, groups = parse_tsp_file(
            filename.name)

        node_list = []
        # If the nodes are not grouped, draw them in the currently
        # selected color
        if groups == []:
            color = tsputil.COLORS[0]
            for node in nodes:
                new_node = Node(len(node_list),
                                int(node[0] / scale),
                                int(node[1] / scale), color)
                node_list.append(new_node)
        # if the nodes are grouped, draw nodes from the same group in the same
        # color
        else:
            # iterate over groups
            for (index, group) in enumerate(groups):
                # iterate over node ids in the group
                for nid in group:
                    # get node coordinates
                    node = nodes[nid - 1]
                    new_node = Node(len(node_list),
                                    int(node[0] / scale),
                                    int(node[1] / scale),
                                    tsputil.COLORS[index])
                    if new_node.nid in startnodes:
                        new_node.start = True
                    node_list.append(new_node)
        return(name, comment, startnodes, node_list, groups)
    else:
        return None


def export_tsp(nodes, scale, comment, pre_filename=None):
    """ Exports the problem data in .tsp format  """
    filename = pre_filename
    if comment is None:
        comment = "PUT PROBLEM DESCRIPTION HERE"
    # check if the function was called with a filename
    if filename is None:
        filename = asksaveasfile(defaultextension=".tsp")
    # check if the user did select a file
    if filename:
        _file = open(filename.name, 'w')
        _file.write("NAME : " + os.path.basename(filename.name) + "\n")
        _file.write("COMMENT : " + comment + "\n")

        groups = construct_groups_string(nodes)
        if not groups == "":
            _file.write("COMMENT : CLUSTERS : " + groups + "\n")

        startnodes = construct_startnodes_string(nodes)
        if not startnodes == "":
            _file.write("COMMENT : STARTNODES : " + startnodes + "\n")

        _file.write("TYPE: TSP" + "\n")
        _file.write("DIMENSION: " + str(len(nodes)) + "\n")
        _file.write("EDGE_WEIGHT_TYPE : EUC_2D" + "\n")
        _file.write("NODE_COORD_SECTION" + "\n")

        for (index, node) in enumerate(nodes):
            _file.write(str(index) + "  " + str(node.x_coord * scale) +
                        " " + str(node.y_coord * scale) + "\n")
        _file.write("EOF")
        _file.close()
        return os.path.basename(filename.name)


def export_tikz(nodes, scale):
    """ Exports the problem data as a tikz graphic in .tex format  """
    filename = asksaveasfile(defaultextension=".tex")
    if filename:
        _file = open(filename.name, 'w')

        _file.write("\\begin{tikzpicture}\n")
        _file.write("\\begin{axis}[%\n")
        _file.write("width=\\textwidth,\n")
        _file.write("scale only axis,\n")
        _file.write("xmin=-100,\n")
        _file.write("xmax=2700,\n")
        _file.write("ymin=-100,\n")
        _file.write("ymax=2100,\n")
        _file.write("y dir=reverse,\n")
        _file.write("axis x line*=bottom,\n")
        _file.write("axis y line*=left\n")
        _file.write("]\n")

        for group in get_groups(nodes):
            _file.write(
                """\\addplot [color=black,mark size=5.0pt,
                        only marks,mark=*,mark options={solid,
                        fill=""" + tsputil.COLORS[group].lower() +
                "},forget plot]\n")
            _file.write("table[row sep=crcr]{%\n")
            for node in nodes:
                if node.color == group:
                    _file.write(
                        str(node.x_coord * scale) + " " +
                        str(node.y_coord * scale) + "\\\\\n")
            _file.write("};\n")
        _file.write("\\end{axis}\n")
        _file.write("\\end{tikzpicture}%\n")
        _file.close()
