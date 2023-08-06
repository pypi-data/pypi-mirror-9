from collections import deque
import time
##import gmpy
import random
import math
import copy
import pickle
import os

#the following two funtion generate random dag
def ranconngrap(nnodes,nedges):
    
    """
   
    this function generate a connected directed acyclic graph,
       topological order is given, from 0 to nnodes-1.
    #Step 1, get a tree
    #Step 2, randomly generate edges in other unconnected pairs.
    """
    left=set(range(1,nnodes))
    connected=[0]
    dag=[[] for i in range(nedges)]
    for i in range(nnodes-1):
        x=random.sample(connected,1)[0]
        y=random.sample(left,1)[0]
        connected.append(y)
        left.remove(y)
        if x<y:
            dag[i]=[x,y]
        else:
            dag[i]=[y,x]
    j=nnodes-1
    vset=range(nnodes)
    while j<nedges:
        tem=random.sample(vset,2)
        if tem[0]>tem[1]:
            tem.reverse()
        if tem not in dag:
            dag[j]=tem[:]
            j+=1;
    return(dag)
            
            
        
def rangrap(nnodes,nedges):
    #generate a dag  
    nodeorder=random.sample(range(nnodes),nnodes)
    index=[[i,j] for i in range(nnodes) for j in range (i+1,nnodes)]
    edgesrandom=random.sample(index,nedges)
    for i in range(nedges):
        edgesrandom[i]=[nodeorder[edgesrandom[i][0]],nodeorder[edgesrandom[i][1]]]
    return(edgesrandom)
                
        


#the following functions generate the CPDAG\essential graph from the given DAG
def tporder(dag,p):
    #algorithm to get the order of a DAG with p vertices
    desdag=[[] for i in range(p)]
    parnum=[0 for i in range(p)]
    NEdge=len(dag)
    for i in range(NEdge):
        desdag[dag[i][0]].append(dag[i][1])
        parnum[dag[i][1]]+=1
    zero_indeg=deque([i for i in range(p) if parnum[i]==0])
    s=0
    tpord=[0 for i in range(p)]
    while len(zero_indeg)>0:
        v=zero_indeg.popleft()
        tpord[s]=v
        s+=1
        cs=desdag[v]
        if len(cs)==0:
            ##next
            continue
        for j in cs:
            parnum[j]-=1
            if parnum[j]==0:
                zero_indeg.appendleft(j)
    return(tpord)
    
def edgeorder(dag,p):
    #algorithm from chickering 2002
    dag1=copy.deepcopy(dag)
 
    tpord=tporder(dag1,p)
    nordmap=[0 for i in range(p)]
    for i in range(p):
        nordmap[tpord[i]]=i        

    a=sorted(dag1,key=lambda x:(nordmap[x[1]], -nordmap[x[0]]))
   
    return(a)
              
def labeledge(dag,p):
    
    """algorithm from chickering 2002,    compelled 1; reversible=-1; unkown=0"""
    """ Chickering, D. M.,  Learning equivalence classes of Bayesian-network structures,     The Journal of Machine Learning Research,2002.   """

    ansdag=[[] for i in range(p)]
    edgenum=[[] for i in range(p)]
    edgeord=edgeorder(dag,p)
    NEdge=len(dag)
    for i in range(NEdge):
        ansdag[edgeord[i][1]].append(edgeord[i][0])
        edgenum[edgeord[i][1]].append(i)
    unlabled=len(dag)
    edgelabel=[0 for i in range(unlabled)]
    while unlabled>0:
        v=edgelabel.index(0) #step 4 , v is index of x to y
        x=edgeord[v][0]
        y=edgeord[v][1]
        for wi in [i for i in range(len(ansdag[x])) if edgelabel[edgenum[x][i]]==1]:
            if ansdag[x][wi] not in ansdag[y]:
                for j in edgenum[y]:
                    if edgelabel[j]==0:
                        unlabled-=1
                    edgelabel[j]=1
                continue
            else:
                wyi=ansdag[y].index(ansdag[x][wi])
                if edgelabel[edgenum[y][wyi]]==0:
                    unlabled-=1
                edgelabel[edgenum[y][wyi]]=1
        #begin step 8         
        if len([z for z in ansdag[y] if z!=x and z not in ansdag[x]])>0:
            for yi in edgenum[y]:
                if edgelabel[yi]==0:
                    unlabled-=1
                    edgelabel[yi]=1
        else:
            for yi in edgenum[y]:
                if edgelabel[yi]==0:
                    unlabled-=1
                    edgelabel[yi]=-1
    for i in range(len(dag)):
        edgeord[i].append(edgelabel[i])            
    return(edgeord)

def cceg(dag,p):
    ## get essential graph from a dag
    ## generate chain components in the essential graph
    ## output is a list containing many feathers of the essential graph
    labg=labeledge(dag,p)
    chaincomps=[]
    diedges=[]
    for i in range(len(dag)):
        if labg[i][2]==-1:
            chaincomps.append([labg[i][0],labg[i][1]])
        else:
            diedges.append([labg[i][0],labg[i][1]])
##    out=conngrap(chaincomps)
##    return(out)
    neighbor={}
    #neighbors in eg graph, all nodes in chain component
    fatherset={}
    #father set in eg graph, some children are in chain component
    for i in range(len(chaincomps)):
        if not (neighbor.has_key(chaincomps[i][1])):
            neighbor[chaincomps[i][1]]=set([chaincomps[i][0]])
        else:
            neighbor[chaincomps[i][1]].add(chaincomps[i][0])
        if not (neighbor.has_key(chaincomps[i][0])):
            neighbor[chaincomps[i][0]]=set([chaincomps[i][1]])
        else:
            neighbor[chaincomps[i][0]].add(chaincomps[i][1])
    for i in range(len(diedges)):
        if not (fatherset.has_key(diedges[i][1])):
            fatherset[diedges[i][1]]=set([diedges[i][0]])
        else:
            fatherset[diedges[i][1]].add(diedges[i][0])
    leftnodes=set(neighbor.keys())
    ccc=[]
    while len(leftnodes)>0:
        visited=set()
        to_visit=[leftnodes.pop()]
        while len(to_visit)!= 0:
            v=to_visit.pop()
            visited.add(v)
            if v in leftnodes:
                leftnodes.remove(v)
            to_visit.extend(neighbor[v]&leftnodes)
        ccc.append(visited.copy())
    ccn=len(ccc)
    ccedgen=[0 for i in range(ccn)]
    neighborset=[{} for i in range(ccn)]
    node2cc={}
    for i in range(ccn):
        for nodesss in ccc[i]:
            neighborset[i][nodesss]=neighbor[nodesss]
            node2cc[nodesss]=i
            ccedgen[i]+=len(neighbor[nodesss])
    ccedgen=map(lambda a: a/2,ccedgen)
    output={}
    output["Neiset"]=neighborset
    
    output["nodes2neiset"]=node2cc
    output["diedges"]=diedges
    output["fatherset"]=fatherset
    output["ccedgeno"]=ccedgen
    output["undiedges"]=chaincomps
    
    return(output)




 
