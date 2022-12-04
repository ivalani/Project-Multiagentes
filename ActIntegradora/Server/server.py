from model_temp import RandomModel
from Robot import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

width = UserSettableParameter('slider', 'Width', 20, 10, 30, 1)

COLORS = {"Full": "#00AA00", "Empty": "#F37417"}
boxy = {True: "white", False: "grey"}

def agent_portrayal(agent):
    if agent is None: return

    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 1,
                 "Color": "red",
                 "r": .8}

    if (isinstance(agent, dropZone)):
        portrayal["Color"] = COLORS[agent.condition]
        portrayal["Layer"] = 0
        portrayal["Shape"] = "rect"
        portrayal["w"] = 1
        portrayal["h"] = 1

    if (isinstance(agent, Box)):
        portrayal["Color"] = boxy[agent.pickedUp]
        portrayal["Layer"] = 0
        portrayal["Shape"] = "rect"
        portrayal["w"] = .5
        portrayal["h"] = .5

    if (isinstance(agent, ObstacleAgent)):
        portrayal["Color"] = "black"
        portrayal["Layer"] = 0
        portrayal["Shape"] = "rect"
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal

model_params = {"N":UserSettableParameter("slider", "Robots", 5, 5, 10, 1),
                "BoxesDensity":UserSettableParameter("slider", "Boxes", .05, .01, .05, .0025),
                "width":UserSettableParameter("slider", "Width", 20, 10, 50, 2),
                "height":UserSettableParameter("slider", "Height", 20, 10, 50, 2)}

grid = CanvasGrid(agent_portrayal, 50, 50, 500, 500)

server = ModularServer(RandomModel, [grid], "Robots against boxes", model_params)

server.port = 8521 # The default
server.launch()