import re
import ast
import os
import tsputil
from Node import *
try:
    # for Python2
    from tkFileDialog import asksaveasfile, askopenfile
except ImportError:
    # for Python3
    from tkinter.filedialog import asksaveasfile, askopenfile


def parseTSPFile(file):
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

    f = open(file, 'r')
    lines = f.readlines()
    for l in range(len(lines)):
        nar = re.match(name_regex, lines[l])
        nr = re.match(node_regex, lines[l])
        cor = re.match(comment_regex, lines[l])
        clr = re.match(cluster_regex, lines[l])
        if len(lines[l]):
            sr = re.match(start_regex, lines[l])
            sr2 = re.match(start_regex2, lines[l])
            # Match Filename
            if nar:
                name = nar.group(1)
            # Match coordinates
            if nr:
                x = int(float(nr.group(2)))
                y = int(float(nr.group(3)))
                nodes.append([x, y])
            # Match Comments
            if cor:
                # Match Clusters
                if clr:
                    groups = clr.group(1)
                    groups = groups.replace(" ", "")
                    groups = ast.literal_eval(groups)
                elif sr:
                    startnodes = [int(sr.group(1))]
                elif sr2:
                    startnodes = sr2.group(1)
                    startnodes = ast.literal_eval(startnodes)
                else:
                    comment = comment + cor.group(1) + "\n"
    f.close
    return (name, comment, startnodes, nodes, groups)


def getGroups(nodes):
    """ return an array holding all occuring colorids of the given nodeset"""
    groups = []
    for n in nodes:
        if n.color not in groups:
            groups.append(n.color)
    return groups


def constructGroupsString(nodes):
    """ Constructs a string representing the grouping of nodes """
    groups = getGroups(nodes)
    if (len(groups) <= 1):
        return ""
    else:
        result = []
        for g in groups:
            group = []
            for n in nodes:
                if(n.color == g):
                    # +1 because .tsp nodes are indexed with 1
                    group.append(n.id + 1)
            result.append(group)
        return str(result)


def constructStartnodesString(nodes):
    res = []
    for node in nodes:
        if node.start:
            res.append(node.id)
    if len(res):
        return str(res)
    else:
        return ""


def parseSolutionfile(file):
    """ Returns the concatenated lines 1 to END """
    result = ""
    f = open(file, 'r')
    lines = f.readlines()
    for l in range(1, len(lines)):
        result += lines[l]
    return result


def importTSP(scale):
    """ Shows a filedialog to select a file to open and calls the callback
        with the parsed data  """
    # show a open-file-dialog
    filename = askopenfile()
    # if the user selected a file, delete old data,parse the file and
    # load the new data. If the user canceled the selection, do nothing.
    if filename:
        name, comment, startnodes, nodes, groups = parseTSPFile(filename.name)

        node_list = []
        # If the nodes are not grouped, draw them in the currently
        # selected color
        if groups == []:
            color = tsputil.colors[0]
            for node in nodes:
                new_node = Node(len(node_list),
                                int(node[0] / scale),
                                int(node[1] / scale), color)
                node_list.append(new_node)
        # if the nodes are grouped, draw nodes from the same group in the same
        # color
        else:
            # iterate over groups
            for (i, g) in enumerate(groups):
                # iterate over node ids in the group
                for e in g:
                    # get node coordinates
                    node = nodes[e - 1]
                    new_node = Node(len(node_list),
                                    int(node[0] / scale),
                                    int(node[1] / scale),
                                    tsputil.colors[i])
                    if new_node.id in startnodes:
                        new_node.start = True
                    node_list.append(new_node)
        return(name, comment, startnodes, node_list, groups)


def exportTSP(nodes, scale, comment, preFilename=None):
    """ Exports the problem data in .tsp format  """
    filename = preFilename
    if comment is None:
        comment = "PUT PROBLEM DESCRIPTION HERE"
    # check if the function was called with a filename
    if filename is None:
        filename = asksaveasfile(defaultextension=".tsp")
    # check if the user did select a file
    if filename:
        f = open(filename.name, 'w')
        f.write("NAME : " + os.path.basename(filename.name) + "\n")
        f.write("COMMENT : " + comment + "\n")

        groups = constructGroupsString(nodes)
        if not groups == "":
            f.write("COMMENT : CLUSTERS : " + groups + "\n")

        startnodes = constructStartnodesString(nodes)
        if not startnodes == "":
            f.write("COMMENT : STARTNODES : " + startnodes + "\n")

        f.write("TYPE: TSP" + "\n")
        f.write("DIMENSION: " + str(len(nodes)) + "\n")
        f.write("EDGE_WEIGHT_TYPE : EUC_2D" + "\n")
        f.write("NODE_COORD_SECTION" + "\n")

        for (i, n) in enumerate(nodes):
            f.write(str(i) + "  " + str(n.x * scale) +
                    " " + str(n.y * scale) + "\n")
        f.write("EOF")
        f.close()
        return os.path.basename(filename.name)


def exportTIKZ(nodes, scale):
    """ Exports the problem data as a tikz graphic in .tex format  """
    filename = asksaveasfile(defaultextension=".tex")
    if filename:
        f = open(filename.name, 'w')

        f.write("\\begin{tikzpicture}\n")
        f.write("\\begin{axis}[%\n")
        f.write("width=\\textwidth,\n")
        f.write("scale only axis,\n")
        f.write("xmin=-100,\n")
        f.write("xmax=2700,\n")
        f.write("ymin=-100,\n")
        f.write("ymax=2100,\n")
        f.write("y dir=reverse,\n")
        f.write("axis x line*=bottom,\n")
        f.write("axis y line*=left\n")
        f.write("]\n")

        for g in getGroups(nodes):
            f.write(
                """\\addplot [color=black,mark size=5.0pt,
                        only marks,mark=*,mark options={solid,
                        fill=""" + tsputil.colors[g].lower() +
                "},forget plot]\n")
            f.write("table[row sep=crcr]{%\n")
            for n in nodes:
                if(n.color == g):
                    f.write(
                        str(n.x * scale) + " " +
                        str(n.y * scale) + "\\\\\n")
            f.write("};\n")
        f.write("\\end{axis}\n")
        f.write("\\end{tikzpicture}%\n")
        f.close()
