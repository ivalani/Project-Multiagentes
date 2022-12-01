from mesa import Agent
from Graph import *
import collections

# Moving Agents

class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID
        direction: Direction in which the agent is moving, its based on the Road's direction. When Intersection, it will choose the next direction based on destiny
        destiny: Coordinates of the destination.
        moving: Boolean that determines if the agent is moving or not
        myDestiny: List of coordinates that the agent will follow to reach the destiny
        lastNode: Last node of the graph that the agent visited
        lastMove: Last move that the agent did
        lastlastMove: Last last move that the agent did
    """
    def __init__(self, unique_id, model, destiny):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            destiny: Coordinates of the destination
        """
        self.unique_id = unique_id
        self.direction = None
        self.destiny = destiny
        self.moving = False
        self.myDestiny = None
        self.lastNode = None
        self.lastMove = None
        self.lastlastMove = None
        super().__init__(unique_id, model)

    def move(self):
        """
        Determines if the agent can move in the direction that was chosen.
        First it interprets the direction, and translates it to a coordinate in next_move.
        Second it checks if the next position is a valid position to move to (No other agents, red lights, pedestrians).
        Third it moves the agent to the next position.
        """
        # Interpretation of the direction into coordinates
        if self.direction == "Up":
            next_move = (self.pos[0], self.pos[1] + 1)
        elif self.direction == "Down":
            next_move = (self.pos[0], self.pos[1] - 1)
        elif self.direction == "Left":
            next_move = (self.pos[0] - 1, self.pos[1])
        elif self.direction == "Right":
            next_move = (self.pos[0] + 1, self.pos[1])
        # If the agent is in an intersection and reached destiny, it will enter the destination and then stop.
        elif self.pos == self.destiny:
            # Gets the coordinates of the destination and enters to it
            whereIsDestination = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True, radius=1)
            thereItIs = [agent for agent in whereIsDestination if isinstance(agent, Destination)]
            next_move = thereItIs[0].pos
            self.model.grid.move_agent(self, next_move)
            self.model.schedule.remove(self)
            return
        # If the agent enters for first time of simulation into an intersection it will get its destiny path and moves to the first node.
        elif self.direction == "Intersection" and self.myDestiny == None:
            # Gets the path to follow and stores it in myDestiny
            x,y = self.pos
            x2,y2 = self.destiny
            self.myDestiny = shortestPath(self.model.list_of_edges, (y,x), (y2,x2))
            # Removes the total weight of the path
            self.myDestiny = self.myDestiny[1]
            # Removes the first node of the path because it is the current node
            if len(self.myDestiny) > 1:
                x,y = self.myDestiny.pop(0)
            # Gets the coordinates of the next node
            x,y = self.myDestiny.pop(0)
            next_move = (y,x)
        # If agent is in an intersection it will move based on the coords of the next node in path
        elif self.direction == "Intersection":
            # Exceptiom for accidental consuption of myDestiny
            if self.myDestiny == [] or self.pos == self.lastlastMove:
                aroundAgent = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False, radius=1)
                agentsFront = [agent for agent in aroundAgent if isinstance(agent, Road)]
                next_move = self.random.choice(agentsFront).pos
                self.myDestiny = None
                self.model.grid.move_agent(self, next_move)
                return
            # Interpretation of the coords of the next node into movement of the agent
            y,x = self.myDestiny.pop(0)
            x2,y2 = self.pos
            self.lastNode = (x,y)

            if (x,y) == (x2,y2):
                y,x = self.myDestiny.pop(0)
            # Right
            if x > x2:
                next_move = ((x2+1),y2)
            # Left
            elif x < x2:
                next_move = ((x2-1),y2)
            # Down
            elif y < y2:
                next_move = (x2,(y2-1))
            # Up
            elif y > y2:
                next_move = (x2,(y2+1))

        # Gets the agents in the next move and that are not a road
        whatIsFront = self.model.grid.get_neighbors(next_move, moore=False, include_center=True, radius=0)
        agentsFront = [agent for agent in whatIsFront if not isinstance(agent, Road)]
        self.lastlastMove = self.lastMove
        self.lastMove = next_move
        # If there is no agent in the next move, it will move
        if agentsFront == []:
            self.model.grid.move_agent(self, next_move)
            self.lastMove = next_move
            self.moving = True
            return
        # If there is an Traffic_Light in the next move, it will check if it is green
        elif isinstance(agentsFront[0], Traffic_Light) or isinstance(agentsFront[-1], Traffic_Light):
            agentsFront = [agent for agent in agentsFront if isinstance(agent, Traffic_Light)]
            if agentsFront[0].state == True:
                # Moves
                self.model.grid.move_agent(self, next_move)
                self.moving = True
                # Saves the last node visited
                if self.direction == "Intersection":
                    print("Nuevo lastNode: ", (y,x))
                    self.lastNode = (y,x)
                return
            else:
                # Stops
                self.moving = False
                self.lastMove = self.lastlastMove
                # Adds the last node visited to the path so it can continue from there next step
                if self.direction == "Intersection":
                    self.myDestiny.insert(0, (y,x))
                return
        # If there is an PedestrianCrossing in the next move, it will check if there is an pedestrian crossing.
        elif isinstance(agentsFront[0], PedestrianCrossing) or isinstance(agentsFront[-1], PedestrianCrossing):
            agentsFront = [agent for agent in agentsFront if isinstance(agent, PedestrianCrossing)]
            if agentsFront[0].state == None or agentsFront[0].state == "Car":
                # Moves
                self.model.grid.move_agent(self, next_move)
                self.moving = True
                # Saves the last node visited
                if self.direction == "Intersection":
                    print("Nuevo lastNode: ", (y,x))
                    self.lastNode = (y,x)
                return
            else:
                # Stops
                self.moving = False
                self.lastMove = self.lastlastMove
                # Adds the last node visited to the path so it can continue from there next step
                if self.direction == "Intersection":
                    self.myDestiny.insert(0, (y,x))
                return
        # Checks if there is a stoped car or bus.
        elif isinstance(agentsFront, Car) or isinstance(agentsFront, Bus):
            if agentsFront[0].moving == True:
                # Moves
                self.model.grid.move_agent(self, next_move)
                self.moving = True
                # Saves the last node visited
                if self.direction == "Intersection":
                    print("Nuevo lastNode: ", (y,x))
                    self.lastNode = (y,x)
                return
            else:
                # Stops
                self.moving = False
                self.lastMove = self.lastlastMove
                # Adds the last node visited to the path so it can continue from there next step
                if self.direction == "Intersection":
                    self.myDestiny.insert(0, (y,x))
                return

    def step(self):
        """
        Determines the new direction it will take, and then moves
        """
        # Gets the direction of current road
        currentIn = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True, radius=0)
        RoadDirection = [agent for agent in currentIn if isinstance(agent, Road)]
        # Saves the direction of the road
        if RoadDirection != []:
            self.direction = RoadDirection[0].direction
        # When the agent is in an intersection, it will get the relative direction of the next node
        elif self.direction == "Intersection" and self.myDestiny != []:
            y,x = self.lastNode
            x2,y2 = self.pos
            # Right
            if x > x2:
                self.direction = "Right"
            # Left
            elif x < x2:
                self.direction = "Left"
            # Down
            elif y < y2:
                self.direction = "Down"
            # Up
            elif y > y2:
                self.direction = "Up"
        # In case the agent is over a traffic light or pedestrian crossing, it will keep its last direction
        else:
            self.direction = self.direction
        print(self.unique_id)
        print("Meta: ", self.destiny)
        print("Antes de mover: ")
        print("lastNode: ", self.lastNode)
        print("pos", self.pos)
        print("myDestiny: ", self.myDestiny)
        print("direction: ", self.direction)
        print("######### En movimiento #######")
        self.move()
        print("-------------------------------")

