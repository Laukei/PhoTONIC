import logging
from logging.config import dictConfig
import time
import csv

from controller import Controller, MOVE_FORWARD, MOVE_BACKWARD, X, Y, Z
from cryostatcontrol.config import addressbook, log_config
from cryostatcontrol.hardware import SIM900
from metrics import Pos

dictConfig(log_config)
logger = logging.getLogger()

SIM928_MODULE_ID = 3
SIM970_MODULE_ID = 7
SIM970_MEAS_CHANNEL = 2
REFERENCE_VOLTAGE = 0.1 #in V
CONTACT_TOLERANCE = 0.5 #if signal is this proportion of REF_CHANNEL or lower, consider probe touching


def test_approach_nonlinearity_repeat():
	with SIM900('ASRL4') as sim900, Controller() as c:
		sim900.write(SIM928_MODULE_ID,f'VOLT {REFERENCE_VOLTAGE}')
		sim900.write(SIM928_MODULE_ID,'OPON')
		time.sleep(0.5)

		def test_contact():
			meas = float(sim900.query(SIM970_MODULE_ID,f'VOLT? {SIM970_MEAS_CHANNEL}'))
			if meas <= CONTACT_TOLERANCE*REFERENCE_VOLTAGE:
				return True
			else:
				return False
				
		c.set_amplitude(Z,20)
		c.set_frequency(Z,100)

		data = []

		MAX_Z = Pos(3000,'um')
		HOME_Z = Pos(2880,'um')

		try:
			for i in range(10):
				logging.info(f'on loop {i}')
				c.home_to_position_um(Z,HOME_Z.um())
				c.wait_til_stopped()
				for j in range(400):
					c.blind_move(Z,MOVE_FORWARD,1)
					c.wait_til_stopped()
					time.sleep(0.1)
					voltage = float(sim900.query(SIM970_MODULE_ID,f'VOLT? {SIM970_MEAS_CHANNEL}'))
					position = c.get_position(Z)
					data.append([i,j,position.um(),voltage])
					print(data[-1])
					if position.um() > MAX_Z.um():
						logging.info(f'position {position.um()} greater than MAX_Z')
						break
		except KeyboardInterrupt:
			print('broken out of loop...')
		finally:
			logging.debug(f'{data}')

		c.home_to_position_um(Z,HOME_Z.um())
		c.wait_til_stopped()
		sim900.write(SIM928_MODULE_ID,'OPOF')


	with open('data_multiple.txt','w') as f:
		w = csv.writer(f,delimiter='\t')
		w.writerows(data)


def test_approach_nonlinearity():
	with SIM900('ASRL4') as sim900, Controller() as c:
		sim900.write(SIM928_MODULE_ID,f'VOLT {REFERENCE_VOLTAGE}')
		sim900.write(SIM928_MODULE_ID,'OPON')
		time.sleep(0.5)

		def test_contact():
			meas = float(sim900.query(SIM970_MODULE_ID,f'VOLT? {SIM970_MEAS_CHANNEL}'))
			if meas <= CONTACT_TOLERANCE*REFERENCE_VOLTAGE:
				return True
			else:
				return False
				
		c.set_amplitude(Z,30)
		c.set_frequency(Z,100)

		data = []

		try:
			for i in range(100):
				input('enter to continue')
				c.blind_move(Z,MOVE_FORWARD,3)
				c.wait_til_stopped()
				contact = test_contact()
				voltage = float(sim900.query(SIM970_MODULE_ID,f'VOLT? {SIM970_MEAS_CHANNEL}'))
				position = c.get_position(Z)
				data.append([position,voltage,contact])
				print(data[-1])
		except KeyboardInterrupt:
			print('broken out of loop...')

		sim900.write(SIM928_MODULE_ID,'OPOF')

	with open('data.txt','w') as f:
		w = csv.writer(f,delimiter='\t')
		w.writerows(data)



def test_read_position():
	with Controller() as c:
		print(f'Z position: {c.get_position(Z).um()} microns')


def test_approach():
	with SIM900('ASRL4') as sim900, Controller() as c:
		sim900.write(SIM928_MODULE_ID,f'VOLT {REFERENCE_VOLTAGE}')
		sim900.write(SIM928_MODULE_ID,'OPON')
		time.sleep(0.5)

		def test_contact():
			meas = float(sim900.query(SIM970_MODULE_ID,f'VOLT? {SIM970_MEAS_CHANNEL}'))
			if meas <= CONTACT_TOLERANCE*REFERENCE_VOLTAGE:
				return True
			else:
				return False
				
		c.set_amplitude(Z,30)
		c.set_frequency(Z,100)

		while test_contact() == False:
			c.blind_move(Z,MOVE_FORWARD,3)
			time.sleep(0.05)

		print('found contact')
		sim900.write(SIM928_MODULE_ID,'OPOF')



def test_sim900():
	with SIM900('ASRL4') as sim900:
		sim900.write(SIM928_MODULE_ID,'VOLT 0.1')
		sim900.write(SIM928_MODULE_ID,'OPON')
		for i in range(10):
			time.sleep(0.1)
			volt = sim900.query(SIM970_MODULE_ID,f'VOLT? {SIM970_MEAS_CHANNEL}')
			print(i,volt)
		sim900.write(SIM928_MODULE_ID,'OPOF')

def test_anc350():
	with Controller() as c:
		# c.reset_position()
		# c.wait_til_stopped()
		# c.home_to_position_um('x',2300)
		for i in range(20):
			c.set_amplitude(Z,20)
			c.set_frequency(Z,300)
			c.blind_move(Z,MOVE_BACKWARD,3)
			print(i)
		c.reset_position()
		exit()
		c.home_to_position_um(X,2300)
		c.home_to_position_um(Y,2300)
		c.wait_til_stopped()
		c.home_to_position_um(Y,2700)
		c.wait_til_stopped()
		# while True:
		# 	print(c.status('x'))
		# 	time.sleep(0.1)


if __name__ == "__main__":
	test_approach_nonlinearity_repeat()