# the following functions are used in other funtions
def find_undipath(pdag, start, end, sepset=set(), path=[]):
    #ref codes from http://www.python.org/doc/essays/graphs.html
    #give a path
    adtem=pdag["nodes2neiset"][start]
    if adtem!=pdag["nodes2neiset"][end]:
        return None
    path = path + [start]
    if start == end:
        return path
    if start not in set(pdag['Neiset'][adtem].keys())-sepset:
        return None
    for node in pdag['Neiset'][adtem][start]-sepset:
        if node not in path:
            newpath = find_undipath(pdag, node, end, sepset,path)
            if newpath: return newpath
    return None

def undipathfds(pdag, start, end, sepset=set()):
    #start and end in the same chain component
    if (not pdag["nodes2neiset"].has_key(start)) | (not pdag["nodes2neiset"].has_key(end)):
        return False
    adtem=pdag["nodes2neiset"][start]
    if pdag["nodes2neiset"][start]!=pdag["nodes2neiset"][end]:
        return False
    fathandnei=pdag['Neiset'][adtem]
    to_visit=set([start])
    visited=set()
    while len(to_visit)!= 0:
        v=to_visit.pop()
        visited.add(v)
        if fathandnei.has_key(v):
            toadd=fathandnei[v]-sepset-visited               
            if end in toadd:
                return True
            to_visit|=toadd
    return False

 

def find_semidipath(fathandnei, start, end, sepset=set(),path=[]):
    #ref codes from http://www.python.org/doc/essays/graphs.html
    #fathandnei: dictionary record a node's father and neighbors
    #note: a path from end to start, father set
    path = path + [start]
    if start == end:
        return path
    if start not in set(fathandnei.keys())-sepset:
        return None
    for node in fathandnei[start]-sepset:
        if node not in path:
            newpath = find_semidipath(fathandnei, node, end,sepset,path)
            if newpath: return newpath
    return None
def semipathfds(fathandnei, start, end, sepset=set()):
    #fathandnei: dictionary record a node's father and neighbors
    #note: no path output
    if not fathandnei.has_key(start):
        return False
    else:
        to_visit=fathandnei[start]-set([end])
    visited=set([start])
    while len(to_visit)!= 0:
        v=to_visit.pop()
        visited.add(v)
        if fathandnei.has_key(v):
            toadd=fathandnei[v]-visited
            if end in toadd:
                return True
            to_visit|=toadd
    return False

def egdataextend(pdag):
    neighborset={}
    for i in pdag['Neiset']:
        for j in i.keys():
            neighborset[j]=copy.copy(i[j])
    sonset=findsonset(pdag)
    adjset=findadj(pdag)
    fatherandnei=find_fandn(pdag)
    pdag['neighborset']=neighborset
    pdag['sonset']=sonset
    pdag['adjset']=adjset
    pdag['fatherandnei']=fatherandnei
    return pdag
    
def jcompelled(pdag,Diedge,disset=set()):
    #True is compelled
    #neighborset is set with nodes connected with the key node by undirected edges.
    #fandnei is the set with nodes adjacent to the key node.
    #QQQQQ
    #compelled must be in the new eg, it's hard to judge locally. a undirected edges
    # in modified graph could be directed in EG.
    #Example, 1-->0,1-->3,2--->3,2--->0,3---0. Delete 2-->0.
    #how to judge 1-->0 compelled?
    fatherset=pdag['fatherset']
    neighborset=pdag['neighborset']
    adjset=pdag['adjset']
    
    x=Diedge[0]
    z=Diedge[1]
    #first case
    if fatherset.has_key(x):
        for w in fatherset[x]-disset:
            if w not in adjset[z]:
                return True
    #last three cases
    hafeset=set()
    for w in ((fatherset[z]-disset)-set([x])):
        if x not in adjset[w]:
            return True
        elif neighborset.has_key(w):
            if x in neighborset[w]:
                
                if len(hafeset)>0:
                    for kk in hafeset:
                        if kk not in adjset[w]:
                            return True
                hafeset.add(w)
        if fatherset.has_key(w):
            if x in fatherset[w]:
                return True
    return False

def findadj(pdag,vset=set()):
    #
    Neighbor={}
    dag=pdag['diedges']+pdag['undiedges']
    for i in dag:        
        if (i[0] in vset and i[1] in vset)|len(vset)==0:
            if not (Neighbor.has_key(i[1])):
                Neighbor[i[1]]=set([i[0]])
            else:
                Neighbor[i[1]].add(i[0])
            if not (Neighbor.has_key(i[0])):
                Neighbor[i[0]]=set([i[1]])
            else:
                Neighbor[i[0]].add(i[1])
    return(Neighbor)

def findsonset(pdag):
    out={}
    for i in pdag['fatherset'].keys():
        for j in pdag['fatherset'][i]:
            if out.has_key(j):
                out[j].add(i)
            else:
                out[j]=set([i])
    return out

def find_fandn(pdag):    
    #discpard=[x,y], x to y
    #find father and neighbor set for function find_semidipath()
    #isolated node not inclued in output
    btem={}
    for i in pdag['fatherset'].keys():
        btem[i]=copy.copy(pdag['fatherset'][i])
##    if discpard!=None:
##        btem[discpard[1]].remove(discpard[0])
    for i in pdag['Neiset']:
        for j in i.keys():
            if btem.has_key(j):
                btem[j]|=i[j]
            else:
                btem[j]=copy.copy(i[j])
    return(btem)
        

def judgeclique(pdag,vset):
    #all vset in a chain component
    if len(vset)==0:
        return True
    n=len(vset)
    for i in vset:
        if len(pdag['Neiset'][pdag['nodes2neiset'][i]][i]&vset)<n-1:
            return False
    return True


def jconn(pdag,nset,fandn):
    # used in pdag2dag function
    #undirected adjacent nodes is connected with other adjacent nodes.
    ved=set()
    for i in nset:
        ved.add(i)
        for j in (fandn-ved):
            if not pdag['adjset'].has_key(j):
                return False
            elif i not in pdag['adjset'][j]:
                return False
    return True
            

