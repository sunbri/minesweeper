import pygame
from pygame.locals import *
import sys
import time
import random
import data
import os
import pickle

# GLOBALS (Sorry, Stan!)
BUFFER = 100
GRID_ROWS = int(sys.argv[1])
GRID_COLS = int(sys.argv[2])
S_SIZE = 20
SCREEN_ROWS = GRID_ROWS * S_SIZE + BUFFER
SCREEN_COLS = GRID_COLS * S_SIZE

# Creates a file with the specified name and extension and adds a different one if it already exists
def create_file(name, ext):
    if not os.path.exists(name + ext):
        return name + ext
    else:
        i = 1
        while True:
            if not os.path.exists('{0}_{1}'.format(name, i) + ext):
                return '{0}_{1}'.format(name, i) + ext
            i += 1

# Loads an image
def load_image(img):
    try:
        surface = pygame.image.load(img)
    except pygame.error:
        raise SystemExit('Could not load image "%s" "%s'%(img, pygame.get_error()))
    return surface.convert_alpha()

# Loads a list of images
def load_images(*imgs):
    images = []
    for img in imgs:
        images.append(load_image(img))
    return images

# Class for each square
class Square(pygame.sprite.Sprite):
    def __init__(self, image, x, y, ID):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.ID = ID

# Returns neighbors of vals[r][c] irreflexive
def get_neighbors(r, c, vals, ring):

    # Gets neighbors in a ring
    n = range(-ring, ring + 1)
    neighbors = [(a, b) for a in n for b in n]

    # Remove the original point
    neighbors.remove((0, 0))

    #neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    res = []
    for v in neighbors:
        if (r+v[0] >= 0 and r+v[0] < len(vals) and c+v[1] >= 0 and c+v[1] < len(vals[0])):
            res.append(vals[r + v[0]][c + v[1]])
        else:
            res.append(None)
    return res


