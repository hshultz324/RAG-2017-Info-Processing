__author__ = 'alanyuen'
import pygame, sys, math, random
import numpy as np
from pygame.locals import*

def sort(array, key = 1):
        less = []
        equal = []
        greater = []

        if len(array) > 1:
                pivot = array[0][key]
                for x in array:
                        if x[key] < pivot:
                                less.append(x)
                        if x[key] == pivot:
                                equal.append(x)
                        if x[key] > pivot:
                                greater.append(x)
                                
                return sort(less)+equal+sort(greater)
        else: 
                return array

############################################################################
# EXTRACTING [X,Y] POINTS FROM DATA
############################################################################

#1B_4M_3S_QT_12_t3.txt
with open("1B_5M_3S_QT_12_t1.txt") as f:
        data = f.readlines()

points = []
for line in data:
        words = line.split(" ")
        if(float(words[0]) < 400):
                continue 
        point = [float(words[0])*math.cos(float(words[1])* math.pi / 180.0),float(words[0])*math.sin(float(words[1]) * math.pi / 180.0)]
        point[0] += 6000 #translate 6m
        point[1] += 6000 #translate 6m
        points.append(point)
############################################################################

############################################################################
# CELL WORK / GRID
############################################################################
class Cell:
    #Cell coordinates are 1 unit per 300 mm
        def __init__(self, coord):
                self.points =[]
                self.cell_coord = coord
                self.cell_size = [0,0]
                self.S_D = 0

        def addPoint(self, pos):
                self.points.append(pos)

        def getDensity(self):
                return len(self.points)

        def getPointsContainer(self):
            #get min_x
            min_x = self.points[0][0]
            for point in self.points:
                min_x = min(min_x, point[0])
            #get min_y
            min_y = self.points[0][1]
            for point in self.points:
                min_y = min(min_y, point[1])
            #get max_x
            max_x = self.points[0][0]
            for point in self.points:
                max_x = max(max_x, point[0])
            #get max_y
            max_y = self.points[0][1]
            for point in self.points:
                max_y = max(max_y, point[1])

            return [min_x, min_y, max_x - min_x, max_y - min_y]


