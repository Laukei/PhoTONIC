# data_multiple.py
import csv
from matplotlib import pyplot as plt
import numpy as np

datasets = []
BIN_SIZE = 1 #must be integer

with open('data_multiple_100runs.txt','r') as f:
	c = csv.reader(f,delimiter='\t')
	next_run = 0
	for row in c:
		if row != []:
			if int(row[0]) == next_run:
				datasets.append({'x':[],'voltage':[],'deltax':[],'first_contact':None})
				next_run = int(row[0]) + 1
			datasets[-1]['x'].append(float(row[2]))
			datasets[-1]['voltage'].append(float(row[3]))
			if float(row[3]) <= 0.05 and datasets[-1]['first_contact'] == None:
				datasets[-1]['first_contact'] = float(row[2])


for dataset in datasets:
	dataset['x_zeroed'] = np.array(dataset['x']) - dataset['first_contact']
	dataset['deltax'] = np.gradient(dataset['x'])


binned_data = {}

rawX = []
rawY = []

for dataset in datasets:
	for i, x in enumerate(dataset['x_zeroed']):
		rawX.append(x)
		rawY.append(dataset['deltax'][i])
		try:
			binned_data[int(x)].append(dataset['deltax'][i])
		except KeyError:
			binned_data[int(x)] = [dataset['deltax'][i]]


X = []
Y = []
Ystd = []


for key in sorted(binned_data.keys()):
	X.append(key)
	Y.append(np.mean(binned_data[key]))
	Ystd.append(np.std(binned_data[key]))


plt.plot(rawX,rawY,'rx')
plt.show()
plt.close()



plt.figure()
plt.errorbar(X,Y,yerr=Ystd,fmt='rx')
plt.xlabel(r'position ($\mu$m)')
plt.ylabel(r'step size ($\mu$m) & voltage (V)')
# plt.errorbar(X,Yvol,yerr=Yvol_std,fmt='b--')
plt.show()