class Pedestrian(Agent):
    """
    Pedestrian agent.
    Atributes:
        unique_id: Unique identifier of the agent
        model: Model in which the agent is
        visited: List of nodes visited by the agent
    """
    def __init__(self, unique_id, model):
        """
        Creates a new pedestrian.
        Args:
            unique_id: agent's ID
            model: model reference
        """
        super().__init__(unique_id, model)
        self.visited=[]

    def move(self):
        # Agent arrive to the destination
        if self.pos == None:
            self.model.schedule.remove(self)
            return

        # Gets the possible next moves Only in sidewalks, pedestrian crossings and below traffic lights.
        posibleSteps = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False, radius=1)
        isPedestrianViable = [agent.pos for agent in posibleSteps if isinstance(agent, PedestrianCrossing) or isinstance(agent, SideWalk) or isinstance(agent, Destination)  or isinstance(agent, Traffic_Light)]

        # It would be better to have a pathfinding algorithm here, but for now it will just move randomly
        next_move = self.random.choice(isPedestrianViable)
        isPedestrianViable.remove(next_move)

        # Checks if the next move has already been visited. In case all visited, it moves random.
        while next_move in self.visited and isPedestrianViable != []:
            next_move = self.random.choice(isPedestrianViable)
            isPedestrianViable.remove(next_move)

        self.visited.append(next_move)

        # Checks what is in the next move.
        whatIsFront = self.model.grid.get_neighbors(next_move, moore=False, include_center=True, radius=0)
        notAPedestrian = [agent for agent in whatIsFront if not isinstance(agent, Pedestrian) or not isinstance(agent, Car)]

        # In case there is a traffic light, it will check if it is red for cars and cross.
        if isinstance(notAPedestrian[0], Traffic_Light):
            if notAPedestrian[0].state == False:
                self.model.grid.move_agent(self, next_move)
                return
            else:
                self.visited.remove(next_move)
                return
        # In case there is a pedestrian crossing, it will check if there are no cars.
        elif isinstance(notAPedestrian[0], PedestrianCrossing):
            if notAPedestrian[0].state == None or notAPedestrian[0].state == "Pedestrian":
                self.model.grid.move_agent(self, next_move)
                return
            else:
                self.visited.remove(next_move)
                return
        # In case there is a destiny it goes inside.
        elif isinstance(notAPedestrian, Destination):
            self.model.schedule.remove(self)
            self.model.grid.move_agent(self, next_move)
            return
        # Moves in sidewalk.
        else:
            self.model.grid.move_agent(self, next_move)
            return

    def step(self):
        self.move()