def findGrouping(cells, density):
    best_points = 0
    direction = 0 #0 - topleft, 1 - topright, 2 - bottomleft, 3 - bottomright

    t_cell_coord = density[0] #cell x,y
    total_points = cells[t_cell_coord[0]][t_cell_coord[1]].getDensity()
    group = [t_cell_coord]
    #check top left
    if(t_cell_coord[0] >= 1 and t_cell_coord[1] >= 1):
        total_points += cells[t_cell_coord[0]-1][t_cell_coord[1]].getDensity()
        total_points += cells[t_cell_coord[0]-1][t_cell_coord[1]-1].getDensity()
        total_points += cells[t_cell_coord[0]][t_cell_coord[1]-1].getDensity()

    if(total_points > best_points):
        best_points = total_points
        direction = 0

    total_points = cells[t_cell_coord[0]][t_cell_coord[1]].getDensity()

    #check top right
    if(t_cell_coord[0] <= 39 and t_cell_coord[1] >= 1):
        total_points += cells[t_cell_coord[0]+1][t_cell_coord[1]].getDensity()
        total_points += cells[t_cell_coord[0]+1][t_cell_coord[1]-1].getDensity()
        total_points += cells[t_cell_coord[0]][t_cell_coord[1]-1].getDensity()

    if(total_points > best_points):
        best_points = total_points
        direction = 1

    total_points = cells[t_cell_coord[0]][t_cell_coord[1]].getDensity()
    #check bottom left
    if(t_cell_coord[0] >= 1 and t_cell_coord[1] <= 39):
        total_points += cells[t_cell_coord[0]-1][t_cell_coord[1]].getDensity()
        total_points += cells[t_cell_coord[0]-1][t_cell_coord[1]+1].getDensity()
        total_points += cells[t_cell_coord[0]][t_cell_coord[1]+1].getDensity()

    if(total_points > best_points):
        best_points = total_points
        direction = 2

    total_points = cells[t_cell_coord[0]][t_cell_coord[1]].getDensity()
    #check bottom right
    if(t_cell_coord[0] <= 39 and t_cell_coord[1] <= 39):
        total_points += cells[t_cell_coord[0]+1][t_cell_coord[1]].getDensity()
        total_points += cells[t_cell_coord[0]+1][t_cell_coord[1]+1].getDensity()
        total_points += cells[t_cell_coord[0]][t_cell_coord[1]+1].getDensity()

    if(total_points > best_points):
        best_points = total_points
        direction = 3

    if(direction == 0):
        group.append([t_cell_coord[0]-1,t_cell_coord[1]])
        group.append([t_cell_coord[0]-1,t_cell_coord[1]-1])
        group.append([t_cell_coord[0],t_cell_coord[1]-1])
    elif(direction == 1):
        group.append([t_cell_coord[0]+1,t_cell_coord[1]])
        group.append([t_cell_coord[0]+1,t_cell_coord[1]-1])
        group.append([t_cell_coord[0],t_cell_coord[1]-1])
    elif(direction == 2):
        group.append([t_cell_coord[0]-1,t_cell_coord[1]])
        group.append([t_cell_coord[0]-1,t_cell_coord[1]+1])
        group.append([t_cell_coord[0],t_cell_coord[1]+1])
    else:
        group.append([t_cell_coord[0]+1,t_cell_coord[1]])
        group.append([t_cell_coord[0]+1,t_cell_coord[1]+1])
        group.append([t_cell_coord[0],t_cell_coord[1]+1])

    return group

    ### with best direction, group all points into one cell
def findOverlap(cluster, unique_clusters):
    for i in range(len(unique_clusters)):
        for c in unique_clusters[i]:
            #print("cluster.cell_coord: [" + str(cluster.cell_coord[0]) + ", " + str(cluster.cell_coord[1]) + " ]")
            #print("c.cell_coord: [" + str(c.cell_coord[0]) + ", " + str(c.cell_coord[1]) + " ]")
            
            l1 = cluster.cell_coord
            r1 = [cluster.cell_coord[0] + cluster.cell_size[0], cluster.cell_coord[1] + cluster.cell_size[1]]
            l2 = c.cell_coord
            r2 = [c.cell_coord[0] + c.cell_size[0], c.cell_coord[1] + c.cell_size[1]]
            #print("[" +str(l1) +"," + str(r1) + "]")
            #print("[" +str(l2) +"," + str(r2) + "]")
            #print()
            isOverlap = not (l1[0] > r2[0] or l2[0] > r1[0] or l1[1] > r2[1] or l2[1] > r1[1])
            #print(isOverlap)
            if isOverlap:
                return i
    return -1

### GRID SIZES ###
MAP_SIZE_MM = [12000, 12000] #12m x 12m
CELL_SIZE_MM = [300,300] #0.3m x 0.3m

### GRID CELL INIT ###
cells = [[Cell([i,j]) for j in range(40)] for i in range(40)]
for point in points:
        cells[int(point[0]/300)][int(point[1]/300)].addPoint(point)


### CELL DENSITY FILL IN ###
densities = []
for c_row in cells:
        for c in c_row: 
                densities.append([(c.cell_coord[0],c.cell_coord[1]),c.getDensity()])
                
### SORT DENSITIES, FIND HIGHEST DENSITY CELLS ###
densities = sort(densities)
high_densities = []

total_densities = 0

for d in densities:
        if(d[1] < 2):
                continue
        high_densities.append(d)
        total_densities += d[1]
        #print(d)
#print("AVERAGE DENSITIES: " + str(total_densities/len(high_densities)))
### ########################################### ###