def findneighbor1(vset,neigh):
    #only used in count function
    neighbor={}
    for i in vset:
        neighbor[i]=neigh[i]&vset
    return(neighbor)

    
        

#The following function pdag2dag first get modified PDAG then generate a DAG from it.

def pdag2dag(pdag,type1,edgeslist):
## get a dag with a valid operator
    fatherset=pdag['fatherset']
    diedges=pdag['diedges']
    neighborset=pdag['neighborset']
    sonset=pdag['sonset']
    adj=pdag['adjset']
    if type1=="InsertU":
        if neighborset.has_key(edgeslist[0]):
            neighborset[edgeslist[0]].add(edgeslist[1])
        else:
            neighborset[edgeslist[0]]=set([edgeslist[1]])
        if neighborset.has_key(edgeslist[1]):
            neighborset[edgeslist[1]].add(edgeslist[0])
        else:
            neighborset[edgeslist[1]]=set([edgeslist[0]])

        if adj.has_key(edgeslist[0]):
            adj[edgeslist[0]].add(edgeslist[1])
        else:
            adj[edgeslist[0]]=set([edgeslist[1]])
        if adj.has_key(edgeslist[1]):
            adj[edgeslist[1]].add(edgeslist[0])
        else:
            adj[edgeslist[1]]=set([edgeslist[0]])
       
    elif type1=="DeleteU":
        neighborset[edgeslist[0]].remove(edgeslist[1])
        neighborset[edgeslist[1]].remove(edgeslist[0])
        if len(neighborset[edgeslist[1]])==0:
            del neighborset[edgeslist[1]]
        if len(neighborset[edgeslist[0]])==0:
            del neighborset[edgeslist[0]]

        adj[edgeslist[0]].remove(edgeslist[1])
        adj[edgeslist[1]].remove(edgeslist[0])
        if len(adj[edgeslist[1]])==0:
            del adj[edgeslist[1]]
        if len(adj[edgeslist[0]])==0:
            del adj[edgeslist[0]]
  
    elif type1=="InsertD":
        diedges.append(edgeslist)
        if fatherset.has_key(edgeslist[1]):
            fatherset[edgeslist[1]].add(edgeslist[0])
        else:
            fatherset[edgeslist[1]]=set([edgeslist[0]])
        if sonset.has_key(edgeslist[0]):
            sonset[edgeslist[0]].add(edgeslist[1])
        else:
            sonset[edgeslist[0]]=set([edgeslist[1]])

        if adj.has_key(edgeslist[0]):
            adj[edgeslist[0]].add(edgeslist[1])
        else:
            adj[edgeslist[0]]=set([edgeslist[1]])
        if adj.has_key(edgeslist[1]):
            adj[edgeslist[1]].add(edgeslist[0])
        else:
            adj[edgeslist[1]]=set([edgeslist[0]])

    elif type1=="DeleteD":
        diedges.remove(edgeslist)
        fatherset[edgeslist[1]].remove(edgeslist[0])
        sonset[edgeslist[0]].remove(edgeslist[1])       
        if len(fatherset[edgeslist[1]])==0:
            del fatherset[edgeslist[1]]
        if len(sonset[edgeslist[0]])==0:
            del sonset[edgeslist[0]] 

        adj[edgeslist[0]].remove(edgeslist[1])
        adj[edgeslist[1]].remove(edgeslist[0])
        if len(adj[edgeslist[1]])==0:
            del adj[edgeslist[1]]
        if len(adj[edgeslist[0]])==0:
            del adj[edgeslist[0]]

    elif type1=="MakeV":
        diedges.append(edgeslist[0:2])
        diedges.append([edgeslist[2],edgeslist[1]])
        neighborset[edgeslist[1]].remove(edgeslist[0])
        neighborset[edgeslist[1]].remove(edgeslist[2])
        neighborset[edgeslist[0]].remove(edgeslist[1])
        neighborset[edgeslist[2]].remove(edgeslist[1])
        for i in [0,1,2]:
            if len(neighborset[edgeslist[i]])==0:
                del neighborset[edgeslist[i]]
                
        if fatherset.has_key(edgeslist[1]):
            fatherset[edgeslist[1]]|=set([edgeslist[0],edgeslist[2]])
        else:
            fatherset[edgeslist[1]]=set([edgeslist[0],edgeslist[2]])
        for i in [0,2]:            
            if sonset.has_key(edgeslist[i]):
                sonset[edgeslist[i]]|=set([edgeslist[1]])
            else:
                sonset[edgeslist[i]]=set([edgeslist[1]])
        
            
    elif type1=="RemoveV":
        diedges.remove(edgeslist[0:2])
        diedges.remove([edgeslist[2],edgeslist[1]])
 
        if neighborset.has_key(edgeslist[1]):
            neighborset[edgeslist[1]]|=set([edgeslist[0],edgeslist[2]])
        else:
            neighborset[edgeslist[1]]=set([edgeslist[0],edgeslist[2]])
        for i in [0,2]:
            if neighborset.has_key(edgeslist[i]):
                neighborset[edgeslist[i]].add(edgeslist[1])
            else:
                neighborset[edgeslist[i]]=set([edgeslist[1]])
            
        fatherset[edgeslist[1]]-=set([edgeslist[0],edgeslist[2]])
        if len(fatherset[edgeslist[1]])==0:
            del fatherset[edgeslist[1]]
            
        for i in [0,2]:
            sonset[edgeslist[i]].remove(edgeslist[1])
            if len(sonset[edgeslist[i]])==0:
                del sonset[edgeslist[i]]


##    return fatherset,sonset,neighborset,diedges
##
##def pdag2dag(fatherset,sonset,neighborset,diedges):
##
##    #fatherset,sonset and neighborset used to gerenate a consistent graph.
##    #
    while len(neighborset)>0:
##        print(neighborset.keys())
        #when some undirected edges are oriented, neighborset must be changed.
        nonoutset=(set(fatherset.keys())|set(neighborset.keys()))-set(sonset.keys())
        iscon=0
        while (len(nonoutset)>0) & (len(neighborset)>0):            
            ii=nonoutset.pop()
            #deal with all non outgoing nodes
            ##deal with nodes without undirected adjacent edges
            
            if not neighborset.has_key(ii):
                if fatherset.has_key(ii):
                    for kk in fatherset[ii]:
                        sonset[kk].remove(ii)                    
                        if len(sonset[kk])==0:
                            del sonset[kk]
                    del fatherset[ii]
                    iscon=1
            #notice that here, ii could has neither neighborset nor fatherest because the structure
            #        of nodes in nonoutset could be changed by provious steps.                 
            else:
                nset=neighborset[ii]
                if not fatherset.has_key(ii):
                    fanei=neighborset[ii]
                else:
                    fanei=neighborset[ii]|fatherset[ii]
                if jconn(pdag,nset,fanei):
                    #the element of pdag is changed step by step 
                    iscon=1
                    #change undirected edges 
                    for kk in neighborset[ii]:
                        diedges.append([kk,ii])
