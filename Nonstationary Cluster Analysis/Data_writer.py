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
