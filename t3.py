import pulp 
import numpy as np
import matplotlib.pyplot as plt
from pulp.constants import LpConstraintEQ

#Nodos
n =11
clientes =[i for i in range(n) if i!=0]
nodos = [0]+clientes
arcos=[(i,j) for i in nodos for j in nodos if i!=j]

#Demanda
np.random.seed(0)
q={n:np.random.randint(10,15) for n in clientes}
q[0]=0
Q=50

#Ventanas de tiempo
e={0:0,1:10,2:10,3:10,4:20,5:20,6:20,7:40,8:40,9:40,10:40} #minimo
l={0:200,1:100,2:100,3:100,4:150,5:150,6:150,7:180,8:180,9:180,10:180}#maximo

s={n:np.random.randint(3,5) for n in clientes} #tiempo servicio nodo i
s[0] =0
#Coordenadas
X=np.random.rand(len(nodos))*100
Y=np.random.rand(len(nodos))*100

#Distancia
distancia = {(i,j): np.hypot(X[i]-X[j],Y[i]-Y[j]) for i in nodos for j in nodos if i!=j}

plt.figure(figsize=(12,5))
plt.scatter(X,Y,color='blue')

#DC
plt.scatter(X[0],Y[0],color='red',marker='D')
plt.annotate("DC",(X[0]-1,Y[0]-5.5))

for i in clientes:
    plt.annotate('$q_{%d}=%d$'%(i,q[i]),(X[i]-1,Y[i]-5.5))

plt.xlabel("Distancia X")
plt.ylabel("Distancia Y")
plt.title("Solucion TSP")

plt.show()

#Create Problem
prob = pulp.LpProblem("CVRP",pulp.LpMinimize)

#Arco Set
x = {i:pulp.LpVariable('a_{}'.format(i),cat ="Binary") for i in arcos}
#Client Set
u = {i:pulp.LpVariable('c_{}'.format(i),upBound=Q,cat ="Continuous" ) for i in clientes}



#Objetive Function
objective = pulp.lpSum(distancia[i,j]*x[i,j] for i,j in arcos)
for i in clientes:
    prob+= pulp.lpSum(x[i,j] for j in nodos if j!=i) == 1
for j in clientes:
    prob+= pulp.lpSum(x[i,j] for i in nodos if j!=i) == 1
for i in clientes:
    prob+= u[i] >= q[i]

prob.setObjective(objective)

prob.solve()
