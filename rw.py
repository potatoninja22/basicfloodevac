list_lines = []

with open('C:\Desktop\Intern\\basicfloodevac\\fire_evacuation\\floorplans\\floorplan_4.txt',"r") as reader:
    for line in reader.readlines():
        list_lines.append(line)

    reader.close()

# line = list_lines[0]

# print(line)

counter = 0

for i in line:
    if i == 'E':
        index = counter
        break
    counter += 1

print(counter)

updated_list = []

for line in list_lines:
    temp = 0
    newl = ""
    for j in line:
        if temp == counter-2 or temp == counter or temp == counter + 2 or temp == counter+4:
            newl += "R"
        else:
            newl += j
        temp += 1
    updated_list.append(newl)

#print(updated_list)

removed_list = []

for line in updated_list:
    conv = line.replace("\n","")
    removed_list.append(conv)

print(removed_list)

with open("C:\\Desktop\\Intern\\basicfloodevac\\fire_evacuation\\floorplans\\floorplan_5.txt","w") as f:
    for i in removed_list:
        f.write(i)
        f.write("\n")
    f.close()

list_lines = []

with open("C:\\Desktop\\Intern\\basicfloodevac\\fire_evacuation\\floorplans\\floorplan_5.txt","r") as f:
    for line in f.readlines():
        list_lines.append(line)
    f.close()

remove_furniture = []

for line in list_lines:
    need = line.replace("F","_")
    remove_furniture.append(need)

remove_line = []

for line in remove_furniture:
    need = line.replace("\n","")
    remove_line.append(need)

with open("C:\\Desktop\\Intern\\basicfloodevac\\fire_evacuation\\floorplans\\floorplan_5.txt","w") as f:
    for i in remove_line:
        f.write(i)
        f.write("\n")
    f.close()


