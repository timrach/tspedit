import re
import ast
import os
from tkinter.filedialog import asksaveasfile, askopenfile
from tsputil import *


def parseTSPFile(file):
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


def importTSP(callback):
    # show a open-file-dialog
    filename = askopenfile()
    # if the user selected a file, delete old data,parse the file and
    # load the new data. If the user canceled the selection, do nothing.
    if filename:
        nodes, groups = parseTSPFile(filename.name)
        callback(os.path.basename(filename.name),nodes, groups)


def exportTSP(nodes, scale, callback):
    filename = asksaveasfile(defaultextension=".tsp")
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
                        fill=""" + colors[g] + "},forget plot]\n")
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
