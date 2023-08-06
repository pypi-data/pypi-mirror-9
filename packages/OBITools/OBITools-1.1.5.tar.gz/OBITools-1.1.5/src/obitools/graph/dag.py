from obitools.graph import DiGraph,Node
from obitools.graph.algorithms.component import componentIterator

class DAG(DiGraph):
    def __init__(self,label='G',indexer=None,nodes=None,edges=None):
        '''
        Directed Graph constructor.

        @param label: Graph name, set to 'G' by default
        @type label: str
        @param indexer: node label indexer
        @type indexer: Indexer instance
        @param nodes: set of nodes to add to the graph
        @type nodes: iterable value
        @param edges: set of edges to add to the graph
        @type edges: iterable value
        '''
        
        self._parents={}
        DiGraph.__init__(self, label, indexer, nodes, edges)
        
    def getNode(self,node=None,index=None):
        if index is None:
            index = self._index.getIndex(node, True)
        return DAGNode(index,self)
    
    def addEdge(self,node1=None,node2=None,index1=None,index2=None,**data):
        index1=self.addNode(node1, index1)
        index2 =self.addNode(node2, index2)

        pindex = set(n.index 
                     for n in self.getNode(index=index1).ancestorIterator())
        
        assert index2 not in pindex,'Child node cannot be a parent node'

        DiGraph.addEdge(self,index1=index1,index2=index2,**data)   

        if index2 in self._parents:
            self._parents[index2].add(index1)
        else:
            self._parents[index2]=set([index1])   

                                 
        return (index1,index2)
    
    def getRoots(self):
        '''
        Return the list of all roots of the DAG (i.e. nodes without parent)
        
        @return: a list of DAGNode
        '''
        return [x for x in self.nodeIterator(lambda n : n.index not in self._parents)]
    
    def getLeaves(self):
        '''
        Return the list of all leaves of the DAG (i.e. nodes without child)
        
        @return: a list of DAGNode
        '''
        return [x for x in self.nodeIterator(lambda n : not n.neighbourIndexSet())]
            

        
    
class DAGNode(Node):
    
    def getParents(self):
        if self.index in self.graph._parents:
            return [DAGNode(p,self.graph) for p in self.graph._parents[self.index]]
        else:
            return []
        
    def ancestorIterator(self):
        if self.index in self.graph._parents:
            for p in self.graph._parents[self.index]:
                parent = DAGNode(p,self.graph)
                yield parent
                for pnode in parent.ancestorIterator():
                    yield pnode
                    
    def getRoot(self):
        x=self
        for x in self.ancestorIterator():
            pass
        return x 
                    
    def leavesIterator(self):
        if not self:
            yield self
        for n in self:
            for nn in n.leavesIterator():
                yield nn
                
    def subgraphIterator(self):
        yield self
        for n in self:
            for nn in n.subgraphIterator():
                yield nn
        
