from config import GRID_ROWS, GRID_COLS


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, goal, obstacles):
    open_list  = {start: heuristic(start, goal)}   # contient les cases qu’on a découvertes mais qu’on n’a pas encore traitées.
    came_from  = {} # stocke la case d'avant
    g_score    = {start: 0} # stocke g(n) de n'importe quel point
    explored   = set()

    while open_list:
        current = min(open_list, key=open_list.get) #(0,0)

        if current == goal:
            # Reconstruct path 
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path, explored

        open_list.pop(current)
        explored.add(current)

        r, c = current # row column
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]: # delta row / column
            neighbor = (r + dr, c + dc)

            # Bounds check
            if not (0 <= neighbor[0] < GRID_ROWS and 0 <= neighbor[1] < GRID_COLS):
                continue
            # Obstacle check
            if neighbor in obstacles:
                continue
            if neighbor in explored:
                continue

            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor]    = tentative_g
                f_score              = tentative_g + heuristic(neighbor, goal)
                open_list[neighbor]  = f_score
                came_from[neighbor]  = current

    return [], explored   # no path found


