import os,csv

def readCSV(file_name = '1M1MPHT4.CSV'):
        with open(file_name, 'rb') as csvfile:
            review_reader = csv.reader(csvfile)
            
            for row in review_reader:
                print row


flders = ["/moving_data/Test/"]

def sortMD(array, key = 1):
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

def getFilePaths(folders):
	file_paths = []
	dir_path = os.getcwd()
	for folder in folders:
		for file in os.listdir(dir_path + folder):
		    if file.endswith(".txt"):
		    	file_paths.append(os.path.join(dir_path + folder, file))
		        print(file_paths[-1])

"""
f = open("List_Of_Files.txt", 'w+')
f.close()
"""



"""
f = open('Cluster_Analysis_Data_File_Record.txt', 'r+')
records = f.read().splitlines()
print(len(records))
if(len(records) is not 0):
    new_data_file_name = "Cluster_Analysis_Data_" + records[-1] + ".txt"
    f.write(str(int(records[-1]) + 1) + "\n")
else:
    new_data_file_name = "Cluster_Analysis_Data_" + str(0) + ".txt"
    f.write(str(1) + "\n")

print(new_data_file_name)
f.close()
"""