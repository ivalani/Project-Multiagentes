from model_temp import RandomModel
from Robot import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

def agent_portrayal(agent):
    if agent is None: return

    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 1,
                 "Color": "red",
                 "r": .8}

    if (isinstance(agent, dropZone)):
        portrayal["Color"] = "orange"
        portrayal["Layer"] = 0
        portrayal["Shape"] = "rect"
        portrayal["w"] = 1
        portrayal["h"] = 1

    if (isinstance(agent, Box)):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 2
        portrayal["Shape"] = "rect"
        portrayal["w"] = .5
        portrayal["h"] = .5

    return portrayal

model_params = {"N":UserSettableParameter("slider", "Robots", 5, 5, 10, 1),
                "BoxesN":UserSettableParameter("slider", "Boxes", 10, 10, 95, 5),
                "width":20, "height":20}

grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)

server = ModularServer(RandomModel, [grid], "Robots against boxes", model_params)

server.port = 8521 # The default
server.launch()