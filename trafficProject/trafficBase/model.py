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
        self.list_of_edges = self.build_edgesList()
        self.traffic_lights = []
        self.num_agents = 10

        self.running = True
        positions_temp = []
        pedPos_temp = []
        destinys_temp = [(1,15),(3,18),(3,23),(6,4),(6,15),(9,8),(13,4),(13,20),(17,14),(17,20),(19,1),(22,5),(22,22)]

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
                        if col in ["v", "^", ">", "<"]:
                            positions_temp.append((c, self.height - r - 1))

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
                        self.schedule.add(agent)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "B":
                        agent = SideWalk(f"sw_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r -1 ))
                        pedPos_temp.append((c, self.height - r - 1))

                    elif col in ["Z", "z"]:
                        agent = PedestrianCrossing(f"pc_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)

        for i in range(self.num_agents):
            destpos = self.random.choice(destinys_temp)
            a = Car(i+1000, self, destpos)
            pos = self.random.choice(positions_temp)
            while isinstance(self.grid.get_cell_list_contents(pos)[-1], Car):
                pos = self.random.choice(positions_temp)
            self.schedule.add(a)
            self.grid.place_agent(a, pos)

        for i in range(self.num_agents):
            a = Pedestrian(i+2000, self)
            pos = self.random.choice(pedPos_temp)
            self.schedule.add(a)
            self.grid.place_agent(a, pos)
        """
        b = Bus(3000, self)
        pos = 13,12
        self.schedule.add(b)
        self.grid.place_agent(b, pos)
"""
    def build_edgesList(self):
        # Mirror map with x and y start at top right corner.
        matrixInverted = []

        # Read map from file.
        with open('2022_base.txt', 'r') as f:
            matrixInverted = [[o for o in line.strip()] for line in f]

        # Matrix of map with corrections of coordinates.
        matrix = []
        for row in range(len(matrixInverted)):
            matrix.insert(0, matrixInverted[row])


        # List of all edges and weights.
        edges_list = []

        # Add edges that have right direction.
        for i in range(len(matrix)):
            # Extracts the weight of the edge.
            counter = 0
            # Determines parent node.
            last_node = None
            for j in range(len(matrix[i])):
                # Is in right direction and has at least one instance of this direction to evade overadding in other intersections where there is not Right.
                if matrix[i][j] == '+' and (">" in matrix[i]):
                    # Prevents adding a Node with no parent.
                    if last_node != None:
                        edges_list.append((last_node, (i,j), counter))
                        counter = 0
                    last_node = (i,j)
                # Weight is counted when the direction is the same and there is no obstacle.
                elif matrix[i][j] == '>' or matrix[i][j] == 'Z' or matrix[i][j] == 's' or matrix[i][j] == 'S':
                    counter += 1
                else:
                    # All other cases are discarded.
                    counter = 0
                    last_node = None

        # Creates a new matrix to rotate the map. And change direction from right to up.
        rows = len(matrix)
        cols = len(matrix[0])
        matrix2 = [[""] * rows for _ in range(cols)]
        for x in range(rows):
            for y in range(cols):
                matrix2[y][rows-x-1] = matrix[x][y]

        # Add edges that have up direction.
        x = 0
        for i in range(len(matrix2)):
            counter = 0
            last_node = None
            y = 24
            for j in range(len(matrix2[i])):
                if matrix2[i][j] == '+' and ("v" in matrix2[i][j:-1] or "v" in matrix2[i][j-3:j]):
                    if last_node != None:
                        edges_list.append((last_node, (y,x), counter))
                        counter = 0
                    last_node = (y,x)
                elif matrix2[i][j] == 'v' or matrix2[i][j] == 'S' or matrix2[i][j] == 'Z' or matrix2[i][j] == 's':
                    counter += 1
                else:
                    counter = 0
                    last_node = None
                y -= 1
            x += 1

        # Creates a new matrix to rotate the map. And change direction from up to left.
        rows = len(matrix2)
        cols = len(matrix2[0])
        matrix3 = [[""] * rows for _ in range(cols)]
        for x in range(rows):
            for y in range(cols):
                matrix3[y][rows-x-1] = matrix2[x][y]

        # Add edges that have left direction.
        x = 24
        for i in range(len(matrix3)):
            counter = 0
            last_node = None
            y = 23
            for j in range(len(matrix3[i])):
                if matrix3[i][j] == '+' and ("<" in matrix3[i]):
                    if last_node != None:
                        edges_list.append((last_node, (x,y), counter))
                        counter = 0
                    last_node = (x,y)
                elif matrix3[i][j] == '<' or matrix3[i][j] == 'Z' or matrix3[i][j] == 's' or matrix3[i][j] == 'S':
                    counter += 1
                else:
                    counter = 0
                    last_node = None
                y -= 1
            x -= 1

        # Creates a new matrix to rotate the map. And change direction from left to down.
        rows = len(matrix3)
        cols = len(matrix3[0])
        matrix4 = [[""] * rows for _ in range(cols)]
        for x in range(rows):
            for y in range(cols):
                matrix4[y][rows-x-1] = matrix3[x][y]

        # Add edges that have down direction.
        x = 23
        for i in range(len(matrix4)):
            counter = 0
            last_node = None
            y = 0
            for j in range(len(matrix4[i])):
                if matrix4[i][j] == '+' and ("^" in matrix4[i][j:-1] or "^" in matrix4[i][j-3:j]):
                    if last_node != None:
                        edges_list.append((last_node, (y,x), counter))
                        counter = 0
                    last_node = (y,x)
                elif matrix4[i][j] == '^' or matrix4[i][j] == 'S' or matrix4[i][j] == 'Z':
                    counter += 1
                else:
                    counter = 0
                    last_node = None
                y += 1
            x -= 1

        return edges_list

    def step(self):
        '''Advance the model by one step.'''
        if self.schedule.steps % 15 == 0:
            for agent in self.traffic_lights:
                agent.state = not agent.state
        self.schedule.step()