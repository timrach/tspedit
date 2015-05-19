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
    # define regular expressions for the fields to parse
    regexes = {'name': re.compile("NAME : (.*)"),
               'comment': re.compile("COMMENT : (?!STARTNODE :|STARTNODES : |CLUSTERS :)(.*)"),
               'single_start': re.compile("COMMENT : STARTNODE : ([0-9])+"),
               'multi_start': re.compile("COMMENT : STARTNODES : (.*)"),
               'nodes':
               re.compile(
                   r"([0-9]+)\ *([0-9]*\.?[0-9]*)\ *([0-9]*\.?[0-9]*)",
                   re.MULTILINE),
               'groups': re.compile("COMMENT : CLUSTERS : (.*)")}
    # initialize results
    result = {'name': 'No Name', 'comment': '', 'startnodes': [],
              'nodes': [], 'groups': []}
    # Define application rules

    def apply_match(regex_name, match):
        """Applies a specific processing rule for each regex sperately as the
        fields vary in data types and structures"""
        if regex_name is 'name':
            result['name'] = match.group(1)
        elif regex_name is 'single_start':
            result['startnodes'] = [int(match.group(1))]
        elif regex_name is 'multi_start':
            result['startnodes'] = ast.literal_eval(match.group(1))
        elif regex_name is 'groups':
            result['groups'] = ast.literal_eval(
                match.group(1).replace(" ", ""))
        elif regex_name is 'comment':
            result['comment'] += match.group(1) + "\n"
        elif regex_name is 'nodes':
            result['nodes'].append([int(float(match.group(2))),
                                    int(float(match.group(3)))])
    # Process the lines in the file and check for matches for each regular
    # expression
    _file = open(file, 'r')
    lines = _file.readlines()
    for line in lines:
        if len(line):
            for regex_name in regexes:
                match = re.match(regexes[regex_name], line)
                if match:
                    apply_match(regex_name, match)
    _file.close()
    return result


def get_groups(nodes):
    """ return an array holding all occuring colorids of the given nodeset"""
    return list(set([node.color for node in nodes]))


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
        data = parse_tsp_file(filename.name)

        #Construct the list of ungrouped nodes
        color = tsputil.COLORS[0]
        node_list = [Node(index, int(node[0] / scale), int(node[1] / scale), color)
                     for (index, node) in enumerate(data['nodes'])]

        # if the nodes are grouped, change node colors accordingly
        for (index, group) in enumerate(data['groups']):
            for nid in group:
                node_list[nid-1].color = tsputil.COLORS[index]

        #mark nodes as startnode if specified
        for nid in data['startnodes']:
            node_list[nid].start = True

        result = data
        result['nodes'] = node_list
        return result
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
            _file.write(str(index + 1) + "  " + str(node.x_coord * scale) +
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
