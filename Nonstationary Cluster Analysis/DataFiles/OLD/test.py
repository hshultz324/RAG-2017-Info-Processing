import math

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

with open("1B_1M_3S_QT_12.txt") as f:
	data = f.readlines()

points = []
for line in data:
	words = line.split(" ")
	point = [float(words[0])*math.cos(float(words[1]) * math.pi / 180.0),float(words[0])*math.sin(float(words[1]) * math.pi / 180.0)]
	point[0] += 6000 #translate 6m
	point[1] += 6000 #translate 6m
	points.append(point)

class Cell:
	def __init__(self, coord):
		self.points =[]
		self.cell_coord = coord

	def addPoint(self, pos):
		self.points.append(pos)

	def getDensity(self):
		return len(self.points)


MAP_SIZE_MM = [12000, 12000] #12m x 12m
CELL_SIZE_MM = [300,300] #0.3m x 0.3m
cells = [[Cell([i,j]) for i in range(40)] for j in range(40)]
for point in points:
	cells[int(point[0]/300)][int(point[0]/300)].addPoint(point)

densities = []
for c_row in cells:
	for c in c_row: 
		densities.append([(c.cell_coord[0],c.cell_coord[1]),c.getDensity()])

densities = sort(densities)

for d in densities:
	if(d[1] == 0):
		continue
	print(d)




