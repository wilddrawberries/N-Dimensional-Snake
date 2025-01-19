import pygame
import sys
import random
from collections import deque
import time

open_message="          ______________________\n\n          N-Dimensional Snake \n          ______________________\n\n Unstoppable, autonomous, always has room to grow. \n\n     Runs into a corner? Adds a new dimension. \n \n     ___________________________________\n"

WINDOW_SIZE = 600
GRID_SIZE = 3
CELL_SIZE = WINDOW_SIZE // GRID_SIZE
FPS = 100
dimrec=0
lenrec=0
framecount=0

################################################################################
# Utility Functions for N-Dimensions
################################################################################

def generate_directions(dim):
    directions = []
    for axis in range(dim):
        step_plus = [0]*dim
        step_plus[axis] = 1
        step_minus = [0]*dim
        step_minus[axis] = -1
        directions.append(tuple(step_plus))
        directions.append(tuple(step_minus))
    return directions

def in_bounds(coord, dim):
    for c in coord:
        if c < 0 or c >= GRID_SIZE:
            return False
    return True

def bfs_path_nd(obstacles, start, goal, dim):
    if start == goal:
        return [start]

    visited = set([start])
    parent = {start: None}
    queue = deque([start])
    dirs = generate_directions(dim)

    while queue:
        current = queue.popleft()
        for d in dirs:
            neighbor = tuple(c + dc for c, dc in zip(current, d))
            if (neighbor not in visited and 
                in_bounds(neighbor, dim) and 
                neighbor not in obstacles):

                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

                if neighbor == goal:
                    # Reconstruct the path
                    path = []
                    n = neighbor
                    while n is not None:
                        path.append(n)
                        n = parent[n]
                    return path[::-1]
    return []

def append_zero_dimension(coord_list):
    # (x,y) -> (x,y,0), etc.
    return [c + (0,) for c in coord_list]

def generate_food_nd(snake, dim):
    """
    Generate a food coordinate in `dim` dimensions, ensuring it's not in the snake.
    We'll assume 'top layer' means all extra coordinates beyond x,y = 0.
    """
    while True:
        # Always randomize x, y in [0 .. GRID_SIZE-1].
        # For the remaining dims, set them to 0 (the "top layer").
        base = [random.randint(0, GRID_SIZE - 1) for iii in range(dim)]#, random.randint(0, GRID_SIZE - 1)]
        
        # If dim=2, that's enough. If dim>2, append zeros for z, w, ...
        #for _ in range(dim - 2):
        #    base.append(0)
        
        candidate = tuple(base)
        
        
        if candidate not in snake:
            
            return candidate

################################################################################
# Main Game Loop
################################################################################

def main():
    #pygame.init()
    #screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    #clock = pygame.time.Clock()

    current_dim = 2
    snake = [(GRID_SIZE//2, GRID_SIZE//2)]
    food = generate_food_nd(snake, current_dim)
    score = 0

    # Default direction in 2D -> (1,0)
    direction = (1, 0)
    path_cache = []

    # Here is the important part: we fix the slice we want to render
    # For 2D, there's no "z" at all. For 3D, we decide which z-plane we want:
    render_slice = 0  # we always draw z=0

    while True:
        # ---------------------------
        # 1. Handle events
        # ---------------------------
        global dimrec
        global lenrec
        global framecount

        

        # ---------------------------
        # 2. BFS path to food
        # ---------------------------
        obstacles = set(snake)
        if not path_cache or snake[0] != path_cache[0]:
            if len(snake[0])>dimrec or len(snake)>lenrec+1000 or framecount>1000000:
                then =time.time()
            path_cache = bfs_path_nd(obstacles, snake[0], food, current_dim)
            #if len(snake[0])>dimrec or len(snake)>lenrec+1000 or framecount>1000000:
                #print(time.time()-then) 
            
            
            if not path_cache:
                # No path => expand dimension
                current_dim += 1
                snake = append_zero_dimension(snake)
                food = append_zero_dimension([food])[0]
                path_cache = []
                continue

        if len(path_cache) > 1:
            next_position = path_cache[1]
        else:
            next_position = path_cache[0]

        # ---------------------------
        # 3. Move Snake
        # ---------------------------
        snake.insert(0, next_position)
        
        framecount+=1
       
        if len(snake[0])>dimrec or len(snake)>lenrec+1000:
            
            
            if len(snake[0])>dimrec:
                print('\n','* ',len(snake[0]),"D Snake trapped in a ",GRID_SIZE," ", (len(snake[0])-1)*('x '+str(GRID_SIZE)+' '), 'Box.','\n',sep='')  # <-- Add this line to print the head's coordinates
            print('Length of Snake:',len(snake),'points long.')
            dimrec=len(snake[0])
             
            lenrec=len(snake)
            #print(snake[10:])  

        if snake[0] == food:
            score += 1
            food = generate_food_nd(snake, current_dim)
            path_cache = []
        else:
            snake.pop()

        if snake.count(snake[0]) > 1:
            print("Game Over!")
            pygame.quit()
            sys.exit()

        # ---------------------------
        # 4. Draw the game
        # ---------------------------
        '''screen.fill((0, 0, 0))  # black background

        # Always show z=0 slice (render_slice=0) if current_dim >= 3.
        # In 2D, just draw x,y. In 3D+, only draw those whose z=0.
        if current_dim == 2:
            # Snake is (x,y)
            for seg in snake:
                pygame.draw.rect(screen, (0, 255, 0),
                                 (seg[0]*CELL_SIZE, seg[1]*CELL_SIZE,
                                  CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, (255, 0, 0),
                             (food[0]*CELL_SIZE, food[1]*CELL_SIZE,
                              CELL_SIZE, CELL_SIZE))
        else:
            # current_dim >= 3, so snake is (x, y, z).
            # Draw only the ones with z == render_slice:
            for seg in snake:
                if seg[2] == render_slice:
                    pygame.draw.rect(screen, (0, 255, 0),
                                     (seg[0]*CELL_SIZE, seg[1]*CELL_SIZE,
                                      CELL_SIZE, CELL_SIZE))
            # Same for food
            if food[2] == render_slice:
                pygame.draw.rect(screen, (255, 0, 0),
                                 (food[0]*CELL_SIZE, food[1]*CELL_SIZE,
                                  CELL_SIZE, CELL_SIZE))

        pygame.display.flip()
        clock.tick(FPS)
        '''

if __name__ == "__main__":
    print(open_message)
    main()
