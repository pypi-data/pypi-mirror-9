''' Container definition for (phylogenetic) bifurcating or multifurcating trees
defined using Newick strings, collections of them, and for splits of these
trees. '''

# Date:   Oct 20 2014
# Author: Alex Safatli
# E-mail: safatli@cs.dal.ca

# Imports

import newick, rearrangement, base
from math import factorial as fact
from numpy import median

# Function Defitions

numberRootedTrees   = lambda t: numberUnrootedTrees(t+1)
numberUnrootedTrees = lambda t: (fact(2*(t-1)-3))/((2**(t-3))*fact(t-3))

# Class Definitions for Trees

class tree(object): # TODO: Integrate with P4 Tree class (?).
    
    ''' Defines a single (phylogenetic) tree by newick string;
    can possess other metadata. '''
    
    def __init__(self,newi='',check=False,structure=None):
        
        ''' If enabled, "check" will force the structure to reroot
        the given Newick string tree to a lowest-order leaf in order
        to ensure a consistent Newick string among any duplicate
        topologies. If a structure is provided and check is disabled,
        all parsing routines are bypassed and the Newick and Structure
        fields of this tree are overriden by the appropriate arguments. 

        :param newi: A Newick or New Hampshire string for a tree (unrooted 
        or rooted).
        :type newi: string
        :param check: An optional argument; boolean indicating whether to
        perform parsing checks on the string. May change what Newick string
        is assigned without changing tree topology.

        '''
        
        self.name   = ''
        self.score  = None
        self.origin = None
        self.newick = newi
        if (check): self._checkNewick(newi)        
        elif (structure == None): self._setNewick(newi)
        else: self.struct = structure
    
    # Getters, Mutators
    
    def getName(self):

        ''' Gets the name of this tree if it has been defined.

        :return: a string

        '''

        return self.name

    def setName(self,n):

        ''' Sets the name of this tree (object).

        :param n: A string indicating this tree's name.
        :type n: a string

        '''

        self.name = n

    def getScore(self):

        ''' Gets the score(s) (objective function) for this tree if it/they 
        has/have been defined.

        :return: a tuple of floats or integers

        '''

        return self.score

    def setScore(self,s):

        ''' Sets the score(s) for this tree. Should be performed by a scorer
        (see scoring functions in the appropriate module).

        :param s: A set of objective function scores.
        :type s: a tuple of floats or integers

        '''

        self.score = s

    def getOrigin(self):

        ''' Gets the "origin" of this tree, or where this tree was acquired
        or constructed from. Usually set by other code or an interface.

        :return: string or None

        '''

        return self.origin

    def setOrigin(self,o):
        
        ''' Set the "origin" or specification of where this tree
        was acquired or constructed from.

        :param o: A string indicating where the tree came from.
        :type o: string or None

        '''
        
        self.origin = o    
        
    def getNewick(self):

        ''' Gets the Newick (New Hampshire) string for this tree.

        :return: a string

        '''

        return self.newick

    def toNewick(self):

        ''' Gets the Newick (New Hampshire) string for this tree.

        :return: a string

        '''

        return self.newick

    def _setNewick(self,n):
        
        ''' PRIVATE: Set Newick string to n; also acquires 
        corresponding "structure" or Newick string without 
        branch lengths. '''
        
        self.newick = n
        self.struct = self._getStructure()
        
    def updateNewick(self,n,reroot=False):
        
        ''' Update the contained Newick string only as long
        as the structure obtained (after rerooting, which is
        an optional parameter) is identical to the contained
        structure. 

        :param n: A Newick or New Hampshire formatted string.
        :type n: a string
        :param reroot: A boolean indicating whether to reroot the provided
        Newick string to a lexicographically lowest-order taxa name to ensure
        redundant topologies across other trees.

        '''

        thisStruct = self._getStructure(reroot=reroot)
        if (thisStruct != self.getStructure()):
            raise ValueError(
                'Updated string infers structural change of tree!')
        self.newick = n
        
    def getStructure(self):

        ''' Returns the tree's "structure", a Newick string without any 
        branch lengths. 

        :return: a string

        '''
        
        return self.struct 
    
    def getRerootedNoBranchLengthNewick(self): 
    
        ''' Returns the tree's "structure", a Newick string without any 
        branch lengths. 

        :return: a string

        '''
        
        return self.getStructure()
    
    def getSimpleNewick(self):

        ''' Return a Newick string with all taxa name replaced with
        successive integers. 

        :return: a string

        '''
    
        o = newick.newickParser(self.newick).parse()
        t = base.treeStructure(o)
        n = t.getAllLeaves()
        for _ in xrange(1,len(n)+1): n[_-1].label = str(_)
        return str(o) + ';'        
    
    # Other Functionality
    
    def toTopology(self):
        
        ''' Return a topology object instance for this tree to allow 
        for rearrangement of the actual structure of the tree. 

        :return: a :class: `rearrangement.topology` object

        '''
        
        t = rearrangement.topology()
        t.fromNewick(self.newick)
        return t
    
    # Internals
        
    def __eq__(self,o):
        if (o == None): return False
        return (o.struct == self.struct)
    
    def __ne__(self,o): return not (self.__eq__(o))
    def __str__(self): return self.newick
    
    def _checkNewick(self,newi):
        
        ''' PRIVATE: Run the Newick string through a 
        parse pass and reroot to lowest-order leaf in
        order to ensure a consistent Newick string. '''
        
        newi = newi.strip('\n').strip(';') + ';'
        topo = rearrangement.topology()
        topo.fromNewick(newi)
        self.newick = topo.toNewick()
        self.struct = self._getStructure(topo.getRoot())
    
    def _getStructure(self,prsd=None,reroot=False):
        
        ''' PRIVATE: Acquires a newick string without any
        defined branch lengths. '''
        
        if prsd: p = prsd
        else: p = newick.newickParser(self.newick).parse()
        if reroot:
            topo = rearrangement.topology(p)
            p = topo.getRoot()
        newick.removeBranchLengths(p)
        return str(p) + ';'
    
