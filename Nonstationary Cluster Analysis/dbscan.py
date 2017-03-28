import sys, math, random, constants, copy
from constants import*

############################################################################
#                                DBSCAN                                    #
############################################################################
# CLASSES:
#           -DataManager, Point, Cluster, DBSCAN, FCAnal
############################################################################

#Retrieves data from txt files and converts into x,y points
class DataManager:
    def __init__(self, data_directory_file):
        self.data_files = open(data_directory_file).read().splitlines()
        self.data_file_counter = 0

        self.points = []
        
        #filter low quality points
        self.MIN_QUALITY = 13

        #const used in polar-cartesian translations
        self.DEG_TO_PI = math.pi/180.0

    def changeDirectoryFile(self, data_directory_file):
        self.data_files = open(data_directory_file).read().splitlines()
        self.data_file_counter = 0
        del points[:]

    #returns points generated from data
    def getPointsFromFile(self, nextFile = 0, delimiter = " ", single_file = ""):
        if single_file != "":
            file_name = single_file
            print("Extracting data from: " + file_name)
        else:
            if(self.data_file_counter + nextFile >= len(self.data_files) or self.data_file_counter + nextFile < 0):
                return None
            self.data_file_counter += nextFile
            file_name = self.data_files[self.data_file_counter]
            print("Extracting data from: " + file_name)

        del self.points[:]

        with open(file_name) as f:
            data = f.readlines()
            
        for line in data:
            words = line.split(delimiter)#words: [ms, mm, deg, quality]

            quality = float(words[3])
            timestamp = float(words[0])
            #if distance is less than half a meter or quality is lower than min, pass
            if quality < self.MIN_QUALITY:
                    continue

            #translates polar to cartesian
            x = float(words[1])*math.cos(float(words[2]) * self.DEG_TO_PI)
            y = float(words[1])*math.sin(float(words[2]) * self.DEG_TO_PI)
            
            #translate 6m from center to corner
            point = [x + (MAP_SIZE_MM[0]/2),y + (MAP_SIZE_MM[0]/2)] 
            self.points.append([point,quality,timestamp])

        return self.points

#holds points
class Point:
    def __init__(self, pos, qual, ts):
        #point data
        self.coord = pos
        self.quality = qual
        self.timestamp = ts

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
        self.name = _name #name/id of the cluster
        self.points = [] #holds points
        self.rect = []  #[x,y,w,h]
        self.centroid = [] #centroid of cluster
        self.avg_time_stamp = 0 #ms timestamp

    def addPoint(self, p):
        self.points.append(p)

    def getRect(self):
        #corner_points is rectangle coordinates: [min_x,min_y,max_x,max_y]
        corner_points = [self.points[0].coord[0],self.points[1].coord[1],self.points[0].coord[0],self.points[1].coord[1]] 
        for p in self.points[1:]:
            #finds top left corner
            if(p.coord[0] < corner_points[0]):
                corner_points[0] = p.coord[0]
            if(p.coord[1] < corner_points[1]):
                corner_points[1] = p.coord[1]
            #finds bottom right corner
            if(p.coord[0] > corner_points[2]):
                corner_points[2] = p.coord[0]
            if(p.coord[1] > corner_points[3]):
                corner_points[3] = p.coord[1]

        #if you want rect to be [x,y,w,h]
        corner_points[2] = corner_points[2] - corner_points[0]
        corner_points[3] = corner_points[3] - corner_points[1]

        self.rect = corner_points
        return self.rect

    def getDrawRect(self):
        draw_rect = [int(self.rect[0]/MM_PXL[0]),int(self.rect[1]/MM_PXL[1]),int(self.rect[2]/MM_PXL[0]),int(self.rect[3]/MM_PXL[1])]
        return draw_rect

    def getCentroid(self):
        self.getRect()
        self.centroid = [self.rect[0] + (self.rect[2]/2.0), self.rect[1] + (self.rect[3]/2.0)]
        return self.centroid

    def getAvgTimeStamp(self):
        self.avg_time_stamp = 0
        for p in self.points:
            self.avg_time_stamp += p.timestamp
        self.avg_time_stamp /= float(len(self.points))
        return self.avg_time_stamp

