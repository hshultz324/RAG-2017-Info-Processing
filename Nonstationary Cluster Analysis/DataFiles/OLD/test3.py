__author__ = 'alanyuen'
import pygame, sys, math, random, time
import numpy as np
from pygame.locals import*

############################################################################
## ** GRAPHICAL INTERFACE **                                               #
############################################################################
##INITIALIZING PYGAME/WINDOW
pygame.init()
pygame.display.set_caption("Tanks")
SCREEN = pygame.display.set_mode((600,600))
GRID_SURFACE = pygame.Surface((600,600))
fpsClock =  pygame.time.Clock()

### DIMENSION CONSTANTS ###
MAP_SIZE_MM = [12000, 12000] #12m x 12m
CELL_SIZE_MM = [300,300] #0.3m x 0.3m

DRAW_MAP_SIZE = [MAP_SIZE_MM[0]/20,MAP_SIZE_MM[1]/20]
CELL_DRAW_SIZE = [CELL_SIZE_MM[0]/20,CELL_SIZE_MM[1]/20]

# DRAWING FUNCTIONS
def drawGrid():
        for i in range(40):
            start_pt = (0,i*CELL_DRAW_SIZE[1])
            end_pt = (DRAW_MAP_SIZE[0],i*CELL_DRAW_SIZE[1])
            pygame.draw.line(GRID_SURFACE, (255,255,255), start_pt, end_pt, 1)

        for i in range(40):
            start_pt = (i*CELL_DRAW_SIZE[0],0)
            end_pt = (i*CELL_DRAW_SIZE[0],DRAW_MAP_SIZE[1])
            pygame.draw.line(GRID_SURFACE, (255,255,255), start_pt, end_pt, 1)
            
        GRID_SURFACE.set_alpha(30)
        SCREEN.blit(GRID_SURFACE,(0,0))

def drawPoint(pos, color = (255,0,0)):
        pygame.draw.circle(SCREEN, color, pos, 1)

def refreshSurfaces():
        SCREEN.fill((0,0,0))
        GRID_SURFACE.fill((3,3,3))
        GRID_SURFACE.set_colorkey((3,3,3))
############################################################################




############################################################################
#                                 MAGIC                                    #
############################################################################
#Retrieves data from txt files and converts into x,y points
class DataManager:
    def __init__(self, data_directory_file):
        self.data_files = open(data_directory_file).read().splitlines()
        self.data_file_counter = 0
        self.points = []
        self.DEG_TO_PI = math.pi/180.0
        self.MIN_QUALITY = 12

    def changeDirectoryFile(data_directory_file):
        self.data_files = open(data_directory_file).read().splitlines()
        self.data_file_counter = 0
        del points[:]

    def getPointsFromFile(file, nextFile = 0, delimiter = " "):

        if(self.data_file_counter + nextFile >= len(self.data_files) or self.data_file_counter + nextFile < 0):
                return None
        self.data_file_counter += nextFile

        del self.points[:]

        with open(self.data_files[self.data_file_counter]) as f:
            data = f.readlines()

        for line in data:
            words = line.split(delimiter)

            #if distance is less than half a meter or quality is lower than min, pass
            if(float(words[0]) < 500 or float(words[2]) < self.MIN_QUALITY):
                    continue 

            #translates polar to cartesian
            x = float(words[0])*math.cos(float(words[1]) * self.DEG_TO_PI)
            y = float(words[0])*math.sin(float(words[1]) * self.DEG_TO_PI)

            #translate 6m from center to corner
            point = [x + 6000,y + 6000] 
            self.points.append(point)

        return points

#holds points
class Point:
    def __init__(self, pos, qual, orig = []):
        #point data
        self.coord = pos
        self.quality = qual
        self.origin = orig

        #flags
        self.visited = False
        self.inCluster = False

        #id
        self.classification = "" #CORE, REACHABLE, NOISE
        self.cluster = "" #cluster name

    def getDistanceFrom(self, pos):
        return math.sqrt((self.coord[0] - pos[0])**2 + (self.coord[1] - pos[1])**2)
#holds points in groups ID'd by DBSCAN
class Cluster:
    def __init__(self, _name):
        self.name = _name
        self.points = []

    def addPoint(self, p):
        self.points.append(p)
