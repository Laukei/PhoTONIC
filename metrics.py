

class Pos:
	'''
	a position class for holding lengths

	useful because the ANC350 often wants lengths in metres
	and the user often wants lengths in microns or millimetres
	'''
	def __init__(self,position,unit='m'):
		if unit == 'm':
			self.position = position
		elif unit == 'mm':
			self.position = position / 1e3
		elif unit == 'um':
			self.position = position / 1e6
		elif unit == 'nm':
			self.position = position / 1e9

	def m(self):
		return self.position

	def mm(self):
		return self.position * 1e3

	def um(self):
		return self.position * 1e6

	def nm(self):
		return self.position * 1e9

	def __str__(self):
		return f'{self.position}'

	def __repr__(self):
		return f'Pos({self.position})'