#Density-based spatial clustering of applications with noise
class DBSCAN:
    #min points, density epsilon, time epsilon
    def __init__(self, mpts = 5, d_eps = 150, t_eps = 50):
        self.minPts = mpts
        self.dist_epsilon = d_eps
        self.time_epsilon = t_eps

        self.time_dependent = True #cluster based on time
        self.space_dependent = True #cluster based on space

        self.clusters = []
        self.cluster_count = 0
        self.cluster_rects = [] #[rect,color]

        self.points = []
        self.noise = []

        self.normalize = True

    def initPoints(self, arr_points):
        for p in arr_points:
            self.points.append(Point(p[0],p[1],p[2]))

    #if you want to change the settings, call these before dbscan_RESET()
    def changeDEps(self, change_val):
        self.dist_epsilon += change_val
    def changeTEps(self, change_val):
        self.time_epsilon += change_val
    def changeMinPts(self, change_val):
        if(self.minPts + change_val > 0):
            self.minPts += change_val

    #resets DBSCAN for new analysis when you change data points or settings
    def RESET(self, points = None):
        del self.clusters[:]
        del self.noise[:]

        if(points):
            del self.points[:]
            self.initPoints(points)
        else:
            for p in self.points:
                p.visited = False
                p.inCluster = False
                p.classification = "" #CORE, REACHABLE, NOISE
                p.cluster = "" #cluster name

        self.minPts = 5
        self.dist_epsilon = 150
        self.analyze()
        self.connectClusters()
        self.generateClusterRects()
        print("num clusters - " + str(len(self.clusters)))
        print("D_eps: " + str(self.dist_epsilon) + " T_eps: " + str(self.time_epsilon) + " minPts: " + str(self.minPts))

    #call this after normalizing
    def normalizeRESET(self):
        del self.noise[:]

        for p in self.points:
            p.visited = False
            p.inCluster = False
            p.classification = "" #CORE, REACHABLE, NOISE
            p.cluster = "" #cluster name

        self.minPts = 20
        self.dist_epsilon = 150
        self.analyze(time_dependent = False)
        self.connectClusters(eps = 50)
        self.generateClusterRects()
        print("num clusters - " + str(len(self.clusters)))
        print("D_eps: " + str(self.dist_epsilon) + " T_eps: " + str(self.time_epsilon) + " minPts: " + str(self.minPts))

    #returns cluster obj
    def findCluster(self, _name):
        for c in self.clusters:
            if(c.name == _name):
                return c
        return None

    #returns the list of points within eps distance
    def queryRegion(self, p, time_dependent = True):
        neighbors = []
        for neighbor in self.points:
            if(neighbor == p):
                continue
            if(time_dependent):
                if(p.getDistanceFrom(neighbor.coord) < self.dist_epsilon) and (abs(p.timestamp - neighbor.timestamp) < self.time_epsilon):
                    neighbors.append(neighbor)
            else:
                if(p.getDistanceFrom(neighbor.coord) < self.dist_epsilon):
                    neighbors.append(neighbor)

        return neighbors

    #called on intial core points to expand the cluster
    def expandCluster(self, p, neighbors, cluster, time_dependent = True):
        #adds p to cluster
        cluster.addPoint(p)
        p.cluster = cluster.name
        p.inCluster = True

        #looks at neighbors for potential density-reachable core points
        for neighbor in neighbors:
            if not neighbor.visited:
                neighbor.visited = True

                n_neighbors = self.queryRegion(neighbor, time_dependent)
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
                cluster.addPoint(neighbor)
                neighbor.cluster = cluster.name
                neighbor.inCluster = True

        self.clusters.append(cluster)

    #uses queryRegion and expandCluster to identify dense regions of points as clusters
    def analyze(self, time_dependent = True):
        #A: look for core points
        for p in self.points:
            if p.visited:
                continue
            p.visited = True

            neighbors = self.queryRegion(p, time_dependent)
            if(len(neighbors) < self.minPts):
                #mark noise temporarily
                self.noise.append(p)
                p.classification = "NOISE"
            else:
                #mark core points
                c = Cluster("cluster_"+str(self.cluster_count))
                self.cluster_count += 1
                p.classification = "CORE"
                self.expandCluster(p, neighbors, c, time_dependent)

        #B: reiterate and look for reachable points in noise
        new_noise = []
        for p in self.noise:
            for neighbor in self.queryRegion(p, time_dependent):
                if(neighbor.classification == "CORE"):
                    #if this point is reachable, then add to the cluster
                    p.classification = "REACHABLE"
                    c = self.findCluster(neighbor.cluster)
                    c.addPoint(p)
                    break
            if p.classification == "NOISE":
                new_noise.append(p)
        self.noise = new_noise

    def connectClusters(self, eps = 1):
        for c_i in self.clusters:
            c_i.getRect()
            for c_j in self.clusters:
                if c_i is c_j:
                    continue
                c_j.getRect()
                #calculates centroid of two clusters
                c_i_centroid= [c_i.rect[0]+(c_i.rect[2]/2),c_i.rect[1]+(c_i.rect[3]/2)]
                c_j_centroid = [c_j.rect[0]+(c_j.rect[2]/2),c_j.rect[1]+(c_j.rect[3]/2)]
                #gets distance between two clusters
                dist = math.sqrt((c_i_centroid[0] - c_j_centroid[0])**2 + (c_i_centroid[1] - c_j_centroid[1])**2)
                #if distance between the two clusters is less than threshold
                if(dist < eps):
                    #merge clusters
                    c_i.points += c_j.points
                    self.clusters.remove(c_j)
                    del c_j
        #print("new num clusters - " + str(len(self.clusters)))

    def generateClusterRects(self):
        del self.cluster_rects[:]

        cluster_colors = generateColors(len(self.clusters))
        for i in range(len(self.clusters)):
            self.clusters[i].getRect()
            self.cluster_rects.append([self.clusters[i].getDrawRect(),cluster_colors[i]])

        return self.cluster_rects

    def normalizePoints(self, velocity_time_multipliers):
        if not self.normalize or not velocity_time_multipliers:
            return
        avg_velocity = sum([v[0] for v in velocity_time_multipliers])/len(velocity_time_multipliers)
        #print("average velocity: " + str(avg_velocity))
        
        for pt in self.points:
            dist_travlled = 0

            #if point's timestamp is before record
            if(pt.timestamp < velocity_time_multipliers[0][1]):
                dist_travlled = velocity_time_multipliers[0][0] * pt.timestamp
            #if point's timestamp is within record
            else:
                dist_travlled = avg_velocity * velocity_time_multipliers[0][1]
                #where the point lies in the velocity_time_multiplier
                for i in range(len(velocity_time_multipliers)):
                    if(pt.timestamp >= velocity_time_multipliers[i][1] and pt.timestamp <= velocity_time_multipliers[i][2]):
                        #if point's timestamp ends at this interval, add the remaining distance travelled
                        dist_travlled += velocity_time_multipliers[i][0] * (pt.timestamp - velocity_time_multipliers[i][1])
                        break
                    else:
                        #add point's velocity * time between clusters
                        dist_travlled += velocity_time_multipliers[i][0] * (velocity_time_multipliers[i][2] - velocity_time_multipliers[i][1])
                #if the timestamp extends past the last recorded velocity, add the rest of the time multiplied by last known velocity
                if(pt.timestamp > velocity_time_multipliers[-1][2]):
                    dist_travlled += velocity_time_multipliers[-1][0] * (pt.timestamp - velocity_time_multipliers[-1][2])

            #currently 1 dimensional normalization
            pt.coord[0] -= dist_travlled
        self.normalizeRESET()

