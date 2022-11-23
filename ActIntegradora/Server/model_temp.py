from mesa import Model, agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from Robot import RobotAgent, Box, dropZone, ObstacleAgent

class RandomModel(Model):
    """
    Model.
    Attributes:
        num_agents: Number of agents in the simulation
        num_boxes: Number of boxes in the simulation
        remaning_boxes: Number of boxes that have not been picked up
        dropZonesCalc: Number of drop zones in the simulation
        dropZones: List of the positions of the drop zones
        size: The size of the grid to model
    """
    def __init__(self, N, BoxesDensity, width, height):
        """
        Creates a new model with Roomba agents.
        Args:
            N: Number of agents in the simulation
            height, width: The size of the grid to model
            BoxesDensity: The density of boxes in the grid must be between 0.01 and .05
        """
        # Variables for agents
        self.num_agents = N
        self.num_boxes = int(BoxesDensity * width * height)
        self.remaning_boxes = self.num_boxes
        self.dropZonesCalc = int(self.num_boxes / 5)
        self.dropZones = []
        # Variables for model
        self.grid = MultiGrid(width,height,torus = False)
        self.size = (width, height)
        self.schedule = RandomActivation(self)
        self.running = True
        self.datacollector = DataCollector(
        agent_reporters={"Steps": lambda a: a.steps_taken if isinstance(a, RobotAgent) else 0})

        # Creates the border of the grid
        border = [(x,y) for y in range(height) for x in range(width) if y in [0, height-1] or x in [0, width - 1]]

        # Creates the drop zone range next to border
        dropZoneBorder = [(x,y) for y in range(height-1) for x in range(width-1) if y in [1, height-2] or x in [1, width - 2]]

        # Places the border
        for pos in border:
            obs = ObstacleAgent(pos, self)
            self.schedule.add(obs)
            self.grid.place_agent(obs, pos)

        # Now it has hardcoded the positions for the drop zones
        # Places the Drop Zones at the corners of the grid
        for i in range(self.dropZonesCalc):
            pos = self.random.choice(dropZoneBorder)
            while (not self.grid.is_cell_empty(pos)):
                pos = self.random.choice(dropZoneBorder)
            drop = dropZone(i+5000, self)
            self.dropZones.append(pos)
            self.schedule.add(drop)
            drop.condition = "Empty"
            self.grid.place_agent(drop, pos)

        # Add the robots to random cords in the grid
        for i in range(self.num_agents):
            a = RobotAgent(i+1000, self)
            self.schedule.add(a)

            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(a, pos)

        # Places the boxes randomly in the grid
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
        if self.remaning_boxes <= 0:
            self.running = False