# Not done
class Bus(Agent):
    """
    Bus agent.
    """
    def __init__(self, unique_id, model):
        """
        Creates a new bus.
        Args:
            unique_id: agent's ID
            model: model reference
        """
        super().__init__(unique_id, model)
        self.route = [(1,9),(6,8),(22,11)]
        self.direction = None
        self.lastDirection = None
        self.moving = False

    def move(self):
        """
        Determines if the agent can move in the direction that was chosen
        """
        if self.pos == self.route[0]:
            if self.direction != self.lastDirection:
                self.direction = self.lastDirection
            else:
                self.direction = self.direction
            temp = self.route[0]
            self.route.remove(self.route[0])
            self.route.append(temp)

        if self.direction == "Up":
            next_move = (self.pos[0], self.pos[1] + 1)
        elif self.direction == "Down":
            next_move = (self.pos[0], self.pos[1] - 1)
        elif self.direction == "Left":
            next_move = (self.pos[0] - 1, self.pos[1])
        elif self.direction == "Right":
            next_move = (self.pos[0] + 1, self.pos[1])
        else:
            return

        whatIsFront = self.model.grid.get_neighbors(next_move, moore=False, include_center=True, radius=0)
        agentsFront = [agent for agent in whatIsFront if not isinstance(agent, Road)]

        if agentsFront == []:
            self.model.grid.move_agent(self, next_move)
            self.moving = True
            return
        elif isinstance(agentsFront[0], Traffic_Light) or isinstance(agentsFront[-1], Traffic_Light):
            agentsFront = [agent for agent in agentsFront if isinstance(agent, Traffic_Light)]
            if agentsFront[0].state == True:
                self.model.grid.move_agent(self, next_move)
                self.moving = True
                return
            else:
                self.moving = False
                return
        elif isinstance(agentsFront[0], PedestrianCrossing) or isinstance(agentsFront[-1], PedestrianCrossing):
            agentsFront = [agent for agent in agentsFront if isinstance(agent, PedestrianCrossing)]
            if agentsFront[0].state == False:
                self.model.grid.move_agent(self, next_move)
                self.moving = True
                return
            else:
                self.moving = False
                return
        elif isinstance(agentsFront, Car) or isinstance(agentsFront, Bus):
            if agentsFront[0].moving == True:
                self.model.grid.move_agent(self, next_move)
                return
            else:
                self.moving = False
                return



    def step(self):
        """
        Determines the new direction it will take, and then moves
        """
        currentIn = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True, radius=0)
        RoadDirection = [agent for agent in currentIn if isinstance(agent, Road)]
        if RoadDirection != []:
            self.lastDirection = self.direction
            self.direction = RoadDirection[0].direction
        else:
            self.direction = self.direction
        print("Posicion Bus:")
        print(self.pos)
        print(self.direction)
        self.move()
        print("-------------------------------------")

# Reactive agents, but not moving

class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color
        """
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        """
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        # if self.model.schedule.steps % self.timeToChange == 0:
        #     self.state = not self.state
        pass

class PedestrianCrossing(Agent):
    """
    Pedestrian crossing agent. Determines where a pedestrian can cross the street
    """
    def __init__(self, unique_id, model):
        """
        Creates a new pedestrian crossing,
        Args:
            unique id: agent's ID
            model: model reference
        """
        super().__init__(unique_id, model)
        self.state = None

    def step(self):
        # Checks if a pedestrian or car is over it.
        AgentOverIt = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True, radius=0)
        if isinstance(AgentOverIt[0], Car) or isinstance(AgentOverIt[0], Bus):
            self.state = "Car"
        elif isinstance(AgentOverIt[0], Pedestrian):
            self.state = "Pedestrian"
        else:
            self.state = None

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        """
        Creates a new destination.,
        Args:
            unique id: agent's ID
            model: model reference
        """
        super().__init__(unique_id, model)

    def step(self):
        # Checks if a car or pedestrian arrived to the destination
        AgentOverIt = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True, radius=0)
        OverIt = [agent for agent in AgentOverIt if isinstance(agent, Car) or isinstance(agent, Pedestrian)]
        # Removes the car or pedestrian from the grid
        if OverIt != []:
            for _ in OverIt:
                self.model.grid.remove_agent(_)

# Environment

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid. Interpreted as a building in Unity.
    """
    def __init__(self, unique_id, model):
        """
        Creates a new building.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass

class SideWalk(Agent):
    """
    Sidewalk agent. Determines where the persons can walk.
    """
    def __init__(self, unique_id, model):
        """
        Creates a new sidewalk.
        Args:
            unique_id: agent's ID
            model: model reference for the agent
        """
        super().__init__(unique_id, model)

    def step(self):
        pass