from monitor import get_monitor, MonitorException
from multiprocessing import Process, Pipe


def start_tk(outpipe):
	from monitor_tk import Monitor
	mon = Monitor(outpipe)
	mon.start()

inpipe = None
try:
	inpipe, outpipe = Pipe()
	#mon = get_monitor(outpipe)
	#import pdb; pdb.set_trace()
	monitor_process = Process(target=start_tk, args=(outpipe,))
	monitor_process.start()
	#mon.start()
except MonitorException:
	print('will not start monitor ui')

inpipe.send("/home/amol/Pictures/wallp.jpg")