#Density-based spatial clustering of applications with noise
class DBSCAN:

    def __init__(self, mpts = 5, eps = 175):
        self.minPts = mpts
        self.epsilon = eps

        self.clusters = []
        self.cluster_count = 0

        self.points = []
        self.noise = []
        
    def initPoints(self, arr_points):
        for p in arr_points:
            self.points.append(Point(p))

    #if you want to change the settings, call these before DBSCAN_RESET()
    def changeEps(self, change_val):
        self.epsilon += change_val
    def changeMinPts(self, change_val):
        self.minPts += change_val

    #resets DBSCAN for new analysis when you change data points or settings
    def RESET(self, points = None):
        del self.clusters[:]
        del self.points[:]
        del self.noise[:]

        if(arr_points):
            self.initPoints(arr_points)

        self.analyze()
        print("num clusters - " + str(len(self.clusters)))
        print("eps: " + str(self.epsilon) + " ... minPts: " + str(self.minPts))

    #returns cluster obj
    def findCluster(self, _name):
        for c in self.clusters:
            if(c.name == _name):
                return c
        return None

    #returns the list of points within eps distance
    def queryRegion(self, p):
        neighbors = []
        for neighbor in self.points:
            if(neighbor == p):
                continue
            if(p.getDistanceFrom(neighbor.coord) < self.epsilon):
                neighbors.append(neighbor)
        return neighbors
    #called on intial core points to expand the cluster
    def expandCluster(self, p, neighbors, cluster):
        #adds p to cluster
        cluster.addPoint(p)
        p.cluster = cluster.name
        p.inCluster = True

        #looks at neighbors for potential density-reachable core points
        for neighbor in neighbors:
            if not neighbor.visited:
                neighbor.visited = True

                n_neighbors = self.queryRegion(neighbor)
                if(len(n_neighbors) > self.minPts):
                    #mark neighbor as core
                    #add the neighbor's neighbors onto the list of pending points to check
                    neighbor.classification = "CORE"
                    neighbors += n_neighbors
                else:
                    self.noise.append(neighbor)
                    neighbor.classification = "NOISE"
            
            if not neighbor.inCluster:
                #mark point in cluster
    #uses queryRegion and expandCluster to identify dense regions of points as clusters
    def analyze(self):
        #A: look for core points
        for p in self.points:
            if p.visited:
                continue
            p.visited = True

            neighbors = self.queryRegion(p)
            if(len(neighbors) < self.minPts):
                #mark noise temporarily
                self.noise.append(p)
                p.classification = "NOISE"
            else:
                #mark core points
                c = Cluster("cluster_"+str(self.cluster_count))
                self.cluster_count += 1
                p.classification = "CORE"
                self.expandCluster(p, neighbors, c)

        #B: reiterate and look for reachable points in noise
        new_noise = []
        for p in self.noise:
            for neighbor in self.queryRegion(p):
                if(neighbor.classification == "CORE"):
                    #if this point is reachable, then add to the cluster
                    p.classification = "REACHABLE"
                    c = self.findCluster(neighbor.cluster)
                    c.addPoint(p)
                    break
            if p.classification == "NOISE":
                new_noise.append(p)
        self.noise = new_noise



                cluster.addPoint(neighbor)
                neighbor.cluster = cluster.name
                neighbor.inCluster = True

        self.clusters.append(cluster)


DATA = DataManager("RadiusDataFiles.txt")

DBSCAN_obj = DBSCAN()
DBSCAN_obj.RESET(DATA.getPointsFromFile("/t/t"))
############################################################################




############################################################################
## ** GRAPHICAL INTERFACE **                                               #
############################################################################
while True:
        refreshSurfaces()
        drawGrid()

        #***
        for pt in DBSCAN_obj.noise:
            drawPoint([int(pt.coord[0]/20),int(pt.coord[1]/20)], (50,50,50))

        for c in DBSCAN_obj.clusters:
            for pt in c.points:
                n_c = [255,0,0]
                if pt.classification == "CORE":
                    n_c[2] = 255
                drawPoint([int(pt.coord[0]/20),int(pt.coord[1]/20)], n_c)
        #***

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
                if event.key == K_LEFTBRACKET:
                        DBSCAN_obj.DBSCAN_RESET(DATA.getPointsFromFile(-1, "/t/t"))
                elif event.key == K_RIGHTBRACKET:
                        DBSCAN_obj.DBSCAN_RESET(DATA.getPointsFromFile(1, "/t/t"))

                #up/down arrow: changes eps value
                #left/right arrow: changes minPts value
                if event.key == K_UP:
                    DBSCAN_obj.changeEps(change_val)
                    DBSCAN_obj.DBSCAN_RESET()
                elif event.key == K_DOWN:
                    DBSCAN_obj.changeEps(-1*change_val)
                    DBSCAN_obj.DBSCAN_RESET()
                elif event.key == K_LEFT:
                    DBSCAN_obj.changeMinPts(-1*change_val)
                    DBSCAN_obj.DBSCAN_RESET()
                elif event.key == K_RIGHT:
                    DBSCAN_obj.changeMinPts(1*change_val)
                    DBSCAN_obj.DBSCAN_RESET()

        pygame.display.update()
        fpsClock.tick(60)

