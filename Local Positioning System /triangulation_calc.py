__author__ = 'alanyuen'
import pygame, sys, math, random
import numpy as np
from pygame.locals import*

##INITIALIZING PYGAME/WINDOW
pygame.init()
pygame.display.set_caption("")

SCREEN = pygame.display.set_mode((500,500))
fpsClock =  pygame.time.Clock()

def refreshSurfaces():
        SCREEN.fill((0,0,0))

class Beacon:
    def __init__(self, _pos):
        self.pos = _pos
        self.signal_radius = 300 #feet

    def getDist(self,pos):
        return (math.sqrt((self.pos[0] - pos[0])**2 + (self.pos[1] - pos[1])**2))

    def transmit(self, pos):
        distance = min(self.getDist(pos),self.signal_radius)
        #interpolate between 0-300 feet
        signal_strength =  (300.0 - distance)/300.0
        return signal_strength

class Bender:
    def __init__(self):
        self.pos = [137,150]

    def intersectOfLines(self, line1, line2):
        a1 = line1[0]
        b1 = line1[1]
        c1 = line1[2]

        a2 = line2[0]
        b2 = line2[1]
        c2 = line2[2]


        if a1*b2 == a2*b1:
            return None

        a = np.array ( ( (a1, b1), (a2, b2) ) )
        b = np.array ( (-c1, -c2) )
        x, y = np.linalg.solve(a,b)

        return [x, y]

    def listen(self, beacons):
        signal_strengths = [b.transmit(self.pos) for b in beacons]

        r = [300.0*(1.0-ss) for ss in signal_strengths]
        print r
        x = [beacons[0].pos[0],beacons[1].pos[0],beacons[2].pos[0],beacons[3].pos[0]]
        y = [beacons[0].pos[1],beacons[1].pos[1],beacons[2].pos[1],beacons[3].pos[1]]
        print (x)
        print (y)
        #ax + by + c = 0

        a_1 = (x[0] - x[1]) * 2.0
        b_1 = (y[0] - y[1]) * 2.0
        c_1 = (r[0]**2 - r[1]**2 - x[0]**2 + x[1]**2 - y[0]**2 + y[1]**2)
        a_2 = (x[1] - x[2]) * 2.0
        b_2 = (y[1] - y[2]) * 2.0
        c_2 = (r[1]**2 - r[2]**2 - x[1]**2 + x[2]**2 - y[1]**2 + y[2]**2)

        return self.intersectOfLines([a_1,b_1,c_1],[a_2,b_2,c_2])

beacons = [Beacon([0,0]),Beacon([200,0]),Beacon([0,200]),Beacon([200,200])]
robot = Bender()
print(robot.listen(beacons))
############################################################################
#                              PYGAME STUFF                                #
############################################################################
while True:
    for b in beacons:
        pygame.draw.circle(SCREEN, (255,255,255), [int(b.pos[0]),int(b.pos[1])], int(b.getDist(robot.pos)), 2)
    for event in pygame.event.get():
        if event.type == QUIT:
                pygame.quit()
                sys.exit()

    pygame.display.update()
    fpsClock.tick(60)