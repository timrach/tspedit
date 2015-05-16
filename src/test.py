from Node import *
from SolverModule import *

class Test:

    def __init__(self):
        node0 = Node(0,  11, 3, "Red")
        node1 = Node(1,  11, 8, "Red")
        node2 = Node(2,  11, 11, "Red")
        node3 = Node(3,  12, 13, "Red")
        node4 = Node(4,  15, 9, "Red")
        node5 = Node(5,  14, 5, "Red")
        node6 = Node(6,  11, 6, "Red")
        node7 = Node(7,  5, 4, "Red")
        node8 = Node(8,  10, 2, "Red")
        node9 = Node(9,  15, 12, "Red")
        node10 = Node(10,  13, 8, "Red")
        node11 = Node(11,  9, 10, "Red")
        node12 = Node(12,  6, 8, "Red")
        node13 = Node(13,  14, 7, "Red")
        node14 = Node(14,  9, 6, "Red")
        node15 = Node(15,  13, 4, "Red")
        node16 = Node(16,  14, 0, "Red")
        node17 = Node(17,  15, 3, "Red")
        node18 = Node(18,  15, 7, "Red")
        node19 = Node(19,  8, 14, "Red")
        self.nodes = [node0,node1,node2,node3,node4,node5,node6,node7,node8,node9,
                      node10,node11,node12,node13,node14,node15,node16,node17,node18,node19]
        self.scale = 100
        self._data = {'nodes' : self.nodes,
                      'scale' : self.scale}

        solver = SolverModule(self,self)
        solver.convexHullModel(_start=5)

    def registerData(self, key, value):
        pass
    def getData(self, key):
        return self._data[key]
    def commitChange(self,key,data):
        pass

if __name__ == '__main__':
    test = Test()