#FC Analysis
class FCAnal:
    def __init__(self):
        self.FC_Clusters = []
        self.FC_groups = []
        self.FC_points = []

        #velocities for only 1 fcgroup for now, will expand to 2d array
        self.FC_velocities = [] #[vel, start_t, end_t]

    def initFCCs(self, FC_Cs):
        self.FC_Clusters = []
        self.FC_groups = []
        self.FC_points = []

        #velocities for only 1 fcgroup for now, will expand to 2d array
        self.FC_velocities = [] #[vel, start_t, end_t]
        self.FC_Clusters = FC_Cs
        for fc in self.FC_Clusters:
            self.FC_points.append(fc.getCentroid())
            fc.getAvgTimeStamp()

    def getVelocities(self):
        if(len(self.FC_velocities) == 0):
            return None
        else:
            return self.FC_velocities

    def analyze(self):
        self.findFCLines()
        self.sortFCLines()
        self.findFCVelocities()

    def findFCLines(self, eps = 300):
        #get by shape first
        self.FC_groups = []
        copy_FC_points = copy.deepcopy(self.FC_points)

        for i in range(len(self.FC_points)):
            fc_i = self.FC_points[i]

            if fc_i in copy_FC_points:
                self.FC_groups.append([[self.FC_Clusters[i]],fc_i[1]]) #[list of fc_points, avg_y * num fc_points]
                copy_FC_points.remove(fc_i)
            
            for j in range(len(self.FC_points)):
                fc_j = self.FC_points[j]

                if fc_j in copy_FC_points:
                    avg_point = self.FC_groups[-1][1]/len(self.FC_groups[-1][0])
                    
                    if(abs(fc_j[1] - avg_point) < eps):
                        self.FC_groups[-1][0].append(self.FC_Clusters[j])
                        self.FC_groups[-1][1] += fc_j[1]
                        copy_FC_points.remove(fc_j)

        #WILL NEED TO SORT BY TIME FOR OVERLAPPING BUCKETS
        del copy_FC_points
        #print(len(self.FC_groups))
    
    def sortFCLines(self):
        if(len(self.FC_groups) == 0):
            return
        #sort by time
        new_group = []
        for FCGroup in self.FC_groups:
            time_list = [fc.avg_time_stamp for fc in FCGroup[0]]
            FCGroup[0] = sort(FCGroup[0], [fc.avg_time_stamp for fc in FCGroup[0]])
            new_group.append(FCGroup[0])
        self.FC_groups = new_group
        #for fc_group in self.FC_groups[0]:
            #print("POS: " + str(fc_group.centroid) + " avg_time_stamp: " + str(fc_group.avg_time_stamp))

    def findFCVelocities(self):
        if(len(self.FC_groups) == 0):
            return
        #only one FCGroup (line) for now
        FCGroup = self.FC_groups[0]
        for i in range(len(FCGroup) - 1):
            delta_dist = getDistance(FCGroup[i].centroid, FCGroup[i+1].centroid)
            delta_time = FCGroup[i+1].avg_time_stamp - FCGroup[i].avg_time_stamp
            velocity = delta_dist/delta_time #m/s
            self.FC_velocities.append([velocity,FCGroup[i].avg_time_stamp,FCGroup[i+1].avg_time_stamp])
        #print(self.FC_velocities)
        return self.FC_velocities