##                        print "kkii",kk,ii
                        neighborset[kk].remove(ii)
                        if len(neighborset[kk])==0:
                            del neighborset[kk]
                    del neighborset[ii]                    
                    #deal with incident edges
                    if fatherset.has_key(ii):
                        for kk in fatherset[ii]:
                            sonset[kk].remove(ii)
                            if len(sonset[kk])==0:
                                del sonset[kk]
                        del fatherset[ii]
                        

        #second while  check the algorithm above
        if iscon==0:
            a="Not consistent"
            print a
            print "fset" ,fatherset
            print "sonset", sonset
            print "neiset", neighborset
            print "di",diedges
            print "undi",pdag['undiedges']
            print type1,edgeslist
            return a

    #end while
    return(diedges)  








#given an operator, the six following functions judge the validity of it
def validityrule1(pdag,insertU):
    #insertU is a list with two elements, like [x,y]
    #x,y are disadjacent pair
    #Notice condition three, some errors exist.
    #why not 0--->3,1--->3,2--->3,1---2,can not insert 0---2????
    x=insertU[0]
    y=insertU[1]
    fatherset=pdag['fatherset']
    nodes2neiset=pdag['nodes2neiset']
    neighborset=pdag['neighborset']
    adjset=pdag['adjset']
    sonset=pdag['sonset']
    
    xk=fatherset.has_key(x)
    yk=fatherset.has_key(y)
    if xk !=yk:
        return False
    if xk & yk:        
        if fatherset[x]!=fatherset[y]:
            return False
    #condition 2
    if nodes2neiset.has_key(x) & nodes2neiset.has_key(y):
        xni=pdag['nodes2neiset'][x]
        yni=pdag['nodes2neiset'][y]
        if xni==yni:
            nxy=pdag['Neiset'][xni][x] & pdag['Neiset'][yni][y]
            if undipathfds(pdag,x,y,nxy):
                return False
    #condition 3
    ##to check the common child edges are still compelled.
    ##add undirected edge to pdag,neighbor and adj
            
    if (not sonset.has_key(x))|(not sonset.has_key(y)):        
        return True
    else:
        chxy=sonset[x]&sonset[y]
    #deepcopy is very time-consuming
##    adjsetback=copy.deepcopy(pdag['adjset'])
##    neighborsetback=copy.deepcopy(pdag['neighborset'])
    if (not adjset.has_key(x))|(not adjset.has_key(y)):
        return True
    else:
        adjset[x].add(y)
        adjset[y].add(x)
    
    if neighborset.has_key(x):
        neighborset[x].add(y)
    else:
        neighborset[x]=set([y])
    
    if neighborset.has_key(y):
        neighborset[y].add(x)
    else:
        neighborset[y]=set([x])
    
    for z in chxy:
        #check x-->z
        if not jcompelled(pdag,[x,z]):
            #change  pdag back
            adjset[x].remove(y)
            adjset[y].remove(x)
            neighborset[x].remove(y)
            neighborset[y].remove(x)
            if len(neighborset[x])==0:
                del neighborset[x]
            if len(neighborset[y])==0:
                del neighborset[y]
##            pdag['adjset']=adjsetback
##            pdag['neighborset']=neighborsetback
            return False
        #check y-->z
        if not jcompelled(pdag,[y,z]):
            #change  pdag back
            adjset[x].remove(y)
            adjset[y].remove(x)
            neighborset[x].remove(y)
            neighborset[y].remove(x)
            if len(neighborset[x])==0:
                del neighborset[x]
            if len(neighborset[y])==0:
                del neighborset[y]
##            pdag['adjset']=adjsetback
##            pdag['neighborset']=neighborsetback

            return False
    adjset[x].remove(y)
    adjset[y].remove(x)
    neighborset[x].remove(y)
    neighborset[y].remove(x)
    if len(neighborset[x])==0:
        del neighborset[x]
    if len(neighborset[y])==0:
        del neighborset[y]
##    pdag['adjset']=adjsetback
##    pdag['neighborset']=neighborsetback
    return True
    

                
                

def validityrule2(pdag,deleteU):
    #delete deleteU from pdag
    #deleteU must be in pdag
    i=pdag['nodes2neiset'][deleteU[0]]
    nxy=pdag['Neiset'][i][deleteU[0]] & pdag['Neiset'][i][deleteU[1]]
    if judgeclique(pdag,nxy):
        return True
    else:
        return False



                            

def newchangerule3(pdag):
    #save father set and neighbor set 
    fatherback={}
    neighborback={}
    for i in pdag['fatherset'].keys():
        fatherback[i]=copy.copy(pdag['fatherset'][i])
    for i in pdag['neighborset'].keys():
        neighborback[i]=copy.copy(pdag['neighborset'][i])

    return fatherback,neighborback

def validityrule3(pdag,insertD):
    ##fatherandnei can be shared for all judgements about rule3
    x=insertD[0]
    y=insertD[1]

    
    #condition 3
    xk=pdag['fatherset'].has_key(x)
    yk=pdag['fatherset'].has_key(y)
    ynk=pdag['nodes2neiset'].has_key(y)
    if xk == yk:
        if not xk:
            return False
        if pdag['fatherset'][x]==pdag['fatherset'][y]:
            return False
    #condition 2
    if xk & ynk:
        qxy=pdag['fatherset'][x]&pdag['Neiset'][pdag['nodes2neiset'][y]][y]
    else:
        qxy=set()
    if not judgeclique(pdag,qxy):
        return False
    #condition 1
    if semipathfds(pdag['fatherandnei'], x, y,qxy):
        return False

    #condition 4 # add by Y.B.
    ##to check the common child edges are still compelled.
    ##Notice in theoretical ana, 0-->1,1-->2,2--->3,3--->4, how about 2-->4?
    ##because a directed edge's two node can not be in a same chain component,
    #the undirected edges adjacnet to children is not affected by insert a edge to graph.
    #
    if (not pdag['sonset'].has_key(x))|(not pdag['sonset'].has_key(y)):        
        return True
    else:
        chxy=pdag['sonset'][x]&pdag['sonset'][y]
