import pulp 
import numpy as np
import matplotlib.pyplot as plt
from pulp.constants import LpConstraintEQ
import matplotlib

#Nodos
n =11
clientes =[i for i in range(n) if i!=0]
nodos = [0]+clientes
arcos=[(i,j) for i in nodos for j in nodos if i!=j]

#Demanda
np.random.seed(0)
q={n:np.random.randint(10,15) for n in clientes}
q[0]=0

#Vehiculos
vehiculos = [1,2,3,4]
#Q=50
Q ={1:50,2:50,3:25,4:25}
#Ventanas de tiempo
e={0:0,1:10,2:10,3:10,4:20,5:20,6:20,7:40,8:40,9:40,10:40} #minimo
l={0:200,1:100,2:100,3:100,4:150,5:150,6:150,7:180,8:180,9:180,10:180}#maximo

s={n:np.random.randint(3,5) for n in clientes} #tiempo servicio nodo i
s[0] =0
#Coordenadas
X=np.random.rand(len(nodos))*100
Y=np.random.rand(len(nodos))*100

#Distancias y tiempos
distancia = {(i,j): np.hypot(X[i]-X[j],Y[i]-Y[j]) for i in nodos for j in nodos if i!=j}
tiempo = {(i,j): np.hypot(X[i]-X[j],Y[i]-Y[j]) for i in nodos for j in nodos if i!=j}


plt.figure(figsize=(12,5))
plt.scatter(X,Y,color='blue')

#DC
plt.scatter(X[0],Y[0],color='red',marker='D')
plt.annotate("DC|$t_{%d}$=(%d$,%d$)" %(0,e[0],l[0]),(X[0]-1,Y[0]-5.5))

for i in clientes:
    plt.annotate('$q_{%d}=%d$|$t_{%d}$=(%d$,%d$)' %(i,q[i],i,e[i],l[i]),(X[i]-1,Y[i]-5.5))

plt.xlabel("Distancia X")
plt.ylabel("Distancia Y")
plt.title("Solucion TSP")

plt.show()

#Create Problem
prob = pulp.LpProblem("CVRP",pulp.LpMinimize)

#Arco Set
arco_var = [(i,j,k) for i in nodos for j in nodos for k in vehiculos if i!=j]
arco_tiempos = [(i,k) for i in nodos for k in vehiculos]

#Client Set
x = {i:pulp.LpVariable('x_{}'.format(i),cat ="Binary") for i in arco_var} 
t = {i:pulp.LpVariable('t_{}'.format(i),cat="Continuous") for i in arco_tiempos}



#Objetive Function
objective = pulp.lpSum(distancia[i,j]*x[i,j,k] for i,j,k in arco_var)

#Restricciones
#Entrada y salida de DC
for j in clientes:
    prob+= pulp.lpSum(x[0,j,k]  for k in vehiculos if j!=i) <=1
#salida
for i in clientes:
    prob+= pulp.lpSum(x[i,0,k] for k in vehiculos if j!=i) <=1
#vehiculo por nodo
for i in clientes:
    prob+= pulp.lpSum(x[i,j,k] for j in nodos for k in vehiculos if i!=j)==1 
#Flujo cada nodo solo visita un nodo y cada nodo es visitado por un nodo
for i in nodos:
    prob+= pulp.lpSum(x[i,j,k] for j in nodos for k in vehiculos if i!=j) - pulp.lpSum(x[j,i,k] for j in nodos for k in vehiculos if i!=j) == 0 

#Capacidad del vehiculo
for k in vehiculos:
    prob+= pulp.lpSum(q[i]*pulp.lpSum(x[i,j,k] for j in nodos if i!=j) for i in clientes) <= Q[k]

#Ventana de Tiempo
    
     

prob+= pulp.lpSum(t[i,k] >= e[i] for i,k in arco_tiempos)
prob+= pulp.lpSum(t[i,k] <=l[i] for i,k in arco_tiempos)

prob.setObjective(objective)

prob.solve()
print(prob)

#*  Dibuja el plano nuevamente
plt.figure(figsize=(10, 10))
for i in range(len(nodos)):
    if i == 0:
        plt.scatter(X[i], Y[i], c='r')
        plt.text(X[i] + 1, Y[i] + 1, 'depot')
    else:
        plt.scatter(X[i], Y[i], c='black')
        demand = q[i]
        plt.text(X[i] + 1, Y[i] + 1, f'{i}({demand})')

plt.xlim([np.min(X)-5, np.max(X)+5])
plt.ylim([np.min(Y)-5, np.max(Y)+5])
plt.title('points: id(demand)')

#* Agrega las rutas recorridas por los vehiculos involucrados
cmap = matplotlib.cm.get_cmap('Dark2')
for i in nodos:
    for j in nodos:
        for k in vehiculos:
            if i != j and pulp.value(x[i, j, k]) == 1:
                plt.plot([X[i], X[j]], [Y[i], Y[j]], color=cmap(k), alpha=0.4)
plt.show()
