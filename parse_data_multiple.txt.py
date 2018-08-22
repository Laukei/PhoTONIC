# data_multiple.py
import csv
from matplotlib import pyplot as plt
import numpy as np
from fit_heaviside import fit

data = []
BIN_SIZE = 1 #must be integer

with open('data_multiple.txt','r') as f:
	c = csv.reader(f,delimiter='\t')
	for row in c:
		if row != []:
			data.append([int(row[0]),int(row[1]),float(row[2]),float(row[3])])

processed_data = {}
processed_voltage = {}
rawX = []
rawY = []
rawYvolt = []

for r, row in enumerate(data):
	try:
		if data[r+1][0] == row[0]:
			p1 = row[2]
			p2 = data[r+1][2]
			delta = p2 - p1
			index = int(p1/float(BIN_SIZE))*int(BIN_SIZE)
			try:
				processed_data[index].append(delta)
				processed_voltage[index].append(row[3])
				rawX.append(p1)
				rawY.append(delta)
				rawYvolt.append(row[3])

			except KeyError:
				processed_data[index] = [delta]
				processed_voltage[index] = [row[3]]
	except IndexError:
		break


plt.plot(rawX,rawY,'rx')
plt.plot(rawX,rawYvolt,'bx')
plt.show()
plt.close()


X = []
Ypos = []
Ypos_std = []
Yvol = []
Yvol_std = []

for key in sorted(processed_data.keys()):
	X.append(key)
	Ypos.append(np.mean(processed_data[key]))
	Ypos_std.append(np.std(processed_data[key]))#/len(processed_data[key]))
	Yvol.append(np.mean(processed_voltage[key]))
	Yvol_std.append(np.std(processed_voltage[key]))


plt.figure()
plt.errorbar(X,Ypos,yerr=Ypos_std,fmt='rx')
plt.xlabel(r'position ($\mu$m)')
plt.ylabel(r'step size ($\mu$m) & voltage (V)')
plt.errorbar(X,Yvol,yerr=Yvol_std,fmt='b--')
plt.show()