##    changeset=set([y])|fatherset[y]|neighborset
##    adjsetback=copy.deepcopy(pdag['adjset'])
##    fathersetback=copy.deepcopy(pdag['fatherset'])
##    neighborsetback=copy.deepcopy(pdag['neighborset'])
    if (not pdag['adjset'].has_key(x))|(not pdag['adjset'].has_key(y)):
        return True
    else:
        faba,neiba=newchangerule3(pdag)
        
        pdag['adjset'][x].add(y)
        pdag['adjset'][y].add(x)       

        if pdag['fatherset'].has_key(y):
            pdag['fatherset'][y].add(x)
        else:
            pdag['fatherset'][y]=set([x])
    #judge whether the father of y that not adjancent to z is compelled
        yfather=pdag['fatherset'][y]-set([x])
        for yfatherk in yfather:
            if len(pdag['adjset'][yfatherk] & chxy)==0:
                #check yfatherk---->y compelled, (those edges with common child y )
                if not jcompelled(pdag,[yfatherk,y]):
                    pdag['fatherset'][y].remove(yfatherk)
                    if pdag['neighborset'].has_key(y):
                        pdag['neighborset'][y].add(yfatherk)
                    else:
                        pdag['neighborset'][y]=set([yfatherk])
                    if pdag['neighborset'].has_key(yfatherk):
                        pdag['neighborset'][yfatherk].add(y)
                    else:
                        pdag['neighborset'][yfatherk]=set([y])
        #oriente y's neighbors not adjacent to x  
        if pdag['neighborset'].has_key(y):
            neiynoconnx=pdag['neighborset'][y]-pdag['adjset'][x]
            if len(neiynoconnx)>0:
                for yunx in neiynoconnx:
                    if pdag['fatherset'].has_key(yunx):
                        pdag['fatherset'][yunx].add(y)
                    else:
                        pdag['fatherset'][yunx]=set([y])
##                    if not (neighborset.has_key(yunx)& (y in neighborset[yunx])):
##                        print yunx,y,neighborset
                    pdag['neighborset'][yunx].remove(y)
                    if len(pdag['neighborset'][yunx])==0:
                        del pdag['neighborset'][yunx]
                    pdag['neighborset'][y]-=neiynoconnx
                    if (pdag['neighborset'][y])==0:
                        del pdag['neighborset'][y]
     
                
        for z in chxy:
            #check x-->z
            if not jcompelled(pdag,[x,z]):
                #change  pdag back
                pdag['adjset'][x].remove(y)
                pdag['adjset'][y].remove(x)
                pdag['fatherset']=faba
                pdag['neighborset']=neiba
    ##            if len(fatherset[y])==0:
    ##                del fatherset[y]
    ##            backrule3(pdag,faba,neiba,[x,y])
                return False
            #check y-->z
            if not jcompelled(pdag,[y,z]):
                #change  pdag back
    ##            fatherset[y].remove(x)
    ##            if len(fatherset[y])==0:
    ##                del fatherset[y]
                pdag['adjset'][x].remove(y)
                pdag['adjset'][y].remove(x)
                pdag['fatherset']=faba
                pdag['neighborset']=neiba

                return False
    ##    fatherset[y].remove(x)
    ##    if len(fatherset[y])==0:
    ##        del fatherset[y]
        pdag['adjset'][x].remove(y)
        pdag['adjset'][y].remove(x)
        pdag['fatherset']=faba
        pdag['neighborset']=neiba
        return True
    




def validityrule4(pdag,deleteD):
    #add a condition by Y.B.
    #to judge each directed edge with child deleteD[1] still compelled.
    #Notice that first orient all undireced edges with  node y, to w-->y,then judge the compellation
    x=deleteD[0]
    y=deleteD[1]
    fatherset=pdag['fatherset']
    neighborset=pdag['neighborset']
    #condition 1
    if pdag['nodes2neiset'].has_key(y):        
        i=pdag['nodes2neiset'][y]
        nny=pdag['Neiset'][i][y]
        if not judgeclique(pdag,nny):
            return False
    #condition 2
    checkset=fatherset[y]-set([x])
    ##first chage all undirected edges with node y to w-->y    
    ##father and neighbor
    if neighborset.has_key(y):
        neighborback={}
        fatherback={}      

        for i in pdag['neighborset'].keys():
            neighborback[i]=copy.copy(pdag['neighborset'][i])
        for i in pdag['fatherset'].keys():
            fatherback[i]=copy.copy(pdag['fatherset'][i])
        for yn in neighborback[y]:
            neighborset[yn].remove(y)
            if len(neighborset[yn])==0:
                del neighborset[yn]
        del neighborset[y]
        fatherset[y]|=neighborback[y]      
        for w in checkset:            
            #check w-->y be compelled            
            if not jcompelled(pdag,[w,y],disset=set([x])):
                #change back
                pdag['fatherset']=fatherback
                pdag['neighborset']=neighborback
                return False
        #chage back
        pdag['fatherset']=fatherback
        pdag['neighborset']=neighborback
        
    else:        
        for w in checkset:        
        #check w-->y be compelled            
            if not jcompelled(pdag,[w,y],disset=set([x])):
                return False
    return True
            





                            


def validityrule6(pdag,makeV):
    ##makeV are  triple nodes [x,y,z], x-y, y-z, and x and z is disadjacent
    ##they are in a chain component
    x=makeV[0]
    z=makeV[2]
    i=pdag['nodes2neiset'][x]
    if not pdag['Neiset'][i].has_key(z):
        print pdag, makeV
    nxy=pdag['Neiset'][i][x] & pdag['Neiset'][i][z]
    if undipathfds(pdag,x,z,nxy):
        return False
    else:
        return True


def validityrule7(pdag,removeV):
    #this function to change a V structure to undirected triple
    #1. father of x is subset of z, father of y is subset of z and father of x and y are equal
    # the father of z is either x's father or x's neighbor, the same for y
    #the undirected path between x and y contains a node in father of z
       
    x=removeV[0]
    z=removeV[1]
    y=removeV[2]
    fatherset=pdag['fatherset']
    sonset=pdag['sonset']
    adjset=pdag['adjset']
    ## condition 1
    xk=fatherset.has_key(x)
    yk=fatherset.has_key(y)
    if xk!=yk:
        return False
    if xk&yk:
        if fatherset[x]!=fatherset[y]:
            return False
        if not fatherset[x].issubset(fatherset[z]):
            return False
    zpa=fatherset[z]-set([x,y])
