import pickle
import os 

# Round it up with data
d = [pickle.load(open("data_data/data/data_%i.p" % i , "rb")) for i in range(0, 220)]
joint_d = [inner for outer in d for inner in outer]

# Change the values to shift down for embedding purposes
new_d = []
for i in range(len(joint_d)):
    t = []
    for j in range(len(joint_d[i])):
        if joint_d[i][j] == 11:
            t.append(10)
        elif joint_d[i][j] == 10:
            t.append(9)
        # Convert no tiles to blanks
        elif joint_d[i][j] == -1:
            print("HEY")
            t.append(0)
        else:
            t.append(joint_d[i][j])
    new_d.append(t)

pickle.dump(new_d, open("joint_d.p", "wb"))

# Do it for labels
l = [pickle.load(open("data_data/labels/labels_%i.p" % i , "rb")) for i in range(0, 220)]
# Change values
new_l = [[1 if x != 11 else 0 for x in sub] for sub in l]
joint_l = [inner for outer in new_l for inner in outer]
pickle.dump(joint_l, open("joint_l.p", "wb"))

print("Done!")