### GATHERING CELL NEIGHBORS ######
###################################
clusters = []
for d in high_densities:
    group = findGrouping(cells,d) #finds the cells to group
    cluster = Cell([None]) #none because we will find the specific x,y
    for coord in group:
        for point in cells[coord[0]][coord[1]].points:
            cluster.addPoint(point)

    cluster_rect = cluster.getPointsContainer()
    cluster.cell_coord = [cluster_rect[0]/300.0,cluster_rect[1]/300.0]
    cluster.cell_size = [cluster_rect[2]/300.0, cluster_rect[3]/300.0]

    clusters.append(cluster)
    #print(cluster.getDensity())
###################################


### FILTER OVERLAPPING CLUSTERS ###
###################################
#check for overlapping clusters and pick the best one
unique_clusters = [[clusters[0]]]
#indentify all the overlapping clusters
#start with first cluster, and insert into test_bank as an entry
#check 2nd one if cluster overlaps anything in the test_bank
    #if it does overlap with something in test_bank, add it into the entry
    #if not, create new entry and put that cluster in it
#repeat until no more clusters

for c in clusters[1:]:
    cluster_group = findOverlap(c,unique_clusters)
    if(cluster_group == -1):
        unique_clusters.append([c])
    else:
        unique_clusters[cluster_group].append(c)

#with each unique cluster, find the max of each one
singleton_unique_clusters = []

for u_q in unique_clusters:
    max_density = 0
    best_cluster_id = 0
    for i in range(len(u_q)):
        if(max_density < u_q[i].getDensity()):
            max_density = u_q[i].getDensity()
            best_cluster_id = i
    singleton_unique_clusters.append(u_q[best_cluster_id])
    #print(u_q[best_cluster_id].getDensity())

#print(len(singleton_unique_clusters))
#####################################

#### STANDARD DEVIATION PER U_Q ####
for u_q in singleton_unique_clusters:

    #center of U_Q
    center_pos = [0,0]
    for p in u_q.points:
        center_pos[0] += p[0]
        center_pos[1] += p[1]
    center_pos[0] /= len(u_q.points)
    center_pos[1] /= len(u_q.points)

    #every distance between p_i and center_pos
    #and calculate mean
    distances = []
    mean_distance = 0
    for p in u_q.points:
        distances.append(math.sqrt((p[0] - center_pos[0])**2 + (p[1] - center_pos[1])**2))
        mean_distance += distances[-1]
    mean_distance /= len(distances)

    #calculate variance
    variance = 0
    for d in distances:
        variance += (d - mean_distance)**2
    variance /= len(distances)

    #calculate standard deviation
    standard_deviation = math.sqrt(variance)
    u_q.S_D = standard_deviation
########################################

for u_c in singleton_unique_clusters:
    print("*")
    print("CLUSTER Pos: " + str(u_c.cell_coord))
    print("CLUSTER Density: " + str(u_c.getDensity()))
    print("CLUSTER Standard Deviation: " + str(u_c.S_D))
    print("*")







############################################################################
## ** GRAPHICAL INTERFACE ** 
############################################################################

##INITIALIZING PYGAME/WINDOW
pygame.init()
pygame.display.set_caption("Tanks")
SCREEN = pygame.display.set_mode((600,600))
GRID_SURFACE = pygame.Surface((600,600))
fpsClock =  pygame.time.Clock()
############################################################################

DRAW_MAP_SIZE = [MAP_SIZE_MM[0]/20,MAP_SIZE_MM[1]/20]
CELL_DRAW_SIZE = [CELL_SIZE_MM[0]/20,CELL_SIZE_MM[1]/20]