##    zk=(len(zpa)>0)
##    if (xk & (not zk)) | (yk & (not zk)):
##        return False
##    if xk:
##        if 
##            return False

##    if yk:
##        if not fatherset[y].issubset(fatherset[z]):
##            return False
    # condition 2
    for pz in zpa:
        if (pz in sonset[x]) | (pz not in adjset[x])|(pz not in adjset[y])|(pz in sonset[y]):
            return False
    #condition 3:

    if undipathfds(pdag,x,y,zpa):
        return False
    return True



    

#generate potential operator set for all types of operators, introducned in V2 of rmcmec

def pairs_rule1(pdag,p,prob=1):
    #find all pairs that satifys rule 1, O(p*p) pairs,undirected edges,
    #need to judge disadjancent pairs
    vset=set(range(p))
    Num=[0,0,0]
    out=[]
    for i in vset:        
        for j in range(i):
            if pdag['adjset'].has_key(i):
                if j not in pdag['adjset'][i]:
                    Num[2]+=1
                    if random.random()<=prob:
                        Num[1]+=1
                        if validityrule1(pdag,[i,j]):
                            out.append([i,j])
                            Num[0]+=1
            else:
                Num[2]+=1
                if random.random()<prob:
                    Num[1]+=1
                    if validityrule1(pdag,[i,j]):
                        out.append([i,j])
                        Num[0]+=1
    return(out,Num)        
                
                
    

 



def pairs_rule2(pdag,gtype="N",prob=1):
    out=[]
    Num=[0,0,0]
    if gtype=="N":
        for i in pdag['undiedges']:
            Num[2]+=1
            if random.random()<=prob:
                Num[1]+=1
                if validityrule2(pdag,i):
                    out.append([i[0],i[1]])
                    Num[0]+=1
      
   
    
    if gtype=="Y":
        gbridge=pdag['bridge']
        ###
        for i in pdag['undiedges']:
            if (i not in gbridge) and ([i[1],i[0]] not in gbridge):                
                Num[2]+=1
                if random.random()<=prob:
                    Num[1]+=1
                    if validityrule2(pdag,i):
                        out.append([i[0],i[1]])
                        Num[0]+=1
              
        
    return out,Num

 
def pairs_rule3(pdag,p,prob=1):
    #find all pairs that satifys rule 3, O(p*p) pairs,undirected edges,
    #all large graph, it's expensive, more than rule 1
    vset=set(range(p))
    Num=[0,0,0]
    out=[]
    for i in vset:
        if pdag['adjset'].has_key(i):
            iset=vset-pdag['adjset'][i]-set([i])
        else:
            iset=vset-set([i])
        for j in iset:
            Num[2]+=1
            if random.random()<=prob:                
                Num[1]+=1
                if validityrule3(pdag,[i,j]):
                    out.append([i,j])
                    Num[0]+=1
    return(out,Num)        
                
    
def pairs_rule4(pdag,gtype="N",prob=1):
    out=[]
    Num=[0,0,0]
    if gtype=="N":
        for i in pdag['diedges']:
            Num[2]+=1
            if random.random()<=prob:
                Num[1]+=1
                if validityrule4(pdag,i):
                    out.append([i[0],i[1]])
                    Num[0]+=1
    
    if gtype=="Y":
        gbridge=pdag['bridge']   
        for i in pdag['diedges']:
            if (i not in gbridge) and ([i[1],i[0]] not in gbridge):
                
                Num[2]+=1
                if random.random()<=prob:
                    Num[1]+=1
                    if validityrule4(pdag,i):
                        out.append([i[0],i[1]])
                        Num[0]+=1        
    return out,Num

def pairs_rule6(pdag,prob=1):
    out=[]
    Num=[0,0,0]
    for ii in pdag['Neiset']:
        ##ii is a chain component
        for y in ii.keys():
            ## y is a node
            tem=list(ii[y])
            n=len(tem)
            for xi in range(n):
                for zi in range(xi+1,n):
                    if tem[zi] not in ii[tem[xi]]:
                        Num[2]+=1
                        if random.random()<=prob:
                            Num[1]+=1
                            if validityrule6(pdag,[tem[xi],y,tem[zi]]):
                                out.append([tem[xi],y,tem[zi]])
                                Num[0]+=1
    return out,Num
                
            
   
def pairs_rule7(pdag,prob=1):
    #to find all triples that satisfy the conditions of rule 7.
    out=[]
    Num=[0,0,0]
    for ii in pdag['fatherset'].keys():
        ## y is a node
        tem=list(pdag['fatherset'][ii])
        n=len(tem)
        for xi in range(n):
            for zi in range(xi+1,n):
                if  tem[zi] not in pdag['adjset'][tem[xi]]:
                    Num[2]+=1
                    if random.random()<=prob:
                        Num[1]+=1
                        if validityrule7(pdag,[tem[xi],ii,tem[zi]]):
                            out.append([tem[xi],ii,tem[zi]])
                            Num[0]+=1
    return out,Num
    








def pairs(pdag,p,ne=0,gtype="N",edgerange=[],prob=1):
##    pdagback=copy.deepcopy(pdag)
    lenlist=[0,0,0,0,0,0]
    if len(edgerange)==1:
        edgerange=[edgerange[0]-1,edgerange[0]+1]        
    if (len(edgerange)>0):
        if ne==edgerange[0]:
            r1,num1=pairs_rule1(pdag,p,prob)
            r3,num3=pairs_rule3(pdag,p,prob)
            r6,num6=pairs_rule6(pdag,prob)
            r7,num7=pairs_rule7(pdag,prob)
            lenlist[0]=num1[0]            
            lenlist[2]=num3[0]
            lenlist[4]=num6[0]
            lenlist[5]=num7[0]
            if sum(lenlist)==0:
                return pairs(pdag,p,ne,gtype,edgerange,prob*2)
            degest=(num1[0]+num3[0]+num6[0]+num7[0])*(num1[2]+num3[2]+num6[2]+num7[2])/(num1[1]+num3[1]+num6[1]+num7[1])
            return r1+r3+r6+r7,lenlist,degest,num7[2]
        
        if ne==edgerange[1]:            
            r2,num2=pairs_rule2(pdag,gtype,prob)
            r4,num4=pairs_rule4(pdag,gtype,prob)
            r6,num6=pairs_rule6(pdag,prob)
            r7,num7=pairs_rule7(pdag,prob)

            lenlist[1]=num2[0]            
            lenlist[3]=num4[0]
            lenlist[4]=num6[0]
            lenlist[5]=num7[0]
            if sum(lenlist)==0:
                return pairs(pdag,p,ne,gtype,edgerange,prob*2)
            degest=(num2[0]+num4[0]+num6[0]+num7[0])*(num2[2]+num4[2]+num6[2]+num7[2])/(num2[1]+num4[1]+num6[1]+num7[1])
          
          
            return r2+r4+r6+r7,lenlist,degest,num7[2]

    #find all pairs satisfys one of rule 1,2,3,4,6,7 
    lenlist=[0,0,0,0,0,0]
    degest=[0,0,0,0,0,0]
    r1,num1=pairs_rule1(pdag,p,prob)
    r3,num3=pairs_rule3(pdag,p,prob)
    r2,num2=pairs_rule2(pdag,gtype,prob)
    r4,num4=pairs_rule4(pdag,gtype,prob)
    r6,num6=pairs_rule6(pdag,prob)
    r7,num7=pairs_rule7(pdag,prob)
    lenlist[1]=num2[0]            
    lenlist[3]=num4[0]
    lenlist[4]=num6[0]
    lenlist[5]=num7[0]
    lenlist[0]=num1[0]            
    lenlist[2]=num3[0]
    if sum(lenlist)==0:
        return pairs(pdag,p,ne,gtype,edgerange,prob*2)
    degest=(num2[0]+num4[0]+num1[0]+num3[0]+num6[0]+num7[0])*(num2[2]+num4[2]+num1[2]+num3[2]+num6[2]+num7[2])/(num2[1]+num4[1]+num1[1]+num3[1]+num6[1]+num7[1])


   
    return r1+r2+r3+r4+r6+r7,lenlist,degest,num7[2]
    






