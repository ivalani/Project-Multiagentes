from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json

class RandomModel(Model):
    """
    Creates a new model with random agents.
    Args:
        N: Number of agents in the simulation
    """
    def __init__(self, N):

        dataDictionary = json.load(open("mapDictionary.json"))

        self.traffic_lights = []

        with open('2022_base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus = False)
            self.schedule = RandomActivation(self)

            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<", "+"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col in ["S", "s"]:
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(dataDictionary[col]))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "B":
                        agent = SideWalk(f"sw_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r -1 ))

                    elif col == "Z":
                        agent = PedestrianCrossing(f"pc_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

        self.num_agents = N
        self.running = True
        positions_temp = [(0,0),(0,22),(22,0),(22,22),(13,9)]
        pedPositions = [(2,2),(20,2),(2,22),(20,22),(11,10)]

        for i in range(self.num_agents):
            a = Car(i+1000, self)
            pos = positions_temp[i]
            self.schedule.add(a)
            self.grid.place_agent(a, pos)

        for i in range(self.num_agents):
            a = Pedestrian(i+2000, self)
            pos = pedPositions[i]
            self.schedule.add(a)
            self.grid.place_agent(a, pos)

        b = Bus(3000, self)
        pos = 13,12
        self.schedule.add(b)
        self.grid.place_agent(b, pos)

        ba = Bus(3001, self)
        pos = 4,6
        self.schedule.add(ba)
        self.grid.place_agent(ba, pos)

    def step(self):
        '''Advance the model by one step.'''
        if self.schedule.steps % 15 == 0:
            for agent in self.traffic_lights:
                agent.state = not agent.state
        self.schedule.step()