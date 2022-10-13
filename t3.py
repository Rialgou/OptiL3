import pulp 
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import random
import linecache


#Leer archivos del txt
dir ='Instancias_Tarea_3/HOMBERGER_C1_2_1.txt'
with open(dir,'r') as fp:
    count = 0
    for line in fp:
        count += 1
file = linecache.getline(dir,5).split()
#Vehiculos
vehiculos = []
for i in range(int(file[0])+1):
    if i!=0:
        vehiculos.append(i)
#print(vehiculos)
#Capacidad
Q = int(file[1])

file =[]
for i in range(count+1):
    if i>=10:
        file.append(linecache.getline(dir,i).split())
#Nodos
clientes =[i for i in range(len(file)) if i!=0]
nodos = [0]+clientes
arcos =[(i,j) for i in nodos for j in nodos if i!=j]

#Demanda
q={n:int(file[n][3]) for n in nodos}
#print(len(q))

#Ventanas de tiempo
e = {n:int(file[n][4]) for n in nodos}
l = {n:int(file[n][5]) for n in nodos}

#Tiempo de servicio
s= {n:int(file[n][6]) for n in nodos}


#COORDS
X= [int(file[n][1]) for n in range(len(file))]
Y= [int(file[n][2]) for n in range(len(file))]

#Distancia
dist = {(i,j): np.hypot(X[i]-X[j],Y[i]-Y[j]) for i in nodos for j in nodos if i!=j}

plt.figure(figsize=(10,10))
plt.scatter(X,Y,color='blue')

#DC
plt.scatter(X[0],Y[0],color='red',marker='D')
plt.annotate("Depot|$t_{%d}$=(%d$,%d$)" %(0,e[0],l[0]),(X[0]-1,Y[0]+1))

for i in clientes:
    plt.annotate('$cliente_{%d}|q_{%d}=%d$|$t_{%d}$=(%d$,%d$)' %(i,i,q[i],i,e[i],l[i]),(X[i]-1,Y[i]+0.5))

plt.xlabel("Distancia X")
plt.ylabel("Distancia Y")
plt.title("Clientes|Demanda|Ventanas de tiempo")

plt.show()

#Create Problem
prob = pulp.LpProblem("VRPTW",pulp.LpMinimize)

#Arco Set
arco_var = [(i,j,k) for i in nodos for j in nodos for k in vehiculos if i!=j]
arco_tiempos = [(i,k) for i in nodos for k in vehiculos]

#Client Set
x = {i:pulp.LpVariable('x_{}'.format(i),cat ="Binary") for i in arco_var} 
t = {i:pulp.LpVariable('t_{}'.format(i),cat="Integer") for i in arco_tiempos}



#Objetive Function
objective = pulp.lpSum(dist[i,j]*x[i,j,k] for i,j,k in arco_var)

#Restricciones
#Entrada y salida de DC
for k in vehiculos:
    prob+= pulp.lpSum(x[0,j,k]  for j in clientes) <=1
#salida
for k in vehiculos:
    prob+= pulp.lpSum(x[i,0,k] for i in clientes) <=1
#vehiculo por nodo
for i in clientes:
    prob+= pulp.lpSum(x[i,j,k] for j in nodos for k in vehiculos if i!=j)==1 
#Flujo cada nodo solo visita un nodo y cada nodo es visitado por un nodo
for k in vehiculos:
    for i in nodos:
        prob+= pulp.lpSum(x[i,j,k] for j in nodos if i!=j) - pulp.lpSum(x[j,i,k] for j in nodos if i!=j) == 0 

#Capacidad del vehiculo
for k in vehiculos:
    prob += pulp.lpSum((q[i]*x[i,j,k]) for i in clientes for j in nodos if i != j) <= Q

#Ventana de Tiempo
for k in vehiculos:
    for i in clientes:
        for j in clientes:
            if i!=j:
                M = max(l[i]+s[i] + dist[i,j] -e[j],0)
                prob+= t[i,k] + s[i] + dist[i,j] - M*(1-x[i,j,k]) <= t[j,k]

for k in vehiculos:
    for i in nodos:
        prob+= t[i,k] >= e[i] 
        prob+= t[i,k] <= l[i]


prob.setObjective(objective)
prob.solve(pulp.PULP_CBC_CMD(timeLimit=1800))
dirW ='Instancias_Tarea_3/HOMBERGER_C1_2_1_respuestas.txt'
fileW = open(dirW,'a')
for i in nodos:
    for j in nodos:
        for k in vehiculos:
            if i!=j:
                if x[i,j,k].value()>0.9:
                    fileW.write(str(x[i,j,k]) + ' = ' + str(x[i,j,k].value()) + '\n')
for i in nodos:
    for k in vehiculos:
        fileW.write(str(t[i,k]) + ' = ' + str(t[i,k].value()) + '\n')


rutas =[]
vehiculo =[]
for k in vehiculos:
    for i in nodos:
        if i!=0 and x[0,i,k].value()==1:
            aux=[0,i]
            while i!=0:
                j=i
                for h in nodos:
                    if j!=h and x[j,h,k].value()>0.9:
                        aux.append(h)
                        i=h
            rutas.append(aux)
            vehiculo.append(k)

tiempoAcumulado =[]
for n in range(len(rutas)):
    for k in range(len(rutas[n])-1):
        if k ==0:
            aux=[0]
        else:
            i=rutas[n][k]
            j=rutas[n][k+1]
            t=dist[i,j]+s[i]+aux[-1]
            aux.append(t)
    tiempoAcumulado.append(aux)
#Plot de la solución, con rutas de cada vehiculo
plt.figure(figsize=(10, 10))
for i in range(len(nodos)):
    if i == 0:
        plt.scatter(X[i], Y[i], c='red',marker='D')
        plt.text(X[i] + 1, Y[i] + 1, 'Depot')
    else:
        plt.scatter(X[i], Y[i], c='blue')
        demand = q[i]
        plt.annotate("$q_{%d}$=%d" %(i,q[i]),(X[i]-1,Y[i]+1))

plt.xlim([np.min(X)-5, np.max(X)+5])
plt.ylim([np.min(Y)-5, np.max(Y)+5])
plt.title('VRPTW result')
random.seed(0)


for r in range(len(rutas)):
    RGBcolor = [random.random(),random.random(),random.random()] 
    for n in range(len(rutas[r])-1):
        i = rutas[r][n]
        j = rutas[r][n+1]
        plt.plot([X[i],X[j]],[Y[i],Y[j]],color=(RGBcolor[0],RGBcolor[1],RGBcolor[2]), alpha=0.4)

plt.xlabel("Distancia X")
plt.ylabel("Distancia Y")
plt.show()
fileW.close()
