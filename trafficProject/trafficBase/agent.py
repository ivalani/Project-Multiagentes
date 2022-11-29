from mesa import Agent
from Graph import *
import collections

class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model, destiny, mySpawnPoint):
        self.direction = None
        self.destiny = destiny
        self.unique_id = unique_id
        self.moving = False
        self.myDestiny = None
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)

    def move(self):
        """
        Determines if the agent can move in the direction that was chosen
        """
        if self.direction == "Up":
            next_move = (self.pos[0], self.pos[1] + 1)
        elif self.direction == "Down":
            next_move = (self.pos[0], self.pos[1] - 1)
        elif self.direction == "Left":
            next_move = (self.pos[0] - 1, self.pos[1])
        elif self.direction == "Right":
            next_move = (self.pos[0] + 1, self.pos[1])
        elif self.direction == "Intersection" and self.pos == self.destiny:
            print("exito")
            whereIsDestination = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True, radius=1)
            thereItIs = [agent for agent in whereIsDestination if isinstance(agent, Destination)]
            next_move = thereItIs[0].pos
        elif self.direction == "Intersection" and self.myDestiny == None:
            # Borrar cuando se corrigan las coordenadas del graafo
            x,y = self.pos
            x2,y2 = self.destiny

            #
            self.myDestiny = shortestPath(self.model.list_of_edges, (y,x), (y2,x2))
            self.myDestiny = self.myDestiny[1]
            idontneedit = self.myDestiny.pop(0)
            print("Removed start point")
            print(idontneedit)
            x,y = self.myDestiny.pop(0)
            next_move = (y,x)
            print("Actualmente en:")
        elif self.direction == "Intersection":
            y,x = self.myDestiny.pop(0)
            print("Referencia de destino:")
            print(x,y)
            x2,y2 = self.pos
            print("Posicion previa:")
            print(x2,y2)
            # undefinded
            if x > x2:
                print("Vamos a derecha")
                next_move = ((x2+1),y2)
            # undefined
            elif x < x2:
                print("Vamos a izquierda")
                next_move = ((x2-1),y2)
            # Goes down to destination
            elif y < y2:
                print("Vamos a abajo")
                next_move = (x2,(y2-1))
            # Goes up to destination
            elif y > y2:
                print("Vamos a arriba")
                next_move = (x2,(y2+1))
            print("Actualmente en:")

        whatIsFront = self.model.grid.get_neighbors(next_move, moore=False, include_center=True, radius=0)
        agentsFront = [agent for agent in whatIsFront if not isinstance(agent, Road)]

        if agentsFront == []:
            self.model.grid.move_agent(self, next_move)
            print(next_move)
            self.moving = True
            return
        elif isinstance(agentsFront[0], Traffic_Light) or isinstance(agentsFront[-1], Traffic_Light):
            agentsFront = [agent for agent in agentsFront if isinstance(agent, Traffic_Light)]
            if agentsFront[0].state == True:
                print(next_move)
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
                print(next_move)
                self.moving = True
                return
            else:
                self.moving = False
                return
        elif isinstance(agentsFront, Car) or isinstance(agentsFront, Bus):
            if agentsFront[0].moving == True:
                self.model.grid.move_agent(self, next_move)
                self.moving = True
                print(next_move)
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
            self.direction = RoadDirection[0].direction
        else:
            self.direction = self.direction
        self.move()
        print("-------------------------------------")

class Pedestrian(Agent):
    """
    Pedestrian agent.
    """
    def __init__(self, unique_id, model):
        """
        Creates a new pedestrian.
        Args:
            unique_id: agent's ID
            model: model reference
        """
        super().__init__(unique_id, model)

    def move(self):
        posibleSteps = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False, radius=1)
        isPedestrianViable = [agent.pos for agent in posibleSteps if isinstance(agent, PedestrianCrossing) or isinstance(agent, SideWalk) or isinstance(agent, Destination) or isinstance(agent, Traffic_Light)]
        next_move = self.random.choice(isPedestrianViable)
        self.model.grid.move_agent(self, next_move)

    def step(self):
        self.move()

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

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
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
        self.state = False

