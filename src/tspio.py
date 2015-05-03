import re
import ast
import os
from tkinter.filedialog import asksaveasfile, askopenfile
import tsputil


def parseTSPFile(file):
    """ Parses data from a tspfile with regexes and returns a tuple
    holding the nodes and groupinformation"""
    # Parse nodes
    node_regex = re.compile("([0-9]+)\ *([0-9]*\.?[0-9]*)\ *([0-9]*\.?[0-9]*)",
                            re.MULTILINE)
    # Parse Clusters
    cluster_regex = re.compile("COMMENT : CLUSTERS : (.*)")

    nodes = []
    groups = []

    f = open(file, 'r')
    lines = f.readlines()
    for l in range(len(lines)):
        m = re.match(node_regex, lines[l])
        n = re.match(cluster_regex, lines[l])
        if m and len(lines[l]):
            x = int(m.group(2))
            y = int(m.group(3))
            nodes.append([x, y])
        if n and len(lines[l]):
            groups = n.group(1)
            groups = groups.replace(" ", "")
            groups = ast.literal_eval(groups)

    f.close
    return (nodes, groups)


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


def parseSolutionfile(file):
    """ Returns the concatenated lines 1 to END """
    result = ""
    f = open(file, 'r')
    lines = f.readlines()
    for l in range(1, len(lines)):
        result += lines[l]
    return result


def importTSP(callback):
    """ Shows a filedialog to select a file to open and calls the callback
        with the parsed data  """
    # show a open-file-dialog
    filename = askopenfile()
    # if the user selected a file, delete old data,parse the file and
    # load the new data. If the user canceled the selection, do nothing.
    if filename:
        nodes, groups = parseTSPFile(filename.name)
        callback(os.path.basename(filename.name), nodes, groups)


def exportTSP(nodes, scale, callback, preFilename=None):
    """ Exports the problem data in .tsp format  """
    filename = preFilename
    # check if the function was called with a filename
    if filename is None:
        filename = asksaveasfile(defaultextension=".tsp")
        print(filename)
    # check if the user did select a file
    if filename:
        f = open(filename.name, 'w')
        f.write("NAME : " + os.path.basename(filename.name) + "\n")
        f.write("COMMENT : INSERT PROBLEM DESCRIPTION HERE" + "\n")

        groups = constructGroupsString(nodes)
        if not groups == "":
            f.write("COMMENT : CLUSTERS : " + groups + "\n")

        f.write("TYPE: TSP" + "\n")
        f.write("DIMENSION: " + str(len(nodes)) + "\n")
        f.write("EDGE_WEIGHT_TYPE : EUC_2D" + "\n")
        f.write("NODE_COORD_SECTION" + "\n")

        for (i, n) in enumerate(nodes):
            f.write(str(i) + "  " + str(n.x * scale) +
                    " " + str(n.y * scale) + "\n")
        f.write("EOF")
        f.close()
        callback(os.path.basename(filename.name))


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