def randompair(pdag,p,ne,gtype,edgerange,prob=1,allpout=0):
    allp,nlist0,estidegree,Vnum=pairs(pdag,p,ne,gtype,edgerange,prob)

    n=sum(nlist0)
    nn=len(nlist0)
    nlist=copy.copy(nlist0)
    for i in range(1,nn):
        nlist[i]=nlist[i-1]+nlist[i]
    no=random.sample(range(n),1)[0]
    edgeslist=allp[no]
    if no<nlist[0]:
        type1="InsertU"
    elif no<nlist[1]:
        type1="DeleteU"
    elif no<nlist[2]:
        type1="InsertD"
    elif no<nlist[3]:
        type1="DeleteD"
    elif no<nlist[4]:
        type1="MakeV"
    else:
        type1="RemoveV"
    if allpout==1:
        return type1,edgeslist,n,nlist,no,nlist0,allp
    return type1,edgeslist,estidegree,Vnum
    
    
    
##def transfer(pdag)
    
def sepgraph(G):
    left=set(G.keys()) 
    H=[]
    while len(left)>0:
        current=left.pop()
        visited={current}
        tovisit=G[current].copy()
        Tg={}
        Tg[current]=G[current].copy()        
        while len(tovisit)>0:
            tem=tovisit.pop() 
            visited.add(tem)
            Tg[tem]=G[tem].copy()
            tovisit.update(G[tem].difference(visited))
            left.remove(tem)
        H.append(Tg)

    return(H)
        
def postroot(root,Neighbor):
    ##vset is set type data
    ##algorithm to get a constrainted essential graph with root as out-point node.
    ##in counting functoin calculate neighbor out of postroot function
    vset=set(Neighbor.keys())
    if root not in vset:
        print("root is not a node of subgraph")            
    currentnode=set([root])
    ccc=list()
    left=vset-currentnode
##    temneighbor={}
##    for i in vset:
##        temneighbor[i]=Neighbor[i]& vset
    while len(left)!=0:
        res=set()
        fatherdict={}
        for i in currentnode:
            nodestem=Neighbor[i].intersection(left)            
            res|= nodestem
            for nodesi in nodestem:                
                if fatherdict.has_key(nodesi):
                    fatherdict[nodesi].add(i)
                else:
                    fatherdict[nodesi]=set([i])            
        resg={i:Neighbor[i]&res for i in res}
        Do=True
        while Do:
            Do=False            
            for i in  resg:      
                removetem=[]
                for j in resg[i]:
                    if not fatherdict[i].issubset(Neighbor[j]):
                        fatherdict[j].add(i)
                        removetem.append((i,j))
                        Do=True
                for edge in removetem:
                    resg[edge[0]].remove(edge[1])
                    resg[edge[1]].remove(edge[0])
            resg={i:resg[i] for i in resg if len(resg[i])>0 }
        ccc.extend(sepgraph(resg))   
        currentnode=res
        left-=res
        
    ccc=[item.keys() for item in ccc]
    nccc=len(ccc)
    ccnodesn=[0 for i in range(nccc)]
    ccedgesn=[0 for i in range(nccc)]
    for i in range(nccc):
        ccnodesn[i]=len(ccc[i])
        tem=set([j for j in ccc[i]])
        while len(tem)!=0:
            ss=tem.pop()
            ccedgesn[i]+=len(Neighbor[ss]&tem)
    return(ccc,ccnodesn,ccedgesn)

#aa,bb,cc = postroot(root,vset)
#d=time.time()-a
#print(d)
#def countec(cc):


def count(neighbor,nedge):    
    #recursive version of count markov equivlence class, there could be too many
    #nested recursive steps to run normally
    nedge=sum([len(neighbor[i])   for i in neighbor])/2  
    p=len(neighbor)
    vset=neighbor.keys()
    ##        print("case 1:",p)
    if nedge==p-1: 
        return(p)
    
    if nedge==p:
        #print(1)
       ##    print("case 2:",2*p)        

        return(2*p)   

    if nedge==p*(p-1)/2-1:
        #print(2)
       ##        print("case 3:",2*myfac(p-1)-myfac(p-2))
        return(2*myfac(p-1)-myfac(p-2))
    if nedge==p*(p-1)/2:
        #print(vset)
        #print(3)
        ##        print("case 4:",myfac(p))
        return(myfac(p))
    if nedge==p*(p-1)/2-2:
        return((p*p-p-4)*myfac(p-3))

    num1=0
    for kkk in vset:
        post,cnp,cne=postroot(kkk,neighbor)
        #print(post)
        temcoun=1
        for kk in range(len(post)):
            temneighbor={i:neighbor[i]&set(post[kk]) for i in post[kk]}
            temcoun*=count(temneighbor,cne[kk])
        num1+=temcoun
    #print(6)
     ##      print("degree not 1:", num1)
    return(num1)
    
##    
 
    
    
def countpdag(pdag):

    neighborsets=pdag['Neiset']
    noedges=pdag['ccedgeno']
    out=1
    cnn=len(neighborsets)
    for ii in range(cnn):
        out*=count(neighborsets[ii],int(noedges[ii]))
    return out





