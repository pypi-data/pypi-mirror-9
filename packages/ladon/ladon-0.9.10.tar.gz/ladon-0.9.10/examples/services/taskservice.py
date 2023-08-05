from ladon.compat import PORTABLE_STRING
from ladon.ladonizer import ladonize
import time

class TaskService(object):

	@ladonize(PORTABLE_STRING, int, rtype=int, tasktype=True)
	def taskExample(self,session_id,counter,**kw):
		set_progress = kw['update_progress']
		repeat = 60.0
		for i in range(int(repeat)):
			time.sleep(.5)
			set_progress(float(i+1.0)/repeat)
		return counter
