import threading
import logging
import time 
from queue import Queue, Empty
from metrics import Pos

axis_map = {
    'x':0,
    'y':1,
    'z':2
}

def launch_monitor_in_thread(anc350):
    commands = Queue()
    replies = Queue()
    monitor = ANC350Monitor(commands,replies,anc350)
    monitor.start()
    return monitor, commands, replies


class ANC350Monitor(threading.Thread):
    '''
    this monitor takes input from queue in form of 'x', 'y', 'z'
    and monitors the ANC350 to disable the channel when homing
    to a position.

    this exists entirely because the ANC350 refuses to stop moving
    the ANPx101-A3-754 positioner.
    '''
    def __init__(self, commands, replies, positioner, **kwargs):
        super().__init__()
        self.p = positioner
        self._commands = commands
        self._sendid = 0
        self._replies = replies
        self.daemon = True
        self._homing_axes = set()
        self._quit = False
        self._instructions = []
        self.sleep_time = 0.05 if kwargs.get('sleep_time') == None else kwargs.get('sleep_time')


    def run(self):
        logging.info('monitor running as {}'.format(threading.currentThread().getName()))
        while True:
            self._check_homing()
            self._get_instructions()
            self._process_instructions()
            if self._check_for_quit():
                return
            time.sleep(self.sleep_time)


    def _check_homing(self):
        for axis in list(self._homing_axes):
            if self._status(axis)['at_target'] == True:
                self._disable_movement_on_axis(axis)
                self._remove_homing(axis)


    def _check_for_quit(self):
        if self._quit and len(self._homing_axes) == 0:
            return True
        return False


    def _get_instructions(self):
        try:
            message = self._commands.get_nowait()
        except Empty:
            message = None
        if message and message[0] > self._sendid:
            self._add_instruction(message)


    def _process_instructions(self):
        try:
            while True:
                message = self._instructions.pop(0)
                function_name = message[1]
                args = [] if len(message) < 3 else message[2]
                kwargs = {} if len(message) < 4 else message[3]
                f = getattr(self,message[1])
                for_reply = f(*args,**kwargs)
                logging.info('instruction {} has reply {}'.format(message,for_reply))
                if for_reply != None:
                    self._reply([message[0],for_reply])
                else:
                    self._reply([message[0]])
        except IndexError:
            pass


    def quit(self):
        self._quit = True


    def _add_instruction(self,message):
        self._sendid = message[0]
        self._instructions.append(message)


    def _reply(self,message):
        self._replies.put(message)


    def home_to_position_um(self,axis,position_um):
        axis_id = axis_map[axis]
        position = Pos(position_um,'um')

        self.p.setTargetPosition(axis_id,position.m())
        self.p.setTargetRange(axis_id,Pos(1,'um').m())
        self.p.startAutoMove(axis_id,True,False)
        self._add_homing(axis)
        self._enable_movement_on_axis(axis)


    def get_moving(self):
        return self._homing_axes


    def _status(self,axis):
        result = self.p.getAxisStatus(axis_map[axis])
        results = {
        'is_connected':result[0],
        'is_enabled':result[1],
        'is_moving':result[2],
        'at_target':result[3],
        'at_eotFwd':result[4],
        'at_eotBwd':result[5],
        'error':result[6]
        }
        return results


    def _add_homing(self,axis):
        self._homing_axes.add(axis)


    def _remove_homing(self,axis):
        self._homing_axes.remove(axis)


    def _enable_movement_on_axis(self,axis):
        self.p.setAxisOutput(axis_map[axis],True,False)


    def _disable_movement_on_axis(self,axis):
        self.p.setAxisOutput(axis_map[axis],False,False)