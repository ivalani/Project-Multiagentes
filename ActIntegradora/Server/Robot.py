from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid

class RobotAgent(Agent):
    """
    Roomba Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.direction = 4
        self.steps_taken = 0
        self.cells_visited = []

    def move(self):
        """
        Determines if the agent can move in the direction that was chosen
        """
        # All possible steps within one unit of the current position
        all_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True, # Boolean for whether to use Moore neighborhood (including diagonals) or Von Neumann (only up/down/left/right).
            include_center=True)

        # Checks which agents are in the surrounding cells
        agentsAround = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=1)

        # List of trash items around the agent
        trashAround = [agent for agent in agentsAround if isinstance(agent, Box)]

        """print(f"Agente: {self.unique_id} movimiento {self.steps_taken} . Vecinos: {trashAround}")"""

        # Checks which grid cells are empty and saves them in a list of possible steps
        freeSpaces = list(map(self.model.grid.is_cell_empty, all_steps))
        next_moves = [p for p,f in zip(all_steps, freeSpaces) if f == True]

        # Checks if the cell has already been visited, in case all surrounding cells have been visited, the agent will move to a random cell
        all_visited = all([p in self.cells_visited for p in next_moves])
        if not all_visited:
            next_moves = [p for p in next_moves if p not in self.cells_visited]

        # Gets position of the cells that have trash in them
        trashMoves = []
        for i in range(len(trashAround)):
            trashMoves.append(trashAround[i].pos)

        trash = False
        i = 0
        if len(trashMoves) != 0:
            next_move = self.random.choice(trashMoves)
            self.cells_visited.append(self.pos)
            i = trashMoves.index(next_move)
            trash = True

        else:
            next_move = self.random.choice(next_moves)
            self.cells_visited.append(self.pos)

        # Now move:
        if self.random.random() < 100:
            self.model.grid.move_agent(self, next_move)
            self.steps_taken+=1
            if trash:
                self.model.grid.remove_agent(trashAround[i])
                self.model.remaning_boxes -= 1
                trash = False

    def step(self):
        """
        Determines the new direction it will take, and then moves
        """
        self.move()

class Box(Agent):
    """
    Box agent. 
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class dropZone(Agent):
    """
    Drop zone agent. Just to add a drop zone to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass
class wallAgent(Agent):
    """
    Wall agent for grid delimitation.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass
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
        self.schedule = RandomActivation(self)
        self.running = True

        # Places the boxes in the grid
        for i in range(self.num_boxes):
            boxy = Box(i+2000, self)
            self.schedule.add(boxy)

            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(boxy, pos)

        # Add the agent to a random empty grid cell
        for i in range(self.num_agents):
            a = RobotAgent(i+1000, self)
            pos = 1,1
            self.schedule.add(a)
            self.grid.place_agent(a, pos)

        self.datacollector.collect(self)

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        self.datacollector.collect(self)

        # Determines if the model should continue running
        if self.remaning_boxes == 0:
            self.running = False