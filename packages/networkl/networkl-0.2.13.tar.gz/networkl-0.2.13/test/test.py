import networkx as nx
import networkl as nl
from random import randrange

N=800
G = nx.barabasi_albert_graph(N,2)                                #create a graph
SparseD = nl.sparse_distance_matrix(G)                         #compute the Sparse Distance Matrix
D = nx.all_pairs_shortest_path_length(G)

new_edges = [(randrange(N),randrange(N)) for c in range(1000)]
for i,j in new_edges:                                 
	if (not G.has_edge(i,j)) or i==j:
		continue
	print 'removing edge (%s,%s)'%(i,j),
	nl.update_distance_matrix(G,D,i,j,mode='remove')	
	G.add_edge(i,j)
	print '  (2)'
	nl.update_distance_matrix(G,SparseD,i,j,mode='remove')
	#G.remove_edge(i,j)
	
Dnew = nx.all_pairs_shortest_path_length(G)
for i in G.nodes():
	for j in G.nodes():
		#print i,j,SparseD[i][j]==D[i][j],Dnew[i][j] == D[i][j]
		if (not SparseD[i][j] == Dnew[i][j]) or (not Dnew[i][j] == D[i][j]):
			print 'err'