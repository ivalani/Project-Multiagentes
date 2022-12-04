import collections
import heapq

def shortestPath(edges, source, sink):
    graph = collections.defaultdict(list)
    for l,r,c in edges:
        graph[l].append((c,r))

    queue, visited = [(0,source,[])], set()
    heapq.heapify(queue)

    while queue:
        (cost, node, path) = heapq.heappop(queue)
        if node not in visited:
            visited.add(node)
            path = path + [node]
            if node == sink:
                return (cost, path)

            for c, neighbour in graph[node]:
                if neighbour not in visited:
                    heapq.heappush(queue, (cost+c, neighbour, path))

    return (0, [source])