############################################################################
# DRAWING FUNCTIONS
############################################################################
def drawGrid():
        for i in range(40):
                pygame.draw.line(GRID_SURFACE, (255,255,255), (0,i*CELL_DRAW_SIZE[1]), (DRAW_MAP_SIZE[0],i*CELL_DRAW_SIZE[1]), 1)
        for i in range(40):
                pygame.draw.line(GRID_SURFACE, (255,255,255), (i*CELL_DRAW_SIZE[0],0), (i*CELL_DRAW_SIZE[0],DRAW_MAP_SIZE[1]), 1)
        GRID_SURFACE.set_alpha(30)
        SCREEN.blit(GRID_SURFACE,(0,0))

def drawPoint(pos):
        pygame.draw.circle(SCREEN, (255,0,0), pos, 1)

def highlightDensityCells(densities, rects):
        for i in range(len(rects)):
                rect = rects[i]
                if( i == len(densities) - 1):
                        color = (255,0,0)
                else:
                        color = (0,255,0)
                pygame.draw.rect(GRID_SURFACE, color , rect)
        
        GRID_SURFACE.set_alpha(100)
        SCREEN.blit(GRID_SURFACE,(0,0))

def highlightCell(rect):
        pygame.draw.rect(GRID_SURFACE, (255,255,255), rect)
        
        GRID_SURFACE.set_alpha(100)
        SCREEN.blit(GRID_SURFACE,(0,0))

def refreshSurfaces():
        SCREEN.fill((0,0,0))
        GRID_SURFACE.fill((3,3,3))
        GRID_SURFACE.set_colorkey((3,3,3))

def highlightClusters(clusters_arg):
    for i in range(len(clusters_arg)):
        #print("cluster size: [" + str(clusters_arg[i].cell_size[0]) + "," +str(clusters_arg[i].cell_size[1]) + "]")
        rect = [0,0,0,0]
        rect[0] = int(clusters_arg[i].cell_coord[0]*CELL_DRAW_SIZE[0])
        rect[1] = int(clusters_arg[i].cell_coord[1]*CELL_DRAW_SIZE[1])
        rect[2] = int(clusters_arg[i].cell_size[0]*CELL_DRAW_SIZE[0])
        rect[3] = int(clusters_arg[i].cell_size[1]*CELL_DRAW_SIZE[1])
        #print("["+ str(i) + "]: AREA - " + str(rect[2]*rect[3]))
        color = (0,255,0)
        pygame.draw.rect(GRID_SURFACE, color, rect)
    GRID_SURFACE.set_alpha(55)
    SCREEN.blit(GRID_SURFACE,(0,0))
############################################################################
############################################################################

while True:
        
        refreshSurfaces()
        drawGrid()

        ########## TOP DENSE CELLS ##########
        density_rects = []
        density_colors = []
        for dense in high_densities:
                density_rects.append([dense[0][0]*CELL_DRAW_SIZE[0], dense[0][1]*CELL_DRAW_SIZE[1], CELL_DRAW_SIZE[0],CELL_DRAW_SIZE[1]])
        #highlightDensityCells(high_densities, density_rects)
        #####################################

        ########## POINTS DISPLAY ##########
        for point in points:
                drawPoint([int(point[0]/20),int(point[1]/20)])
        ####################################

        ########### HIGHLIGHTING CLUSTERS ####
        highlightClusters(singleton_unique_clusters)
        ######################################

        ######### MOUSE INFO DISPLAY ##########
        if pygame.mouse.get_pressed()==(1,0,0):
            mouse_pos = pygame.mouse.get_pos()
            mouse_rect =[int(mouse_pos[0]/CELL_DRAW_SIZE[0]),int(mouse_pos[1]/CELL_DRAW_SIZE[1]),CELL_DRAW_SIZE[0],CELL_DRAW_SIZE[1]]
            print("[" + str(mouse_rect[0])+ "," + str(mouse_rect[1]) + "] Density: " + str(cells[mouse_rect[0]][mouse_rect[1]].getDensity()))
        #######################################
        

        for event in pygame.event.get():
                if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
        pygame.display.update()
        fpsClock.tick(60)

