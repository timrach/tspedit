from Node import *
from SolverModule import *

class Test:

    def __init__(self):
        node0 = Node(0, 0,0, "Red")
        node1 = Node(1, 10,0, "Red")
        node2 = Node(2, 5,10, "Red")
        node3 = Node(3, 5,5, "Red")
        node4 = Node(4, 4,1, "Red")
        node5 = Node(5, 3,5, "Red")
        node6 = Node(6, 14,8, "Red")
        node7 = Node(7, 12,5, "Red")
        self.nodes = [node0,node1,node2,node3,node4,node5,node6,node7]
        self.scale = 100
        self._data = {'nodes' : self.nodes,
                      'scale' : self.scale}

        solver = SolverModule(self,self)
        solver.convexHullModel()

    def registerData(self, key, value):
        pass
    def getData(self, key):
        return self._data[key]
    def commitChange(self,key,data):
        pass

if __name__ == '__main__':
    test = Test()