def myfac(n):
    k=1
    for i in range(1,n+1):
        k*=i
    return(k)

def countfreq(arr,digit=0,weight=1,edgerange=[]):
##porbabilities list.
    if len(arr)==0:
        return(0)
    
    freq= {} 
    i=0
    n=len(arr)
    sumt=0
    if len(edgerange)==0:
        low=0
        upp=10**6
    elif len(edgerange)==1:
        low=upp=edgerange[0]
    else:
        low=edgerange[0]
        upp=edgerange[1]
    
    for i in range(n):
        if (arr[i][2]>=low) & (arr[i][2]<=upp):            
            if weight==1:
                aa=1.0/arr[i][1]
            else:
                aa=1        
            if digit==1:
                lab=int(math.log10(arr[i][0]))
            else:
                lab=arr[i][0]
            if freq.has_key(lab):
                freq[lab]+=aa
                sumt+=aa
            else:
                freq[lab]=aa
                sumt+=aa
    for i in freq.keys():
        freq[i]=freq[i]/float(sumt)
    return(freq)

def egmcmc(p,ne,N,gtype="N",edgerange=[],prob=1,log=0):
    ## this function use mcmc to calculate the size distribution with edge constraints 
   ## in edgerange=[]
    outputs=[{} for i in range(N+1)]
    out=[[0,0,0] for i in range(N)]
    dag=rangrap(p,ne)
    
        
    for i in range(N):        
        pdag=cceg(dag,p)
        outputs[i]=pdag
        pdag0=copy.deepcopy(pdag)
        out[i][0]=countpdag(pdag)
        if pdag!=pdag0:
            print pdag0, pdag
            return None
        out[i][2]=ne
        pdag=egdataextend(pdag)
##        
        type1,edgeslist,estidegree,Num=randompair(pdag,p,ne,gtype,edgerange,prob)
##        if pdag0!=pdag:
##            print("change pdag")
##            return pdag0,pdag
##        
        out[i][1]=estidegree
        if (type1=="InsertU")|(type1=="InsertD"):
            ne+=1
        elif (type1=="DeleteU")|(type1=="DeleteD"):
            ne-=1               
        
        dag=pdag2dag(pdag,type1,edgeslist)       

    freq=countfreq(out,log,1,edgerange)
    return freq,out


def large(p,ne=0,gtype="N",prob=1,edgerange=[]):   
    #
    dag=rangrap(p,ne)
    for ntime in range(100): 
        t1=time.time()
        output=[]
        for i in range(50000):
            temo=[]
            pdag=cceg(dag,p)
            pdag0=copy.deepcopy(pdag)
            n=countpdag(pdag)
            temo.append(n)
    ##        output.append(pdag)
            ccn=len(pdag['Neiset'])
            aa=[0 for iiii in range(ccn)]
            for jjj in range(ccn):
                aa[jjj]=len(pdag['Neiset'][jjj])
            temo.append(aa)
            temo.append(pdag['ccedgeno'])
                           
            pdag=egdataextend(pdag)
            type1,edgeslist,estidegree,Vnum=randompair(pdag,p,ne,gtype,edgerange,prob)
            temo.extend([ne,Vnum,estidegree,type1,edgeslist])       
            pdag=egdataextend(pdag0)
            dag=pdag2dag(pdag,type1,edgeslist)
            output.append(temo)
            if (type1=="InsertU")|(type1=="InsertD"):            
                ne+=1
            elif (type1=="DeleteU")|(type1=="DeleteD"):
                ne-=1               
        b=int(time.time()-t1)
        output.append(b)
        os.chdir("D:\\Program\\python\\Pathy-data\\small") 
        fn="Node"+str(p)+"prob"+str(prob)+"ntime"+str(ntime)+".pkl"
        f = open(fn, 'wb')
        pickle.dump(output, f)
        f.close()

###need to look into the estimation of degrees.
        ##
def small(p,rep,n,gtype="N",prob=1):
    ##run simulations rep times with p vertices and n steps in each
    ## output mean, std of these simultions as well as the fre with all data for each size 
    freqs=[]
    outs=[]
    for ntime in range(rep):
        ne=random.randint(0,p*(p-1)/2)
        freq,out=egmcmc(p,ne,n,gtype,prob=prob)
        freqs.append(freq)
        outs.extend(out)
    fre=countfreq(outs)
    keys1=fre.keys()
    means={}
    for i in keys1:
        means[i]=0
    for i in range(rep):
        for j in keys1:
            if j in freqs[i].keys():
                means[j]+=freqs[i][j]
    for i in means.keys():
        means[i]=means[i]/rep
    std={}

    for i in keys1:
        std[i]=0
    for i in range(rep):
        for j in keys1:
            if j in freqs[i].keys():
                std[j]+=(freqs[i][j]-means[j])**2
            else:
                std[j]+=(0-means[j])**2
    for i in std.keys():
        std[i]=math.sqrt(std[i]/rep)
    return means,std,fre
        



    
    ###################################################
    ##to create an exe file
    
    ##1. first generate a file contains:
    
    ####from distutils.core import setup
    ####import py2exe
    
    ####setup(console=['stb.py'])
    
    ## run this two comonds in cmd, before doing this, install py2exe
    
    ## python setup.py install
    ## python setup.py py2exe
    ######################################################
    
    
def smalldemo(gtype="N"):
    myp=int(raw_input("The number of vertices: "))
    mystep=int(raw_input("The length of MCMC: "))
    myrep=int(raw_input("The number of simulations: "))
    print "runing..."
    t1=time.time()
    mean,std,fre=small(myp,myrep,mystep,gtype)
    tt=time.time()-t1
    print   tt, "seconds", "are used totally"
    print "OUTPUT"
    print "Size: Freq  Mean(Std)"
    pformat='{3:s}:{0:.5f} {1:.5f}({2:.5f})'
    sizeout=sorted(list(fre.keys()))
    for i in sizeout:
        print pformat.format(fre[i],mean[i],std[i],str(i))
    
    print "freqs are calculated with all", mystep,"*",myrep, "steps"
    print "means are the averages of freqs in", myrep, "simulations."
    
    
    
    ###################################################
    ##to create an exe file
    
    ##1. first generate a file contains:
    
    ####from distutils.core import setup
    ####import py2exe
    
    ####setup(console=['stb.py'])
    
    ## run this two comonds in cmd, before doing this, install py2exe
    
    ## python setup.py install
    ## python setup.py py2exe
    ######################################################
    
    