def main():

    ##############################################################################
    #              TEMPORARY FOR GATHERING TRAINING AND TESTING DATA             #
    ##############################################################################
    data = []
    labels = []

    # Initialize the pygame module
    pygame.init()

    # Initialize font
    pygame.font.init()
    font = pygame.font.SysFont('helvetica', 20)

    # Set title of screen
    pygame.display.set_caption('Minesweeper Solver')

    # Create a surface 
    screen = pygame.display.set_mode((SCREEN_COLS, SCREEN_ROWS))

    # Game clock
    clock = pygame.time.Clock()

    # Load up num images
    nums = load_images('blank.png', 'one.png', 'two.png', 'three.png', 'four.png', 'five.png', 'six.png', 'seven.png', 'eight.png', 'mine.png', 'block.png', 'flag.png')
    highlight = load_image('highlight.png')
    
    # Loop variable
    running = True

    # Game groups
    all = pygame.sprite.RenderUpdates()
    Square.containers = all

    # Generate the initial values (-1 for nothing so far)
    vals = []

    # Generate initial grid of Squares
    grid = [[Square(nums[10], j*S_SIZE, i*S_SIZE, 10) for j in range(GRID_COLS)] for i in range(GRID_ROWS)]

    # Neighbor dict
    neighbor_dict = {
        8: [],
        7: [],
        6: [],
        5: [],
        4: [],
        3: [],
        2: [],
        1: [],
        0: []
    }

    # Recalculates the neighbors - yes, this is very slow
    def calculate_neighbors():

        # Clear dict before use again
        for key in neighbor_dict:
            neighbor_dict[key] = []

        # Update the matrix of open neighbors
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                # Only calculate for unclicked blocks
                if(grid[r][c].ID == 10):
                    grid[r][c].neighbors = sum(p != None and p.ID != 10 for p in get_neighbors(r, c, grid, 1))
                    neighbor_dict[grid[r][c].neighbors].append((r, c))

    # Flood fill to empty out blanks
    def floodfill(r_pos, c_pos):
        if (r_pos < 0 or r_pos >= GRID_ROWS or c_pos < 0 or c_pos >= GRID_COLS):
            return

        if (vals[r_pos][c_pos] == 0 and grid[r_pos][c_pos].ID != 0):
            grid[r_pos][c_pos].image = nums[0]
            grid[r_pos][c_pos].ID = 0
        else:
            grid[r_pos][c_pos].image = nums[vals[r_pos][c_pos]]
            grid[r_pos][c_pos].ID = vals[r_pos][c_pos]
            return
        
        floodfill(r_pos + 1, c_pos)
        floodfill(r_pos - 1, c_pos)
        floodfill(r_pos, c_pos + 1)
        floodfill(r_pos, c_pos - 1)
        floodfill(r_pos - 1, c_pos - 1)
        floodfill(r_pos + 1, c_pos - 1)
        floodfill(r_pos - 1, c_pos + 1)
        floodfill(r_pos + 1, c_pos + 1)

    # Boolean for whether can click or not
    lost = False

    # Flag to generate the board on the first click
    started = False

    # Number of mines
    mines = -1

    # Random beginning for click
    rand_row = random.randint(0, GRID_ROWS - 1)
    rand_col = random.randint(0, GRID_COLS - 1)
    
    # Game loop
    while running:

        # Parse quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Generate the board - only the vals need to be generated?
        if not started:

            # Quite possibly the worst way to generate a working board, but whatever
            while True:

                # Reset the vals array
                vals = [[0 for j in range(GRID_COLS)] for i in range(GRID_ROWS)]

                # Plants the mines
                mines = 0
                for i in range(GRID_ROWS):
                    for j in range(GRID_COLS):
                        if (random.uniform(0, 1) > 0.8):
                            vals[i][j] = 9
                            mines += 1
                
                # Gets the values for the future, no need to bound check
                def get_vals(r, c):
                    if r < 0 or c < 0 or r >= GRID_ROWS or c >= GRID_COLS:
                        return 0
                    return vals[r][c]

                # Plants the numbers around the mines
                for i in range(GRID_ROWS):
                    for j in range(GRID_COLS):
                        if (vals[i][j] == 9): continue
                        numMines = 0
                        if (get_vals(i+1, j+1) == 9): numMines += 1
                        if (get_vals(i+1, j-1) == 9): numMines += 1
                        if (get_vals(i+1, j) == 9): numMines += 1
                        if (get_vals(i-1, j+1) == 9): numMines += 1
                        if (get_vals(i-1, j-1) == 9): numMines += 1
                        if (get_vals(i-1, j) == 9): numMines += 1
                        if (get_vals(i, j+1) == 9): numMines += 1
                        if (get_vals(i ,j-1) == 9): numMines += 1
                        vals[i][j] = numMines

                # Fail condition
                if (vals[rand_row][rand_col] == 0):
                    started = True

                    # Click the spot
                    grid[rand_row][rand_col].ID = 0
                    grid[rand_row][rand_col].image = nums[0]
                    floodfill(rand_row, rand_col)

                    calculate_neighbors()
                    break
                else:
                    # Reset the mines
                    mines = 0

 
        ##############################################################################
        #              TEMPORARY FOR GATHERING TRAINING AND TESTING DATA             #
        ##############################################################################
        # Get move from AI starting with the place with the most neighbors
        # Using the neighbor_dict, we can extract data from the game into an object and
        # pickle the data
        # We train on those images since that is the algorithm that the deep net is going
        # to learn how to play with
        for key in neighbor_dict:
            # Neighbor dict should only contain those with ID = 10 (block)
            if len(neighbor_dict[key]) > 0:

                # Clear the current square from the dictionary
                curr = neighbor_dict[key][0]
                neighbor_dict[key].remove(curr)

                # If it was a mine, change it to a flag
                value = vals[curr[0]][curr[1]] 
                if value == 9:
                    # Reduce the number of mines by 1
                    mines -= 1
                    vals[curr[0]][curr[1]] = 11

                # Put stuff into lists
                data.append([s.ID if s != None else -1 for s in get_neighbors(curr[0], curr[1], grid, 2)])
                labels.append(vals[curr[0]][curr[1]])

                # Floodfill it out
                if vals[curr[0]][curr[1]] == 0:
                    floodfill(curr[0], curr[1])
                else:
                    grid[curr[0]][curr[1]].ID = vals[curr[0]][curr[1]] 
                    grid[curr[0]][curr[1]].image = nums[vals[curr[0]][curr[1]]]
                            
                calculate_neighbors()
                break

        # End stuff 
        if mines == 0:
            pickle.dump(data, open(create_file('data_data/data/data', '.p'), "wb"))
            pickle.dump(labels, open(create_file('data_data/labels/labels', '.p'), "wb"))
            running = False

        # Fill the screen
        screen.fill((0, 0, 0))

        # Draw the scene by blitting everything on 
        all.draw(screen)

        # Highlight for mouse
        col, row = pygame.mouse.get_pos()
        r_mouse = row // S_SIZE * S_SIZE
        c_mouse = col // S_SIZE * S_SIZE
        if (not lost and r_mouse >= 0 and r_mouse < SCREEN_ROWS - BUFFER and c_mouse >= 0 and c_mouse < SCREEN_COLS and 
                grid[r_mouse//S_SIZE][c_mouse//S_SIZE].ID == 10):
            screen.blit(highlight, (c_mouse, r_mouse))

        # Display text if lost
        if (lost):
            text = 'You lose, ya idiot!'
            screen.blit(font.render(text, False, (255, 255, 255)), (SCREEN_COLS / 2 - font.size(text)[0] / 2, SCREEN_ROWS - BUFFER / 2 - font.size(text)[1] / 2))

        # Update the display
        pygame.display.update()

        # Framerate
        dt = clock.tick(80) / 1000

# Run if only module being run
if __name__ == "__main__":
    main()
