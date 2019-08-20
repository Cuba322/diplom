import json
import sys
import os

#----- Helping functions -----
def show_msg_and_exit(msg):
	print(msg)
	print("Press enter to exit...")
	input()


#----- Main code -----
if len(sys.argv)<2:
	show_msg_and_exit("Empty argument")
	
file_name = sys.argv[1]
if not os.path.isfile(file_name):
	show_msg_and_exit("Wrong argument")

print("Start generating")

with open(file_name, 'r') as in_file:
	data = json.load(in_file)
out_flows_of_passengers = {}
list_dic = []
for el in data['routes']:
	route = el['route']
	for i in range(0, len(route)):
		for j in range(i+1, len(route)):
			dic = {}
			dic['indexes'] = [route[i], route[j]]
			dic['intensity'] = 0
			list_dic.append(dic)
data['flows_of_passengers'] = list_dic
path_left_part, extension = os.path.splitext(file_name)
path_left_part += '_generated'
new_file_name = path_left_part + extension
with open(new_file_name, 'w') as out_file:
	json.dump(data, out_file, indent=4)
		
show_msg_and_exit("End generating")