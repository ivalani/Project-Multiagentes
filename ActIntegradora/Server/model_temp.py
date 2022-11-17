from mesa import Model, agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from Robot import RobotAgent, Box, dropZone

class RandomModel(Model):
    """
    Creates a new model with Roomba agents.
    Args:
        N: Number of agents in the simulation
        height, width: The size of the grid to model
    """
    def __init__(self, N, BoxesN, width, height):
        self.num_agents = N
        self.num_boxes = BoxesN
        self.remaning_boxes = BoxesN
        self.grid = MultiGrid(width,height,torus = False)
        self.size = (width, height)
        self.schedule = RandomActivation(self)
        self.running = True
        self.dropZones = []

        self.datacollector = DataCollector(
        agent_reporters={"Steps": lambda a: a.steps_taken if isinstance(a, RobotAgent) else 0})

        # Now it has hardcoded the positions for the drop zones
        # Places the Drop Zones at the corners of the grid
        dropZonePos = [(self.size[0]-1,self.size[1]-1), (0,self.size[1]-1), (self.size[0]-1,0)]
        for i in range(3):
            drop = dropZone(i+3000, self)
            pos = dropZonePos[i]
            self.schedule.add(drop)
            self.grid.place_agent(drop, pos)
            self.dropZones.append(pos)

        # Add the robots to [1,1] in the grid
        for i in range(self.num_agents):
            a = RobotAgent(i+1000, self)
            pos = 1,1
            self.schedule.add(a)
            self.grid.place_agent(a, pos)

        # Places the boxes in the grid
        for i in range(self.num_boxes):
            boxy = Box(i+2000, self)
            self.schedule.add(boxy)

            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(boxy, pos)

        self.datacollector.collect(self)

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        self.datacollector.collect(self)

        # Determines if the model should continue running
        if self.remaning_boxes == 0:
            self.running = False