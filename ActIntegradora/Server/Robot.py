from mesa import Agent
import math

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
        self.closest_dropZone = None
        self.last_box = None
        self.with_box = False

    def move(self):
        """
        Determines if the agent can move in the direction that was chosen
        """
        ## Basic movement around 4 directions. Counts visited cells.
        # All possible steps within one unit of the current position.
        all_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=True)

        # Checks which grid cells are empty and saves them in a list of possible steps.
        freeSpaces = list(map(self.model.grid.is_cell_empty, all_steps))
        next_moves = [p for p,f in zip(all_steps, freeSpaces) if f == True]

        # Checks if the cell has already been visited, in case all surrounding cells have been visited, the agent will move to a random cell.
        all_visited = all([p in self.cells_visited for p in next_moves])
        if not all_visited:
            next_moves = [p for p in next_moves if p not in self.cells_visited]

        #
        # In case all cell around are being occupied by other agents, the agent will stay at the same position.
        if next_moves == []:
            next_moves = [self.pos]

        ## Movement based on boxes around the agent.
        # Checks which agents are in the surrounding cells.
        agentsAround = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True, radius=1)

        # List of boxes around the agent.
        boxesAround = [agent for agent in agentsAround if isinstance(agent, Box)]
        # Detect if there agent is next to drop zone.
        besideDropZone = [agent for agent in agentsAround if isinstance(agent, dropZone)]

        #
        # Save of the last seen box.
        if len(boxesAround) > 0 and self.with_box:
            self.last_box = boxesAround[0]

        # Gets position of the cells that have boxes in them.
        boxesPos = []
        for i in range(len(boxesAround)):
            boxesPos.append(boxesAround[i].pos)

        indexBox = 0

        # Selection of the next_move, by jerarquical order.

        # 1:
        # The agent has a box and has a position for a Dropzone to deliver.
        # Delivers the box to the closest dropZone.
        if self.with_box and self.closest_dropZone != None:
            boxesPos = []
            x,y = self.pos
            x2,y2 = self.closest_dropZone
            # Movement when dropZone position is lesser than self position.
            if x > x2:
                x -= 1
            elif y > y2:
                y -= 1
            # Movement when dropZone position is greater than self position.
            elif x < x2:
                x += 1
            elif y < y2:
                y += 1
            # Stays 1 step in dropZone when destination reached.
            else:
                x,y = self.closest_dropZone
            pos = (x,y)
            next_move = (pos)

        # 2:
        # The agent has a cooridnate for a last box seen.
        # Moves to the last box seen when it was moving to deliver another box.
        elif self.last_box != None and self.last_box.pos:
            x,y = self.pos
            x2,y2 = self.last_box.pos
            # Movement when last_box position is lesser than self position.
            if x > x2:
                x -= 1
            elif y > y2:
                y -= 1
            # Movement when last_box position is greater than self position.
            elif x < x2:
                x += 1
            elif y < y2:
                y += 1
            pos = x,y
            next_move = pos
            # Redundancy.
            if self.pos == self.last_box.pos:
                if next_move in boxesPos:
                    self.with_box = True
                    i = boxesPos.index(next_move)
                    self.closest_dropZone = self.get_closest_dropZone(self,next_move)
                self.cells_visited.append(self.pos)

        # 3:
        # The agent moves to pickup a box if it is next to one.
        # If more than one box is next to the agent, it will pick a random one.
        elif len(boxesPos) != 0:
            next_move = self.random.choice(boxesPos)
            # Save the next move as a visited cell.
            self.cells_visited.append(self.pos)
            i = boxesPos.index(next_move)
            self.with_box = True
            self.closest_dropZone = self.get_closest_dropZone(self,next_move)

        # 4:
        # The agent moves to a random cell.
        # The condition is to move to a cell that is free.
        # Priority is given to cells that have not been visited.
        # If all cells around are occupied, the agent will stay at the same position.
        else:
            next_move = self.random.choice(next_moves)
            # Save the next move as a visited cell.
            self.cells_visited.append(self.pos)

        # Now move:
        if self.random.random() < 100:
            self.model.grid.move_agent(self, next_move)
            if self.pos == self.last_box:
                self.last_box = None
            self.steps_taken+=1
            if self.with_box and boxesPos != []:
                self.model.grid.remove_agent(boxesAround[i])


    def step(self):
        """
        Determines the new direction it will take, and then moves
        """
        self.move()

    def get_closest_dropZone(self,x,y):
        """
        Returns the closest drop zone to the given position
        """
        position = y
        closest = self.model.dropZones[0]
        for i in range(1, len(self.model.dropZones)):
            if self.distance_to(position, self.model.dropZones[i]) < self.distance_to(position, closest):
                closest = self.model.dropZones[i]
        return closest

    def distance_to(self,posA,posB):
        """
        Returns the distance between two points.
        """
        x1, y1 = posA
        x2, y2 = posB
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

class Box(Agent):
    """
    Trash agent. Just to add dirty cells to the grid.
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
        self.stacked_boxes = 0

    def dropBay(self):
        """
        Drops a box in the drop zone.
        """
        agentsAround = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True, radius=1)
        RobotAround = [agent for agent in agentsAround if isinstance(agent, RobotAgent)]
        print(RobotAround)
        for rob in RobotAround:
            if  rob.pos == self.pos and rob.with_box:
                rob.with_box = False
                self.stacked_boxes += 1
                rob.closest_dropZone = None
                self.model.remaning_boxes -= 1
                print("stacked boxes: ", self.stacked_boxes, "in drop zone: ", self.unique_id)
        if self.stacked_boxes == 5:
            self.model.dropZones.remove(self.pos)

    def step(self):
        if self.stacked_boxes == 5:
            pass
        else:
            self.dropBay()

class ObstacleAgent(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass