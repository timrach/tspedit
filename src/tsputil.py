colors = ["Black", "Red", "Green", "Blue", "Orange", "Cyan",
          "Magenta", "Yellow", "Gray", "White", "Brown",
          "Pink", "Purple", "Violet"]


def getGroups(nodes):
    """ return an array holding all occuring colorids of the given nodeset"""
    groups = []
    for n in nodes:
        if not n.color in groups:
            groups.append(n.color)
    return groups


def constructGroupsString(nodes):
    """ """
    groups = getGroups(nodes)
    if (len(groups) <= 1):
        return ""
    else:
        result = []
        for g in groups:
            group = []
            for n in nodes:
                if(n.color == g):
                    #+1 because .tsp nodes are indexed with 1
                    group.append(n.id + 1)
            result.append(group)
        return str(result)