"""
OLDIES *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

v1 findFCVelocities()
########################
if(len(self.FC_groups) == 0):
    return
#only one FCGroup (line) for now
FCGroup = self.FC_groups[0]
for i in range(len(FCGroup) - 1):
    delta_dist_x = getDistance([FCGroup[i].centroid[0],0],[FCGroup[i+1].centroid[0],0])
    delta_dist_y = getDistance([0,FCGroup[i].centroid[1]],[0,FCGroup[i+1].centroid[1]])
    delta_time = FCGroup[i+1].avg_time_stamp - FCGroup[i].avg_time_stamp
    velocity = [delta_dist_x/delta_time,delta_dist_y/delta_time] #m/s
    self.FC_velocities.append([velocity,FCGroup[i].avg_time_stamp,FCGroup[i+1].avg_time_stamp])
#print(self.FC_velocities)
return self.FC_velocities

---

v2 normalizePoints()
########################
if not self.normalize or not velocity_time_multipliers:
    return
avg_velocity_x = sum([v[0][0] for v in velocity_time_multipliers])/len(velocity_time_multipliers)
avg_velocity_y = sum([v[0][1] for v in velocity_time_multipliers])/len(velocity_time_multipliers)
#print("average velocity: " + str(avg_velocity))

for pt in self.points:
    dist_travlled_x = 0
    dist_travlled_y = 0

    #if point is within the recorded timestamps
    if(pt.timestamp >= velocity_time_multipliers[0][1]):
        dist_travlled_x = avg_velocity_x * velocity_time_multipliers[0][0][0]
        dist_travlled_y = avg_velocity_y * velocity_time_multipliers[0][0][1]
        #where the point lies in the velocity_time_multiplier
        for i in range(len(velocity_time_multipliers)):
            if(pt.timestamp > velocity_time_multipliers[i][1] and pt.timestamp <= velocity_time_multipliers[i][2]):
                dist_travlled_x += velocity_time_multipliers[i][0][0] * (pt.timestamp - velocity_time_multipliers[i][1])
                dist_travlled_y += velocity_time_multipliers[i][0][1] * (pt.timestamp - velocity_time_multipliers[i][1])
                break
            else:
                dist_travlled_x += velocity_time_multipliers[i][0][0] * (velocity_time_multipliers[i][2] - velocity_time_multipliers[i][1])
                dist_travlled_y += velocity_time_multipliers[i][0][1] * (velocity_time_multipliers[i][2] - velocity_time_multipliers[i][1])
        
        if(pt.timestamp > velocity_time_multipliers[-1][2]):
            dist_travlled_x += avg_velocity_x * (pt.timestamp - velocity_time_multipliers[-1][2])
            dist_travlled_y += avg_velocity_y * (pt.timestamp - velocity_time_multipliers[-1][2])
    else:
        dist_travlled_x = avg_velocity_x * pt.timestamp
        dist_travlled_y = avg_velocity_y * pt.timestamp

    pt.coord[0] -= dist_travlled_x
    pt.coord[1] -= dist_travlled_y

self.normalizeRESET()

--

v1  normalizePoints()
########################
for cluster in self.clusters:
    for pt in cluster.points:

        avg_velocity_to_pt = 0
        within_known_time_stamp = False
        
        for i in range(len(velocity_time_multipliers)):
            v_t = velocity_time_multipliers[i]
            avg_velocity_to_pt += v_t[0]
            #pt is within timestamp
            if(pt.timestamp >= v_t[1] and pt.timestamp < v_t[2]):
                within_known_time_stamp = True
                avg_velocity_to_pt /= i+1
                break

        if(within_known_time_stamp):
            offset = avg_velocity_to_pt * pt.timestamp
            offset = 0
            pt.coord[0] -= offset/5
            #print("point timestamp: " + str(pt.timestamp) + " velocity: " + str(avg_velocity_to_pt) + "offset value: " + str(offset))
        else:
            offset = avg_velocity * pt.timestamp
            offset = 0
            #print("point timestamp: " + str(pt.timestamp) + " velocity: " + str(avg_velocity) + "offset value: " + str(offset))
            pt.coord[0] -= offset/5
        
        pt.coord[0] -= avg_velocity * pt.timestamp

    self.normalizeRESET()
---
""" 