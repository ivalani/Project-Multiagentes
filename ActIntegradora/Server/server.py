from model_temp import RandomModel, trashAgent
from mesa.visualization.modules import CanvasGrid, BarChartModule, PieChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

def agent_portrayal(agent):
    if agent is None: return

    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "red",
                 "r": 0.5}

    if (isinstance(agent, trashAgent)):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2

    return portrayal

model_params = {"N":UserSettableParameter("slider", "Roombas", 1, 1, 5, 1), "trashN":UserSettableParameter("slider", "Dirty cells", 10, 10, 95, 5), "maxSteps":UserSettableParameter("slider", "Max Total Steps", 75, 10, 200, 5), "width":10, "height":10}

grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
bar_chart = BarChartModule(
    [{"Label":"Steps", "Color":"#AA0000"}],
    scope="agent", sorting="ascending", sort_by="Steps")


server = ModularServer(RandomModel, [grid, bar_chart], "Roomba Agents", model_params)

server.port = 8521 # The default
server.launch()