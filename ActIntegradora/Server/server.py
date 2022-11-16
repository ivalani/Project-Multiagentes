from model_temp import dropZone, Box
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

def agent_portrayal(agent):
    if agent is None: return

    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "Layer": 1,
                 "Color": "red",
                 "w": .8,
                 "h": .8}

    if (isinstance(agent, dropZone)):
        portrayal["Color"] = "orange"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    if (isinstance(agent, Box)):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 2
        portrayal["w"] = .5
        portrayal["h"] = .5

    return portrayal

model_params = {"N":UserSettableParameter("slider", "Robots", 1, 1, 5, 1),
                "BoxesN":UserSettableParameter("slider", "Boxes", 10, 10, 95, 5),
                "width":10, "height":10}

grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

server = ModularServer(RandomModel, [grid], "Robots against boxes", model_params)

server.port = 8521 # The default
server.launch()