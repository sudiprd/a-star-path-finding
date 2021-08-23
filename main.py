import pygame
import math
from queue import PriorityQueue

#for window creating with caption
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")


RED = (255, 0, 0)   #already looked at it
GREEN = (0, 255, 0)  #open set
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255) # Not visited yet
BLACK = (0, 0, 0) #barrier, not to go from there, avoid it
PURPLE = (128, 0, 128)  # its the path
ORANGE = (255, 165, 0)  #start node
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot:
    def __init__(self, row, col, width, total_rows):
            #instances->objects
        self.row = row
        self.col = col
        self.x = row * width    # x, y are the coordinate, need to track with 
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self): #method
        return self.row, self.col

    #how it cover the area, color- RED, how to consider it, it is method
    def is_closed(self):
        #what make close set spot, what makes it red
        return self.color == RED
    
    def is_open(self):
        return self.color == GREEN
    
    def is_barrier(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE
    
    def reset(self):
        self.color = WHITE

    #define to make call the cubes/spots
    def make_closed(self):
        self.color = RED
    
    def make_open(self):
        self.color = GREEN
    
    def make_start(self):
        self.color= ORANGE

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):  #win- window, where to draw, pass a argument
        #how to draw the rectangle, it position ,color etc
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
    
    def update_neighbors(self, grid):
        #check the up, down, left ,right
        self.neighbors = []

        if self.row < self.total_rows -1 and not grid[self.row +1][self.col].is_barrier(): # downward--> add +1 with grid
            self.neighbors.append(grid[self.row +1][self.col])
        
        if self.row > 0  and not grid[self.row - 1][self.col].is_barrier(): #upward- 
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): #left --> add +1 with grid
            self.neighbors.append(grid[self.row][self.col - 1])
    
    #this method used to compare with class "spot" together
    def __lt__(self, other):  #lt stands for lasttend
        return False



#heuristics function
def h(p1,p2):  #p -> point
    #distance between the point using manhattan distance
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()



def algorithm(draw, grid, start, end):
    count = 0 #keep track when we add into the queue, also breaks ties in duplicates number
    open_set = PriorityQueue()
    #we take F set, 0 as argument
    open_set.put((0, count, start))
    #node A came from node B.
    came_from = {}
    g_score = {spot : float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot : float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos()) #heuristics, estimate how far start node is from the n node

    #check items are present or not the nodes in PQ 
    open_set_hash = {start} #PQ does not tell us, if node is in queue or not

    while not open_set.empty():  
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2] # [2] #open set contain f score- count and node
        open_set_hash.remove(current) #pop out from PQ
    
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        #considering the neighbor with the current node
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            #finding the optimal path
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] =temp_g_score
                f_score[neighbor] =temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open() #current neighbor
        
        draw()
        
        if current != start:
            current.make_closed()

    return False # do not find the path 



def make_grid(rows, width): #rows= columns so ,couldnt include col here
    grid= []
    gap= width // rows  #integer division- what gap should be 
    
    for i in range(rows):
        grid.append([])
        for j in range(rows):  # for columns
            #call a new spot  calling class spot
            spot = Spot(i,j, gap, rows) #spot object create
            grid[i].append(spot)  #have bunch   of list inside of list in the spot

    return grid
#draw grid lines only
def draw_grid(win, rows, width):
    gap = width // rows

    for i in range(rows):
        pygame.draw.line(win, GREY,(0, i * gap), (width, i *gap)) # draw a horizontal lines for the row
                                    #x, y
        #for columns- vertical lines ,coordiantes are flipping 
        for j in range(rows):
             pygame.draw.line(win, GREY,(j * gap, 0), (j *gap, width))

#main grid draw
def draw(win, grid, rows, width):
    #fill() -> fill the win througout, in each frame, redraw everything
    win.fill(WHITE)
    
    for row in grid:
        for spot in row:
            spot.draw(win)  #calling the draw function
    
    draw_grid(win, rows, width)
    pygame.display.update()

#position, when we click on, as pos-> mouse position
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


#check, collision, barrier, new beginning etc.

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None
    
    run = True
    started = False
    while run:
        draw(win, grid, ROWS, width)

         #beginning of this while loop, all the event that is happen check what they are
        #event such that- press a mouse,  press keyboard, timer runout etc etc.
        for event in pygame.event.get() :
            if event.type == pygame.QUIT: #need to check initially
                run= False # stop the game

            if started:
                continue #cause, while algorithm is running, it should not quite untill said it

     #now, while pressing mouse
            if pygame.mouse.get_pressed()[0]: #[0] for the left side of mouse button
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)  # helper function get_clicked_pos at what spot it clicked
                spot = grid[row][col]
                if not start and spot != end: #spot!= end mean that, start and end position not to be in single position 
                    start =spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()
                
                elif spot != end and spot != start:
                     spot.make_barrier()

            
            elif pygame.mouse.get_pressed()[2]:  ## 0 1 2 -> left centre right (mouse position)
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None
                

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                        
                    algorithm(lambda : draw(win, grid, ROWS, width), grid, start, end)
                    #lambda is anonymus function

                #reset the game again and again
                if event.key == pygame.K_c:
                    start= None
                    end = None
                    grid = make_grid(ROWS, width)


    pygame.quit() #exist the pygame window

main(WIN, WIDTH)

#PS- barrier are not the neighbors, to spread out neighbors should have white space, if you cicrle out with barrier, inside the barrier, white spot are useless


