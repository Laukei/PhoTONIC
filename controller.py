import time
import logging
# from queue import Empty

from anc350 import Positioner
from metrics import Pos
from monitor import launch_monitor_in_thread
from monitor import axis_map


default_positions = {
	'x': Pos(2500,'um'),
	'y': Pos(2500,'um'),
	'z': Pos(0,'um')
}

class Controller:
	def __init__(self,positioner=0):
		self.p = Positioner(positioner)
		self._homing_axes = set()
		self._monitor, self._commands, self._replies = launch_monitor_in_thread(self.p)
		self._sendid = 0
		self._outstanding_replies = set()


	def reset_position(self):
		'''
		moves the X, Y, and Z axes to their default position
		'''
		for axis in axis_map:
			messageid = self.home_to_position_um(axis,default_positions.get(axis).um(),False)
			self._outstanding_replies.add(messageid)
		for axis in axis_map:
			self._outstanding_replies.remove(self._wait_for_reply()[0])
		self.wait_til_stopped()
		assert len(self._outstanding_replies) == 0


	def blind_move(self,axis,**kwargs):
		'''
		moves without feedback a certain number of sawtooth waves
		'''
		pass


	def home_to_position_um(self,axis,position_um,wait=True):
		'''
		homes an axis to a position
		'''
		messageid = self._send(['home_to_position_um',(axis,position_um)]) #send the axis to the homing monitor
		if wait == False:
			return messageid
		else:
			reply = self._wait_for_reply()
			assert reply[0] == messageid


	def wait_til_stopped(self):
		'''
		blocks until monitor thread confirms no axis is moving
		'''
		while True:
			messageid = self._send(['get_moving'])
			reply = self._wait_for_reply()
			assert reply[0] == messageid
			if len(reply[1]) == 0:
				break
			else:
				logging.info('still moving, waiting...')
				time.sleep(0.1)


	def _wait_for_reply(self):
		'''
		low-level function to check for reply from monitor thread
		should never need to use this directly - use public functions
		'''
		message = self._replies.get()
		# except Empty:
		# 	message = None
		logging.info('reply received: {}'.format(message))
		return message


	def _send(self,message):
		'''
		low-level function to send message to monitor thread
		'''
		messageid = self._messageid()
		self._commands.put([messageid] + message)
		return messageid


	def _messageid(self):
		'''
		low-level function to ensure no duplicate messages sent
		should never need to call this directly - use _send()
		'''
		self._sendid += 1
		return self._sendid


	def __enter__(self,*args,**kwargs):
		return self


	def __exit__(self,*args,**kwargs):
		self.close()


	def close(self):
		'''
		closes monitor thread and disconnects from positioner
		'''
		self._send(['quit'])
		self._monitor.join()
		self.p.disconnect()

