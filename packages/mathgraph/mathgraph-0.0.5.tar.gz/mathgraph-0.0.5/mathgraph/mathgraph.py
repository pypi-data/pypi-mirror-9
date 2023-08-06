import numpy as np
import networkx as nx
import mathchem as mc
import itertools as it
from numpy import linalg as la


class MathGraph ():
    r"""
    MathGraph
    """
    
    __NX_graph = None
    __Mol_graph = None
    
    
    def _reset_(self):
        """ Reset all attributes """
        self.__NX_graph = None
        self.__Mol_graph = None
        
    def __init__(self):
        """ Molecular graph class """
	self.__NX_graph = nx.Graph()

    def NX_graph(self):
        """ Return NetworkX graph object """
        return self.__NX_graph

    def Mol_graph(self):
        """ Return Mathchem graph object """
	if self.__Mol_graph is None:
		nxg = self.NX_graph()
        	self.__Mol_graph = mc.Mol(nx.generate_graph6(nxg))
	return self.__Mol_graph

    def add_edge(self, u, v=None):
	"""Add edge between u and v""" 
	nxg = self.NX_graph()
	
	if isinstance(u, (int, long)) == False:
		x = u.id	
	else:
		x = u
	if isinstance(u, (int, long)) == False:
		y = v.id	
	else:
		y = v
	
	nxg.add_edge(x, y)
        
    def degree_matrix(self):
	""" degrees matrix """
	nxg = self.NX_graph()
	mcg = self.Mol_graph()
	nodes = nxg.nodes()
        DM = np.ndarray((len(nodes), len(nodes)))
	degrees = np.array(mcg.degrees())
	for i in nodes:
		for j in nodes:
			if i == j: 
				DM[i,i] = degrees[i]
			else:
				DM[i,j] = 0

	return DM
	
    def subset (self):
        """ find subsets of nodes """
        nxg = self.NX_graph()
	nodes = nxg.nodes()
	subsets_array = []
	num = 1
	for i in nodes:
		subsets = set(it.combinations(nodes,num))
		subsets_array.append([])
		for j in subsets:
			t = set(list(j))
			subsets_array[num-1].append(t)
		num += 1
	return subsets_array

    def complementary_subset(self):
	""" find complement sets for every subset of nodes """
	subsets_array = self.subset()
        nxg = self.NX_graph()
	nodes = nxg.nodes()
	nodes_set = set([])
	num = 1
	comp_subsets_array = []
	for i in nodes:
		nodes_set.add(i)
	for i in nodes:
		comp_subsets_array.append([])
		diffs = set([])
		for j in subsets_array[num-1]:
			diffs = nodes_set - j
			comp_subsets_array[num-1].append(diffs)
		num += 1
	return comp_subsets_array


    def dominating_condition(self, k, num, count):
	""" logic to verify presence of dominance """
        subsets_array = self.subset()
        nxg = self.NX_graph()
	nodes = nxg.nodes()
	subset_row = subsets_array[num-1]
	lcount = 1	
	for j in subset_row:
		if lcount == count:
			for m in j:
				if nxg.has_edge(k,m):
					return 1
		lcount += 1
			
	return 0 


    def dominating_set(self):
	""" dominating sets of a graph """
	comp_subsets_array = self.complementary_subset()
	nodes_set = set([])
	dom_set = []
	num = 1
        nxg = self.NX_graph()
	nodes = nxg.nodes()
	num = 1
	for i in nodes:
		nodes_set.add(i)
	for i in nodes:
		comp_subset_row = comp_subsets_array[num-1]
		count = 1
		for j in comp_subset_row:
			ret = 0
			for k in j:
				ret = self.dominating_condition(k, num, count)
				if ret == 0:
					break;				
			if ret == 1:
				dom_set.append(nodes_set - j)	
			count += 1
		num += 1
	return dom_set

    def minimal_dominating_set(self):
	""" minimal dominating sets of a graph """
	minimal_dom_set = []
	dom_set = self.dominating_set()
	dom_len = len(dom_set[0])
	for i in dom_set:
		if dom_len != len(i): 
			break;
		minimal_dom_set.append(i)
	return minimal_dom_set

    def minimal_dominating_energy(self):
	""" Minimal dominating energy """
	minimal_dom_set = self.minimal_dominating_set()
	print minimal_dom_set
	energy = []
	nxg = self.NX_graph()
	mcg = self.Mol_graph()
	nodes = nxg.nodes()
	adj = np.array(mcg.adjacency_matrix())
	for j in minimal_dom_set:
		for u, v in nxg.edges_iter():
			if u in j and v in j:
				adj[u,v] = 1
		for i in nodes:
			if i in j:
				adj[i,i] = 1
		s = la.eigvalsh(adj).tolist()
		s.sort(reverse=True)
		a = np.sum(s,dtype=np.longdouble)/len(s)
		energy.append(np.float64(np.sum( map( lambda x: abs(x-a) ,s), dtype=np.longdouble)))

	return energy

    def covering_set(self):
	""" covering sets of a graph """
	cover_set = []
	nxg = self.NX_graph()
	nodes = nxg.nodes()
        subsets_array = self.subset()
	num = 1
	for i in nodes:
		subset_row = subsets_array[num-1]
        	for j in subset_row:
			flag = 0
			for u, v in nxg.edges_iter():
				if u in j or v in j:
					flag = 1
				else:
					flag = 0
					break;
			if flag == 1:
				cover_set.append(j)
		num += 1
	return cover_set

    def minimal_covering_set(self):
	""" covering sets of a graph """
	minimal_cover_set = []
	cover_set = self.covering_set()
	cover_len = len(cover_set[0])
	for i in cover_set:
		if cover_len != len(i): 
			break;
		minimal_cover_set.append(i)

	return minimal_cover_set

    def minimal_covering_energy(self):
	""" Minimal covering energy """
	minimal_cover_set = self.minimal_covering_set()
	print minimal_cover_set
	energy = []
	nxg = self.NX_graph()
	mcg = self.Mol_graph()
	nodes = nxg.nodes()
	adj = np.array(mcg.adjacency_matrix())
	for j in minimal_cover_set:
		for u, v in nxg.edges_iter():
			if u in j and v in j:
				adj[u,v] = 1
		for i in nodes:
			if i in j:
				adj[i,i] = 1
		s = la.eigvalsh(adj).tolist()
		s.sort(reverse=True)
		a = np.sum(s,dtype=np.longdouble)/len(s)
		energy.append(np.float64(np.sum( map( lambda x: abs(x-a) ,s), dtype=np.longdouble)))

	return energy

    def min_laplacian_dominating_energy(self):
	""" laplacian covering energy """
	nxg = self.NX_graph()
	minimal_dom_set = self.minimal_dominating_set()
	energy = []
	nodes = nxg.nodes()
	mcg = self.Mol_graph()
	degree_array = np.array(self.degree_matrix())
	adj = np.array(mcg.adjacency_matrix())
	for j in minimal_dom_set:
		for u, v in nxg.edges_iter():
			if u in j and v in j:
				adj[u,v] = 1
		for i in nodes:
			if i in j:
				adj[i,i] = 1
		print adj
		lap = adj - degree_array
		print lap
		s = la.eigvalsh((lap)).tolist()
		s.sort(reverse=True)
		a = np.sum(s,dtype=np.longdouble)/len(s)
		energy.append(np.float64(np.sum( map( lambda x: abs(x-a) ,s), dtype=np.longdouble)))

	return energy

    def atom_bond_connectivity_index2(self):
        """ Atom-Bond Connectivity Index (ABC2) """
	nxg = self.NX_graph()
	mcg = self.Mol_graph()
        s = np.longdouble(0) # summator
	la = mcg.edges()
	lb = mcg.vertices()
        for (x,y) in nxg.edges():
        	s1 = np.longdouble(0) # summator
        	s2 = np.longdouble(0) # summator
		t1 = []
		t2 = []
		la = mcg.distances_from_vertex(x)
		lb = mcg.distances_from_vertex(y)
		for  keys,values in la.items():
			t1.append(values)
		for  keys,values in lb.items():
			t2.append(values)
		for v in mcg.vertices():
			if t1[v]<t2[v]:
				s1 += 1
			elif t1[v]>t2[v]:
				s2 += 1
			
			if s1 != 0 and s2 != 0:
				s += np.longdouble( ( (s1 + s2 - 2 ) / (s1 * s2)) ** .5 )
	
        return np.float64(s)

    def atom_bond_connectivity_index4(self):
        """ Atom-Bond Connectivity Index (ABC4) """
        nxg = self.NX_graph()
	mcg = self.Mol_graph()
        s = np.longdouble(0) # summator
        for (x,y) in nxg.edges():
                s1 = np.longdouble(0) # summator
                s2 = np.longdouble(0) # summator
                l = nx.all_neighbors(nxg, x)
                m = nx.all_neighbors(nxg, y)
                for i in l:
                        s1 += np.float64(mcg.degrees()[i])
                for i in m:
                        s2 += np.float64(mcg.degrees()[i])
			if s1 != 0 and s2 != 0:
                		s += np.longdouble( ( (s1 + s2 - 2 ) / (s1 * s2)) ** .5 )
        return np.float64(s)

    def seidel_energy(self):
        """ seidel energy """
	mcg = self.Mol_graph()
        s = la.eigvalsh(mcg.seidel_matrix()).tolist()
        s.sort(reverse=True)
        a = np.sum(s,dtype=np.longdouble)/len(s)
        return np.float64(np.sum( map( lambda x: abs(x-a) ,s), dtype=np.longdouble))

    def maximum_degree_energy(self):
                """ Max degree energy """
		mcg = self.Mol_graph()
                m = mcg.order()
                n = mcg.vertices()
                RD = np.ndarray((m, m))
                for i in n:
                        for j in n:
                                if mcg.distance_matrix()[i,j] == 1:
                                        RD[i,j] = np.maximum(mcg.degrees()[i], mcg.degrees()[j]);
                                else:
                                        RD[i,j] = 0;
                s = la.eigvalsh(RD).tolist()
                s.sort(reverse=True)
                a = np.sum(s,dtype=np.longdouble)/len(s)
                return np.float64(np.sum( map( lambda x: abs(x-a) ,s), dtype=np.longdouble))

    def common_neighbourhood(self):
                """ common neighbourhood """
                nxg = self.NX_graph()
		mcg = self.Mol_graph()
                m = mcg.order()
                n = mcg.vertices()
                RD = np.ndarray((m, m))
                for i in n:
                        for j in n:
                                if i == j:
                                        RD[i, j] = 0
                                        continue
                                l =  nx.common_neighbors(nxg, i, j)
                                count = 0
                                for k in l:
                                        count += 1
                                RD[i,j] = count
                return RD

    def atom_bond_connectivity_index5(self):
        """ Atom-Bond Connectivity Index (ABC5) """
        nxg = self.NX_graph()
        s = np.longdouble(0) # summator
        for (x,y) in nxg.edges():
                ex = np.longdouble(0) # summator
                ey = np.longdouble(0) # summator
                ex = nx.eccentricity(nxg, x)
                ey = nx.eccentricity(nxg, y)
		if ex != 0 and ey != 0:
                	s += np.longdouble( ( (ex + ey - 2 ) / (ex * ey)) ** .5 )
        return np.float64(s)
