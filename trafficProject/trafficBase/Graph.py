from collections import defaultdict

class Graph:
    """
    Weighted Graph class
    """
    def __init__(self, vertices):
        """
        Creates a new Graph.
        Args:
            vertices: Number of vertices in the graph = 0
        """
        self.V = vertices
        self.graph = defaultdict(list)

        # Mirror map with x and y start at top right corner.
        matrixInverted = []

        # Read map from file.
        with open('2022_basetest.txt', 'r') as f:
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
                elif matrix[i][j] == '>' or matrix[i][j] == 'Z' or matrix[i][j] == 's':
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
                if matrix2[i][j] == '+' and ("^" in matrix2[i][j:-1] or "^" in matrix2[i][j-3:j]):
                    if last_node != None:
                        edges_list.append((last_node, (y,x), counter))
                        counter = 0
                    last_node = (y,x)
                elif matrix2[i][j] == '^' or matrix2[i][j] == 'S' or matrix2[i][j] == 'Z':
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
                elif matrix3[i][j] == '<' or matrix3[i][j] == 'Z' or matrix3[i][j] == 's':
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
                if matrix4[i][j] == '+' and ("v" in matrix4[i][j:-1] or "v" in matrix4[i][j-3:j]):
                    if last_node != None:
                        edges_list.append((last_node, (y,x), counter))
                        counter = 0
                    last_node = (y,x)
                elif matrix4[i][j] == 'v' or matrix4[i][j] == 'S' or matrix4[i][j] == 'Z':
                    counter += 1
                else:
                    counter = 0
                    last_node = None
                y += 1
            x -= 1

        for i in range(len(edges_list)):
            self.addEdge(edges_list[i][0], edges_list[i][1], edges_list[i][2])

    def addEdge(self,src,dest,w):
        newNode = [dest,w]
        self.graph[src].append(newNode)
        self.V += 1

    def printPath(self, parent, j):
        Path_len = 1
        if parent[j] == -1 and j < self.V_org : #Base Case : If j is source
            print(j),
            return 0 # when parent[-1] then path length = 0
        l = self.printPath(parent , parent[j])

        #increment path length
        Path_len = l + Path_len

        # print node only if its less than original node length.
        # i.e do not print any new node that has been added later
        if j < self.V_org :
            print(j),

        return Path_len

    def findShortestPath(self,src, dest):

        visited =[False]*(self.V)
        parent =[-1]*(self.V)

        queue=[]

        queue.append(src)
        visited[src] = True

        while queue :

            s = queue.pop(0)

            if s == dest:
                return self.printPath(parent, s)

            for i in self.graph[s]:
                if visited[i] == False:
                    queue.append(i)
                    visited[i] = True
                    parent[i] = s

g = Graph(0)
src = (9,17)
dest = (15,13)

print ("Shortest Path between %d and %d is  " %(src, dest)),
l = g.findShortestPath(src, dest)
print ("\nShortest Distance between %d and %d is %d " %(src, dest, l)),