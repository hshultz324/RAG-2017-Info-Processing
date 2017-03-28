__author__ = 'alanyuen'
import math

### DIMENSION CONSTANTS ###
MAP_SIZE_MM = [18000, 18000] #12m x 12m
CELL_SIZE_MM = [300,300] #0.3m x 0.3m
WINDOW_SIZE = [800,800]
MM_PXL = [MAP_SIZE_MM[0]/WINDOW_SIZE[0],MAP_SIZE_MM[1]/WINDOW_SIZE[1]]

POINT_DRAW_SIZE = 1
RECT_STROKE_WIDTH = 0

def sort(array, key):
    arr_less = []
    arr_equal = []
    arr_greater = []

    key_less = []
    key_greater = []

    if len(array) > 1:
        pivot = key[0]
        for i in range(len(key)):
            if key[i] < pivot:
                arr_less.append(array[i])
                key_less.append(key[i])
            if key[i] == pivot:
                arr_equal.append(array[i])
            if key[i] > pivot:
                arr_greater.append(array[i])
                key_greater.append(key[i])

        return sort(arr_less, key_less)+arr_equal+sort(arr_greater, key_greater) 
    else:  
        return array

def getDistance(pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def generateColors(size = 10):
    colors = []
    size = ((size/3) + 1)*3
    value_increment = 255/(size/3)
    if size < 9:
    	size = 9
    for i in range(size/3):
        for j in range(size/3):
            for k in range(size/3):
                colors.append([255-(i*value_increment),255-(j*value_increment),255-(k*value_increment)])

    return colors
