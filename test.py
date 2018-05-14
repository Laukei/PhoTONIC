from controller import Controller
import time

def test():
	with Controller() as c:
		# c.reset_position()
		# c.wait_til_stopped()
		# c.home_to_position_um('x',2300)
		c.reset_position()
		c.home_to_position_um('x',2300)
		c.home_to_position_um('y',2300)
		c.wait_til_stopped()
		c.home_to_position_um('y',2700)
		c.wait_til_stopped()
		# while True:
		# 	print(c.status('x'))
		# 	time.sleep(0.1)


if __name__ == "__main__":
	test()