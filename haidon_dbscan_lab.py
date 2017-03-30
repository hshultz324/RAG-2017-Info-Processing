import pygame, sys, math, random, time, dbscan, constants
from pygame.locals import*
from dbscan import*
from constants import*

"""
***dbscan_obj.normalize ==> True to normalize points, False to see raw points
"""

#determines whether the DBSCAN lab opens files written in DATA_LIST_FILE_NAME or whether to pick individual data files
MULTIPLE_FILES = True
DATA_LIST_FILE_NAME = ["DataFiles/List_Of_Files.txt"]
LIST_FILE_ID = 0
DATA_TEXT_FILE_NAME = ["DataFiles/new_data/Control/Radius/CONTROLR_5B_3M_6S_QT_10_t1.txt", "DataFiles/test3.txt"]
TEXT_FILE_ID = 0
DELIM = ["\t\t", " ", ","] 
DELIM_ID = 0 #**make sure you match delimiter with what files you're anaylzing

#Creates DataManager class that parses data files and stores them in as point objects
DATA = DataManager(DATA_LIST_FILE_NAME[LIST_FILE_ID])

#choose between initializing the DataManager with a single and series of files
if MULTIPLE_FILES:
    fileData = DATA.getPointsFromFile(delimiter = DELIM[DELIM_ID])
else:
    fileData = DATA.getPointsFromFile(single_file = DATA_TEXT_FILE_NAME[TEXT_FILE_ID], delimiter = DELIM[DELIM_ID])


#ms per frame
resolution = 500
#playback speed
speed = 5

index = 0;
dataPoints = []

for i in range(0,20000/resolution):
   dataPoints.append([])

for p in fileData:
    dataPoints[int(p[2]/resolution)].append(p)


############################################################################
## ** GRAPHICAL INTERFACE **                                               #
############################################################################
##INITIALIZING PYGAME/WINDOW
pygame.init()
pygame.display.set_caption("DBSCAN")

screen = pygame.display.set_mode((WINDOW_SIZE[0],WINDOW_SIZE[1]))
grid_surface = pygame.Surface((WINDOW_SIZE[0],WINDOW_SIZE[1]))
annot_surface = pygame.Surface((WINDOW_SIZE[0],WINDOW_SIZE[1]))

fpsClock =  pygame.time.Clock()

DRAW_MAP_SIZE = [MAP_SIZE_MM[0]/MM_PXL[0],MAP_SIZE_MM[1]/MM_PXL[1]]
CELL_DRAW_SIZE = [CELL_SIZE_MM[0]/MM_PXL[0],CELL_SIZE_MM[1]/MM_PXL[1]]

# DRAWING FUNCTIONS
def drawGrid():
    for i in range(MAP_SIZE_MM[0]/CELL_SIZE_MM[0]):
        start_pt = (0,i*CELL_DRAW_SIZE[1])
        end_pt = (DRAW_MAP_SIZE[0],i*CELL_DRAW_SIZE[1])
        pygame.draw.line(grid_surface, (255,255,255), start_pt, end_pt, 1)

    for i in range(MAP_SIZE_MM[1]/CELL_SIZE_MM[1]):
        start_pt = (i*CELL_DRAW_SIZE[0],0)
        end_pt = (i*CELL_DRAW_SIZE[0],DRAW_MAP_SIZE[1])
        pygame.draw.line(grid_surface, (255,255,255), start_pt, end_pt, 1)

    grid_surface.set_alpha(30)
    screen.blit(grid_surface,(0,0))

def drawPoint(pos, color = (255,0,0)):
    pygame.draw.circle(screen, color, pos, POINT_DRAW_SIZE)

def drawRect(rect, color = (255,255,255)):
    pygame.draw.rect(annot_surface, color, rect, RECT_STROKE_WIDTH)
    annot_surface.set_alpha(100)
    screen.blit(annot_surface,(0,0))

def refreshSurfaces():
        screen.fill((0,0,0))
        grid_surface.fill((1,1,1))
        grid_surface.set_colorkey((1,1,1))
        annot_surface.fill((1,1,1))
        annot_surface.set_colorkey((1,1,1))

############################################################################

while True:
        refreshSurfaces()
        drawGrid()

        #*** DRAWING POINTS ***#
        for pt, quality, timestamp in dataPoints[index]:
            drawPoint([int(pt[0]/MM_PXL[0]),int(pt[1]/MM_PXL[1])], (255,255,255))
        #**********************#

        keys = pygame.key.get_pressed()
        if keys[K_SPACE]:
            change_val = 5
        else:
            change_val = 1

        for event in pygame.event.get():
            if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            if event.type == KEYDOWN:
                #[: previous file
                #]: next file
                """if event.key == K_LEFTBRACKET:
                    if MULTIPLE_FILES:
                        index = index-1
                        print(index)
                elif event.key == K_RIGHTBRACKET:
                    if MULTIPLE_FILES:
                        index = index+1
                        print(index)"""
                if event.key == K_LEFT:
                    index = 0
                    fileData = DATA.getPointsFromFile(-1, DELIM[DELIM_ID])
                    dataPoints = []
                    
                    for i in range(0,20000/resolution):
                        dataPoints.append([])

                    for p in fileData:
                        dataPoints[int(p[2]/resolution)].append(p)
                elif event.key == K_RIGHT:
                    index = 0
                    fileData = DATA.getPointsFromFile(1, DELIM[DELIM_ID])
                    dataPoints = []
                    
                    for i in range(0,20000/resolution):
                        dataPoints.append([])
                    
                    for p in fileData:
                        dataPoints[int(p[2]/resolution)].append(p)

        index = index + 1
        if index>=(20000/resolution):
            index = 0
        
        pygame.display.update()
        fpsClock.tick(speed)
