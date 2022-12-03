# Presentación del reto TC2008B 
## _Indice_ 
- [Presentación del reto TC2008B](#presentación-del-reto-tc2008b)
  - [_Indice_](#indice)
  - [_Instalacion_](#instalacion)
  - [_Propuesta formal_](#propuesta-formal)
  - [_Tarea M4_](#tarea-m4)
  - [_Modelacion de agentes_](#modelacion-de-agentes)
    - [_Agentes involucrados actualización_](#agentes-involucrados-actualización)
    - [_Interaccion entre agentes actualización:_](#interaccion-entre-agentes-actualización)
    - [_Prioridad de acciones_](#prioridad-de-acciones)

--- 
## _Instalacion_
Para poder probar el proyecto es necesario clonar el repositorio e instalas los requerimientos incluidos en el archivo txt, como en el siguiente ejemplo. 

```powershell
Windows PowerShell
Copyright (C) Microsoft Corporation. Todos los derechos reservados.

Prueba la nueva tecnología PowerShell multiplataforma https://aka.ms/pscore6

PS C:\Users\> cd Downloads
PS C:\Users\Downloads> git clone https://github.com/ivalani/Project-Multiagentes.git

--- Cloning into "Project-Multiagentes" ..... Finished

PS C:\Users\Downloads> cd Project-Multiagentes
PS C:\Users\Downloads\cd Project-Multiagentes>pip install -r requirements.txt
```

Una vez finalizados estos pasos podemos pasar al siguiente paso, que es correr nuestro programa, para ello primero es necesario encender el servidor de flask que se encuentra en trafficProject/Server/serverFlask.py 

Despues de correr "serverFlask.py", podemos abrir en Unity la carpeta de TrafficVisualization e ir a la escena "BuildCity", donde al tener encendido el servidos podremos correr la escena y ver la ciudad inteligente. 


## _Propuesta formal_ 

Al inicio del bloque se diseño una propuesta formal inicial que ha tenido leve cambios que se podran ver en el desarrollo de cada uno de los avances reportados. 

Para saber mas sobre el proyecto y la problematica, puede leerse la "propuesta formal inicial" aqui: [Propuesta formal](https://github.com/ivalani/Project-Multiagentes/blob/main/Arranque_de_proyecto/propuesta.md)

Esta parte de la entrega cuenta como el primer avance del proyecto, que conforma el "arranque del proyecto" 

## _Tarea M4_ 
Conforma el inicio y el modelado de los agentes que interactuan en la ciudad. 
Puedes ver mas a detalle [aqui](https://github.com/ivalani/Project-Multiagentes/blob/main/trafficProject/Documents/M4.md)

## _Modelacion de agentes_ 
Esta parte del proyecto se cuenta como el segundo avance del proyecto, donde: 

### _Agentes involucrados actualización_
Se presentan los agentes de la propuesta formal, con ligeros cambios

![Diagrama de agentes avance 2](Documents/agentes.drawio.png)

### _Interaccion entre agentes actualización:_

Se presenta una definición de interacciones y protocolos basicos entre los agentes que deben de presentarse minimamente, es decir, en este proyecto se espera poder añadir un agente "autobus" que actua como un agente aparte de los "autos", tambien el agente "peatones" esta considerado como un agente extra, por ello se crea un diagrama minimo esperado. 

![Diagrama de protocolos avance 2](Documents/basic-protocols.drawio.png)

Se mantiene la interacción global definida previamente en el primer avance. 

![Diagrama de protocolos avance 1](/Arranque_de_proyecto/Diagramas/protocolos.png)

### _Prioridad de acciones_ 

Acciones basicas que seran tomadas como base, se actualizaran conforme sea necesario

![Diagrama de prioridad de acciones](Documents/priorityDiagram.drawio.png)
