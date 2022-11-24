from mesa import Agent
import math

class RobotAgent(Agent):
    """
    Robot Agent that moves randomly in search of boxes and delivers them to DropZones.
    Attributes:
        unique_id: Agent's ID
        steps_taken: Number of steps taken by the agent
        cells_visited: List of cells visited by the agent
        closest_dropZone: Coordinata of closest drop zone to the agent
        last_box: Coordinata of last box found by the agent when delivering another to a drop zone
        with_box: Boolean that indicates if the agent is carrying a box
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
        Determines movement of the agent.
        """
        ############ LISTS OF OPTIONS FOR MOVEMENT ############
        # All possible steps within one cell of the current position.
        all_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=True)

        # Checks which grid cells are empty and saves them in a list of possible steps.
        freeSpaces = list(map(self.model.grid.is_cell_empty, all_steps))
        next_moves = [p for p,f in zip(all_steps, freeSpaces) if f == True]

        # Checks if the cell has already been visited, in case all surrounding cells have been visited, the agent will move to a random cell.
        all_visited = all([p in self.cells_visited for p in next_moves])
        if not all_visited:
            next_moves = [p for p in next_moves if p not in self.cells_visited]

        # In case all cell around are being occupied by other agents, the agent will stay at the same position.
        if next_moves == []:
            next_moves = [self.pos]

        # List of all agents in the surrounding cells.
        agentsAround = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True, radius=1)

        # List of boxes around the agent.
        boxesAround = [agent for agent in agentsAround if isinstance(agent, Box)]

        # Gets position of the cells that have boxes in them.
        boxesPos = []
        for i in range(len(boxesAround)):
            boxesPos.append(boxesAround[i].pos)

        # Saves the coords of the last seen box when delivering a box.
        if len(boxesAround) > 0 and self.with_box:
            self.last_box = boxesAround[0]

        ############# MOVEMENT #############
        # Selection of the next_move, by jerarquical order of conditions and using the previus lists.

        # 1:
        # The agent has a box and has a position for a Dropzone to deliver.
        # Delivers the box to the closest dropZone.
        if self.with_box and self.closest_dropZone != None:
            boxesPos = []
            options = ["x","y"]
            x,y = self.pos
            x2,y2 = self.closest_dropZone
            # Already in destiny axis
            if x == x2:
                options.remove("x")
            elif y == y2:
                options.remove("y")
            # Randomly selects an axis to move.
            choice = self.random.choice(options)
            # Movement in x.
            if choice == "x":
                if x > x2:
                    x -= 1
                elif x < x2:
                    x += 1
                # Stays 1 step in dropZone when destination reached.
                else:
                    x,y = self.pos
            # Movement in y.
            elif choice == "y":
                if y > y2:
                    y -= 1
                elif y < y2:
                    y += 1
                # Stays 1 step in dropZone when destination reached.
                else:
                    x,y = self.pos
            pos = (x,y)
            next_move = (pos)
            # If next_move is not free, moves randomly.
            if not self.model.grid.is_cell_empty(next_move) and next_move != self.closest_dropZone:
                next_move = self.random.choice(next_moves)

        # 2:
        # The agent has a cooridnate for a last box seen.
        # Moves to the last box seen when it was moving to deliver another box.
        elif self.last_box != None and self.last_box.pos:
            options = ["x","y"]
            x,y = self.pos
            x2,y2 = self.last_box.pos
            # Already in destiny axis
            if x == x2:
                options.remove("x")
            elif y == y2:
                options.remove("y")
            # Randomly selects an axis to move.
            choice = self.random.choice(options)
            # Movement in x.
            if choice == "x":
                if x > x2:
                    x -= 1
                elif x < x2:
                    x += 1
                # Stays 1 step in dropZone when destination reached.
                else:
                    x,y = self.pos
            # Movement in y.
            elif choice == "y":
                if y > y2:
                    y -= 1
                elif y < y2:
                    y += 1
                # Stays 1 step in dropZone when destination reached.
                else:
                    x,y = self.pos
            pos = x,y
            next_move = pos
            # If next_move is not free, moves randomly.
            if not self.model.grid.is_cell_empty(next_move) and next_move != self.last_box.pos:
                next_move = self.random.choice(next_moves)
            # Destination reached.
            if self.pos == self.last_box.pos:
                # Destination still has a box.
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
            # Exception when reached destination for last_box but didnt find a box.
            if self.pos == self.last_box:
                self.last_box = None
            self.steps_taken+=1
            # Removes from the grid the box
            if self.with_box and boxesPos != []:
                self.model.grid.remove_agent(boxesAround[i])


    def step(self):
        """
        Moves the agent by steps.
        """
        self.move()

    def get_closest_dropZone(self,x,y):
        """
        Returns the closest drop zone to the given position
        Args:
            x: x coordinate
            y: y coordinate
        """
        position = y
        # Gets first dropZone coord.
        closest = self.model.dropZones[0]
        # Compares distances between the given position and the dropZones.
        for i in range(1, len(self.model.dropZones)):
            if self.distance_to(position, self.model.dropZones[i]) < self.distance_to(position, closest):
                # Coord of the dropZone with the smaller euler value is saved.
                closest = self.model.dropZones[i]
        return closest

    def distance_to(self,posA,posB):
        """
        Returns the distance between two points.
        Args:
            posA: position of the first point.
            posB: position of the second point.
        """
        x1, y1 = posA
        x2, y2 = posB
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

class Box(Agent):
    """
    Box agent.
    Attributes:
        unique_id: Agent's ID
    """
    def __init__(self, unique_id, model):
        """
        Creates a new box agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)

    def step(self):
        pass

class dropZone(Agent):
    """
    DropZone agent "stores" boxes, has a limit of 5. Also functions as pivot for change in behacior of robot agent.
    Attributes:
        unique_id: Agent's ID
        stacked_boxes: Number of boxes stacked in the dropZone
        condition: Based on N of boxes in the dropZone. N < 5: "Empty" Orange, N = 5: "Full" Green
    """
    def __init__(self, unique_id, model):
        """
        Creates a new dropZone agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.stacked_boxes = 0
        self.condition = "Empty"

    def OpenBay(self):
        """
        Can receive boxes until it reaches 5.
        """
        # List of robots around
        agentsAround = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True, radius=1)
        RobotAround = [agent for agent in agentsAround if isinstance(agent, RobotAgent)]

        for rob in RobotAround:
            # If the robot is carrying a box, and is in dropZone drops the box.
            if  rob.pos == self.pos and rob.with_box:
                rob.with_box = False
                self.stacked_boxes += 1
                rob.closest_dropZone = None
                self.model.remaning_boxes -= 1
        # When reached 5 boxes, the dropZone changes color to green and behavior to closed.
        if self.stacked_boxes == 5:
            self.model.dropZones.remove(self.pos)
            self.condition = "Full"

    def ClosedBay(self):
        """
        Cant receive boxes. All agents that come are send to other close dropZone.
        """
        # List of robots around
        agentsAround = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True, radius=1)
        RobotAround = [agent for agent in agentsAround if isinstance(agent, RobotAgent)]
        for rob in RobotAround:
            if  rob.pos == self.pos and rob.with_box:
                rob.closest_dropZone = rob.get_closest_dropZone(rob,rob.pos)

    def step(self):
        if self.stacked_boxes == 5:
            self.ClosedBay()
        else:
            self.OpenBay()

class ObstacleAgent(Agent):
    """
    Obstacle agent
    Attributes:
        unique_id: Agent's ID
    """
    def __init__(self, unique_id, model):
        """
        Creates a new Obstacle agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)

    def step(self):
        pass