class treeSet(base.Sized,base.Iterable):
    
    ''' Represents an ordered, disorganized collection of trees 
    that do not necessarily comprise a combinatorial space. '''
    
    def __init__(self):
       
        self.trees = list()    
    
    def addTree(self,tr): 

        ''' Add a tree object to the collection. 

        :param tr: A tree object.
        :type tr: :class: `tree`

        '''
    
        self.trees.append(tr)

    def addTreeByNewick(self,newick):
        
        ''' Add a tree to the structure by Newick string. 

        :param newick: A New Hampshire or Newick string.
        :type newick: a string

        '''
        
        t = tree(newick)
        return self.addTree(t)    
        
    def removeTree(self,tr):
        
        ''' Remove a tree object from the collection if present. 

        :param tr: A tree object (present in the collection).
        :type tr: :class: `tree`

        '''
        
        if tr in self.trees:
            self.trees.remove(tr)
    
    def indexOf(self,tr):
        
        ''' Acquire the index in this collection of a tree object. 
        Returns -1 if not found. 

        :param tr: A tree object.
        :type tr: :class: `tree`
        :return: an integer [-1,length of collection)

        '''
        
        if tr in self.trees: return self.trees.index(tr)
        else: return -1
    
    def __getitem__(self,i): return self.trees[i]
    def __setitem__(self,i,o): self.trees[i] = o
    def __len__(self): return len(self.trees)
    
    def __iter__(self):
        
        for t in self.trees: yield t
    
    def iterTrees(self):
        
        ''' Iterate over all trees found in this set. '''
        
        for t in self: yield t    
    
    def toTreeFile(self,fout):
        
        ''' Output this landscape as a series of trees, separated by
        newlines, as a text file saved at the given path. 

        :param fout: A string indicating a file system path to a file.
        :type fout: a string

        '''
        
        o = open(fout,'w')
        o.write(str(self))
        o.close()
        return fout
    
    @staticmethod
    def fromTreeFile(fin):
        
        ''' Acquire a file where newlines separate Newick strings, and create
        an instance of treeSet from those trees. '''
        
        t = treeSet()
        o = open(fin,'r')
        for line in o.readlines():
            newickString = line.strip()
            t.addTreeByNewick(newickString)
        o.close()
        return t
        
    def __str__(self):
        return '\n'.join([t.getNewick() for t in self.trees])
    
# Bipartition Class Definitions    
    
class bipartition(object):

    ''' A tree bipartition. Requires a tree topology. Using the term borrowed
    from nomenclature of a bipartite graph, a bipartition for a phylogenetic
    tree coincides with the definition of two disjoint sets U and V . A branch
    in a phylogenetic tree defines a single bipartition that divides the tree
    into two disjoint sets U and V . The set U comprises all of the children
    leaf of the subtree associated with that branch. The set V contains the rest
    of the leaves or taxa in the tree. '''

    def __init__(self,topol,bra=None):
        
        ''' Construct a bipartition from a branch in a topology. 
        
        :param topol: A topology.
        :type topol: :class: `rearrangement.topology`
        :param bra: An optional argument; can still acquire a bipartition from a
        string.
        :type bra: :class: `newick.branch`
        
        '''
        
        self.topology = topol
        self.branch   = bra
        self.btuple   = None # Tuple list representation.
        self.strrep   = None # String representation
        self.shortstr = ''   # Shorter string representation
        self.shortmap = None # Shorter string mapping of taxa to symbols
        self.reconfis = None # Possible reconfigurations as rearrangement objects.
        self._getStringRepresentation()
        self._getBranchListRepresentation()
    
    def __hash__(self): return hash(self.shortstr)
    
    def __eq__(self,o):
        
        if (type(o) != bipartition): return False
        l,r   = self.strrep
        lo,ro = o.strrep
        return ((lo==l and ro==r) or (ro==l and lo==r))
    
    def __ne__(self,o): return not self.__eq__(o)
    
    def _getStringRepresentation(self):
        
        ''' PRIVATE: Obtain string representation of a branch in a topology. '''
        
        if (self.branch == None): return
        if (self.topology == None):
            raise ValueError('Topology does not exist or is equal to None.')
        
        z            = self.topology.getStrBipartitionFromBranch(self.branch)
        l,r          = sorted(z[0]),sorted(z[1])
        self.strrep  = (l,r)
        
    def _getShortStringRepresentation(self):
        
        ''' PRIVATE: Obtain short string representation of branch/bipartition. '''
        
        ind  = 65 # 'A'
        l,r  = self.strrep
        x    = max((l,r),key=lambda d:len(d))
        if x == l: y = r
        else: y = l
        l,r  = x,y
        o    = ''
        lbls = [x for x in l] + [x for x in r]
        lblm = {}
        lbls = sorted(lbls) # Sort them.
        for i in lbls:
            lblm[i] = chr(ind)
            ind += 1
        for i in l: o += lblm[i]
        o += ':'
        for i in r: o += lblm[i]
        self.shortstr = o
        self.shortmap = lblm
        
    def _getBranchListRepresentation(self):
        
        l = [self.branch] + newick.getAllBranches(self.branch)
        r = [branch for branch in self.topology.getBranches(
            ) if not branch in l]
        self.btuple = (l,r)       
        
    def _getBranchFromString(self):
        
        ''' PRIVATE: Obtain branch information from a string representation. '''
        
        if not self.strrep or type(self.strrep) != tuple:
            raise IOError('Could not read string representation of bipartition.')
        self.branch = self.topology.getBranchFromStrBipartition(self.strrep)
        
    def _makeSPRRearrangements(self):
        
        ''' PRIVATE: Perform possible rearrangements. '''
        
        self.reconfis = self.topology.allSPRForBranch(self.branch)

    def fromStringRepresentation(self,st):
        
        ''' Acquire all component elements from a string representation 
        of a bipartition. 
        
        :param st: A string representation from a :class:`.bipartition` object.
        
        '''
        
        self.strrep = st
        self._getBranchFromString()
        
    def getBranch(self):
        
        ''' Get branch corresponding to this bipartition.
        
        :returns: :class:`newick.branch`
        
        '''
        
        return self.branch
    
    def getBranchIndex(self):
        
        ''' Return an index of the branch with respect to a post order traversal
        of the topology. 

        :return: an integer

        '''
        
        nodes = base.treeStructure.postOrderTraversal(self.topology.getRoot())
        for i in xrange(len(nodes)):
            node = nodes[i]
            if node.parent == self.branch:
                return i
    
    def getStringRepresentation(self):
        
        ''' Get the string representation corresponding to this bipartition. 

        :return: a string

        '''
        
        return self.strrep
    
    def getShortStringRepresentation(self):
        
        ''' Get the shorter string representation corresponding to this
        bipartition. 

        :return: a string

        '''
        
        if self.shortstr == '': self._getShortStringRepresentation()
        return self.shortstr
    
    def getShortStringMappings(self):
        
        ''' Get the mapping of symbols from taxa names for the shorter
        string representation. '''
        
        if self.shortstr == '': self._getShortStringRepresentation()
        return self.shortmap
    
    def getBranchListRepresentation(self):
        
        ''' Get the tuple of lists of branches that represent this bipartition.
        '''
        
        return self.btuple
    
    def getSPRRearrangements(self):
        
        ''' Return the set of all scores related to this bipartition. '''
        
        if (self.reconfis == None): self._makeSPRRearrangements()
        return self.reconfis
    
    def getSPRScores(self,ls,node=None):
        
        ''' Given a landscape, return all possible scores, not actively
        performing scoring if not done. '''
        
        # Get starting information.
        scores = list() # Output scoreset.
        if node is None:
            origin = self.topology # Starting topology.
            orstruct = origin.toTree().getStructure()
            # Acquire node corresponding to this topology.
            start = ls.findTreeTopologyByStructure(orstruct)
            if (start == None):
                raise ValueError(
                    'Could not find topology corresponding to bipartition.')
        else: start = node
            
        # Get neighbors.
        neighbors = ls.graph.neighbors(start)
        
        # Investigate all rearrangements.
        rearrangements = self.getSPRRearrangements()
        resultants = [x.toTree().getStructure() for x in rearrangements]
        for neighbor in neighbors:
            node   = ls.getNode(neighbor)
            tree   = ls.getTree(neighbor)
            struct = tree.getStructure()
            if struct in resultants:
                scores.append(tree.score[0])
        return scores
    
    def getMedianSPRScore(self,ls,node=None):
        
        ''' Given a landscape, return the median SPR score. '''
        
        li = [x for x in self.getSPRScores(ls,node) if x]
        if len(li) > 0: return median(li)
        else: return None
        
    def getBestSPRScore(self,ls,node=None):
        
        ''' Given a landscape, return the best SPR score. '''
        
        li = [x for x in self.getSPRScores(ls,node) if x]
        if len(li) > 0: return max(li)
        else: return None
